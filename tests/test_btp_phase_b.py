"""
tests/test_btp_phase_b.py — Tests Phase B, lot Claude Code (skills V2).

Mission : ZORAN_JOBS_20260521 · Phase B · lot Claude Code.
Signé : Claude Code, prestataire, 2026-05-21.

Skills hors 20/80 (zéro collision avec les lots Sonnet) — domaines : thermique,
acoustique, charges, VRD, enveloppe, sécurité, économie, CVC.

Chaque skill : 1 cas positif vérifié à la main + 1 cas négatif (ValueError).
Chargement via le runtime réel (Registry + Loader, hash sha256 + validation V2).

Exécutable : python tests/test_btp_phase_b.py
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

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


print("=" * 60)
print("TESTS BTP PHASE B — lot Claude Code")
print("=" * 60)

_reg = Registry()
_reg.load_from_dir(ROOT / "skills_examples")
_loader = Loader()


def run_of(skill_id: str):
    """Charge un skill via le runtime (hash + validation V2) et renvoie run."""
    manifest = _reg.get(skill_id)
    if manifest is None:
        raise AssertionError(f"{skill_id} absent du registry")
    module, err = _loader.load(manifest)
    if module is None:
        raise AssertionError(f"{skill_id} non chargé : {err}")
    return module.run


def raises_value_error(fn, payload) -> bool:
    try:
        fn(payload)
        return False
    except ValueError:
        return True
    except Exception:
        return False


def manifest_v2_ok(skill_id: str) -> bool:
    """Vérifie que le skill est bien V2 : multi-frame présent, poids = 1.0."""
    m = _reg.get(skill_id)
    if m is None or not m.coherence_multi_frame:
        return False
    total = sum(c.get("weight", 0.0) for c in m.coherence_multi_frame.values())
    return abs(total - 1.0) <= 0.01


# ===========================================================================
# BLOC THERMIQUE — 4 skills
# ===========================================================================
print("\n[Bloc Thermique]")

# --- btp_calc_resistance_thermique ---
run = run_of("btp_calc_resistance_thermique")
# béton 0.20 m / λ=1.75  →  R=0.11429 ; laine 0.14 m / λ=0.035 → R=4.0
# R_total = Rsi 0.13 + 0.11429 + 4.0 + Rse 0.04 = 4.2843 ; U = 1/4.2843 = 0.2334
r = run({"couches": [{"materiau": "beton", "epaisseur_m": 0.20, "lambda_w_mk": 1.75},
                     {"materiau": "laine", "epaisseur_m": 0.14, "lambda_w_mk": 0.035}]})
check("resistance_thermique : R ≈ 4.2843 m²K/W (calcul main)",
      abs(r["resistance_totale_m2k_w"] - 4.2843) < 0.001)
check("resistance_thermique : U ≈ 0.2334 W/m²K", abs(r["coefficient_u_w_m2k"] - 0.2334) < 0.001)
check("resistance_thermique : couches vides → ValueError",
      raises_value_error(run, {"couches": []}))
check("resistance_thermique : manifest V2 valide", manifest_v2_ok("btp_calc_resistance_thermique"))

# --- btp_calc_deperdition_paroi ---
run = run_of("btp_calc_deperdition_paroi")
# U=0.5, S=10 m², ΔT=20 K → Φ = 0.5 × 10 × 20 = 100 W
r = run({"coefficient_u_w_m2k": 0.5, "surface_m2": 10, "delta_temperature_k": 20})
check("deperdition_paroi : Φ = 100 W (calcul main)", abs(r["deperdition_w"] - 100.0) < 0.01)
# via R = 2.0 → U = 0.5 → même résultat
r2 = run({"resistance_m2k_w": 2.0, "surface_m2": 10, "delta_temperature_k": 20})
check("deperdition_paroi : R=2.0 → Φ = 100 W (U dérivé)", abs(r2["deperdition_w"] - 100.0) < 0.01)
check("deperdition_paroi : surface nulle → ValueError",
      raises_value_error(run, {"coefficient_u_w_m2k": 0.5, "surface_m2": 0,
                               "delta_temperature_k": 20}))

# --- btp_classe_dpe_estimatif ---
run = run_of("btp_classe_dpe_estimatif")
check("dpe : 150 kWh_ep/m².an → classe C", run({"consommation_kwh_ep_m2_an": 150})["classe_dpe"] == "C")
check("dpe : 50 → classe A", run({"consommation_kwh_ep_m2_an": 50})["classe_dpe"] == "A")
check("dpe : 500 → classe G", run({"consommation_kwh_ep_m2_an": 500})["classe_dpe"] == "G")
check("dpe : conso négative → ValueError",
      raises_value_error(run, {"consommation_kwh_ep_m2_an": -10}))

# --- btp_calc_pont_thermique_lineaire ---
run = run_of("btp_calc_pont_thermique_lineaire")
# ψ=0.5 × L=10 + ψ=0.2 × L=5  =  5.0 + 1.0 = 6.0 W/K
r = run({"ponts": [{"type": "plancher", "psi_w_mk": 0.5, "longueur_m": 10},
                   {"type": "refend", "psi_w_mk": 0.2, "longueur_m": 5}]})
check("pont_thermique : déperdition = 6.0 W/K (calcul main)",
      abs(r["deperdition_ponts_w_k"] - 6.0) < 0.001)
check("pont_thermique : liste vide → ValueError", raises_value_error(run, {"ponts": []}))
check("pont_thermique : manifest V2 valide", manifest_v2_ok("btp_calc_pont_thermique_lineaire"))

# ===========================================================================
# BLOC ACOUSTIQUE — 2 skills
# ===========================================================================
print("\n[Bloc Acoustique]")

# --- btp_calc_affaiblissement_acoustique ---
run = run_of("btp_calc_affaiblissement_acoustique")
# m=250 kg/m², f=500 Hz → R = 20·log10(125000) − 47 = 54.9 dB
r = run({"masse_surfacique_kg_m2": 250, "frequence_hz": 500})
check("affaiblissement : R ≈ 54.9 dB (calcul main)", abs(r["affaiblissement_db"] - 54.9) < 0.1)
check("affaiblissement : masse nulle → ValueError",
      raises_value_error(run, {"masse_surfacique_kg_m2": 0, "frequence_hz": 500}))

# --- btp_verif_isolement_acoustique_reglementaire ---
run = run_of("btp_verif_isolement_acoustique_reglementaire")
check("isolement : mur 55 dB >= 53 → conforme",
      run({"type_paroi": "mur_entre_logements", "isolement_mesure_db": 55})["conforme"] is True)
check("isolement : choc 60 dB > 58 → non conforme",
      run({"type_paroi": "plancher_choc", "isolement_mesure_db": 60})["conforme"] is False)
check("isolement : choc 50 dB <= 58 → conforme",
      run({"type_paroi": "plancher_choc", "isolement_mesure_db": 50})["conforme"] is True)
check("isolement : type de paroi inconnu → ValueError",
      raises_value_error(run, {"type_paroi": "xxx", "isolement_mesure_db": 55}))

# ===========================================================================
# BLOC CHARGES / ENVELOPPE — 3 skills
# ===========================================================================
print("\n[Bloc Charges / Enveloppe]")

# --- btp_calc_charge_neige ---
run = run_of("btp_calc_charge_neige")
# sk=0.65, angle=20° → μ1=0.8 → s = 0.8 × 1 × 1 × 0.65 = 0.52 kN/m²
r = run({"charge_sol_sk_kn_m2": 0.65, "angle_toiture_deg": 20})
check("charge_neige : s = 0.52 kN/m² (calcul main, μ1=0.8)",
      abs(r["charge_neige_kn_m2"] - 0.52) < 0.001 and abs(r["mu_forme"] - 0.8) < 0.001)
# angle=45° → μ1 = 0.8 × (60−45)/30 = 0.4 → s = 0.26
r2 = run({"charge_sol_sk_kn_m2": 0.65, "angle_toiture_deg": 45})
check("charge_neige : angle 45° → μ1=0.4, s=0.26", abs(r2["charge_neige_kn_m2"] - 0.26) < 0.001)
check("charge_neige : sk négatif → ValueError",
      raises_value_error(run, {"charge_sol_sk_kn_m2": -1, "angle_toiture_deg": 20}))
check("charge_neige : veto_capable (skill structure)",
      _reg.get("btp_calc_charge_neige").veto_capable is True)

# --- btp_calc_charge_exploitation_plancher ---
run = run_of("btp_calc_charge_exploitation_plancher")
# catégorie B (bureaux) qk=2.5 kN/m², surface 20 m² → total = 50 kN
r = run({"categorie": "B", "surface_m2": 20})
check("charge_exploitation : B → qk=2.5, total=50 kN (calcul main)",
      r["charge_repartie_qk_kn_m2"] == 2.5 and abs(r["charge_totale_repartie_kn"] - 50.0) < 0.01)
check("charge_exploitation : catégorie inconnue → ValueError",
      raises_value_error(run, {"categorie": "Z", "surface_m2": 20}))

# --- btp_verif_etancheite_air_re2020 ---
run = run_of("btp_verif_etancheite_air_re2020")
check("etancheite : maison Q4=0.5 <= 0.6 → conforme",
      run({"type_batiment": "maison_individuelle", "q4pa_surf_mesure": 0.5})["conforme"] is True)
check("etancheite : maison Q4=0.8 > 0.6 → non conforme",
      run({"type_batiment": "maison_individuelle", "q4pa_surf_mesure": 0.8})["conforme"] is False)
check("etancheite : type de bâtiment inconnu → ValueError",
      raises_value_error(run, {"type_batiment": "bureau", "q4pa_surf_mesure": 0.5}))

# ===========================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
