"""skill btp_verif_poinconnement_dalle_ec2 — verif poinconnement EC2 §6.4.

Mission : ZORAN_JOBS_20260521 · Phase B Structure avancee (5/5).
Source : NF EN 1992-1-1 §6.4 (poinconnement dalles BA).

Methode EC2 §6.4 :
  1. Perimetre de controle u_1 a 2d de la face chargee (§6.4.2)
     Pour colonne rectangulaire : u_1 = 2(c1+c2) + 2π × 2d (= 2(c1+c2) + 4πd)
  2. Contrainte de cisaillement applique :
     v_Ed = β × V_Ed / (u_1 × d)
     β = 1.15 typique (coin) / 1.0 (centree) / 1.4 (bord) - simplifie centree ici
  3. Resistance sans armature de poinconnement (§6.4.4) :
     v_Rd,c = C_Rd,c × k × (100 × ρ_l × f_ck)^(1/3)
     k = 1 + √(200/d) ≤ 2.0
     ρ_l = √(ρ_lx × ρ_ly) ≤ 0.02
     borne inferieure v_min (§6.2.2(1))
  4. v_Rd,max (§6.4.5(3) NA) : 0.5 × ν × f_cd
     ν = 0.6 × (1 - fck/250)
  5. Verifications :
     - Au perimetre u_0 (face colonne) : v_Ed,0 ≤ v_Rd,max
     - Au perimetre u_1 (2d) : v_Ed,1 ≤ v_Rd,c (sans armatures)
       ou v_Rd,cs (avec armatures, §6.4.5)

⚠️ MVP : colonne rectangulaire centree (β=1.0). Pour colonnes en bord
   ou coin, appliquer §6.4.3(3) avec β ou methode du moment d'excentrement.
   Pas d'armatures de poinconnement (etriers verticaux ou doubles têtes)
   — si v_Rd,c depasse, on signale et oriente vers BET.

Contrat io :
    inputs : {V_Ed_kN, c1_mm, c2_mm, d_mm, fck_mpa, rho_lx, rho_ly, beta?}
    outputs : {u_0_mm, u_1_mm, v_Ed_0_mpa, v_Ed_1_mpa, v_Rd_c_mpa,
               v_Rd_max_mpa, conforme_u0, conforme_u1, armatures_requises, reference}
"""
from __future__ import annotations

import math

GAMMA_C = 1.5
ALPHA_CC = 1.0
C_RD_C = 0.18 / GAMMA_C  # = 0.12


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    V_Ed = inputs.get("V_Ed_kN")
    for nom in ("c1_mm", "c2_mm", "d_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} entier > 0 requis (mm)")
    if not isinstance(V_Ed, (int, float)) or V_Ed <= 0:
        raise ValueError("V_Ed_kN > 0 requis")
    fck = inputs.get("fck_mpa")
    if not isinstance(fck, (int, float)) or fck <= 0 or fck > 90:
        raise ValueError("fck_mpa in (0..90] requis (limite EC2 §3.1.6)")
    rho_lx = inputs.get("rho_lx")
    rho_ly = inputs.get("rho_ly")
    for nom, v in [("rho_lx", rho_lx), ("rho_ly", rho_ly)]:
        if not isinstance(v, (int, float)) or v <= 0 or v > 0.04:
            raise ValueError(f"{nom} in (0..0.04] requis (taux d'armature longitudinal)")

    c1 = inputs["c1_mm"]
    c2 = inputs["c2_mm"]
    d = inputs["d_mm"]
    beta = inputs.get("beta", 1.0)  # 1.0 centree (§6.4.3(6))
    if not isinstance(beta, (int, float)) or beta <= 0:
        raise ValueError("beta > 0 requis")

    fcd = ALPHA_CC * fck / GAMMA_C

    # Perimetres
    u_0 = 2 * (c1 + c2)  # face colonne
    u_1 = 2 * (c1 + c2) + 4 * math.pi * d  # a 2d (cercle aux 4 coins)

    # Contraintes appliquees (MPa = N/mm²) — V_Ed en kN → ×1000 en N
    V_Ed_N = V_Ed * 1000.0
    v_Ed_0 = beta * V_Ed_N / (u_0 * d)  # N/mm² = MPa
    v_Ed_1 = beta * V_Ed_N / (u_1 * d)

    # v_Rd,c sans armatures (§6.4.4)
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    rho_l = min(math.sqrt(rho_lx * rho_ly), 0.02)
    vRdc = C_RD_C * k * ((100.0 * rho_l * fck) ** (1.0 / 3.0))
    v_min = 0.035 * (k ** 1.5) * math.sqrt(fck)
    vRdc = max(vRdc, v_min)

    # v_Rd,max (§6.4.5(3) NA)
    nu = 0.6 * (1.0 - fck / 250.0)
    vRdmax = 0.5 * nu * fcd

    conforme_u0 = v_Ed_0 <= vRdmax
    conforme_u1 = v_Ed_1 <= vRdc

    return {
        "u_0_mm": round(u_0, 1),
        "u_1_mm": round(u_1, 1),
        "v_Ed_0_mpa": round(v_Ed_0, 3),
        "v_Ed_1_mpa": round(v_Ed_1, 3),
        "v_Rd_c_mpa": round(vRdc, 3),
        "v_Rd_max_mpa": round(vRdmax, 3),
        "v_min_mpa": round(v_min, 3),
        "k_facteur_taille": round(k, 3),
        "rho_l_geom": round(rho_l, 5),
        "conforme_u0": conforme_u0,
        "conforme_u1": conforme_u1,
        "armatures_requises": (not conforme_u1) and conforme_u0,
        "verdict_global": "OK" if (conforme_u0 and conforme_u1) else
                          ("RUPTURE_FACE_COLONNE_revoir_dimensions" if not conforme_u0
                           else "ARMATURES_POINCONNEMENT_REQUISES_§6.4.5"),
        "reference": "NF EN 1992-1-1 §6.4 (perimetres u_0, u_1 a 2d + v_Rd,c + v_Rd,max NA)",
    }
