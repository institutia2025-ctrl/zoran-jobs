"""skill Calcul de débit d'eaux pluviales de toiture.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Enveloppe.
Source : NF DTU 60.11 — réseaux d'évacuation des eaux pluviales.

Calcule le débit d'eaux pluviales à évacuer d'une toiture :
    Q = surface_en_plan × intensité_pluviale     (l/s)

⚠️ MVP : débit sur surface projetée en plan. Ne dimensionne pas finement les
chéneaux et descentes (tableaux DTU 60.11 selon forme, pente, type de moignon).
Loi 1 : l'intensité pluviale dépend de la région. La valeur par défaut
0.05 l/s/m² (3 l/min/m²) est la base de calcul courante du DTU 60.11,
surchargeable selon les données pluviométriques locales.

Contrat io :
    inputs  : {surface_toiture_m2, intensite_pluviale_l_s_m2?}
    outputs : {debit_ep_l_s, surface_toiture_m2, intensite_pluviale_l_s_m2, reference}
"""

from __future__ import annotations

INTENSITE_DEFAUT = 0.05  # l/s/m² — base de calcul courante DTU 60.11 (3 l/min/m²)


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    surface = inputs.get("surface_toiture_m2")
    intensite = inputs.get("intensite_pluviale_l_s_m2", INTENSITE_DEFAUT)

    if not _nombre(surface) or surface <= 0:
        raise ValueError("surface_toiture_m2 : nombre > 0 requis")
    if not _nombre(intensite) or intensite <= 0:
        raise ValueError("intensite_pluviale_l_s_m2 : nombre > 0 requis")

    debit = float(surface) * float(intensite)
    return {
        "debit_ep_l_s": round(debit, 3),
        "surface_toiture_m2": float(surface),
        "intensite_pluviale_l_s_m2": float(intensite),
        "reference": "NF DTU 60.11 — évacuation des eaux pluviales (Q = S × i)",
    }
