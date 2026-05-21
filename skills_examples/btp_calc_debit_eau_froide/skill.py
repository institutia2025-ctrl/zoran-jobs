"""skill Débit probable d'eau froide (coefficient de simultanéité).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Plomberie.
Source : NF DTU 60.11 (réseaux d'alimentation en eau — débits probables).

Calcule le débit probable d'eau froide d'un réseau à partir du débit brut total
(somme des débits des appareils) et d'un coefficient de simultanéité :
    coefficient = 0,8 / √(n − 1)   pour n ≥ 2 appareils  (= 1 pour n = 1)
    Q_probable  = débit_brut_total × coefficient

Tous les appareils d'un logement ne puisent jamais en même temps : le
coefficient de simultanéité corrige le débit brut vers le débit réellement
probable, base du dimensionnement des canalisations.

⚠️ MVP : coefficient de simultanéité général (logement courant). Ne traite pas
les cas particuliers (collectivités, usages industriels, robinets à débit
permanent) ni le bouclage d'eau chaude.
Loi 1 : les débits bruts des appareils sont des données normatives fournies.

Contrat io :
    inputs  : {debit_brut_total_l_s, nombre_appareils}
    outputs : {coefficient_simultaneite, debit_probable_l_s, reference}
"""

from __future__ import annotations

import math


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    debit_brut = inputs.get("debit_brut_total_l_s")
    nb = inputs.get("nombre_appareils")
    if not isinstance(debit_brut, (int, float)) or isinstance(debit_brut, bool) or debit_brut <= 0:
        raise ValueError("debit_brut_total_l_s : nombre > 0 requis")
    if not isinstance(nb, int) or isinstance(nb, bool) or nb < 1:
        raise ValueError("nombre_appareils : entier >= 1 requis")

    coefficient = 1.0 if nb <= 1 else 0.8 / math.sqrt(nb - 1)
    debit_probable = float(debit_brut) * coefficient
    return {
        "nombre_appareils": nb,
        "coefficient_simultaneite": round(coefficient, 4),
        "debit_brut_total_l_s": float(debit_brut),
        "debit_probable_l_s": round(debit_probable, 4),
        "reference": "NF DTU 60.11 (débit probable — coefficient de simultanéité)",
    }
