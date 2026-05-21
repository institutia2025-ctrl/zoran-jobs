"""skill Débit de ventilation VMC réglementaire d'un logement.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc CVC.
Source : arrêté du 24 mars 1982 relatif à l'aération des logements (modifié).

Donne le débit global minimal extrait exigé pour un logement, selon son nombre
de pièces principales. Barème de l'arrêté du 24 mars 1982 (m³/h) :
    1 pièce → 35 ; 2 → 60 ; 3 → 75 ; 4 → 90 ; 5 → 105 ; 6 → 120 ; 7 → 135.
Au-delà de 2 pièces, le débit progresse de 15 m³/h par pièce principale
supplémentaire.

⚠️ MVP : débit GLOBAL minimal extrait. Ne donne pas la répartition par pièce
de service (cuisine, bains, WC) ni les débits de pointe (cuisine), ni le
dimensionnement des bouches et du réseau.
Loi 1 : barème repris de l'arrêté du 24 mars 1982 — aucune valeur fabriquée.

Contrat io :
    inputs  : {nb_pieces_principales}
    outputs : {debit_global_minimal_m3h, nb_pieces_principales, reference}
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    nb = inputs.get("nb_pieces_principales")
    if not isinstance(nb, int) or isinstance(nb, bool) or nb < 1:
        raise ValueError("nb_pieces_principales : entier >= 1 requis")

    # Arrêté du 24/03/1982 : 1 pièce → 35 ; à partir de 2 pièces → 60 + 15/(pièce).
    debit = 35 if nb == 1 else 60 + 15 * (nb - 2)
    return {
        "debit_global_minimal_m3h": debit,
        "nb_pieces_principales": nb,
        "reference": "Arrêté du 24 mars 1982 relatif à l'aération des logements",
    }
