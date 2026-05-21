"""skill Vérification de pente d'évacuation (eaux usées / eaux pluviales).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc VRD.
Source : NF DTU 60.11 (réseaux d'évacuation gravitaire des eaux).

Calcule la pente d'un tronçon d'évacuation et la compare à une pente minimale :
    pente (%) = (dénivelé / longueur) × 100

⚠️ MVP : vérifie la pente géométrique vs un minimum. Ne dimensionne pas le
diamètre, ne vérifie ni l'auto-curage (vitesse d'écoulement) ni les contre-pentes.
Loi 1 : la pente minimale dépend du réseau. La valeur par défaut 1.0 % est un
ordre de grandeur courant pour l'évacuation gravitaire (NF DTU 60.11),
surchargeable par l'appelant selon le CCTP.

Contrat io :
    inputs  : {denivele_m, longueur_m, pente_min_pct?}
    outputs : {pente_pct, pente_cm_par_m, conforme, pente_min_pct, reference}
"""

from __future__ import annotations

PENTE_MIN_DEFAUT_PCT = 1.0  # ordre de grandeur courant — évacuation gravitaire


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    denivele = inputs.get("denivele_m")
    longueur = inputs.get("longueur_m")
    pente_min = inputs.get("pente_min_pct", PENTE_MIN_DEFAUT_PCT)

    if not _nombre(denivele) or denivele < 0:
        raise ValueError("denivele_m : nombre >= 0 requis")
    if not _nombre(longueur) or longueur <= 0:
        raise ValueError("longueur_m : nombre > 0 requis")
    if not _nombre(pente_min) or pente_min <= 0:
        raise ValueError("pente_min_pct : nombre > 0 requis")

    pente = float(denivele) / float(longueur) * 100.0
    return {
        "pente_pct": round(pente, 3),
        "pente_cm_par_m": round(pente, 2),
        "pente_min_pct": float(pente_min),
        "conforme": pente >= float(pente_min),
        "reference": "NF DTU 60.11 (réseaux d'évacuation gravitaire des eaux)",
    }
