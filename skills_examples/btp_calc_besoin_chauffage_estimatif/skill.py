"""skill Besoin de chauffage annuel estimatif.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Confort thermique.
Source : méthode des degrés-jours unifiés (DJU).

Estime le besoin de chauffage annuel d'un bâtiment :
    besoin = déperditions_totales × DJU × 24 / 1000   (kWh/an)
avec déperditions_totales le coefficient global de déperdition (W/K) et DJU les
degrés-jours unifiés de la zone climatique.

⚠️ MVP : estimation par degrés-jours — déperditions par transmission + ventilation
agrégées dans le coefficient fourni. Ne tient pas compte des apports gratuits
(solaire, internes) ni du rendement de l'installation : c'est un besoin BRUT,
pas une consommation. Pour une consommation, appliquer apports et rendement.
Loi 1 : déperditions et DJU sont fournis (DJU dépend de la zone climatique).

Contrat io :
    inputs  : {deperditions_totales_w_k, dju}
    outputs : {besoin_chauffage_kwh_an, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    deperditions = inputs.get("deperditions_totales_w_k")
    dju = inputs.get("dju")
    if not _nombre(deperditions) or deperditions <= 0:
        raise ValueError("deperditions_totales_w_k : nombre > 0 requis")
    if not _nombre(dju) or dju <= 0:
        raise ValueError("dju : nombre > 0 requis (degrés-jours de la zone climatique)")

    besoin = float(deperditions) * float(dju) * 24.0 / 1000.0
    return {
        "besoin_chauffage_kwh_an": round(besoin, 1),
        "deperditions_totales_w_k": float(deperditions),
        "dju": float(dju),
        "reference": "Méthode des degrés-jours unifiés (DJU) — besoin de chauffage brut",
    }
