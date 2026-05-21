"""skill btp_diag_desordre_carrelage — diagnostic desordres carrelage colle.

Mission : ZORAN_JOBS_20260521 · Phase A BTP · AXE 4 Pathologies (5/5).
Sources :
  - NF DTU 52.2 (decembre 2009) : Pose collee revetements ceramiques.
  - Cahier du CSTB 3567 : Classification des locaux selon humidite (EA, EB, EB+, EC).

Approche checklist : evalue 5 desordres typiques observables visuellement
ou au son (decollement, faiencage joints, sonnant creux, fissures, taches).
Croise avec local (EB+/EC) pour identifier origine probable.

⚠️ MVP : oriente reparation. Une depose complete n'est ordonnee qu'apres
   sondage etendu (zone affectee, support sous-jacent, etancheite).

Contrat io :
    inputs : {
        "decollement_localise": bool,
        "sonnant_creux": bool,            # carreaux qui sonnent creux au choc
        "faiencage_joints": bool,         # fissures fines dans les joints
        "fissures_carreaux": bool,        # fissures traversant les carreaux
        "taches_humidite": bool,
        "classe_local"?: str              # "EA"/"EB"/"EB+"/"EC" (CSTB 3567)
    }
    outputs : {
        "nb_desordres": int,
        "gravite": str,
        "origine_probable": list[str],
        "actions_recommandees": list[str],
        "reference": str
    }
"""
from __future__ import annotations

CLASSES_LOCAL = {"EA", "EB", "EB+", "EC"}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    flags = {}
    for k in ("decollement_localise", "sonnant_creux", "faiencage_joints",
              "fissures_carreaux", "taches_humidite"):
        v = inputs.get(k)
        if not isinstance(v, bool):
            raise ValueError(f"{k} (bool) requis")
        flags[k] = v

    local = inputs.get("classe_local")
    if local is not None and local not in CLASSES_LOCAL:
        raise ValueError(f"classe_local doit etre dans {sorted(CLASSES_LOCAL)} (CSTB 3567)")

    nb = sum(flags.values())

    if flags["fissures_carreaux"] or (flags["decollement_localise"] and flags["sonnant_creux"]):
        gravite = "elevee"
    elif nb >= 3:
        gravite = "moyenne"
    elif nb >= 1:
        gravite = "faible"
    else:
        gravite = "faible"

    # Origine probable (raisonnement metier DTU 52.2)
    origines = []
    if flags["decollement_localise"] or flags["sonnant_creux"]:
        origines.append("Defaut adherence colle/support (planeite, humidite, primaire absent).")
    if flags["fissures_carreaux"]:
        origines.append("Mouvement du support (joints de fractionnement manquants ou retrait/dilatation).")
    if flags["faiencage_joints"]:
        origines.append("Mortier de jointoiement inadapte ou supports non desolidarises.")
    if flags["taches_humidite"] and (local in {"EB+", "EC"} if local else True):
        origines.append("Defaut etancheite sous carrelage (SPEC en local humide DTU 52.2 §3 + CSTB 3567).")
    if not origines:
        origines.append("Aucun desordre detecte — verifier que tous les criteres ont ete examines.")

    actions = []
    if flags["fissures_carreaux"] or flags["decollement_localise"]:
        actions.append("Sondage etendu : verifier % de zone affectee (>10% = depose generale conseille).")
    if flags["sonnant_creux"]:
        actions.append("Cartographie au son sur 100% de la zone : reporter les zones creuses sur plan.")
    if flags["taches_humidite"]:
        actions.append("Verifier presence SPEC ou DTU 52.2 §3.4 (locaux EB+/EC).")
    if not actions:
        actions.append("Surveillance simple, aucune action curative immediate.")

    return {
        "nb_desordres": nb,
        "gravite": gravite,
        "origine_probable": origines,
        "actions_recommandees": actions,
        "classe_local": local,
        "reference": "NF DTU 52.2 (decembre 2009) + Cahier CSTB 3567",
    }
