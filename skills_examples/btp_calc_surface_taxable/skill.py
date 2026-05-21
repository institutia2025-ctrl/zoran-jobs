"""skill Calcul de la surface taxable (taxe d'aménagement).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Réglementation.
Source : Code de l'urbanisme — assiette de la taxe d'aménagement (surface taxable).

Calcule la surface taxable :
    surface_taxable = surface close et couverte (sous plafond > 1,80 m)
                      − surfaces sous 1,80 m de hauteur
                      − vides et trémies

⚠️ MVP : calcul de l'assiette de surface. Ne calcule pas le montant de la taxe
(qui dépend de la valeur forfaitaire au m², des taux communal/départemental et
des abattements et exonérations applicables).
Loi 1 : les surfaces mesurées sont fournies — le skill ne les estime pas.

Contrat io :
    inputs  : {surface_close_couverte_m2, surface_sous_1m80_m2?, surface_vides_tremies_m2?}
    outputs : {surface_taxable_m2, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    close_couverte = inputs.get("surface_close_couverte_m2")
    sous_1m80 = inputs.get("surface_sous_1m80_m2", 0.0)
    vides = inputs.get("surface_vides_tremies_m2", 0.0)

    if not _nombre(close_couverte) or close_couverte <= 0:
        raise ValueError("surface_close_couverte_m2 : nombre > 0 requis")
    if not _nombre(sous_1m80) or sous_1m80 < 0:
        raise ValueError("surface_sous_1m80_m2 : nombre >= 0 requis")
    if not _nombre(vides) or vides < 0:
        raise ValueError("surface_vides_tremies_m2 : nombre >= 0 requis")

    taxable = float(close_couverte) - float(sous_1m80) - float(vides)
    if taxable < 0:
        raise ValueError("surface taxable négative : les déductions dépassent "
                         "la surface close et couverte (données incohérentes)")
    return {
        "surface_taxable_m2": round(taxable, 2),
        "deductions_m2": round(float(sous_1m80) + float(vides), 2),
        "reference": "Code de l'urbanisme — surface taxable (taxe d'aménagement)",
    }
