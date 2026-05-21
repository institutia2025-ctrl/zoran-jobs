"""skill btp_verif_poteau_beton — verification poteau BA compression centrée.

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Structure (1/5).
Source : NF EN 1992-1-1 (Eurocode 2) §6.1 (resistance) + §5.8.3.1 (elancement).

Cas couvert : poteau rectangulaire BA, compression centree, classe XC1-XC4,
section non elancee. Verification N_Rd >= N_Ed avec :

    N_Rd = A_c × f_cd + A_s × f_yd

avec :
    f_cd = α_cc × f_ck / γ_c  (α_cc=1.0, γ_c=1.5 ANF)
    f_yd = f_yk / γ_s         (γ_s=1.15 ANF)
    A_c  = b × h (mm²)

Vérification d'élancement (EC2 §5.8.3.1) :
    λ = lo / i  avec i = h/√12 pour section rectangulaire
    λ_lim = 20·A·B·C / √n  (simplifié : si λ ≤ 30 -> non élancé OK MVP)

⚠️ MVP : compression centrée pure, pas de moment, pas de flambement complet.
   Si élancement détecté, le skill renvoie un avertissement et ne valide pas.

Contrat io :
    inputs : {
        "b_mm": int,                 # largeur section
        "h_mm": int,                 # hauteur section
        "longueur_libre_mm": int,    # longueur libre lo
        "fck_mpa": float,            # ex 25 pour C25/30
        "fyk_mpa": float,            # ex 500 pour B500B
        "As_mm2": float,             # section totale armatures
        "N_Ed_kN": float             # effort normal ELU
    }
    outputs : {
        "N_Rd_kN": float,
        "conforme": bool,
        "ratio_utilisation": float,  # N_Ed / N_Rd
        "elancement": float,
        "elance": bool,              # True si lambda > 30 -> EC2 §5.8 detaille requis
        "reference": str
    }
"""
from __future__ import annotations

import math

ALPHA_CC = 1.0
GAMMA_C = 1.5  # ANF (Annexe Nationale Francaise EC2)
GAMMA_S = 1.15  # ANF


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    for nom in ("b_mm", "h_mm", "longueur_libre_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} doit etre un entier > 0 (en mm)")
    for nom in ("fck_mpa", "fyk_mpa", "As_mm2", "N_Ed_kN"):
        v = inputs.get(nom)
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"{nom} doit etre un nombre > 0")

    b, h, lo = inputs["b_mm"], inputs["h_mm"], inputs["longueur_libre_mm"]
    fck, fyk = inputs["fck_mpa"], inputs["fyk_mpa"]
    As, N_Ed = inputs["As_mm2"], inputs["N_Ed_kN"]

    # Resistances de calcul (EC2 §3.1.6, §3.2.7)
    fcd = ALPHA_CC * fck / GAMMA_C  # MPa
    fyd = fyk / GAMMA_S  # MPa

    Ac = b * h  # mm²
    N_Rd_N = Ac * fcd + As * fyd  # en N (MPa × mm² = N)
    N_Rd_kN = N_Rd_N / 1000.0

    # Elancement (EC2 §5.8.3.1) — rayon de giration mini pour section rectangulaire
    h_min = min(b, h)
    i = h_min / math.sqrt(12)  # mm
    lambda_ = lo / i

    elance = lambda_ > 30.0  # seuil simplifié MVP — sinon EC2 §5.8.3 complet requis

    conforme = (N_Ed <= N_Rd_kN) and (not elance)

    return {
        "N_Rd_kN": round(N_Rd_kN, 2),
        "conforme": conforme,
        "ratio_utilisation": round(N_Ed / N_Rd_kN, 3),
        "elancement": round(lambda_, 2),
        "elance": elance,
        "fcd_mpa": round(fcd, 2),
        "fyd_mpa": round(fyd, 2),
        "reference": "NF EN 1992-1-1 §6.1 + §5.8.3.1 (Annexe Nationale Francaise γc=1.5, γs=1.15)",
    }
