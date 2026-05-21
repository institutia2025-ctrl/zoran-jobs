"""skill btp_diag_desordre_carrelage — diagnostic desordres carrelage (uplift v1.1).

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 4 Patho (5/5, v1.1 uplift).
Sources :
  - NF DTU 52.2 (decembre 2009) §3.4 : pose collee revetements ceramiques
    avec exigences SPEC en locaux humides.
  - Cahier CSTB 3567 : Classification des locaux EA/EB/EB+/EC.
  - Retour experience AQC : seuils % surface affectee pour decision
    reprise locale vs depose generale (10% standard pratique).

Approche v1.1 :
  - Checklist 5 desordres visuels/auditifs
  - + surface_affectee_pct (cle pour decision)
  - + presence SPEC (Système d'Étanchéité Liquide) si local EB+/EC
  - + verdict type_intervention ("surveillance"|"reprise_locale"|"depose_generale")
  - + croisement origine probable (DTU 52.2 §3)

⚠️ MVP : checklist + carto. Une vraie cartographie demande releve in situ.

Contrat io :
    inputs : {
        "decollement_localise": bool,
        "sonnant_creux": bool,
        "faiencage_joints": bool,
        "fissures_carreaux": bool,
        "taches_humidite": bool,
        "surface_affectee_pct"?: float,        # % surface ou desordre observe
        "classe_local"?: str,                  # "EA"/"EB"/"EB+"/"EC" (CSTB 3567)
        "presence_spec"?: bool                 # SPEC pose si local EB+/EC
    }
    outputs : {
        "nb_desordres": int,
        "gravite": str,
        "type_intervention": str,              # "surveillance"|"reprise_locale"|"depose_generale"|"reprise_etancheite"
        "origine_probable": list[str],
        "actions_recommandees": list[str],
        "spec_obligatoire": bool,
        "reference": str
    }
"""
from __future__ import annotations

CLASSES_LOCAL = {"EA", "EB", "EB+", "EC"}
CLASSES_HUMIDES = {"EB+", "EC"}  # SPEC obligatoire DTU 52.2 §3.4
SEUIL_DEPOSE_PCT = 10.0  # retour experience AQC, peut etre ajuste


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

    surf_pct = inputs.get("surface_affectee_pct")
    if surf_pct is not None:
        if not isinstance(surf_pct, (int, float)) or not (0.0 <= surf_pct <= 100.0):
            raise ValueError("surface_affectee_pct dans [0..100] si fourni")

    spec = inputs.get("presence_spec")
    if spec is not None and not isinstance(spec, bool):
        raise ValueError("presence_spec (bool) requis si fourni")

    nb = sum(flags.values())

    # SPEC obligatoire selon DTU 52.2 §3.4 si local humide
    spec_obligatoire = local in CLASSES_HUMIDES
    spec_manquant = spec_obligatoire and spec is False

    # Type intervention (croisement nb desordres + surface + SPEC)
    if spec_manquant and flags["taches_humidite"]:
        type_int = "reprise_etancheite"  # priorite : refaire l'etancheite
    elif surf_pct is not None and surf_pct >= SEUIL_DEPOSE_PCT:
        type_int = "depose_generale"
    elif flags["fissures_carreaux"] or (flags["decollement_localise"] and flags["sonnant_creux"]):
        type_int = "reprise_locale"
    elif nb >= 3:
        type_int = "reprise_locale"
    elif nb >= 1:
        type_int = "surveillance"
    else:
        type_int = "surveillance"

    # Gravite
    if type_int in ("depose_generale", "reprise_etancheite"):
        gravite = "elevee"
    elif type_int == "reprise_locale":
        gravite = "moyenne"
    else:
        gravite = "faible"

    # Origine probable
    origines = []
    if flags["decollement_localise"] or flags["sonnant_creux"]:
        origines.append("Defaut adherence colle/support (planeite, humidite support, primaire absent).")
    if flags["fissures_carreaux"]:
        origines.append("Mouvement du support (joints de fractionnement manquants ou retrait/dilatation).")
    if flags["faiencage_joints"]:
        origines.append("Mortier de jointoiement inadapte ou supports non desolidarises.")
    if flags["taches_humidite"]:
        if spec_manquant:
            origines.append("Defaut etancheite SPEC absente en local humide (DTU 52.2 §3.4).")
        else:
            origines.append("Infiltration ponctuelle ou condensation (verifier ventilation).")
    if not origines:
        origines.append("Aucun desordre detecte — verifier que tous les criteres ont ete examines.")

    actions = []
    if type_int == "depose_generale":
        actions.append(f"Surface affectee {surf_pct}% >= {SEUIL_DEPOSE_PCT}% (seuil AQC) : depose generale recommandee.")
    if type_int == "reprise_etancheite":
        actions.append("Refaire SPEC selon DTU 52.2 §3.4 avant toute repose de carrelage.")
    if flags["sonnant_creux"]:
        actions.append("Cartographie au son sur 100% de la zone : reporter les zones creuses sur plan.")
    if flags["fissures_carreaux"]:
        actions.append("Sondage destructif (depose 1-2 carreaux) pour confirmer origine.")
    if spec_obligatoire and spec is None:
        actions.append(f"Local {local} : verifier presence SPEC (info manquante).")
    if not actions:
        actions.append("Surveillance simple, photographier date + reverifier dans 6-12 mois.")

    return {
        "nb_desordres": nb,
        "gravite": gravite,
        "type_intervention": type_int,
        "origine_probable": origines,
        "actions_recommandees": actions,
        "spec_obligatoire": spec_obligatoire,
        "classe_local": local,
        "reference": "NF DTU 52.2 §3.4 + Cahier CSTB 3567 + retour experience AQC (seuil 10%)",
    }
