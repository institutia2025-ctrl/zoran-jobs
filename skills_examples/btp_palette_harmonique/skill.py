"""skill palette_harmonique — décorateur / coloriste.

Mission : ZORAN_JOBS_20260521 · Phase A BTP.
Produit une palette de 3 couleurs harmoniques en HSL à partir d'une teinte de base.
Théorie : harmonie triadique (teintes équidistantes sur le cercle chromatique de 120°).

Contrat io :
    inputs  : {"hue": int [0..359], "saturation"?: int [0..100], "lightness"?: int [0..100]}
    outputs : {"palette": list[dict("hue","saturation","lightness")], "harmony": "triadique"}
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Génère 3 teintes triadiques. Loi 1 : aucune invention, théorie HSL pure."""
    inputs = inputs or {}
    hue = inputs.get("hue")
    if not isinstance(hue, int) or not (0 <= hue <= 359):
        raise ValueError("hue doit etre un entier dans [0..359]")
    s = inputs.get("saturation", 60)
    lum = inputs.get("lightness", 50)
    if not (0 <= s <= 100) or not (0 <= lum <= 100):
        raise ValueError("saturation et lightness doivent etre dans [0..100]")

    palette = [{"hue": (hue + 120 * i) % 360, "saturation": s, "lightness": lum} for i in range(3)]
    return {"palette": palette, "harmony": "triadique"}
