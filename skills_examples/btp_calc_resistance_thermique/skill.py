"""skill Calcul de résistance thermique de paroi — niveau ingénierie thermique.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Thermique.
Source : NF EN ISO 6946 (résistance thermique des composants de bâtiment).

Calcule la résistance thermique totale R d'une paroi multicouche :
R = Rsi + Σ(e_i / λ_i) + Rse, et le coefficient U = 1 / R.

⚠️ MVP : ne traite pas les lames d'air non ventilées, les ponts thermiques
intégrés, ni les hétérogénéités latérales (méthode des isothermes) — ces cas
relèvent d'un bureau d'études thermiques.
Loi 1 : aucune valeur fabriquée — Rsi/Rse sont les valeurs conventionnelles de
la NF EN ISO 6946 ; les conductivités λ sont fournies par l'appelant.

Contrat io :
    inputs  : {couches:[{materiau,epaisseur_m,lambda_w_mk}], rsi?, rse?}
    outputs : {resistance_totale_m2k_w, coefficient_u_w_m2k, detail, reference}
"""

from __future__ import annotations

# Résistances superficielles conventionnelles (NF EN ISO 6946, flux horizontal).
RSI_DEFAUT = 0.13  # m².K/W — résistance superficielle intérieure
RSE_DEFAUT = 0.04  # m².K/W — résistance superficielle extérieure


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    couches = inputs.get("couches")
    if not isinstance(couches, list) or not couches:
        raise ValueError("couches : liste non vide de couches attendue")
    rsi = float(inputs.get("rsi", RSI_DEFAUT))
    rse = float(inputs.get("rse", RSE_DEFAUT))
    if rsi < 0 or rse < 0:
        raise ValueError("rsi/rse : valeurs négatives interdites")

    detail: list[dict] = []
    r_couches = 0.0
    for i, couche in enumerate(couches):
        couche = couche or {}
        epaisseur = float(couche.get("epaisseur_m", 0.0))
        lam = float(couche.get("lambda_w_mk", 0.0))
        if epaisseur <= 0:
            raise ValueError(f"couche #{i} : epaisseur_m doit être > 0")
        if lam <= 0:
            raise ValueError(f"couche #{i} : lambda_w_mk doit être > 0")
        r = epaisseur / lam
        r_couches += r
        detail.append({"materiau": couche.get("materiau", f"couche_{i}"),
                       "resistance_m2k_w": round(r, 4)})

    r_total = rsi + r_couches + rse
    return {
        "resistance_totale_m2k_w": round(r_total, 4),
        "coefficient_u_w_m2k": round(1.0 / r_total, 4),
        "detail": detail,
        "reference": "NF EN ISO 6946 (résistance thermique des parois)",
    }
