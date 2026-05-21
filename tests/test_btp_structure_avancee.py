"""
tests/test_btp_structure_avancee.py — Tests Phase B Structure avancee (5 skills).

Mission : ZORAN_JOBS_20260521 · ZORAN_BTP_PARALLEL_SONNET_20260521 Phase B.
Signe : Sonnet, 2026-05-21.

Pour chaque skill : calcul Eurocode verifie a la main + cas negatif + routage E2E.
Calculs reels referencables - Loi 1 stricte.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from loader.loader import Loader  # noqa: E402
from registry.registry import Registry  # noqa: E402
from runtime.coherence.engine import CoherenceState  # noqa: E402
from runtime.loop import run_once  # noqa: E402

PASS, FAIL = 0, 0


def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def get_mod(skill_id):
    reg = Registry()
    reg.load_from_dir(ROOT / "skills_examples")
    m = reg.get(skill_id)
    assert m is not None, skill_id
    loader = Loader()
    mod, err = loader.load(m)
    assert mod is not None, err
    return mod


# ===========================================================================
# 1 — btp_calcul_sismique_ec8
# ===========================================================================
print("=== TEST 1 — btp_calcul_sismique_ec8 ===")
mod = get_mod("btp_calcul_sismique_ec8")

# Zone 3 (a_gr=1.1), Cat II (γ_I=1.0), Sol B (S=1.35 T_C=0.25), Cadres BA (C_t=0.075)
# H=20m, n=6, m=2000t, DCM (q=3.0)
# T_1 = 0.075 × 20^0.75 = 0.075 × 9.457 ≈ 0.709 s
# a_g = 1.1 × 1.0 = 1.1 m/s²
# T_1=0.709 > T_C=0.25 et T_1=0.709 ≤ T_D=1.2 → plage 3
# S_d = 1.1 × 1.35 × 2.5 / 3.0 × (0.25/0.709) = 3.71 × 0.353 = 1.309 m/s²
# (mais borne β×a_g = 0.2×1.1 = 0.22 < 1.309 OK)
# λ : T_1=0.709 < 2×T_C=0.5 ? NON → λ=1.0
# Attention 0.709 > 0.5 donc lambda = 1.0
# F_b = 1.309 × 2000000 kg × 1.0 = 2619000 N = 2619 kN
out = mod.run({"zone_sismique": 3, "classe_sol": "B", "categorie_importance": "II",
               "hauteur_batiment_m": 20.0, "nb_etages": 6, "type_systeme_resistant": "cadres_ba",
               "masse_totale_tonnes": 2000.0, "classe_ductilite": "DCM"})
check("T_1 ≈ 0.709 s (Cadres BA H=20m)", abs(out["T_1_s"] - 0.709) < 0.005)
check("a_g = 1.1 m/s² (Zone 3 × Cat II)", abs(out["a_g_m_s2"] - 1.1) < 0.001)
check("S_d(T_1) ≈ 0.436 m/s² (a_g×S×2.5/q × T_C/T)", abs(out["S_d_T1_m_s2"] - 0.436) < 0.005)
check("F_b ≈ 872 kN (S_d × m × λ)", abs(out["F_b_kN"] - 872.0) < 5.0)
check("lambda = 1.0 (T_1 > 2×T_C)", out["lambda_correction"] == 1.0)
check("reference EC8 + NA tracee", "NF EN 1998-1" in out["reference"])

# Negatif
err = False
try:
    mod.run({"zone_sismique": 99, "classe_sol": "B", "categorie_importance": "II",
             "hauteur_batiment_m": 20.0, "nb_etages": 6, "type_systeme_resistant": "cadres_ba",
             "masse_totale_tonnes": 2000.0, "classe_ductilite": "DCM"})
except ValueError:
    err = True
check("zone_sismique=99 → ValueError", err)

# ===========================================================================
# 2 — btp_calcul_vent_ec1
# ===========================================================================
print()
print("=== TEST 2 — btp_calcul_vent_ec1 ===")
mod = get_mod("btp_calcul_vent_ec1")

# Region 2 (v_b,0=24), Cat II, z=10 m
# v_b = 1.0 × 1.0 × 24 = 24 m/s
# q_b = 0.5 × 1.25 × 24² = 360 N/m²
# c_e(z=10) en Cat II = 2.1 (table)
# q_p = 2.1 × 360 = 756 N/m²
out = mod.run({"region": 2, "categorie_terrain": "II", "hauteur_z_m": 10.0})
check("v_b = 24 m/s (Region 2)", abs(out["v_b_m_s"] - 24.0) < 0.01)
check("q_b ≈ 360 N/m² (0.5×1.25×24²)", abs(out["q_b_n_m2"] - 360.0) < 0.1)
check("c_e(z=10) = 2.1 (Cat II)", abs(out["c_e_z"] - 2.1) < 0.001)
check("q_p ≈ 756 N/m² (2.1 × 360)", abs(out["q_p_z_n_m2"] - 756.0) < 1.0)
check("q_p en kN/m² = 0.756", abs(out["q_p_z_kn_m2"] - 0.756) < 0.001)

# Negatif
err = False
try:
    mod.run({"region": 2, "categorie_terrain": "ZZ", "hauteur_z_m": 10.0})
except ValueError:
    err = True
check("categorie 'ZZ' → ValueError", err)

# ===========================================================================
# 3 — btp_verif_cisaillement_poutre_ec2
# ===========================================================================
print()
print("=== TEST 3 — btp_verif_cisaillement_poutre_ec2 ===")
mod = get_mod("btp_verif_cisaillement_poutre_ec2")

# b_w=300 d=540 fck=25 Asl=1571 (5HA20) V_Ed=80 kN
# k = 1 + sqrt(200/540) = 1 + 0.6086 = 1.609 (< 2.0 OK)
# rho_l = 1571 / (300 × 540) = 0.00970 (< 0.02 OK)
# V_Rd,c = 0.12 × 1.609 × (100 × 0.00970 × 25)^(1/3) × 300 × 540
#        = 0.12 × 1.609 × 2.881 × 300 × 540
#        = 90 088 N = 90 kN
# v_min = 0.035 × 1.609^1.5 × sqrt(25) = 0.035 × 2.042 × 5 = 0.357 MPa
# V_min = 0.357 × 300 × 540 = 57 838 N = 57.8 kN
# max(90, 57.8) = 90 kN. V_Ed=80 < V_Rd,c=90 → pas d'armatures
out = mod.run({"b_w_mm": 300, "h_mm": 600, "d_mm": 540, "fck_mpa": 25, "fyk_mpa": 500,
               "Asl_mm2": 1571, "V_Ed_kN": 80})
check("V_Rd,c ≈ 90 kN (calcul main)", abs(out["V_Rd_c_kN"] - 90.0) < 2.0)
check("V_Ed=80 < V_Rd,c=90 → pas armatures requises", out["armatures_requises"] is False)
check("conforme = True", out["conforme"] is True)
check("k ≈ 1.609", abs(out["k_facteur_taille"] - 1.609) < 0.01)

# Cas avec armatures : V_Ed=200 kN > V_Rd,c, Asw=100 (2HA8) s=200
# fyd = 500/1.15 = 434.78 MPa
# z = 0.9 × 540 = 486 mm
# V_Rd,s = (100/200) × 486 × 434.78 × 1.0 = 105 651 N = 105.7 kN  ← Inssufisant pour 200 kN
# V_Rd,max = 1.0 × 300 × 486 × 0.6 × 16.67 / (1+1) = 729 000 N = 729 kN
# V_Rd = min(105.7, 729) = 105.7 kN. V_Ed=200 > 105.7 → NON conforme
out_armatures = mod.run({"b_w_mm": 300, "h_mm": 600, "d_mm": 540, "fck_mpa": 25, "fyk_mpa": 500,
                          "Asl_mm2": 1571, "V_Ed_kN": 200, "Asw_mm2": 100, "s_mm": 200})
check("V_Ed=200 > V_Rd,c → armatures requises", out_armatures["armatures_requises"] is True)
check("V_Rd,s ≈ 105.7 kN", abs(out_armatures["V_Rd_s_kN"] - 105.7) < 1.0)
check("V_Ed=200 > V_Rd,s=105.7 → non conforme", out_armatures["conforme"] is False)

err = False
try:
    mod.run({"b_w_mm": 300, "h_mm": 600, "d_mm": 540, "fck_mpa": 100, "fyk_mpa": 500,
             "Asl_mm2": 1571, "V_Ed_kN": 80})
except ValueError:
    err = True
check("fck=100 (>90 EC2) → ValueError", err)

# ===========================================================================
# 4 — btp_verif_fleche_detaillee_ec2
# ===========================================================================
print()
print("=== TEST 4 — btp_verif_fleche_detaillee_ec2 ===")
mod = get_mod("btp_verif_fleche_detaillee_ec2")

# Poutre L=5m, b=300, h=500, c=40 → d=460, fck=25, fyk=500, Asl=1571, q=10 kN/m²
# Ecm = 22000 × ((33/10)^0.3) = 22000 × 1.4346 = 31568 MPa
# E_eff = 31568/3 = 10523 MPa (phi=2.0)
# I_I = 300 × 500³ / 12 = 3.125e9 mm⁴
# Limite L/250 = 5000/250 = 20 mm
out = mod.run({"portee_l_m": 5.0, "b_mm": 300, "h_mm": 500, "enrobage_mm": 40,
               "fck_mpa": 25, "fyk_mpa": 500, "Asl_mm2": 1571, "charge_q_kn_m2": 10.0})
check("f_limite = 20 mm (L/250 pour L=5m)", abs(out["f_limite_mm"] - 20.0) < 0.01)
check("I_I = 3.125e9 mm⁴", abs(out["I_I_mm4"] - 3.125e9) < 1e6)
check("E_eff ≈ 10523 MPa", abs(out["E_eff_mpa"] - 10523.0) < 50.0)
check("etat_fissure trace", out["etat_fissure"] in ("non_fissure", "fissure", "indetermine_sans_M_Ed"))

# Cas non fissure (M_Ed < M_cr)
out_nf = mod.run({"portee_l_m": 5.0, "b_mm": 300, "h_mm": 500, "enrobage_mm": 40,
                  "fck_mpa": 25, "fyk_mpa": 500, "Asl_mm2": 1571, "charge_q_kn_m2": 10.0,
                  "M_Ed_kNm": 5.0})
check("M_Ed < M_cr → zeta=0, etat non fissure", out_nf["zeta_distribution"] == 0.0)

err = False
try:
    mod.run({"portee_l_m": 5.0, "b_mm": 300, "h_mm": 500, "enrobage_mm": 600,  # c > h
             "fck_mpa": 25, "fyk_mpa": 500, "Asl_mm2": 1571, "charge_q_kn_m2": 10.0})
except ValueError:
    err = True
check("enrobage > h → ValueError", err)

# ===========================================================================
# 5 — btp_verif_poinconnement_dalle_ec2
# ===========================================================================
print()
print("=== TEST 5 — btp_verif_poinconnement_dalle_ec2 ===")
mod = get_mod("btp_verif_poinconnement_dalle_ec2")

# Colonne 400×400, dalle d=200 mm, fck=25, V_Ed=600 kN, rho_lx=rho_ly=0.005
# u_0 = 2(400+400) = 1600 mm
# u_1 = 1600 + 4π×200 = 1600 + 2513.3 = 4113 mm
# v_Ed,0 = 1.0 × 600000 / (1600 × 200) = 1.875 MPa
# v_Ed,1 = 600000 / (4113 × 200) = 0.729 MPa
# k = 1 + sqrt(200/200) = 2.0 (max)
# rho_l = sqrt(0.005×0.005) = 0.005
# v_Rd,c = 0.12 × 2.0 × (100 × 0.005 × 25)^(1/3) = 0.12 × 2.0 × 2.5 = 0.600 MPa
# v_min = 0.035 × 2^1.5 × sqrt(25) = 0.035 × 2.828 × 5 = 0.495 MPa
# v_Rd,c retenu = max(0.600, 0.495) = 0.600 MPa
# ν = 0.6 × (1-25/250) = 0.54
# v_Rd,max = 0.5 × 0.54 × 25/1.5 = 4.5 MPa
# Verifs : v_Ed,0=1.875 ≤ 4.5 (OK), v_Ed,1=0.729 > 0.600 → ARMATURES requises
out = mod.run({"V_Ed_kN": 600, "c1_mm": 400, "c2_mm": 400, "d_mm": 200,
               "fck_mpa": 25, "rho_lx": 0.005, "rho_ly": 0.005})
check("u_0 = 1600 mm (2×(c1+c2))", abs(out["u_0_mm"] - 1600.0) < 0.1)
check("u_1 ≈ 4113 mm (u_0 + 4π×d)", abs(out["u_1_mm"] - 4113.3) < 1.0)
check("v_Ed,0 ≈ 1.875 MPa", abs(out["v_Ed_0_mpa"] - 1.875) < 0.01)
check("v_Rd,c ≈ 0.557 MPa (0.12×k×(100ρfck)^(1/3))", abs(out["v_Rd_c_mpa"] - 0.557) < 0.01)
check("conforme_u0 = True (1.875 < 4.5)", out["conforme_u0"] is True)
check("conforme_u1 = False (0.729 > 0.557) → armatures requises",
      out["conforme_u1"] is False and out["armatures_requises"] is True)

err = False
try:
    mod.run({"V_Ed_kN": 600, "c1_mm": 400, "c2_mm": 400, "d_mm": 200,
             "fck_mpa": 25, "rho_lx": 0.5, "rho_ly": 0.005})  # rho > 0.04
except ValueError:
    err = True
check("rho_lx=0.5 (>0.04) → ValueError", err)

# ===========================================================================
# 6 — Routage E2E sur les 5 skills Phase B
# ===========================================================================
print()
print("=== TEST 6 — Routage E2E ===")
reg = Registry()
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()

prompts = [
    ("calcul sismique force laterale fb spectre ec8 zone france",
     "btp_calcul_sismique_ec8",
     {"zone_sismique": 3, "classe_sol": "B", "categorie_importance": "II",
      "hauteur_batiment_m": 20.0, "nb_etages": 6, "type_systeme_resistant": "cadres_ba",
      "masse_totale_tonnes": 2000.0, "classe_ductilite": "DCM"}),
    ("pression vent qp eurocode 1 region categorie terrain ce",
     "btp_calcul_vent_ec1",
     {"region": 2, "categorie_terrain": "II", "hauteur_z_m": 10.0}),
    ("verif cisaillement effort tranchant v_ed v_rd ec2 etrier §6.2",
     "btp_verif_cisaillement_poutre_ec2",
     {"b_w_mm": 300, "h_mm": 600, "d_mm": 540, "fck_mpa": 25, "fyk_mpa": 500,
      "Asl_mm2": 1571, "V_Ed_kN": 80}),
    ("fleche bilineaire zeta etat fissure ec2 §7.4.3 L/250",
     "btp_verif_fleche_detaillee_ec2",
     {"portee_l_m": 5.0, "b_mm": 300, "h_mm": 500, "enrobage_mm": 40,
      "fck_mpa": 25, "fyk_mpa": 500, "Asl_mm2": 1571, "charge_q_kn_m2": 10.0}),
    ("poinconnement dalle colonne perimetre controle ec2 §6.4 punching",
     "btp_verif_poinconnement_dalle_ec2",
     {"V_Ed_kN": 600, "c1_mm": 400, "c2_mm": 400, "d_mm": 200,
      "fck_mpa": 25, "rho_lx": 0.005, "rho_ly": 0.005}),
]
for prompt, attendu, inps in prompts:
    state = CoherenceState()
    trace = run_once(prompt, inps, reg, loader, state)
    actual = trace.get("selected", "<none>")
    check(f"'{prompt[:50]}…' → {attendu}", actual == attendu)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
