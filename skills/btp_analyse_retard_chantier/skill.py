"""
skill btp_analyse_retard_chantier — Analyse de retard de chantier.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (conduite)
Méthode : 5 pourquoi (recherche de cause racine) + matrice de criticité 5x5
(probabilité x gravité). Point d'entrée : run(inputs: dict) -> dict.
"""

from __future__ import annotations


def _niveau(criticite: int) -> str:
    """Niveau de criticité sur la matrice 5x5 (criticité = proba x gravité)."""
    if criticite <= 4:
        return "faible"
    if criticite <= 9:
        return "modere"
    if criticite <= 14:
        return "eleve"
    return "critique"


_RECO = {
    "faible": "Suivi simple en réunion de chantier.",
    "modere": "Action corrective planifiée, point hebdomadaire.",
    "eleve": "Plan d'action immédiat, escalade au conducteur de travaux.",
    "critique": "Cellule de crise, révision du planning, information du maître d'ouvrage.",
}


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    description = str(inp.get("description_retard", "")).strip()
    chaine = [str(x).strip() for x in (inp.get("chaine_pourquoi") or []) if str(x).strip()]
    proba = min(5, max(1, int(inp.get("probabilite", 1))))
    gravite = min(5, max(1, int(inp.get("gravite", 1))))

    profondeur = len(chaine)
    complete = profondeur >= 5
    cause_racine = (chaine[-1] if chaine
                    else "(non identifiée — aucune chaîne de pourquoi fournie)")
    criticite = proba * gravite
    niveau = _niveau(criticite)

    reco = _RECO[niveau]
    if not complete:
        reco += (f" Analyse 5-pourquoi incomplète ({profondeur}/5) : "
                 f"approfondir avant de conclure.")

    return {
        "description": description,
        "cause_racine": cause_racine,
        "profondeur_analyse": profondeur,
        "analyse_complete": complete,
        "criticite": criticite,
        "niveau_criticite": niveau,
        "recommandation": reco,
    }
