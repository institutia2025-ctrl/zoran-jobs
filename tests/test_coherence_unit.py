"""
tests/test_coherence_unit.py — Tests UNITAIRES isolés du Coherence Engine.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP (consolidation)
Signé : Claude, prestataire, 2026-05-21

Complète les tests d'intégration : ici on prouve que chaque fonction
mathématique du moteur de cohérence est correcte EN ISOLATION TOTALE.
Aucun registry, aucun loader, aucun router. Juste de l'arithmétique
prédictible à la main.

12 assertions ciblant les cas limites identifiés à l'audit indépendant.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from runtime.coherence.engine import (  # noqa: E402
    CoherenceState,
    compute_S,
    delta_S,
    dS_dt,
)

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


print("=== TEST 1 — compute_S : valeurs canoniques (predictible a la main) ===")
# S = (β × ΔΦ) / (1 + T + σ)
check("compute_S(1,1,0,0) == 1.0", compute_S(1, 1, 0, 0) == 1.0)
check("compute_S(5,5,0,0) == 25.0 (INV-1 limit case)", compute_S(5, 5, 0, 0) == 25.0)
check("compute_S(2,3,1,1) == 2.0 (=6/3)", compute_S(2, 3, 1, 1) == 2.0)
check("compute_S(0,5,0,0) == 0 (beta=0 nullifie)", compute_S(0, 5, 0, 0) == 0.0)
check("compute_S(5,0,0,0) == 0 (delta_phi=0 nullifie)", compute_S(5, 0, 0, 0) == 0.0)

print()
print("=== TEST 2 — compute_S : robustesse aux entrees pathologiques ===")
# INV-1 : dénominateur additif ⇒ jamais d'infini, jamais de NaN
s_huge_T = compute_S(1, 1, 1e18, 0)
check("T=1e18 n'explose pas, S fini > 0", math.isfinite(s_huge_T) and s_huge_T > 0)
# Entrées négatives sur T/σ doivent être clampées à 0 par l'engine (max(0., ...))
check("T negatif clampe → compute_S(1,1,-5,0) == 1.0", compute_S(1, 1, -5, 0) == 1.0)
check("sigma negatif clampe → compute_S(1,1,0,-5) == 1.0", compute_S(1, 1, 0, -5) == 1.0)

print()
print("=== TEST 3 — delta_S : signe et magnitude ===")
state = CoherenceState(beta=1.0, delta_phi=0.0, T=0.0, sigma=0.0)
coh_positive = {"expected_delta_phi": 0.5, "expected_T_added": 0.0, "expected_sigma_added": 0.0}
coh_negative = {"expected_delta_phi": 0.0, "expected_T_added": 0.5, "expected_sigma_added": 0.5}
check("delta_S > 0 si skill apporte ΔΦ", delta_S(state, coh_positive) > 0)
check("delta_S <= 0 si skill ajoute T/sigma sans gain", delta_S(state, coh_negative) <= 0)

print()
print("=== TEST 4 — dS_dt : cinematique ===")
empty = CoherenceState()
check("dS_dt() == 0 si historique vide ou trop court", dS_dt(empty) == 0.0)
trend_up = CoherenceState()
trend_up.S_history = [1.0, 2.0, 3.0]
check("dS_dt > 0 sur historique croissant (1,2,3)", dS_dt(trend_up) > 0)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
