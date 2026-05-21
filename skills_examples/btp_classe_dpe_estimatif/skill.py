"""skill Classe DPE estimative — niveau diagnostic énergétique.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Thermique.
Source : arrêté du 31/03/2021 relatif au DPE (méthode 3CL-DPE 2021),
seuils de l'étiquette « énergie » exprimés en énergie primaire.

Donne la classe énergétique (A..G) indicative d'un logement à partir de sa
consommation annuelle d'énergie primaire.

⚠️ MVP : axe ÉNERGIE uniquement. Le DPE réglementaire retient la PLUS MAUVAISE
des deux étiquettes — énergie et climat (GES) — ce skill ne calcule pas le GES.
Résultat indicatif : ne vaut pas un DPE opposable établi par un diagnostiqueur.
Loi 1 : seuils repris de l'arrêté DPE 2021, aucun seuil fabriqué.

Contrat io :
    inputs  : {consommation_kwh_ep_m2_an}
    outputs : {classe_dpe, borne_classe, reference}
"""

from __future__ import annotations

# Seuils de l'étiquette énergie (énergie primaire, kWh/m²/an) — arrêté DPE 2021.
SEUILS = [
    ("A", 0.0, 70.0), ("B", 70.0, 110.0), ("C", 110.0, 180.0),
    ("D", 180.0, 250.0), ("E", 250.0, 330.0), ("F", 330.0, 420.0),
    ("G", 420.0, float("inf")),
]


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    conso = inputs.get("consommation_kwh_ep_m2_an")
    if not isinstance(conso, (int, float)) or isinstance(conso, bool):
        raise ValueError("consommation_kwh_ep_m2_an : nombre attendu")
    conso = float(conso)
    if conso < 0:
        raise ValueError("consommation_kwh_ep_m2_an : valeur négative interdite")

    for classe, bas, haut in SEUILS:
        if (bas <= conso < haut) or (haut == float("inf") and conso >= bas):
            borne = (f">= {bas:.0f} kWh_ep/m².an" if haut == float("inf")
                     else f"{bas:.0f}-{haut:.0f} kWh_ep/m².an")
            return {
                "classe_dpe": classe,
                "borne_classe": borne,
                "reference": "Arrêté DPE du 31/03/2021 (étiquette énergie, 3CL-DPE)",
            }
    raise ValueError("consommation hors barème")
