"""skill Vérification de pente de toiture / couverture.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Enveloppe.
Source : NF DTU série 40 (travaux de couverture).

Vérifie que la pente d'une toiture est compatible avec la pente minimale
admissible du procédé de couverture. La pente minimale dépend du matériau, de
la zone climatique et de la situation (protégée / normale / exposée) : elle est
fournie par l'appelant d'après le tableau du DTU 40 applicable.

⚠️ MVP : compare la pente posée à une pente minimale fournie. Ne contient pas
les abaques DTU 40 (matériau × zone × situation) — c'est l'appelant qui les lit.
Loi 1 : la pente minimale n'est pas inventée — elle est fournie d'après le DTU 40.

Contrat io :
    inputs  : {pente_posee_pct, pente_min_dtu_pct, materiau?}
    outputs : {conforme, pente_posee_pct, pente_min_dtu_pct, marge_pct, verdict, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    posee = inputs.get("pente_posee_pct")
    mini = inputs.get("pente_min_dtu_pct")
    materiau = str(inputs.get("materiau", "(non précisé)"))

    if not _nombre(posee) or posee < 0:
        raise ValueError("pente_posee_pct : nombre >= 0 requis")
    if not _nombre(mini) or mini <= 0:
        raise ValueError("pente_min_dtu_pct : nombre > 0 requis (tableau DTU 40)")

    posee = float(posee)
    mini = float(mini)
    conforme = posee >= mini
    return {
        "conforme": conforme,
        "pente_posee_pct": posee,
        "pente_min_dtu_pct": mini,
        "marge_pct": round(posee - mini, 2),
        "materiau": materiau,
        "verdict": ("Pente de couverture conforme au DTU 40."
                    if conforme else
                    "Pente insuffisante — risque d'infiltration (DTU 40)."),
        "reference": "NF DTU série 40 — pente minimale selon matériau / zone / situation",
    }
