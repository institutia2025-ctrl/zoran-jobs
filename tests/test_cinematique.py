"""
tests/test_cinematique.py — Test compétition de skills + cinématique dS/dt.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP (consolidation)
Signé : Claude, prestataire, 2026-05-21

Vérifie les 3 propriétés que ZORAN exige avant Oracle :
  1. COMPÉTITION — plusieurs skills se disputent un prompt, le Router CHOISIT
  2. CINÉMATIQUE — quand S s'effondre (dS/dt < 0), le skill correcteur est
     privilégié (bonus cinématique)
  3. S REMONTE — après exécution du correcteur, la cohérence remonte réellement

Exécutable directement : `python tests/test_cinematique.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# FIX-DEF-1 2026-05-21 : sortie console UTF-8 — portabilité multi-OS.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from loader import Loader  # noqa: E402
from registry import Registry  # noqa: E402
from router import route, score_skill  # noqa: E402
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


reg = Registry()
report = reg.load_from_dir(ROOT / "skills_examples")
print(f"Registry : {report['n_loaded']} skills chargés, {report['n_rejected']} rejetés")
# Robuste à l'ajout de skills : on exige les skills NÉCESSAIRES à ce test,
# pas un compte exact (qui casserait à chaque nouveau skill exemple).
_needed = {"echo", "memory_recall", "printer_connect", "network_diag", "coherence_repair"}
check("les skills nécessaires au test sont chargés",
      _needed.issubset(set(reg.list_skills())))
check("0 skill rejeté", report["n_rejected"] == 0)

print()
print("=== TEST 1 — COMPÉTITION : le Router doit vraiment choisir ===")
# "connecte mon imprimante au reseau" → printer_connect ET network_diag matchent
ranked = route("connecte mon imprimante au reseau", reg.all_manifests(), CoherenceState())
ids = [c.skill_id for c in ranked]
check("≥ 2 skills en compétition", len(ranked) >= 2)
check("printer_connect candidat", "printer_connect" in ids)
check("network_diag candidat", "network_diag" in ids)
check("classement strict (scores différents)",
      len({c.score for c in ranked}) == len(ranked) or len(ranked) < 2)
print(f"  classement : {[(c.skill_id, c.score) for c in ranked]}")

print()
print("=== TEST 2 — CINÉMATIQUE : dérive S<0 ⇒ bonus au skill correcteur ===")
repair = reg.get("coherence_repair")
prompt = "il faut corriger la coherence"
# Sans dérive : S_history plat
state_plat = CoherenceState(S_history=[2.0, 2.0, 2.0])
score_plat = score_skill(prompt, repair, state_plat)
# Avec dérive : S_history descendant → dS/dt < 0
state_derive = CoherenceState(S_history=[5.0, 3.0, 1.0])
score_derive = score_skill(prompt, repair, state_derive)
print(f"  coherence_repair sans dérive : score={score_plat.score} bonus={score_plat.bonus_cinematique}")
print(f"  coherence_repair avec dérive : score={score_derive.score} bonus={score_derive.bonus_cinematique}")
check("sans dérive : bonus cinématique neutre (1.0)", score_plat.bonus_cinematique == 1.0)
check("avec dérive : bonus cinématique actif (1.5)", score_derive.bonus_cinematique == 1.5)
check("le correcteur est mieux classé sous dérive", score_derive.score > score_plat.score)

print()
print("=== TEST 3 — S REMONTE : exécuter le correcteur restaure la cohérence ===")
# État de cohérence basse
state = CoherenceState(beta=1.0, delta_phi=0.1, T=0.0, sigma=0.0)
loader = Loader()
trace = run_once("corriger la coherence du systeme", {}, reg, loader, state)
print(f"  trace : S_before={trace.get('S_before')} → S_after={trace.get('S_after')} "
      f"(ΔS={trace.get('delta_S_real')})")
check("status == ok", trace.get("status") == "ok")
check("skill correcteur sélectionné", trace.get("selected") == "coherence_repair")
check("S_after > S_before (la cohérence est remontée)",
      trace.get("S_after", 0) > trace.get("S_before", 999))
check("ΔS réel positif", trace.get("delta_S_real", -1) > 0)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
