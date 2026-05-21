"""skill Calcul de charge de neige sur toiture.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Charges.
Source : NF EN 1991-1-3 (Eurocode 1 — actions sur les structures : neige).

Calcule la charge de neige sur une toiture :
    s = μi × Ce × Ct × sk
avec μi coefficient de forme, Ce coefficient d'exposition, Ct coefficient
thermique, sk charge de neige au sol (kN/m²).

⚠️ MVP : toiture à versant unique, coefficient de forme μ1 (NF EN 1991-1-3
§5.3.2). Ne traite pas les accumulations (toitures multiples, redans, obstacles)
ni la neige glissante.
Loi 1 : sk dépend de la région et de l'altitude — il est FOURNI par l'appelant
(carte de l'Annexe Nationale NF EN 1991-1-3). Aucune valeur de sk n'est inventée.

Contrat io :
    inputs  : {charge_sol_sk_kn_m2, angle_toiture_deg, coef_exposition?, coef_thermique?}
    outputs : {charge_neige_kn_m2, mu_forme, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _mu1(angle_deg: float) -> float:
    """Coefficient de forme μ1 — toiture à versant unique (NF EN 1991-1-3 §5.3.2)."""
    if angle_deg <= 30.0:
        return 0.8
    if angle_deg < 60.0:
        return 0.8 * (60.0 - angle_deg) / 30.0
    return 0.0


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    sk = inputs.get("charge_sol_sk_kn_m2")
    angle = inputs.get("angle_toiture_deg")
    ce = inputs.get("coef_exposition", 1.0)
    ct = inputs.get("coef_thermique", 1.0)

    if not _nombre(sk) or sk <= 0:
        raise ValueError("charge_sol_sk_kn_m2 > 0 requis (carte NF EN 1991-1-3)")
    if not _nombre(angle) or not (0.0 <= angle <= 90.0):
        raise ValueError("angle_toiture_deg attendu dans [0..90]")
    if not _nombre(ce) or ce <= 0 or not _nombre(ct) or ct <= 0:
        raise ValueError("coef_exposition et coef_thermique doivent être > 0")

    mu = _mu1(float(angle))
    charge = mu * float(ce) * float(ct) * float(sk)
    return {
        "charge_neige_kn_m2": round(charge, 3),
        "mu_forme": round(mu, 3),
        "reference": "NF EN 1991-1-3 §5.2/§5.3 (charge de neige sur toiture)",
    }
