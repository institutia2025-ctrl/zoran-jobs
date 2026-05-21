"""skill Calibre de protection d'un circuit électrique.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Électricité.
Source : NF C 15-100 (coordination protection / canalisation).

Détermine le calibre de protection (disjoncteur) d'un circuit. La règle de
coordination de la NF C 15-100 est :
    I_B ≤ I_n ≤ I_z
avec I_B = courant d'emploi, I_n = calibre de la protection, I_z = courant
admissible de la canalisation. Le skill retient le plus petit calibre normalisé
respectant cette double inégalité.

Une protection mal calibrée est un risque de surchauffe / incendie — ce skill
est veto_capable.

⚠️ MVP : règle de coordination de base (I_B ≤ I_n ≤ I_z). Ne traite pas la
protection contre les courts-circuits (pouvoir de coupure) ni la sélectivité.
Loi 1 : I_B et I_z sont fournis ; I_z se lit dans les tableaux NF C 15-100.

Contrat io :
    inputs  : {courant_emploi_a, courant_admissible_a}
    outputs : {calibre_recommande_a, calibres_valides_a, conforme, reference}
"""

from __future__ import annotations

# Calibres normalisés de disjoncteurs (A).
CALIBRES = [2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100]


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    i_b = inputs.get("courant_emploi_a")
    i_z = inputs.get("courant_admissible_a")
    if not _nombre(i_b) or i_b <= 0:
        raise ValueError("courant_emploi_a : nombre > 0 requis")
    if not _nombre(i_z) or i_z <= 0:
        raise ValueError("courant_admissible_a : nombre > 0 requis")
    i_b = float(i_b)
    i_z = float(i_z)

    valides = [c for c in CALIBRES if i_b <= c <= i_z]
    conforme = bool(valides)
    return {
        "courant_emploi_a": i_b,
        "courant_admissible_a": i_z,
        "calibres_valides_a": valides,
        "calibre_recommande_a": (min(valides) if valides else None),
        "conforme": conforme,
        "verdict": (f"Calibre recommandé : {min(valides)} A (NF C 15-100)." if conforme
                    else "Aucun calibre valide — la canalisation (I_z) est trop "
                         "faible pour le courant d'emploi : revoir la section."),
        "reference": "NF C 15-100 (coordination protection / canalisation : I_B ≤ I_n ≤ I_z)",
    }
