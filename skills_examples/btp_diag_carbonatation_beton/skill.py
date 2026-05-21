"""skill btp_diag_carbonatation_beton — diagnostic carbonatation beton arme.

Mission : ZORAN_JOBS_20260521 · Phase A BTP · AXE 4 Pathologies (3/5).
Sources :
  - NF EN 14630 : Methode de mesure de la profondeur de carbonatation par
    indicateur colore (phenolphtaleine). Mesure in situ d'une carotte.
  - NF EN 1992-1-1 (EC2) §4.4 : enrobages nominaux selon classe d'exposition.
  - NF EN 206-1 : classes d'exposition XC1 a XC4 (carbonatation).

Principe : la corrosion des armatures par carbonatation devient possible
quand le front de carbonatation atteint l'armature (depassivation du pH).
Le critere est donc : profondeur_carbonatation versus enrobage.

⚠️ MVP : compare deux mesures simples. Ne predit pas la cinetique future
   (modele de Tuutti ou abaques k necessaires pour projection 50 ans).

Contrat io :
    inputs : {
        "profondeur_carbonatation_mm": float,    # mesure phenolphtaleine (EN 14630)
        "enrobage_nominal_mm": float,            # enrobage de l'armature (plan, sondage)
        "classe_exposition": str                 # "XC1", "XC2", "XC3", "XC4" (EN 206-1)
    }
    outputs : {
        "depassivation_atteinte": bool,           # carbonatation >= enrobage
        "marge_mm": float,                        # enrobage - carbonatation (negatif = depassivation)
        "verdict": str,
        "actions_recommandees": list[str],
        "reference": str
    }
"""
from __future__ import annotations

CLASSES_XC = {"XC1", "XC2", "XC3", "XC4"}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    pc = inputs.get("profondeur_carbonatation_mm")
    enrobage = inputs.get("enrobage_nominal_mm")
    classe = inputs.get("classe_exposition")

    for nom, val in [("profondeur_carbonatation_mm", pc), ("enrobage_nominal_mm", enrobage)]:
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"{nom} doit etre un nombre >= 0 (en mm)")
    if classe not in CLASSES_XC:
        raise ValueError(f"classe_exposition doit etre dans {sorted(CLASSES_XC)} (NF EN 206-1)")

    marge = enrobage - pc
    depassivation = marge <= 0

    if depassivation:
        verdict = "DEPASSIVATION ATTEINTE : risque de corrosion active des armatures"
        actions = [
            "Sondage etendu pour cartographier la zone carbonatee.",
            "Mesure potentiel d'electrode (NF EN 1504-9) pour confirmer activite corrosion.",
            "Reparation : decapage + passivation + mortier de reparation (NF EN 1504-3).",
        ]
    elif marge < 5:
        verdict = f"Marge critique {marge:.1f} mm — reparation preventive recommandee"
        actions = [
            "Programmer reparation preventive sous 12-24 mois.",
            "Mesure potentiel d'electrode pour anticiper.",
        ]
    elif marge < 10:
        verdict = f"Marge faible {marge:.1f} mm — surveillance renforcee"
        actions = [
            "Re-mesure carbonatation tous les 5 ans.",
            "Verifier etat de la peau du beton (microfissuration accelere la carbonatation).",
        ]
    else:
        verdict = f"OK : marge confortable {marge:.1f} mm"
        actions = ["Suivi normal selon cycle d'inspection prevu (typiquement 10 ans)."]

    return {
        "depassivation_atteinte": depassivation,
        "marge_mm": round(marge, 2),
        "verdict": verdict,
        "actions_recommandees": actions,
        "classe_exposition": classe,
        "reference": "NF EN 14630 (mesure) + NF EN 1992-1-1 §4.4 (enrobages) + NF EN 206-1 (classes)",
    }
