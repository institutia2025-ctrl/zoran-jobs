"""skill btp_verif_poutre_flexion — verification poutre BA flexion simple.

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Structure (2/5).
Source : NF EN 1992-1-1 §6.1 (flexion ELU).

Approche simplifiee section rectangulaire armee a la traction (As inferieures).
Methode : moment ultime resistant M_Rd avec hypothese bras de levier z = 0.9 × d
(approximation §6.1 EC2, valide si μ < 0.371 pour beton C50/60 max) :

    M_Rd = As × fyd × z

⚠️ MVP : pas de poutre en T, pas d'armatures de compression, pas de cisaillement.
   Le bras de levier 0.9d est une approximation rapide ; un calcul exact passe
   par le diagramme rectangle simplifie EC2 §3.1.7.

Contrat io :
    inputs : {
        "b_mm": int,
        "h_mm": int,
        "enrobage_mm": int,
        "fck_mpa": float,
        "fyk_mpa": float,
        "As_mm2": float,             # armatures tendues
        "M_Ed_kNm": float            # moment ELU
    }
    outputs : {
        "M_Rd_kNm": float,
        "conforme": bool,
        "ratio_utilisation": float,
        "etat": str,                 # "ok"/"sous-armee"/"sur-armee"
        "reference": str
    }
"""
from __future__ import annotations

GAMMA_C = 1.5
GAMMA_S = 1.15
ALPHA_CC = 1.0


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    for nom in ("b_mm", "h_mm", "enrobage_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} doit etre un entier > 0 (en mm)")
    for nom in ("fck_mpa", "fyk_mpa", "As_mm2", "M_Ed_kNm"):
        v = inputs.get(nom)
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"{nom} doit etre un nombre > 0")

    b, h, c = inputs["b_mm"], inputs["h_mm"], inputs["enrobage_mm"]
    fck, fyk = inputs["fck_mpa"], inputs["fyk_mpa"]
    As, M_Ed = inputs["As_mm2"], inputs["M_Ed_kNm"]

    if fck > 50.0:
        raise ValueError("MVP limite a fck <= 50 MPa (C50/60). Au-dela, EC2 §3.1.6(101) BHP requis")
    if c >= h:
        raise ValueError("enrobage >= hauteur : section impossible")

    fcd = ALPHA_CC * fck / GAMMA_C
    fyd = fyk / GAMMA_S

    d = h - c  # hauteur utile
    z = 0.9 * d  # bras de levier approche

    M_Rd_Nmm = As * fyd * z  # N × mm
    M_Rd_kNm = M_Rd_Nmm / 1.0e6

    # Verification non sur-armee : mu = M_Rd / (b × d² × fcd)
    mu = M_Rd_Nmm / (b * d * d * fcd)
    if mu > 0.371:
        etat = "sur-armee"  # depasse mu_lim pour beton ductile, deconseille
    elif mu < 0.05:
        etat = "sous-armee"
    else:
        etat = "ok"

    conforme = (M_Ed <= M_Rd_kNm) and (etat != "sur-armee")

    return {
        "M_Rd_kNm": round(M_Rd_kNm, 2),
        "conforme": conforme,
        "ratio_utilisation": round(M_Ed / M_Rd_kNm, 3),
        "etat": etat,
        "mu": round(mu, 3),
        "fcd_mpa": round(fcd, 2),
        "fyd_mpa": round(fyd, 2),
        "reference": "NF EN 1992-1-1 §6.1 + §3.1.7 (ANF γc=1.5, γs=1.15)",
    }
