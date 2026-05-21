"""skill Pression d'eau disponible à un point de puisage.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Plomberie.
Source : NF DTU 60.11 (réseaux d'alimentation en eau).

Calcule la pression disponible à un point de puisage :
    P_dispo = P_réseau − (perte de charge linéique × longueur) − 0,1 × hauteur
avec 0,1 bar par mètre d'élévation (1 bar ≈ 10 m de colonne d'eau).

⚠️ MVP : pertes de charge linéiques fournies (elles dépendent du débit, du
diamètre et du matériau). Ne traite pas les pertes de charge singulières
(coudes, vannes, compteur) ni les coups de bélier.
Loi 1 : la perte de charge linéique provient d'un calcul hydraulique ou d'un
abaque — elle est fournie, jamais inventée.

Contrat io :
    inputs  : {pression_reseau_bar, longueur_m, perte_charge_bar_par_m,
               hauteur_m, pression_min_requise_bar?}
    outputs : {pression_disponible_bar, conforme, reference}
"""

from __future__ import annotations

PRESSION_MIN_DEFAUT_BAR = 1.0  # pression de service minimale usuelle à un robinet


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    p_reseau = inputs.get("pression_reseau_bar")
    longueur = inputs.get("longueur_m")
    perte_lin = inputs.get("perte_charge_bar_par_m")
    hauteur = inputs.get("hauteur_m")
    p_min = inputs.get("pression_min_requise_bar", PRESSION_MIN_DEFAUT_BAR)

    if not _nombre(p_reseau) or p_reseau <= 0:
        raise ValueError("pression_reseau_bar : nombre > 0 requis")
    if not _nombre(longueur) or longueur < 0:
        raise ValueError("longueur_m : nombre >= 0 requis")
    if not _nombre(perte_lin) or perte_lin < 0:
        raise ValueError("perte_charge_bar_par_m : nombre >= 0 requis")
    if not _nombre(hauteur) or hauteur < 0:
        raise ValueError("hauteur_m : nombre >= 0 requis")
    if not _nombre(p_min) or p_min <= 0:
        raise ValueError("pression_min_requise_bar : nombre > 0 requis")

    perte_lineaire = float(perte_lin) * float(longueur)
    perte_statique = 0.1 * float(hauteur)
    p_dispo = float(p_reseau) - perte_lineaire - perte_statique
    conforme = p_dispo >= float(p_min)
    return {
        "pression_disponible_bar": round(p_dispo, 3),
        "perte_lineaire_bar": round(perte_lineaire, 3),
        "perte_statique_bar": round(perte_statique, 3),
        "pression_min_requise_bar": float(p_min),
        "conforme": conforme,
        "verdict": ("Pression disponible suffisante au point de puisage." if conforme
                    else "Pression insuffisante — surpresseur ou diamètre supérieur à prévoir."),
        "reference": "NF DTU 60.11 (alimentation en eau — pression disponible)",
    }
