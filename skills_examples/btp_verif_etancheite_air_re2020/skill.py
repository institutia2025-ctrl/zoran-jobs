"""skill Vérification de la perméabilité à l'air de l'enveloppe (RE2020).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Charges/Enveloppe.
Source : RE2020 (exigence de perméabilité à l'air de l'enveloppe) ; mesure par
test d'infiltrométrie selon NF EN ISO 9972 (méthode de la porte soufflante).

Compare la perméabilité à l'air mesurée Q4Pa-surf au seuil réglementaire selon
le type de bâtiment. Q4Pa-surf est le débit de fuite sous 4 Pa rapporté à la
surface de l'enveloppe déperditive hors plancher bas, en m³/(h·m²).

⚠️ MVP : seuils maison individuelle et logement collectif. Ne traite pas les
bâtiments tertiaires (exigences distinctes) ni le calcul du Q4Pa-surf lui-même
(qui résulte de la mesure in situ).
Loi 1 : seuils repris des exigences RE2020 ; la valeur mesurée est fournie par
le test d'infiltrométrie, non estimée par le skill.

Contrat io :
    inputs  : {type_batiment, q4pa_surf_mesure}
    outputs : {conforme, q4pa_surf_mesure, seuil_re2020, marge, verdict, reference}
"""

from __future__ import annotations

# Seuils Q4Pa-surf en m³/(h·m²) — valeurs de référence RE2020.
SEUILS = {
    "maison_individuelle": 0.60,
    "logement_collectif": 1.00,
}


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    type_batiment = str(inputs.get("type_batiment", "")).lower()
    q4 = inputs.get("q4pa_surf_mesure")
    if type_batiment not in SEUILS:
        raise ValueError(f"type_batiment doit être dans {sorted(SEUILS)}")
    if not isinstance(q4, (int, float)) or isinstance(q4, bool) or q4 < 0:
        raise ValueError("q4pa_surf_mesure : nombre >= 0 requis")
    q4 = float(q4)

    seuil = SEUILS[type_batiment]
    conforme = q4 <= seuil
    return {
        "conforme": conforme,
        "q4pa_surf_mesure": q4,
        "seuil_re2020": seuil,
        "marge": round(seuil - q4, 3),
        "verdict": ("Perméabilité à l'air conforme RE2020."
                    if conforme else
                    f"Perméabilité {q4} > seuil {seuil} m³/(h·m²) — NON conforme RE2020."),
        "reference": "RE2020 (perméabilité à l'air) + NF EN ISO 9972 (mesure infiltrométrie)",
    }
