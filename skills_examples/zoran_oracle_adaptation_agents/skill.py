"""skill Oracle d'adaptation des agents — dimensionnement + réveil cohérent.

Mission : ZORAN_JOBS_20260521 · skill méta d'orchestration.
Inspiration : discipline ZORAN — un projet très ambitieux doit se dérouler de
A à Z, mais il ne doit JAMAIS tourner en boucle de façon incohérente. L'oracle
est le cerveau qui, à chaque cycle, décide : (1) combien d'agents mobiliser
— locaux (gratuits) ou API (coûteux) — et (2) s'il faut se réveiller au cycle
suivant ou s'arrêter.

Ce skill est une FONCTION PURE — il ne lance aucun agent, n'ouvre aucune API,
ne dort pas, ne se réveille pas tout seul. Il DÉCIDE. Le « wake-up permanent »,
le serveur léger qui héberge l'oracle et le pilotage depuis un téléphone sont
du HARNAIS agentique : ils rappellent l'oracle à chaque cycle et appliquent sa
décision. Un skill du runtime reste sans réseau ni process (invariant).

« Ne jamais s'arrêter » au sens naïf = emballement (runaway). La vraie valeur
d'un oracle est de tourner jusqu'à ce qu'il décide de s'arrêter pour une raison
COHÉRENTE. D'où 5 verdicts, dans cet ordre de priorité strict :

  1. TERMINE          — toutes les étapes sont faites. Succès.
  2. STOP_INCOHERENCE — la cohérence courante est passée sous le seuil :
                        continuer amplifierait l'erreur. C'est l'arrêt
                        prioritaire — le mode d'échec que l'oracle existe
                        pour empêcher.
  3. STOP_BUDGET      — l'enveloppe budgétaire est épuisée. Le budget est un
                        plafond de gouvernance : l'oracle ne bascule pas
                        silencieusement en « tout local gratuit » sans une
                        re-décision humaine.
  4. STOP_RESSOURCE   — il reste du travail mais aucun agent n'est mobilisable.
  5. CONTINUER        — sinon : on dimensionne les agents et on se réveille.

Allocation (verdict CONTINUER) : un agent par étape `a_faire`, locaux d'abord
(gratuits), puis API dans la limite finançable par le budget restant.

Contrat io :
    inputs  : {etapes:[{id,statut,charge}], agents_disponibles:{api,local},
               budget_restant, coherence_courante?, cycle?,
               cout_api_par_agent?, charge_par_agent?, seuil_coherence?,
               journal?}
    outputs : {verdict, reveil, progression_pct, etapes_restantes,
               agents_a_mobiliser:{api,local}, prochaines_etapes,
               cout_estime_cycle, budget_apres_cycle,
               cycles_restants_estimes, journal, explication, reference}
"""

from __future__ import annotations

import math

STATUTS = {"fait", "en_cours", "a_faire"}


def _nombre(valeur, nom: str, *, mini=None, maxi=None, strict_mini=False):
    """Convertit en float et vérifie les bornes. Lève ValueError sinon."""
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise ValueError(f"{nom} : nombre attendu")
    v = float(valeur)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError(f"{nom} : nombre fini attendu")
    if mini is not None and (v <= mini if strict_mini else v < mini):
        borne = ">" if strict_mini else ">="
        raise ValueError(f"{nom} : valeur {borne} {mini} attendue")
    if maxi is not None and v > maxi:
        raise ValueError(f"{nom} : valeur <= {maxi} attendue")
    return v


def _entier_positif(valeur, nom: str) -> int:
    """Convertit en int >= 0. Lève ValueError sinon."""
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        raise ValueError(f"{nom} : entier attendu")
    if valeur < 0:
        raise ValueError(f"{nom} : entier >= 0 attendu")
    return valeur


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}

    # --- étapes -------------------------------------------------------------
    etapes = inputs.get("etapes")
    if not isinstance(etapes, list) or not etapes:
        raise ValueError("etapes : liste non vide attendue")
    norm: list[dict] = []
    for i, et in enumerate(etapes):
        et = et or {}
        eid = str(et.get("id", "")).strip()
        if not eid:
            raise ValueError(f"etapes[{i}].id : identifiant non vide requis")
        statut = str(et.get("statut", "")).lower()
        if statut not in STATUTS:
            raise ValueError(
                f"etapes[{i}].statut : attendu l'un de {sorted(STATUTS)}")
        charge = _nombre(et.get("charge", 1.0), f"etapes[{i}].charge",
                         mini=0.0, strict_mini=True)
        norm.append({"id": eid, "statut": statut, "charge": charge})

    # --- agents disponibles -------------------------------------------------
    agents = inputs.get("agents_disponibles") or {}
    if not isinstance(agents, dict):
        raise ValueError("agents_disponibles : objet {api, local} attendu")
    api_dispo = _entier_positif(agents.get("api", 0), "agents_disponibles.api")
    local_dispo = _entier_positif(
        agents.get("local", 0), "agents_disponibles.local")

    # --- budget et paramètres ----------------------------------------------
    budget = _nombre(inputs.get("budget_restant", 0.0), "budget_restant",
                     mini=0.0)
    coherence = _nombre(inputs.get("coherence_courante", 1.0),
                        "coherence_courante", mini=0.0, maxi=1.0)
    seuil = _nombre(inputs.get("seuil_coherence", 0.3), "seuil_coherence",
                    mini=0.0, maxi=1.0)
    cout_api = _nombre(inputs.get("cout_api_par_agent", 1.0),
                       "cout_api_par_agent", mini=0.0, strict_mini=True)
    charge_agent = _nombre(inputs.get("charge_par_agent", 1.0),
                           "charge_par_agent", mini=0.0, strict_mini=True)
    cycle_brut = inputs.get("cycle", 1)
    if isinstance(cycle_brut, bool) or not isinstance(cycle_brut, int) \
            or cycle_brut < 1:
        raise ValueError("cycle : entier >= 1 attendu")
    cycle = cycle_brut
    journal = list(inputs.get("journal") or [])

    # --- mesure du réel -----------------------------------------------------
    charge_totale = sum(e["charge"] for e in norm)
    charge_faite = sum(e["charge"] for e in norm if e["statut"] == "fait")
    charge_restante = charge_totale - charge_faite
    a_faire = [e for e in norm if e["statut"] == "a_faire"]
    en_cours = [e for e in norm if e["statut"] == "en_cours"]
    etapes_restantes = len(a_faire) + len(en_cours)
    progression_pct = round(100.0 * charge_faite / charge_totale, 2)

    # --- verdict (ordre de priorité strict) --------------------------------
    agents_a_mobiliser = {"api": 0, "local": 0}
    cout_estime_cycle = 0.0
    prochaines_etapes: list[str] = []

    if etapes_restantes == 0:
        verdict = "TERMINE"
        explication = ("Toutes les étapes sont faites — le projet est mené à "
                       "son terme. Aucun cycle supplémentaire.")
    elif coherence < seuil:
        verdict = "STOP_INCOHERENCE"
        explication = (
            f"Cohérence courante {coherence:.2f} < seuil {seuil:.2f} : "
            "continuer amplifierait l'erreur. Arrêt pour re-cadrage humain.")
    elif budget <= 0:
        verdict = "STOP_BUDGET"
        explication = (
            "Enveloppe budgétaire épuisée. L'oracle ne bascule pas seul en "
            "exécution locale illimitée : une re-décision humaine est requise.")
    else:
        # Agents mobilisables : locaux d'abord, puis API finançable.
        api_finançable = min(api_dispo, int(budget // cout_api))
        besoin = len(a_faire)
        local_utilises = min(besoin, local_dispo)
        api_utilises = min(besoin - local_utilises, api_finançable)
        total_mobilises = local_utilises + api_utilises

        if besoin > 0 and total_mobilises == 0:
            verdict = "STOP_RESSOURCE"
            explication = (
                f"{besoin} étape(s) à faire mais aucun agent mobilisable "
                "(ni local disponible, ni API finançable). Arrêt.")
        else:
            verdict = "CONTINUER"
            agents_a_mobiliser = {"api": api_utilises, "local": local_utilises}
            cout_estime_cycle = round(api_utilises * cout_api, 4)
            prochaines_etapes = [e["id"] for e in a_faire[:total_mobilises]]
            if total_mobilises > 0:
                explication = (
                    f"{total_mobilises} agent(s) mobilisé(s) "
                    f"({local_utilises} local, {api_utilises} API) sur "
                    f"{besoin} étape(s) à faire. Réveil au cycle suivant.")
            else:
                explication = (
                    f"{len(en_cours)} étape(s) en cours, aucune étape neuve à "
                    "lancer ce cycle. Réveil pour attendre leur achèvement.")

    reveil = "continuer" if verdict == "CONTINUER" else "stop"
    budget_apres_cycle = round(budget - cout_estime_cycle, 4)

    # --- estimation des cycles restants (heuristique, charge / débit) ------
    debit_cycle = (agents_a_mobiliser["api"]
                   + agents_a_mobiliser["local"]) * charge_agent
    if verdict == "TERMINE":
        cycles_restants_estimes: int | None = 0
    elif verdict == "CONTINUER" and debit_cycle > 0:
        cycles_restants_estimes = math.ceil(charge_restante / debit_cycle)
    else:
        cycles_restants_estimes = None

    # --- journal cumulatif --------------------------------------------------
    entree = {
        "sequence": len(journal) + 1,
        "cycle": cycle,
        "verdict": verdict,
        "progression_pct": progression_pct,
        "agents_mobilises": dict(agents_a_mobiliser),
        "cout_cycle": cout_estime_cycle,
        "budget_apres": budget_apres_cycle,
        "coherence": coherence,
    }
    journal_maj = journal + [entree]

    return {
        "verdict": verdict,
        "reveil": reveil,
        "progression_pct": progression_pct,
        "etapes_restantes": etapes_restantes,
        "agents_a_mobiliser": agents_a_mobiliser,
        "prochaines_etapes": prochaines_etapes,
        "cout_estime_cycle": cout_estime_cycle,
        "budget_apres_cycle": budget_apres_cycle,
        "cycles_restants_estimes": cycles_restants_estimes,
        "journal": journal_maj,
        "explication": explication,
        "reference": ("Oracle d'adaptation ZORAN — dimensionnement d'agents + "
                      "réveil cohérent ; arrêt sur fin / incohérence / budget / "
                      "ressource"),
    }
