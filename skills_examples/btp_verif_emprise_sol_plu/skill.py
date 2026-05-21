"""skill Vérification de l'emprise au sol vis-à-vis du PLU.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Réglementation.
Source : Plan Local d'Urbanisme (PLU) — coefficient d'emprise au sol.

Vérifie que l'emprise au sol d'un projet respecte le coefficient d'emprise au
sol (CES) maximal fixé par le PLU :
    ratio_emprise = emprise_au_sol / surface_terrain
    conforme si ratio_emprise ≤ CES_max

⚠️ MVP : vérifie le seul ratio d'emprise au sol. Ne vérifie ni les autres
règles du PLU (hauteur, prospects, recul, stationnement, espaces verts), ni les
servitudes.
Loi 1 : le CES_max provient du règlement du PLU de la zone — il est fourni.

Contrat io :
    inputs  : {emprise_au_sol_m2, surface_terrain_m2, ces_max}
    outputs : {ratio_emprise, ces_max, emprise_max_autorisee_m2, conforme, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    emprise = inputs.get("emprise_au_sol_m2")
    terrain = inputs.get("surface_terrain_m2")
    ces_max = inputs.get("ces_max")

    if not _nombre(emprise) or emprise <= 0:
        raise ValueError("emprise_au_sol_m2 : nombre > 0 requis")
    if not _nombre(terrain) or terrain <= 0:
        raise ValueError("surface_terrain_m2 : nombre > 0 requis")
    if not _nombre(ces_max) or not (0.0 < ces_max <= 1.0):
        raise ValueError("ces_max : nombre dans ]0..1] requis (coefficient du PLU)")

    ratio = float(emprise) / float(terrain)
    emprise_max = float(ces_max) * float(terrain)
    conforme = ratio <= float(ces_max)
    return {
        "ratio_emprise": round(ratio, 4),
        "ces_max": float(ces_max),
        "emprise_max_autorisee_m2": round(emprise_max, 2),
        "conforme": conforme,
        "verdict": ("Emprise au sol conforme au PLU." if conforme
                    else "Emprise au sol dépassée — projet non conforme au PLU."),
        "reference": "PLU — coefficient d'emprise au sol (CES)",
    }
