"""skill Vérification d'un poteau bois en compression axiale.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Charpente bois.
Source : NF EN 1995-1-1 (Eurocode 5) §6.1.4 (compression axiale).

Vérifie un poteau bois en compression centrée :
    A = b·h                       (section)
    σ = N_Ed / A                  (contrainte de compression)
    conforme si σ ≤ fc,0,d        (résistance de compression axiale de calcul)

⚠️ MVP : compression axiale pure, section courte. Ne traite PAS le flambement
(§6.3 EC5 — vérification au déversement/flambement par l'élancement et le
coefficient kc). Un poteau élancé doit être vérifié au flambement séparément.
Loi 1 : fc,0,d dépend de la classe de bois et des coefficients EC5 (kmod, γM) —
elle est fournie par l'appelant.

Contrat io :
    inputs  : {b_mm, h_mm, N_Ed_kN, fc_0_d_mpa}
    outputs : {contrainte_compression_mpa, conforme, taux_travail, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    for nom in ("b_mm", "h_mm", "N_Ed_kN", "fc_0_d_mpa"):
        v = inputs.get(nom)
        if not _nombre(v) or v <= 0:
            raise ValueError(f"{nom} : nombre > 0 requis")

    b = float(inputs["b_mm"])
    h = float(inputs["h_mm"])
    n_ed = float(inputs["N_Ed_kN"])
    fc_0_d = float(inputs["fc_0_d_mpa"])

    aire = b * h                       # mm²
    contrainte = n_ed * 1000.0 / aire  # MPa
    conforme = contrainte <= fc_0_d
    return {
        "contrainte_compression_mpa": round(contrainte, 3),
        "fc_0_d_mpa": fc_0_d,
        "taux_travail": round(contrainte / fc_0_d, 3),
        "conforme": conforme,
        "verdict": ("Poteau conforme en compression axiale (EC5 §6.1.4)."
                    if conforme else
                    "Poteau NON conforme — compression axiale dépassée. "
                    "Vérifier aussi le flambement (EC5 §6.3)."),
        "reference": "NF EN 1995-1-1 §6.1.4 (compression axiale du bois)",
    }
