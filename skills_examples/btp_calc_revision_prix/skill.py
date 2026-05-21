"""skill Révision de prix d'un marché de travaux.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Économie.
Source : clause de révision de prix — formule paramétrique (index BT,
marchés de travaux publics et privés).

Applique la formule paramétrique de révision :
    P_révisé = P0 × [ a + (1 − a) × (I / I0) ]
avec a = terme fixe (part non révisable), I/I0 = rapport de l'index courant
sur l'index de référence.

⚠️ MVP : formule à un seul index. Ne traite pas les formules multi-index
(plusieurs paramètres b, c… pondérés) ni les clauses d'actualisation distinctes.
Loi 1 : le terme fixe et les valeurs d'index sont fournis (clause du marché +
index BT publiés) — le skill ne les invente pas.

Contrat io :
    inputs  : {prix_initial_eur, terme_fixe, index_initial, index_courant}
    outputs : {prix_revise_eur, coefficient_revision, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    prix = inputs.get("prix_initial_eur")
    terme_fixe = inputs.get("terme_fixe")
    index_initial = inputs.get("index_initial")
    index_courant = inputs.get("index_courant")

    if not _nombre(prix) or prix <= 0:
        raise ValueError("prix_initial_eur : nombre > 0 requis")
    if not _nombre(terme_fixe) or not (0.0 <= terme_fixe <= 1.0):
        raise ValueError("terme_fixe : nombre dans [0..1] requis")
    if not _nombre(index_initial) or index_initial <= 0:
        raise ValueError("index_initial : nombre > 0 requis")
    if not _nombre(index_courant) or index_courant <= 0:
        raise ValueError("index_courant : nombre > 0 requis")

    coef = terme_fixe + (1.0 - terme_fixe) * (index_courant / index_initial)
    prix_revise = prix * coef
    return {
        "prix_revise_eur": round(prix_revise, 2),
        "coefficient_revision": round(coef, 5),
        "reference": "Formule paramétrique de révision de prix (index BT, marchés de travaux)",
    }
