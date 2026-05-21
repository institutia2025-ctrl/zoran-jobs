"""skill Vérification de garde-corps (hauteur et barreaudage).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Sécurité.
Source : NF P01-012 (dimensions des garde-corps — règles de sécurité).

Vérifie la protection contre les chutes : hauteur du garde-corps et écartement
du remplissage (barreaudage). Une valeur insuffisante engage la sécurité des
occupants — ce skill est veto_capable.

Règles (NF P01-012) :
- hauteur ≥ 1,00 m (garde-corps vertical courant).
- écartement du barreaudage vertical ≤ 0,11 m (zone de sécurité basse).

⚠️ MVP : garde-corps vertical à barreaudage. Ne traite pas les garde-corps en
verre faisant pare-chute ni les remplissages horizontaux (effet échelle —
proscrits en présence d'enfants).
Loi 1 : seuils repris de la NF P01-012.

Contrat io :
    inputs  : {hauteur_mm, ecartement_barreaux_mm}
    outputs : {conforme, non_conformites, verdict, reference}
"""

from __future__ import annotations

HAUTEUR_MIN_MM = 1000.0
ECARTEMENT_MAX_MM = 110.0


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    hauteur = inputs.get("hauteur_mm")
    ecartement = inputs.get("ecartement_barreaux_mm")

    if not _nombre(hauteur) or hauteur <= 0:
        raise ValueError("hauteur_mm : nombre > 0 requis")
    if not _nombre(ecartement) or ecartement <= 0:
        raise ValueError("ecartement_barreaux_mm : nombre > 0 requis")

    hauteur, ecartement = float(hauteur), float(ecartement)
    nc: list[str] = []
    if hauteur < HAUTEUR_MIN_MM:
        nc.append(f"hauteur {hauteur} mm < {HAUTEUR_MIN_MM:.0f} mm minimum")
    if ecartement > ECARTEMENT_MAX_MM:
        nc.append(f"écartement barreaudage {ecartement} mm > {ECARTEMENT_MAX_MM:.0f} mm "
                  f"(passage du corps d'un enfant)")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "verdict": ("Garde-corps conforme NF P01-012."
                    if conforme else
                    f"{len(nc)} non-conformité(s) — garde-corps non conforme (risque de chute)."),
        "reference": "NF P01-012 (dimensions des garde-corps)",
    }
