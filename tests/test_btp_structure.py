"""
tests/test_btp_structure.py — Tests Phase A Structure simple (5 skills V2).

Mission : ZORAN_JOBS_20260521 · Phase A AXE 3.
Signé : Frederic TABARY + Claude Sonnet, 2026-05-21.

Pour chaque skill : calculs vérifiés à la main + cas négatif + routage E2E.
Toutes les valeurs sont des **calculs Eurocode 2 / EC7 vérifiables**.
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


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def get_mod(skill_id: str):
    reg = Registry()
    reg.load_from_dir(ROOT / "skills_examples")
    m = reg.get(skill_id)
    assert m is not None, skill_id
    loader = Loader()
    mod, err = loader.load(m)
    assert mod is not None, err
    return mod


# ===========================================================================
# 1 — btp_verif_poteau_beton
# ===========================================================================
print("=== TEST 1 — btp_verif_poteau_beton ===")
mod = get_mod("btp_verif_poteau_beton")

# Cas verifiable a la main :
# b=300mm h=300mm L=3000mm fck=25 fyk=500 As=1257 mm² (4HA20) N_Ed=600 kN
# fcd = 25/1.5 = 16.667 ; fyd = 500/1.15 = 434.78
# N_Rd = 300*300*16.667 + 1257*434.78 = 1500000 + 546520 = 2046520 N = 2046.5 kN
# elancement : i = 300/sqrt(12)=86.6 ; lambda = 3000/86.6 = 34.6 -> elance !
out = mod.run({"b_mm": 300, "h_mm": 300, "longueur_libre_mm": 3000,
               "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1257, "N_Ed_kN": 600})
check("N_Rd ≈ 2046 kN (calcul main)", abs(out["N_Rd_kN"] - 2046.52) < 1.0)
check("elancement λ ≈ 34.6 (calcul main)", abs(out["elancement"] - 34.64) < 0.1)
check("elance=True (lambda > 30) → non conforme MVP",
      out["elance"] is True and out["conforme"] is False)

# Cas non elance : L=2000 -> lambda=23
out2 = mod.run({"b_mm": 300, "h_mm": 300, "longueur_libre_mm": 2000,
                "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1257, "N_Ed_kN": 600})
check("L=2000mm → non elance + conforme",
      out2["elance"] is False and out2["conforme"] is True)

# Negatif
err = False
try:
    mod.run({"b_mm": -100, "h_mm": 300, "longueur_libre_mm": 2000,
             "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1257, "N_Ed_kN": 600})
except ValueError:
    err = True
check("b_mm negatif → ValueError", err)


# ===========================================================================
# 2 — btp_verif_poutre_flexion
# ===========================================================================
print()
print("=== TEST 2 — btp_verif_poutre_flexion ===")
mod = get_mod("btp_verif_poutre_flexion")

# b=300 h=600 c=40 As=1571mm² (5HA20) fck=25 fyk=500 M_Ed=200 kNm
# d = 560 ; fyd=434.78 ; z=0.9*560=504 mm
# M_Rd = 1571 * 434.78 * 504 = 344 226 235 Nmm ≈ 344.2 kNm
out = mod.run({"b_mm": 300, "h_mm": 600, "enrobage_mm": 40,
               "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1571, "M_Ed_kNm": 200})
check("M_Rd ≈ 344 kNm (calcul main)", abs(out["M_Rd_kNm"] - 344.2) < 1.0)
check("conforme (M_Ed=200 < M_Rd=344)", out["conforme"] is True)

# Cas M_Ed depasse
out_ko = mod.run({"b_mm": 300, "h_mm": 600, "enrobage_mm": 40,
                  "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1571, "M_Ed_kNm": 400})
check("M_Ed=400 > M_Rd=344 → non conforme", out_ko["conforme"] is False)

# Negatif
err = False
try:
    mod.run({"b_mm": 300, "h_mm": 600, "enrobage_mm": 700,  # enrobage > h
             "fck_mpa": 25, "fyk_mpa": 500, "As_mm2": 1571, "M_Ed_kNm": 200})
except ValueError:
    err = True
check("enrobage > h → ValueError", err)


# ===========================================================================
# 3 — btp_verif_dalle_simple
# ===========================================================================
print()
print("=== TEST 3 — btp_verif_dalle_simple ===")
mod = get_mod("btp_verif_dalle_simple")

# L=5m, h=200mm, c=25mm, type=simple, fck=25
# d=175 mm ; ratio=5000/175=28.57 > 25 → non conforme
out = mod.run({"portee_l_m": 5.0, "epaisseur_h_mm": 200, "enrobage_mm": 25,
               "type_appui": "simple", "fck_mpa": 25})
check("L=5m h=200mm appui simple → non conforme (ratio 28.6 > 25)",
      out["conforme"] is False and abs(out["ratio_l_d"] - 28.57) < 0.1)

# h=250 → d=225 ; ratio=22.2 < 25 → conforme
out_ok = mod.run({"portee_l_m": 5.0, "epaisseur_h_mm": 250, "enrobage_mm": 25,
                  "type_appui": "simple", "fck_mpa": 25})
check("h=250mm → conforme (ratio 22.2 < 25)", out_ok["conforme"] is True)

# Negatif
err = False
try:
    mod.run({"portee_l_m": 5.0, "epaisseur_h_mm": 200, "enrobage_mm": 25,
             "type_appui": "yolo", "fck_mpa": 25})
except ValueError:
    err = True
check("type_appui='yolo' → ValueError", err)


# ===========================================================================
# 4 — btp_fondation_semelle_isolee
# ===========================================================================
print()
print("=== TEST 4 — btp_fondation_semelle_isolee ===")
mod = get_mod("btp_fondation_semelle_isolee")

# N=600 kN ; sigma_sol=200 kPa
# A_mini = 600/200 = 3 m² ; B = sqrt(3) ≈ 1.73 m ≈ 1750 mm (arrondi 50)
# A_corrigee = 1.75² = 3.0625 m² ; sigma_appliquee = 600/3.0625 = 195.9 kPa
out = mod.run({"N_Ed_kN": 600, "sigma_sol_kpa": 200,
               "source_etude_sol": "G2 rapport BET geotech 2024",
               "profondeur_ancrage_mm": 800})
check("B ≈ 1750 mm (calcul main)", out["B_cote_mm"] == 1750)
check("sigma_appliquee ≈ 195.9 kPa", abs(out["contrainte_appliquee_kpa"] - 195.92) < 1.0)
check("conforme (sigma_appliquee < sigma_sol)", out["conforme"] is True)
check("source etude tracee", "G2" in out["source_etude_sol_tracee"])

# Negatif : source manquante (Loi 1)
err = False
try:
    mod.run({"N_Ed_kN": 600, "sigma_sol_kpa": 200,
             "source_etude_sol": "",
             "profondeur_ancrage_mm": 800})
except ValueError:
    err = True
check("source vide → ValueError (Loi 1)", err)


# ===========================================================================
# 5 — btp_ferraillage_min_eurocode
# ===========================================================================
print()
print("=== TEST 5 — btp_ferraillage_min_eurocode ===")
mod = get_mod("btp_ferraillage_min_eurocode")

# POTEAU : b=300 h=300 N=600 kN ; fyd=434.78
# As_min = max( 0.1 * 600000 / 434.78 , 0.002 * 90000 )
#        = max( 138.0 , 180.0 ) = 180.0 mm²
out_p = mod.run({"element": "poteau", "b_mm": 300, "h_mm": 300, "enrobage_mm": 30,
                 "fck_mpa": 25, "fyk_mpa": 500, "N_Ed_kN": 600})
check("poteau 300×300 N=600 → As_min = 180 mm² (regle 0.002·Ac)",
      abs(out_p["As_min_mm2"] - 180.0) < 0.1)

# POUTRE : b=300 h=600 c=40 → d=560 ; fctm = 0.3 × 25^(2/3) = 0.3 × 8.5499 = 2.5650
# As_min = max( 0.26 × (2.565/500) × 300 × 560 , 0.0013 × 300 × 560 )
#        = max( 224.0 , 218.4 ) = 224.0 mm² environ
out_b = mod.run({"element": "poutre", "b_mm": 300, "h_mm": 600, "enrobage_mm": 40,
                 "fck_mpa": 25, "fyk_mpa": 500})
check("poutre 300×600 → As_min ≈ 224 mm² (regle fctm)",
      abs(out_b["As_min_mm2"] - 224.0) < 1.0)

# DALLE : b=1000 par defaut h=200 c=25 → d=175 ; fctm=2.565
# As_min = max( 0.26 × (2.565/500) × 1000 × 175 , 0.0013 × 1000 × 175 )
#        = max( 233.4 , 227.5 ) = 233.4 mm²/m
out_d = mod.run({"element": "dalle", "h_mm": 200, "enrobage_mm": 25,
                 "fck_mpa": 25, "fyk_mpa": 500})
check("dalle h=200 → As_min ≈ 233 mm²/m", abs(out_d["As_min_mm2"] - 233.4) < 1.0)

# Negatif : poteau sans N_Ed
err = False
try:
    mod.run({"element": "poteau", "b_mm": 300, "h_mm": 300, "enrobage_mm": 30,
             "fck_mpa": 25, "fyk_mpa": 500})
except ValueError:
    err = True
check("poteau sans N_Ed → ValueError", err)


# ===========================================================================
# 6 — Routage E2E
# ===========================================================================
print()
print("=== TEST 6 — Routage E2E sur les 5 skills Structure ===")
reg = Registry()
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()

prompts = [
    ("verifier poteau beton compression ec2 elancement",
     "btp_verif_poteau_beton",
     {"b_mm": 300, "h_mm": 300, "longueur_libre_mm": 2000, "fck_mpa": 25,
      "fyk_mpa": 500, "As_mm2": 1257, "N_Ed_kN": 600}),
    ("verifier poutre flexion moment eurocode 2",
     "btp_verif_poutre_flexion",
     {"b_mm": 300, "h_mm": 600, "enrobage_mm": 40, "fck_mpa": 25,
      "fyk_mpa": 500, "As_mm2": 1571, "M_Ed_kNm": 200}),
    ("predimensionner dalle epaisseur fleche l/d",
     "btp_verif_dalle_simple",
     {"portee_l_m": 5.0, "epaisseur_h_mm": 250, "enrobage_mm": 25,
      "type_appui": "simple", "fck_mpa": 25}),
    ("dimensionner semelle isolee fondation sigma sol DTU 13.1 EC7",
     "btp_fondation_semelle_isolee",
     {"N_Ed_kN": 600, "sigma_sol_kpa": 200,
      "source_etude_sol": "G2 BET 2024", "profondeur_ancrage_mm": 800}),
    ("calcul ferraillage minimum armature poteau ec2 §9.5",
     "btp_ferraillage_min_eurocode",
     {"element": "poteau", "b_mm": 300, "h_mm": 300, "enrobage_mm": 30,
      "fck_mpa": 25, "fyk_mpa": 500, "N_Ed_kN": 600}),
]
for prompt, attendu, inps in prompts:
    state = CoherenceState()
    trace = run_once(prompt, inps, reg, loader, state)
    actual = trace.get("selected", "<none>")
    check(f"'{prompt[:45]}…' → {attendu}", actual == attendu)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
