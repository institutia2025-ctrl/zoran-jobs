"""skill verif_seisme_classe1_asn — ingénieur structure nucléaire.

Mission : ZORAN_JOBS_20260521 · Phase A BTP.
Vérification simplifiée : un bâtiment classé EIPS (Élément Important Pour la Sûreté)
d'une INB (Installation Nucléaire de Base) est-il dimensionné pour le SMS retenu ?

Référence publique : RFS 2001-01 (Règle Fondamentale de Sûreté ASN, mai 2001)
   "Détermination du risque sismique pour la sûreté des installations nucléaires
    de base de surface", disponible sur asn.fr.

Approche RFS 2001-01 : on retient le **Séisme Majoré de Sécurité (SMS)** comme
enveloppe du SMHV (Séisme Maximal Historiquement Vraisemblable, période de
retour 1000 ans) avec une marge sécuritaire ; le SMS est défini par son spectre
de réponse et son accélération maximale au sol (PGA).

⚠️ MVP : démonstration de l'API du skill, pas une vérification de sûreté.
Une vraie note de calcul EIPS demande IRSN/Areva-AREVA/EDF + audit ASN.
Loi 1 : aucune valeur de PGA fictive injectée — l'utilisateur fournit les
mesures du site, le skill compare aux seuils utilisateur.

Contrat io :
    inputs : {
        "pga_smhv_g": float,               # PGA du SMHV en g (du site)
        "marge_sms": float,                # marge SMS / SMHV (>= 1.0)
        "pga_dimensionnement_g": float,    # PGA pris en compte par le calcul
        "classe_eips": str                 # "F1A", "F1B", "F2" (catégories sismiques RFS)
    }
    outputs : {
        "sms_calcule_g": float,
        "marge_disponible": float,         # pga_dim / sms_calcule
        "conforme": bool,                  # marge >= 1.0
        "verdict": str,
        "reference": "RFS 2001-01 (ASN, mai 2001)"
    }
"""

from __future__ import annotations

CLASSES_AUTORISEES = {"F1A", "F1B", "F2"}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    pga_smhv = inputs.get("pga_smhv_g")
    marge_sms = inputs.get("marge_sms")
    pga_dim = inputs.get("pga_dimensionnement_g")
    classe = inputs.get("classe_eips")

    for nom, val in [("pga_smhv_g", pga_smhv), ("pga_dimensionnement_g", pga_dim)]:
        if not isinstance(val, (int, float)) or val <= 0:
            raise ValueError(f"{nom} doit etre un nombre > 0 (en g)")
    if not isinstance(marge_sms, (int, float)) or marge_sms < 1.0:
        raise ValueError("marge_sms doit etre >= 1.0 (principe RFS 2001-01)")
    if classe not in CLASSES_AUTORISEES:
        raise ValueError(f"classe_eips doit etre dans {sorted(CLASSES_AUTORISEES)}")

    sms = pga_smhv * marge_sms
    marge_disponible = pga_dim / sms
    conforme = marge_disponible >= 1.0

    if conforme and marge_disponible >= 1.20:
        verdict = "OK avec marge confortable (>= 20%)"
    elif conforme:
        verdict = "OK strict (marge < 20%, revoir si evolution donnees site)"
    else:
        verdict = "NON CONFORME : PGA dim < SMS - reprise du dimensionnement requise"

    return {
        "sms_calcule_g": round(sms, 4),
        "marge_disponible": round(marge_disponible, 3),
        "conforme": conforme,
        "verdict": verdict,
        "classe_eips": classe,
        "reference": "RFS 2001-01 (ASN, mai 2001)",
    }
