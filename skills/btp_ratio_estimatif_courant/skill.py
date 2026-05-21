"""
skill btp_ratio_estimatif_courant — Estimation de coût par ratios courants.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (économie)
Référence : ratios publics courants (ordres de grandeur type SLPM / Batiprix,
France, hors foncier et VRD). Point d'entrée : run(inputs: dict) -> dict.

Donne une estimation de coût travaux par ratio €/m², avec fourchette
d'incertitude. Résultat INDICATIF — à recaler par un économiste de la
construction sur la base d'un programme détaillé.
"""

from __future__ import annotations

# Ratios indicatifs €/m² de surface (ordre de grandeur, hors foncier et VRD).
RATIOS = {
    "maison_individuelle": {"economique": 1300, "courant": 1700, "haut_de_gamme": 2500},
    "extension":           {"economique": 1700, "courant": 2200, "haut_de_gamme": 3200},
    "renovation_complete": {"economique": 900,  "courant": 1400, "haut_de_gamme": 2200},
    "renovation_legere":   {"economique": 400,  "courant": 700,  "haut_de_gamme": 1100},
    "logement_collectif":  {"economique": 1500, "courant": 1900, "haut_de_gamme": 2700},
}
STANDINGS = ("economique", "courant", "haut_de_gamme")
MARGE = 0.15  # incertitude +/- 15 %


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    ouvrage = str(inp.get("type_ouvrage", "")).lower()
    surface = float(inp.get("surface_m2", 0.0))
    standing = str(inp.get("niveau_standing", "courant")).lower()

    erreurs: list[str] = []
    if ouvrage not in RATIOS:
        erreurs.append(f"type d'ouvrage '{ouvrage}' inconnu (attendu : {sorted(RATIOS)})")
    if standing not in STANDINGS:
        erreurs.append(f"standing '{standing}' inconnu (attendu : {list(STANDINGS)})")
        standing = "courant"
    if surface <= 0:
        erreurs.append("surface invalide (doit être > 0)")

    if ouvrage not in RATIOS or surface <= 0:
        return {
            "erreurs": erreurs,
            "ratio_applique_eur_m2": 0,
            "cout_estime_eur": 0,
            "fourchette_basse_eur": 0,
            "fourchette_haute_eur": 0,
            "avertissement": "Estimation impossible — paramètres invalides.",
        }

    ratio = RATIOS[ouvrage][standing]
    cout = ratio * surface
    return {
        "erreurs": erreurs,
        "ratio_applique_eur_m2": ratio,
        "cout_estime_eur": round(cout),
        "fourchette_basse_eur": round(cout * (1 - MARGE)),
        "fourchette_haute_eur": round(cout * (1 + MARGE)),
        "avertissement": ("Estimation par ratio — ordre de grandeur indicatif, "
                          "hors foncier/VRD/aléas. À valider par un économiste "
                          "de la construction."),
    }
