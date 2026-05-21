"""
tests/test_oracle.py — Test de l'Oracle minimal (Phase 2).

Mission : ZORAN_JOBS_20260521 · Phase 2
Signé : Claude, prestataire, 2026-05-21

Prouve que l'Oracle FALSIFIE — il ne fait pas confiance au manifest, il mesure :
  - greet_ok et greet_ko déclarent TOUS DEUX produire {greeting:str}
  - greet_ok respecte ce contrat · greet_ko produit {message:str} (violation)
  - l'Oracle doit RÉVÉLER la violation et désigner greet_ok gagnant
  - le verdict doit être déterministe

Exécutable directement : `python tests/test_oracle.py`.
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
from oracle import compare, evaluate_skill  # noqa: E402
from registry import Registry  # noqa: E402

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
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()
test_cases = [{"name": "Fred"}, {"name": "Xavier"}, {"name": "ZORAN"}]

print("=== TEST 1 — Mesure individuelle (Oracle observe le RÉEL) ===")
m_ok = evaluate_skill(reg.get("greet_ok"), test_cases, loader)
m_ko = evaluate_skill(reg.get("greet_ko"), test_cases, loader)
print(f"  greet_ok : success={m_ok['success_rate']} io_conf={m_ok['io_conformity_rate']} stable={m_ok['stable']}")
print(f"  greet_ko : success={m_ko['success_rate']} io_conf={m_ko['io_conformity_rate']} stable={m_ko['stable']}")
check("greet_ok : success_rate == 1.0", m_ok["success_rate"] == 1.0)
check("greet_ok : io_conformity == 1.0 (respecte son contrat)", m_ok["io_conformity_rate"] == 1.0)
check("greet_ko : success_rate == 1.0 (il ne plante PAS)", m_ko["success_rate"] == 1.0)
check("greet_ko : io_conformity == 0.0 (VIOLE son contrat)", m_ko["io_conformity_rate"] == 0.0)

print()
print("=== TEST 2 — Verdict : l'Oracle désigne le skill conforme ===")
result = compare(reg.get("greet_ok"), reg.get("greet_ko"), test_cases, loader)
print(f"  winner = {result['winner']}")
check("le gagnant est greet_ok", result["winner"] == "greet_ok")
check("greet_ko n'est PAS gagnant malgré 0 exception",
      result["winner"] != "greet_ko")

print()
print("=== TEST 3 — Déterminisme du verdict ===")
r1 = compare(reg.get("greet_ok"), reg.get("greet_ko"), test_cases, loader)
r2 = compare(reg.get("greet_ok"), reg.get("greet_ko"), test_cases, loader)
check("compare() déterministe (2 appels → même gagnant)", r1["winner"] == r2["winner"])
# l'ordre des arguments ne change pas le verdict
r3 = compare(reg.get("greet_ko"), reg.get("greet_ok"), test_cases, loader)
check("verdict indépendant de l'ordre des arguments", r3["winner"] == "greet_ok")

print()
print("=== TEST 4 — Un skill non chargeable est jugé pire que tout ===")
bad = reg.get("greet_ko")
orig = bad.hash
bad.hash = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
res_bad = compare(reg.get("greet_ok"), bad, test_cases, loader)
check("skill non chargeable (hash KO) perd le verdict", res_bad["winner"] == "greet_ok")
check("skill non chargeable → loadable False", res_bad["skill_b"]["loadable"] is False)
bad.hash = orig

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
