"""skill btp_ferraillage_min_eurocode — sections minimales d'armatures EC2.

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Structure (5/5).
Source : NF EN 1992-1-1 (Eurocode 2) §9 (dispositions constructives).

Calcule les sections minimales d'armatures longitudinales selon l'element :

POTEAU (§9.5.2) :
    As_min = max( 0.10 × N_Ed / fyd , 0.002 × Ac )

POUTRE (§9.2.1.1) :
    As_min = max( 0.26 × (fctm/fyk) × bt × d , 0.0013 × bt × d )

DALLE (§9.3.1.1) :
    Identique poutre avec bt = 1000 mm (par metre lineaire)

avec :
    fctm = 0.30 × fck^(2/3)   pour fck <= 50 MPa (§3.1.6)
    fyd = fyk / 1.15

⚠️ MVP : pas de prise en compte des armatures de cisaillement (§9.2.2),
   ni des dispositions sismiques (§5.4-5.7 EC8).

Contrat io :
    inputs : {
        "element": str,              # "poteau" | "poutre" | "dalle"
        "b_mm": int,                 # poteau: largeur ; poutre: bt ; dalle: 1000 par defaut
        "h_mm": int,
        "enrobage_mm": int,
        "fck_mpa": float,
        "fyk_mpa": float,
        "N_Ed_kN"?: float            # requis si element="poteau"
    }
    outputs : {
        "As_min_mm2": float,
        "regle_appliquee": str,
        "fctm_mpa": float,
        "reference": str
    }
"""
from __future__ import annotations

ELEMENTS = {"poteau", "poutre", "dalle"}
GAMMA_S = 1.15


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    elem = inputs.get("element")
    if elem not in ELEMENTS:
        raise ValueError(f"element doit etre dans {sorted(ELEMENTS)}")

    for nom in ("h_mm", "enrobage_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} entier > 0 requis")
    for nom in ("fck_mpa", "fyk_mpa"):
        v = inputs.get(nom)
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"{nom} > 0 requis")

    b = inputs.get("b_mm")
    if elem == "dalle":
        b = b or 1000
    if not isinstance(b, int) or b <= 0:
        raise ValueError("b_mm entier > 0 requis (sauf dalle : defaut 1000)")

    h = inputs["h_mm"]
    c = inputs["enrobage_mm"]
    fck = inputs["fck_mpa"]
    fyk = inputs["fyk_mpa"]
    if c >= h:
        raise ValueError("enrobage >= h : section impossible")

    fyd = fyk / GAMMA_S
    fctm = 0.30 * (fck ** (2.0 / 3.0)) if fck <= 50 else None
    if fctm is None:
        raise ValueError("fck > 50 MPa : domaine BHP (§3.1.6 EC2 (101)), formule fctm differente")

    d = h - c

    if elem == "poteau":
        N = inputs.get("N_Ed_kN")
        if not isinstance(N, (int, float)) or N <= 0:
            raise ValueError("N_Ed_kN > 0 requis pour element=poteau")
        N_N = N * 1000.0  # kN -> N
        Ac = b * h  # mm²
        regle = "EC2 §9.5.2 max(0.10·N_Ed/fyd , 0.002·Ac)"
        as_min = max(0.10 * N_N / fyd, 0.002 * Ac)
    else:  # poutre ou dalle (meme formule, b different)
        regle = "EC2 §9.2.1.1 / §9.3.1.1 max(0.26·fctm/fyk·b·d , 0.0013·b·d)"
        as_min = max(0.26 * (fctm / fyk) * b * d, 0.0013 * b * d)

    return {
        "As_min_mm2": round(as_min, 1),
        "regle_appliquee": regle,
        "fctm_mpa": round(fctm, 2),
        "fyd_mpa": round(fyd, 2),
        "element": elem,
        "reference": "NF EN 1992-1-1 §9.2/§9.3/§9.5 + §3.1.6 (fctm)",
    }
