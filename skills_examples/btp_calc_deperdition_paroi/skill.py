"""skill Calcul de déperdition thermique d'une paroi — niveau ingénierie thermique.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Thermique.
Source : NF EN ISO 13789 (coefficient de transfert thermique par transmission).

Calcule le flux de déperdition par transmission d'une paroi :
Φ = U × S × ΔT, avec U = 1 / R lorsque la résistance est fournie.

⚠️ MVP : déperdition par transmission surfacique uniquement — n'inclut ni les
ponts thermiques (voir btp_calc_pont_thermique_lineaire) ni les déperditions
par renouvellement d'air.
Loi 1 : aucune valeur fabriquée — U ou R, surface et ΔT sont fournis.

Contrat io :
    inputs  : {coefficient_u_w_m2k?, resistance_m2k_w?, surface_m2, delta_temperature_k}
    outputs : {deperdition_w, coefficient_u_w_m2k, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    surface = inputs.get("surface_m2")
    delta_t = inputs.get("delta_temperature_k")
    if not _nombre(surface) or surface <= 0:
        raise ValueError("surface_m2 doit être un nombre > 0")
    if not _nombre(delta_t):
        raise ValueError("delta_temperature_k : nombre attendu")
    surface = float(surface)
    delta_t = float(delta_t)

    u = inputs.get("coefficient_u_w_m2k")
    r = inputs.get("resistance_m2k_w")
    if _nombre(u):
        u = float(u)
        if u <= 0:
            raise ValueError("coefficient_u_w_m2k doit être > 0")
    elif _nombre(r):
        r = float(r)
        if r <= 0:
            raise ValueError("resistance_m2k_w doit être > 0")
        u = 1.0 / r
    else:
        raise ValueError("fournir coefficient_u_w_m2k ou resistance_m2k_w")

    deperdition = u * surface * delta_t
    return {
        "deperdition_w": round(deperdition, 2),
        "coefficient_u_w_m2k": round(u, 4),
        "reference": "NF EN ISO 13789 (déperditions par transmission)",
    }
