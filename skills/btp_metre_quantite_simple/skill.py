"""
skill btp_metre_quantite_simple — Métré de quantités par calcul géométrique.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (économie)
Point d'entrée : run(inputs: dict) -> dict.

Calcule des quantités élémentaires de métré (surfaces, volumes, linéaires) à
partir d'éléments géométriques simples, et agrège les totaux par catégorie.
"""

from __future__ import annotations


def _quantite(element: dict) -> tuple[str | None, float]:
    """Retourne (catégorie, quantité) pour un élément géométrique. Unités : m."""
    typ = str(element.get("type", "")).lower()
    d = element.get("dimensions") or {}
    longueur = float(d.get("longueur", 0.0))
    largeur = float(d.get("largeur", 0.0))
    hauteur = float(d.get("hauteur", 0.0))
    base = float(d.get("base", 0.0))
    if typ == "surface_rect":
        return "surface", longueur * largeur
    if typ == "surface_triangle":
        return "surface", 0.5 * base * hauteur
    if typ == "volume_box":
        return "volume", longueur * largeur * hauteur
    if typ == "lineaire":
        return "lineaire", longueur
    return None, 0.0


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    elements = inp.get("elements") or []

    detail: list[dict] = []
    total = {"surface": 0.0, "volume": 0.0, "lineaire": 0.0}
    erreurs: list[str] = []
    for i, element in enumerate(elements):
        element = element or {}
        categorie, quantite = _quantite(element)
        if categorie is None:
            erreurs.append(f"élément #{i} : type '{element.get('type')}' inconnu "
                           f"(attendu : surface_rect, surface_triangle, "
                           f"volume_box, lineaire)")
            continue
        total[categorie] += quantite
        detail.append({"index": i, "type": element.get("type"),
                        "categorie": categorie, "quantite": round(quantite, 3)})

    return {
        "detail": detail,
        "total_surface_m2": round(total["surface"], 3),
        "total_volume_m3": round(total["volume"], 3),
        "total_lineaire_ml": round(total["lineaire"], 3),
        "nb_elements": len(elements),
        "erreurs": erreurs,
    }
