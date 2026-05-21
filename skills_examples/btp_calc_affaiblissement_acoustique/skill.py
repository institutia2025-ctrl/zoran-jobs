"""skill Calcul d'affaiblissement acoustique d'une paroi — loi de masse.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Acoustique.
Source : loi de masse (acoustique du bâtiment), méthode NF EN 12354-1.

Estime l'indice d'affaiblissement acoustique R d'une paroi simple homogène,
dans le domaine gouverné par la masse :
    R = 20 · log10(m × f) − 47   (dB)
avec m = masse surfacique (kg/m²) et f = fréquence (Hz).

⚠️ MVP : loi de masse seule — valable dans la zone « masse », hors fréquence
critique (coïncidence) et hors résonances. Ne traite pas les parois doubles
(système masse-ressort-masse) ni les transmissions latérales (flanking).
Loi 1 : la loi de masse est une formule publique ; m et f sont fournis.

Contrat io :
    inputs  : {masse_surfacique_kg_m2, frequence_hz}
    outputs : {affaiblissement_db, domaine, reference}
"""

from __future__ import annotations

import math


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    masse = inputs.get("masse_surfacique_kg_m2")
    freq = inputs.get("frequence_hz")
    if not _nombre(masse) or masse <= 0:
        raise ValueError("masse_surfacique_kg_m2 doit être un nombre > 0")
    if not _nombre(freq) or freq <= 0:
        raise ValueError("frequence_hz doit être un nombre > 0")

    affaiblissement = 20.0 * math.log10(float(masse) * float(freq)) - 47.0
    return {
        "affaiblissement_db": round(affaiblissement, 1),
        "domaine": "loi de masse (zone gouvernée par la masse)",
        "reference": "Loi de masse acoustique — méthode NF EN 12354-1",
    }
