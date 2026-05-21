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
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
