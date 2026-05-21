"""skill Calcul de volume de terrassement (déblai + foisonnement).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc VRD.
Source : métré de terrassement — calcul géométrique + coefficient de foisonnement.

Calcule le volume en place d'un déblai (longueur × largeur × profondeur) et le
volume foisonné à évacuer (volume en place × coefficient de foisonnement).

⚠️ MVP : fouille à section rectangulaire constante. Ne traite pas les talus
(fruit de pente), les fouilles en gradins ni les terrains hétérogènes.
Loi 1 : le coefficient de foisonnement dépend de la nature du sol (étude
géotechnique). La valeur par défaut 1.25 est un ordre de grandeur indicatif
pour terrain ordinaire — à confirmer par l'étude de sol.

Contrat io :
    inputs  : {longueur_m, largeur_m, profondeur_m, coefficient_foisonnement?}
    outputs : {volume_en_place_m3, volume_foisonne_m3, coefficient_foisonnement, reference}
"""

from __future__ import annotations

FOISONNEMENT_DEFAUT = 1.25  # terrain ordinaire — ordre de grandeur indicatif


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    longueur = inputs.get("longueur_m")
    largeur = inputs.get("largeur_m")
    profondeur = inputs.get("profondeur_m")
    coef = inputs.get("coefficient_foisonnement", FOISONNEMENT_DEFAUT)

    for nom, val in (("longueur_m", longueur), ("largeur_m", largeur),
                     ("profondeur_m", profondeur)):
        if not _nombre(val) or val <= 0:
            raise ValueError(f"{nom} doit être un nombre > 0")
    if not _nombre(coef) or coef < 1.0:
        raise ValueError("coefficient_foisonnement doit être un nombre >= 1.0")

    volume_en_place = float(longueur) * float(largeur) * float(profondeur)
    volume_foisonne = volume_en_place * float(coef)
    return {
        "volume_en_place_m3": round(volume_en_place, 3),
        "volume_foisonne_m3": round(volume_foisonne, 3),
        "coefficient_foisonnement": float(coef),
        "reference": "Métré de terrassement — volume géométrique × coefficient de foisonnement",
    }
