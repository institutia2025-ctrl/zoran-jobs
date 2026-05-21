"""skill Vérification d'isolement acoustique réglementaire (logements).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Acoustique.
Source : arrêté du 30 juin 1999 (Nouvelle Réglementation Acoustique — NRA),
exigences acoustiques applicables aux bâtiments d'habitation.

Compare une grandeur d'isolement mesurée au seuil réglementaire selon la nature
de la paroi. Attention au sens du critère : pour les bruits aériens un isolement
ÉLEVÉ est exigé ; pour les bruits de choc un niveau transmis FAIBLE est exigé.

⚠️ MVP : seuils principaux logements neufs (NRA). Ne couvre pas les ERP, les
établissements d'enseignement ni les hôpitaux (réglementations dédiées).
Loi 1 : seuils repris de l'arrêté du 30/06/1999, aucun seuil fabriqué.

Contrat io :
    inputs  : {type_paroi, isolement_mesure_db}
    outputs : {conforme, grandeur, seuil_reglementaire, marge_db, verdict, reference}
"""

from __future__ import annotations

# Seuils NRA (arrêté du 30/06/1999) — sens "min" = à dépasser, "max" = à ne pas dépasser.
SEUILS = {
    "mur_entre_logements": {"sens": "min", "valeur": 53.0, "grandeur": "DnT,A (bruit aérien, dB)"},
    "facade":              {"sens": "min", "valeur": 30.0, "grandeur": "DnT,A,tr (façade, dB)"},
    "plancher_choc":       {"sens": "max", "valeur": 58.0, "grandeur": "L'nT,w (bruit de choc, dB)"},
}


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    type_paroi = str(inputs.get("type_paroi", "")).lower()
    mesure = inputs.get("isolement_mesure_db")
    if type_paroi not in SEUILS:
        raise ValueError(f"type_paroi doit être dans {sorted(SEUILS)}")
    if not _nombre(mesure):
        raise ValueError("isolement_mesure_db : nombre attendu")
    mesure = float(mesure)

    seuil = SEUILS[type_paroi]
    if seuil["sens"] == "min":
        conforme = mesure >= seuil["valeur"]
        marge = round(mesure - seuil["valeur"], 1)
    else:  # max — bruit de choc : plus le niveau transmis est bas, mieux c'est
        conforme = mesure <= seuil["valeur"]
        marge = round(seuil["valeur"] - mesure, 1)

    return {
        "conforme": conforme,
        "grandeur": seuil["grandeur"],
        "seuil_reglementaire": seuil["valeur"],
        "marge_db": marge,
        "verdict": ("Isolement conforme à la NRA."
                    if conforme else "Isolement NON conforme à la NRA."),
        "reference": "Arrêté du 30 juin 1999 (Nouvelle Réglementation Acoustique)",
    }
