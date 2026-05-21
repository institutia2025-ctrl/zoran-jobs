"""
skill btp_verif_menuiserie_pvc_dtu36_5 — Vérification de pose de fenêtre PVC.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (second œuvre)
Référence : NF DTU 36.5 (mise en œuvre des fenêtres et portes extérieures).
Point d'entrée : run(inputs: dict) -> dict.

Vérifie une pose de menuiserie : nombre de points de fixation au regard de
l'entraxe maximal admis, calage périphérique, étanchéité air/eau.
"""

from __future__ import annotations

import math

ENTRAXE_FIXATION_MAX_MM = 800.0   # entraxe maximal entre points de fixation
DISTANCE_ANGLE_MAX_MM = 200.0     # distance maximale d'un point depuis un angle
TYPES_POSE = {"neuf", "renovation", "depose_totale"}


def _points_montant(longueur_mm: float) -> int:
    """Points de fixation requis sur un montant vertical : 2 en extrémité, plus
    des intermédiaires pour que l'entraxe reste <= 800 mm (principe DTU 36.5)."""
    utile = max(0.0, longueur_mm - 2 * DISTANCE_ANGLE_MAX_MM)
    intermediaires = max(0, math.ceil(utile / ENTRAXE_FIXATION_MAX_MM) - 1)
    return 2 + intermediaires


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json. Retourne un verdict de conformité."""
    inp = inputs or {}
    largeur = float(inp.get("largeur_mm", 0.0))
    hauteur = float(inp.get("hauteur_mm", 0.0))
    nb_points = int(inp.get("nb_points_fixation", 0))
    type_pose = str(inp.get("type_pose", "neuf")).lower()
    etancheite = bool(inp.get("etancheite_realisee", False))
    calage = bool(inp.get("calage_realise", False))

    # Fixations réparties sur les deux montants verticaux (principe DTU 36.5).
    requis = 2 * _points_montant(hauteur)

    nc: list[str] = []
    if type_pose not in TYPES_POSE:
        nc.append(f"type de pose '{type_pose}' inconnu (attendu : {sorted(TYPES_POSE)})")
    if largeur <= 0 or hauteur <= 0:
        nc.append("dimensions de la menuiserie invalides")
    if nb_points < requis:
        nc.append(f"{nb_points} points de fixation < {requis} requis "
                  f"(entraxe max {ENTRAXE_FIXATION_MAX_MM:.0f} mm)")
    if not calage:
        nc.append("calage périphérique non réalisé (cales d'assise obligatoires)")
    if not etancheite:
        nc.append("étanchéité air/eau non réalisée (calfeutrement périphérique requis)")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "nb_points_requis": requis,
        "verdict": ("Pose de menuiserie conforme DTU 36.5."
                    if conforme else
                    f"{len(nc)} non-conformité(s) DTU 36.5."),
    }
