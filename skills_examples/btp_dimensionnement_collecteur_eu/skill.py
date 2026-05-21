"""skill Débit de pointe d'eaux usées et diamètre de collecteur.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc VRD.
Source : NF EN 12056-2 + NF DTU 60.11 — évacuation gravitaire des eaux usées.

Calcule le débit de pointe probable d'eaux usées :
    Q = K × √(Σ unités de vidange)     (l/s)
K = coefficient de fréquentation (selon l'usage du bâtiment), ΣUV = somme des
unités de vidange des appareils sanitaires raccordés.

⚠️ MVP : calcule le débit de pointe et propose un DN minimal indicatif. Le choix
définitif du diamètre suit le tableau de la NF EN 12056-2 (taux de remplissage,
pente, ventilation primaire/secondaire) — à confirmer par un bureau d'études fluides.
Loi 1 : K dépend de l'usage (intermittent 0.5, fréquent 0.7, congestionné 1.0,
usage spécial 1.2 — NF EN 12056-2) ; il est fourni. Les unités de vidange par
appareil sont des données normatives fournies par l'appelant.

Contrat io :
    inputs  : {unites_vidange_total, coef_frequentation_k?}
    outputs : {debit_pointe_l_s, dn_minimal_indicatif, coef_frequentation_k, reference}
"""

from __future__ import annotations

import math

K_DEFAUT = 0.5  # usage intermittent (habitation, bureau) — NF EN 12056-2

# DN minimal indicatif par tranche de débit (ordre de grandeur — à confirmer EN 12056-2).
_DN_INDICATIF = [
    (0.5, "DN 40"), (1.5, "DN 50"), (2.5, "DN 75"), (4.0, "DN 90"),
    (7.0, "DN 100"), (12.0, "DN 125"), (20.0, "DN 160"),
]


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    uv = inputs.get("unites_vidange_total")
    k = inputs.get("coef_frequentation_k", K_DEFAUT)

    if not _nombre(uv) or uv <= 0:
        raise ValueError("unites_vidange_total : nombre > 0 requis")
    if not _nombre(k) or k <= 0:
        raise ValueError("coef_frequentation_k : nombre > 0 requis")

    debit = float(k) * math.sqrt(float(uv))
    dn = next((d for seuil, d in _DN_INDICATIF if debit <= seuil),
              "DN > 160 (étude hydraulique requise)")
    return {
        "debit_pointe_l_s": round(debit, 3),
        "dn_minimal_indicatif": dn,
        "coef_frequentation_k": float(k),
        "reference": "NF EN 12056-2 (Q = K·√ΣUV) + NF DTU 60.11",
    }
