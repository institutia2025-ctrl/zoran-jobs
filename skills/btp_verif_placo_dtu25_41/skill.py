"""
skill btp_verif_placo_dtu25_41 — Vérification d'ouvrage en plaques de plâtre.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (second œuvre)
Référence : NF DTU 25.41 (ouvrages en plaques de plâtre à faces cartonnées).
Point d'entrée : run(inputs: dict) -> dict.

Vérifie les paramètres clés d'une cloison/doublage : épaisseur de plaque,
entraxe des montants, entraxe de vissage, adéquation du type de plaque au local.
"""

from __future__ import annotations

ENTRAXE_MONTANTS_MAX_MM = 600.0   # entraxe courant maximal d'ossature
ENTRAXE_VIS_MAX_MM = 300.0        # pas de vissage maximal sur montant
EPAISSEUR_MIN_MM = 12.5           # plaque standard de cloison/doublage
TYPES_PLAQUE = {"standard", "hydrofuge", "feu", "haute_durete"}


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json. Retourne un verdict de conformité."""
    inp = inputs or {}
    epaisseur = float(inp.get("epaisseur_plaque_mm", 0.0))
    entraxe_montants = float(inp.get("entraxe_montants_mm", 0.0))
    entraxe_vis = float(inp.get("entraxe_vis_mm", 0.0))
    type_plaque = str(inp.get("type_plaque", "standard")).lower()
    local_humide = bool(inp.get("local_humide", False))

    nc: list[str] = []
    if epaisseur < EPAISSEUR_MIN_MM:
        nc.append(f"épaisseur plaque {epaisseur} mm < {EPAISSEUR_MIN_MM} mm minimum")
    if entraxe_montants > ENTRAXE_MONTANTS_MAX_MM:
        nc.append(f"entraxe montants {entraxe_montants} mm > "
                  f"{ENTRAXE_MONTANTS_MAX_MM} mm (DTU 25.41)")
    if entraxe_montants <= 0:
        nc.append("entraxe montants non renseigné")
    if entraxe_vis > ENTRAXE_VIS_MAX_MM:
        nc.append(f"entraxe vis {entraxe_vis} mm > {ENTRAXE_VIS_MAX_MM} mm "
                  f"(fixation insuffisante)")
    if type_plaque not in TYPES_PLAQUE:
        nc.append(f"type de plaque '{type_plaque}' inconnu (attendu : {sorted(TYPES_PLAQUE)})")
    if local_humide and type_plaque != "hydrofuge":
        nc.append("local humide : plaque hydrofuge (H1) exigée, type déclaré non hydrofuge")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "verdict": ("Ouvrage en plaques de plâtre conforme DTU 25.41."
                    if conforme else
                    f"{len(nc)} non-conformité(s) DTU 25.41."),
    }
