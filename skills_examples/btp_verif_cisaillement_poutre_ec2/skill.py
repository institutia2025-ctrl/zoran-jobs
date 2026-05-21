"""skill btp_verif_cisaillement_poutre_ec2 — verif effort tranchant EC2 §6.2.

Mission : ZORAN_JOBS_20260521 · Phase B Structure avancee (3/5).
Source : NF EN 1992-1-1 §6.2 (cisaillement poutres BA).

Methode EC2 :
  1. V_Rd,c (beton seul, §6.2.2 eq.6.2.a/b) :
     V_Rd,c = [C_Rd,c × k × (100 × ρ_l × f_ck)^(1/3)] × b_w × d
     avec :
       C_Rd,c = 0.18 / γ_c = 0.12 (γ_c=1.5 NA)
       k = 1 + √(200/d) ≤ 2.0 (avec d en mm)
       ρ_l = A_sl / (b_w × d) ≤ 0.02
     Borne inferieure (§6.2.2(1)) :
       V_Rd,c >= v_min × b_w × d
       v_min = 0.035 × k^1.5 × √f_ck (eq.6.3N NA)

  2. Si V_Ed ≤ V_Rd,c : pas d'armatures de cisaillement necessaires (sauf min reglementaire §9.2.2).

  3. Si V_Ed > V_Rd,c : armatures requises (§6.2.3, biellage)
     V_Rd,s = (A_sw/s) × z × f_ywd × cot(θ)
     V_Rd,max = α_cw × b_w × z × ν1 × f_cd / (cot θ + tan θ)
     avec : θ in [21.8°, 45°], z ≈ 0.9 × d, ν1 = 0.6 simplifie, α_cw = 1.0

⚠️ MVP : on prend θ = 45° (cot θ = 1) — choix conservateur classique.
   Pour optimisation (θ plus faible = moins d'armatures), iteration §6.2.3(2) requise.

Contrat io :
    inputs : {b_w_mm, h_mm, d_mm, fck_mpa, fyk_mpa, Asl_mm2,
              V_Ed_kN, Asw_mm2?, s_mm?}
    outputs : {V_Rd_c_kN, v_min_mpa, armatures_requises:bool,
               V_Rd_s_kN?, V_Rd_max_kN?, conforme:bool, reference}
"""
from __future__ import annotations

import math

GAMMA_C = 1.5
GAMMA_S = 1.15
ALPHA_CC = 1.0
C_RD_C = 0.18 / GAMMA_C  # = 0.12


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    for nom in ("b_w_mm", "h_mm", "d_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} entier > 0 requis")
    for nom in ("fck_mpa", "fyk_mpa", "Asl_mm2", "V_Ed_kN"):
        v = inputs.get(nom)
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"{nom} > 0 requis")

    b_w = inputs["b_w_mm"]
    d = inputs["d_mm"]
    fck = inputs["fck_mpa"]
    fyk = inputs["fyk_mpa"]
    Asl = inputs["Asl_mm2"]
    V_Ed = inputs["V_Ed_kN"]

    if fck > 90.0:
        raise ValueError("fck > 90 MPa : hors domaine EC2 (§3.1.6)")

    fcd = ALPHA_CC * fck / GAMMA_C
    fyd = fyk / GAMMA_S

    # k facteur de taille
    k = min(1 + math.sqrt(200.0 / d), 2.0)
    rho_l = min(Asl / (b_w * d), 0.02)

    # V_Rd,c (eq. 6.2.a) : N
    VRdc_N = C_RD_C * k * ((100.0 * rho_l * fck) ** (1.0 / 3.0)) * b_w * d
    # Borne inferieure v_min (eq. 6.3N NA)
    v_min = 0.035 * (k ** 1.5) * math.sqrt(fck)
    VRdc_min_N = v_min * b_w * d
    VRdc_N = max(VRdc_N, VRdc_min_N)
    VRdc_kN = VRdc_N / 1000.0

    out = {
        "V_Rd_c_kN": round(VRdc_kN, 2),
        "v_min_mpa": round(v_min, 3),
        "k_facteur_taille": round(k, 3),
        "rho_l": round(rho_l, 5),
        "fcd_mpa": round(fcd, 2),
        "armatures_requises": V_Ed > VRdc_kN,
    }

    if V_Ed <= VRdc_kN:
        # Pas besoin d'armatures (sauf min §9.2.2 - hors scope)
        out["conforme"] = True
        out["ratio_utilisation_beton"] = round(V_Ed / VRdc_kN, 3)
    else:
        # Armatures requises
        Asw = inputs.get("Asw_mm2")
        s = inputs.get("s_mm")
        if not isinstance(Asw, (int, float)) or Asw <= 0:
            raise ValueError("Asw_mm2 > 0 requis si V_Ed > V_Rd,c (armatures de cisaillement)")
        if not isinstance(s, (int, float)) or s <= 0:
            raise ValueError("s_mm > 0 requis si V_Ed > V_Rd,c (espacement)")

        # theta = 45° (conservatif), cot θ = 1.0
        cot_theta = 1.0
        z = 0.9 * d
        # V_Rd,s = (A_sw/s) × z × f_ywd × cot θ
        VRds_N = (Asw / s) * z * fyd * cot_theta
        # V_Rd,max = α_cw × b_w × z × ν1 × f_cd / (cot θ + tan θ)
        nu1 = 0.6
        alpha_cw = 1.0
        VRdmax_N = alpha_cw * b_w * z * nu1 * fcd / (cot_theta + 1.0 / cot_theta)
        VRds_kN = VRds_N / 1000.0
        VRdmax_kN = VRdmax_N / 1000.0
        VRd_kN = min(VRds_kN, VRdmax_kN)

        out["V_Rd_s_kN"] = round(VRds_kN, 2)
        out["V_Rd_max_kN"] = round(VRdmax_kN, 2)
        out["V_Rd_kN_retenu"] = round(VRd_kN, 2)
        out["conforme"] = V_Ed <= VRd_kN
        out["ratio_utilisation_armatures"] = round(V_Ed / VRd_kN, 3)

    out["reference"] = "NF EN 1992-1-1 §6.2.2 + §6.2.3 (Annexe Nationale Francaise γc=1.5, γs=1.15)"
    return out
