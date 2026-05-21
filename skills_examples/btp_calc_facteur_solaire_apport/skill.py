"""skill Calcul de l'apport solaire d'une baie vitrée.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Confort thermique.
Source : facteur solaire g d'un vitrage (NF EN 410) ; cadre confort d'été RE2020.

Calcule l'apport solaire instantané transmis par une baie :
    apport = surface_vitrage × facteur_solaire_g × irradiation
Le facteur solaire g (0 à 1) traduit la part d'énergie solaire transmise par le
vitrage ; l'irradiation est l'éclairement énergétique reçu (W/m²).

⚠️ MVP : apport instantané d'une baie, sans protection solaire mobile ni
masques. Ne calcule pas le risque de surchauffe global (indicateur DH de la
RE2020) — il faudrait l'inertie, la ventilation et l'occultation.
Loi 1 : g (fiche du vitrage) et l'irradiation sont fournis, jamais inventés.

Contrat io :
    inputs  : {surface_vitrage_m2, facteur_solaire_g, irradiation_w_m2}
    outputs : {apport_solaire_w, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    surface = inputs.get("surface_vitrage_m2")
    g = inputs.get("facteur_solaire_g")
    irradiation = inputs.get("irradiation_w_m2")

    if not _nombre(surface) or surface <= 0:
        raise ValueError("surface_vitrage_m2 : nombre > 0 requis")
    if not _nombre(g) or not (0.0 < g <= 1.0):
        raise ValueError("facteur_solaire_g : nombre dans ]0..1] requis")
    if not _nombre(irradiation) or irradiation < 0:
        raise ValueError("irradiation_w_m2 : nombre >= 0 requis")

    apport = float(surface) * float(g) * float(irradiation)
    return {
        "apport_solaire_w": round(apport, 1),
        "surface_vitrage_m2": float(surface),
        "facteur_solaire_g": float(g),
        "reference": "Facteur solaire g du vitrage (NF EN 410) — cadre confort d'été RE2020",
    }
