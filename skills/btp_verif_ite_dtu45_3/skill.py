"""
skill btp_verif_ite_dtu45_3 — Vérification d'une isolation thermique extérieure.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (second œuvre)
Référence : NF DTU 45.3 (isolation thermique par l'extérieur).
Point d'entrée : run(inputs: dict) -> dict.

Vérifie les paramètres de mise en œuvre d'une ITE collée-chevillée : nature et
épaisseur de l'isolant, densité de chevillage, taux d'encollage, support.
Les seuils sont des ordres de grandeur courants ; un avis technique (ATe/DTA)
ou un CCTP peut imposer des valeurs plus strictes.
"""

from __future__ import annotations

EPAISSEUR_MIN_MM = 80.0      # minimum de mise en œuvre courant
EPAISSEUR_PERF_MM = 100.0    # en deçà : performance thermique limite
CHEVILLES_MIN_M2 = 5.0       # densité minimale en partie courante
COLLAGE_MIN_PCT = 40.0       # taux d'encollage minimal (collé-calé)
ISOLANTS = {"pse", "pse_graphite", "laine_de_roche", "fibre_de_bois", "polyurethane"}
SUPPORTS_OK = {"beton", "maconnerie", "maconnerie_enduite", "ancien_enduit_adherent"}


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json. Retourne un verdict de conformité."""
    inp = inputs or {}
    isolant = str(inp.get("type_isolant", "")).lower()
    epaisseur = float(inp.get("epaisseur_isolant_mm", 0.0))
    chevilles = float(inp.get("nb_chevilles_m2", 0.0))
    collage = float(inp.get("collage_pct", 0.0))
    support = str(inp.get("support", "")).lower()

    nc: list[str] = []
    avert: list[str] = []
    if isolant not in ISOLANTS:
        nc.append(f"isolant '{isolant}' inconnu (attendu : {sorted(ISOLANTS)})")
    if epaisseur < EPAISSEUR_MIN_MM:
        nc.append(f"épaisseur isolant {epaisseur} mm < {EPAISSEUR_MIN_MM} mm minimum")
    elif epaisseur < EPAISSEUR_PERF_MM:
        avert.append(f"épaisseur {epaisseur} mm < {EPAISSEUR_PERF_MM} mm : "
                     f"performance thermique limite")
    if chevilles < CHEVILLES_MIN_M2:
        nc.append(f"{chevilles} chevilles/m² < {CHEVILLES_MIN_M2} minimum (calé-chevillé)")
    if collage < COLLAGE_MIN_PCT:
        nc.append(f"surface encollée {collage}% < {COLLAGE_MIN_PCT}% minimum")
    if support not in SUPPORTS_OK:
        nc.append(f"support '{support}' non vérifié apte (attendu : {sorted(SUPPORTS_OK)})")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "avertissements": avert,
        "verdict": ("ITE conforme DTU 45.3 (collée-chevillée)."
                    if conforme else
                    f"{len(nc)} non-conformité(s) DTU 45.3."),
    }
