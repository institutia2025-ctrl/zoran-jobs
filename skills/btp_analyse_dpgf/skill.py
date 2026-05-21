"""
skill btp_analyse_dpgf — Analyse de DPGF et détection d'anomalies.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (économie)
Point d'entrée : run(inputs: dict) -> dict.

Analyse une Décomposition du Prix Global et Forfaitaire ligne à ligne et
détecte les anomalies : incohérence montant != quantité x prix unitaire,
champs manquants, quantités ou prix nuls. Recalcule le total.
"""

from __future__ import annotations

TOLERANCE = 0.01  # écart relatif toléré sur montant = quantité x PU (1 %)


def _est_nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    lignes = inp.get("lignes") or []

    anomalies: list[str] = []
    total = 0.0
    for i, ligne in enumerate(lignes):
        ligne = ligne or {}
        designation = str(ligne.get("designation", "")).strip()
        quantite = ligne.get("quantite")
        prix_unitaire = ligne.get("prix_unitaire")
        montant = ligne.get("montant")
        ref = designation or f"ligne #{i}"

        if not designation:
            anomalies.append(f"{ref} : désignation manquante")
        if not _est_nombre(quantite):
            anomalies.append(f"{ref} : quantité absente ou non numérique")
            quantite = 0.0
        if not _est_nombre(prix_unitaire):
            anomalies.append(f"{ref} : prix unitaire absent ou non numérique")
            prix_unitaire = 0.0
        if quantite == 0:
            anomalies.append(f"{ref} : quantité nulle")
        if prix_unitaire == 0:
            anomalies.append(f"{ref} : prix unitaire nul")

        attendu = quantite * prix_unitaire
        if _est_nombre(montant):
            if abs(montant - attendu) > max(TOLERANCE * abs(attendu), 0.01):
                anomalies.append(f"{ref} : montant {montant} != "
                                 f"quantité x PU ({round(attendu, 2)})")
            total += montant
        else:
            anomalies.append(f"{ref} : montant absent — recalculé à {round(attendu, 2)}")
            total += attendu

    return {
        "nb_lignes": len(lignes),
        "anomalies": anomalies,
        "nb_anomalies": len(anomalies),
        "total_calcule_eur": round(total, 2),
        "coherent": not anomalies,
        "verdict": ("DPGF cohérente — aucune anomalie détectée."
                    if not anomalies else
                    f"{len(anomalies)} anomalie(s) détectée(s) dans la DPGF."),
    }
