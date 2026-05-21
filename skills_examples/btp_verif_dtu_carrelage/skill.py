"""skill verif_dtu_carrelage — vérification conformité DTU 52.2.

Mission : ZORAN_JOBS_20260521 · Phase A BTP.
Source : NF DTU 52.2 (décembre 2009), pose collée revêtements céramiques.

Vérifie deux critères du DTU 52.2 sur des mesures de support :
- planéité : 5 mm max sous la règle de 2 m, 2 mm max sous le règlet de 0,20 m
- verticalité (sur paroi) : 5 mm max sur 2,50 m

Loi 1 : tolérances exactes du DTU 52.2 (lot08), pas d'invention.

Contrat io :
    inputs  : {
        "planeite_2m_mm": float,         # mesure planéité sur règle 2 m, en mm
        "planeite_20cm_mm": float,       # mesure planéité sur règlet 0,20 m, en mm
        "verticalite_250cm_mm"?: float   # optionnel, si pose murale
    }
    outputs : {
        "conforme": bool,
        "violations": list[str],
        "reference": "NF DTU 52.2 (decembre 2009)"
    }
"""

from __future__ import annotations

# Seuils issus du DTU 52.2 §3 (lot08_revetements/dtu_52_2.md)
PLANEITE_2M_MAX_MM = 5.0
PLANEITE_20CM_MAX_MM = 2.0
VERTICALITE_250CM_MAX_MM = 5.0


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    violations: list[str] = []

    p2m = inputs.get("planeite_2m_mm")
    if not isinstance(p2m, (int, float)):
        raise ValueError("planeite_2m_mm requis (nombre, en mm)")
    if p2m > PLANEITE_2M_MAX_MM:
        violations.append(
            f"Planeite regle 2m : {p2m} mm > {PLANEITE_2M_MAX_MM} mm (DTU 52.2 §3)"
        )

    p20 = inputs.get("planeite_20cm_mm")
    if not isinstance(p20, (int, float)):
        raise ValueError("planeite_20cm_mm requis (nombre, en mm)")
    if p20 > PLANEITE_20CM_MAX_MM:
        violations.append(
            f"Planeite reglet 0,20m : {p20} mm > {PLANEITE_20CM_MAX_MM} mm (DTU 52.2 §3)"
        )

    if (vert := inputs.get("verticalite_250cm_mm")) is not None:
        if not isinstance(vert, (int, float)):
            raise ValueError("verticalite_250cm_mm si fourni doit etre un nombre")
        if vert > VERTICALITE_250CM_MAX_MM:
            violations.append(
                f"Verticalite sur 2,50m : {vert} mm > {VERTICALITE_250CM_MAX_MM} mm (DTU 52.2 §3)"
            )

    return {
        "conforme": len(violations) == 0,
        "violations": violations,
        "reference": "NF DTU 52.2 (decembre 2009)",
    }
