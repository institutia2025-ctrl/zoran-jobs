"""skill Calcul de la poussée active des terres (théorie de Rankine).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Géotechnique.
Source : théorie de Rankine (poussée active) ; cadre NF EN 1997-1 (Eurocode 7).

Calcule la poussée active des terres sur un écran vertical, terre-plein
horizontal, sol pulvérulent (sans cohésion), sans nappe :
    K_a = tan²(45° − φ/2)         (coefficient de poussée active)
    P_a = ½ · K_a · γ · H²        (poussée résultante par mètre linéaire)
La résultante s'applique au tiers inférieur de la hauteur (H/3 depuis le pied).

⚠️ MVP : sol pulvérulent (cohésion nulle), écran vertical, terre-plein
horizontal, statique, hors nappe phréatique. Ne traite ni la butée, ni la
poussée au repos, ni les surcharges, ni les sols cohérents, ni les effets
sismiques.
Loi 1 : γ (poids volumique) et φ (angle de frottement interne) proviennent de
l'étude géotechnique — ils sont fournis, jamais inventés.

Contrat io :
    inputs  : {hauteur_ecran_m, poids_volumique_kn_m3, angle_frottement_deg}
    outputs : {coefficient_ka, poussee_resultante_kn_ml, point_application_m, reference}
"""

from __future__ import annotations

import math


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    hauteur = inputs.get("hauteur_ecran_m")
    gamma = inputs.get("poids_volumique_kn_m3")
    phi = inputs.get("angle_frottement_deg")
    if not _nombre(hauteur) or hauteur <= 0:
        raise ValueError("hauteur_ecran_m : nombre > 0 requis")
    if not _nombre(gamma) or gamma <= 0:
        raise ValueError("poids_volumique_kn_m3 : nombre > 0 requis")
    if not _nombre(phi) or not (0.0 < phi < 90.0):
        raise ValueError("angle_frottement_deg : nombre dans ]0..90[ requis")

    hauteur = float(hauteur)
    ka = math.tan(math.radians(45.0 - float(phi) / 2.0)) ** 2
    poussee = 0.5 * ka * float(gamma) * hauteur ** 2
    return {
        "coefficient_ka": round(ka, 4),
        "poussee_resultante_kn_ml": round(poussee, 3),
        "point_application_m": round(hauteur / 3.0, 3),
        "reference": "Théorie de Rankine (poussée active) — cadre NF EN 1997-1",
    }
