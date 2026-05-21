"""skill Vérification de dégagement d'évacuation (largeur / unités de passage).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Sécurité.
Source : règlement de sécurité contre l'incendie dans les ERP, article CO 36
(unités de passage).

Vérifie qu'un dégagement offre la largeur réglementaire pour le nombre d'unités
de passage (UP) requis. Conversion UP → largeur (article CO 36) :
- 1 UP        → 0,90 m
- 2 UP        → 1,40 m
- n UP (n≥3)  → n × 0,60 m

Une largeur insuffisante compromet l'évacuation — ce skill est veto_capable.

⚠️ MVP : conversion UP → largeur réglementaire. Le nombre d'UP requis se
détermine d'après l'effectif et le type d'ERP (articles CO 34 à CO 38) — il est
FOURNI par l'appelant, ce skill ne le calcule pas.
Loi 1 : les valeurs 0,90 / 1,40 / 0,60 m sont celles de l'article CO 36.

Contrat io :
    inputs  : {largeur_degagement_m, unites_passage_requises}
    outputs : {conforme, largeur_min_requise_m, marge_m, verdict, reference}
"""

from __future__ import annotations


def _largeur_min(unites: int) -> float:
    """Largeur réglementaire pour `unites` unités de passage (ERP — article CO 36)."""
    if unites == 1:
        return 0.90
    if unites == 2:
        return 1.40
    return unites * 0.60


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    largeur = inputs.get("largeur_degagement_m")
    unites = inputs.get("unites_passage_requises")

    if not isinstance(largeur, (int, float)) or isinstance(largeur, bool) or largeur <= 0:
        raise ValueError("largeur_degagement_m : nombre > 0 requis")
    if not isinstance(unites, int) or isinstance(unites, bool) or unites < 1:
        raise ValueError("unites_passage_requises : entier >= 1 requis")

    requise = _largeur_min(unites)
    largeur = float(largeur)
    conforme = largeur >= requise
    return {
        "conforme": conforme,
        "unites_passage_requises": unites,
        "largeur_min_requise_m": round(requise, 2),
        "largeur_degagement_m": largeur,
        "marge_m": round(largeur - requise, 3),
        "verdict": ("Dégagement conforme (article CO 36)."
                    if conforme else
                    "Largeur de dégagement insuffisante — évacuation compromise (CO 36)."),
        "reference": "Règlement de sécurité ERP — article CO 36 (unités de passage)",
    }
