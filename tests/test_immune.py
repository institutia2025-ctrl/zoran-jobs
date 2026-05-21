"""
tests/test_immune.py — Test du système immunitaire runtime (Phase 3).

Mission : ZORAN_JOBS_20260521 · Phase 3
Signé : Claude, prestataire, 2026-05-21

Prouve les 4 propriétés exigées par ZORAN :
  1. QUARANTAINE — 3 violations io → désactivation automatique
  2. PROMOTION   — candidate propre (N évals, 0 violation, stable, latence OK) → active
  3. ROLLBACK    — la dernière transition est annulable immédiatement
  4. JOURNAL     — chaque transition est tracée, signée, intègre

Test self-contained, journal jetable (fichier temporaire).
Exécutable : `python tests/test_immune.py`.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# FIX-DEF-1 2026-05-21 : sortie console UTF-8 — portabilité multi-OS.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from quarantine import ImmuneSystem, Journal  # noqa: E402

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


# Métriques Oracle factices (déterministes, prédictibles à la main)
CLEAN = {"io_conformity_rate": 1.0, "latency_avg_ms": 5.0, "stable": True}
VIOLATION = {"io_conformity_rate": 0.0, "latency_avg_ms": 5.0, "stable": True}


def _fresh_immune():
    """Un ImmuneSystem neuf avec un journal jetable."""
    tmp = Path(tempfile.mkdtemp()) / "journal.jsonl"
    return ImmuneSystem(Journal(tmp)), tmp


print("=== TEST 1 — QUARANTAINE : 3 violations io → désactivation ===")
imm, _ = _fresh_immune()
t1 = imm.record("bad_skill", VIOLATION)
check("1 violation → pas encore de transition", t1 is None)
t2 = imm.record("bad_skill", VIOLATION)
check("2 violations → pas encore de transition", t2 is None)
t3 = imm.record("bad_skill", VIOLATION)
check("3 violations → transition déclenchée", t3 is not None)
check("transition vers 'quarantine'", t3 and t3["to"] == "quarantine")
check("lifecycle effectif == quarantine", imm.lifecycle("bad_skill") == "quarantine")

print()
print("=== TEST 2 — PROMOTION : candidate propre → active ===")
imm2, _ = _fresh_immune()
imm2.record("good_skill", CLEAN)
imm2.record("good_skill", CLEAN)
check("2 évals propres → pas encore promu", imm2.lifecycle("good_skill") == "candidate")
t = imm2.record("good_skill", CLEAN)  # 3e éval propre
check("3 évals propres → transition", t is not None)
check("promotion vers 'active'", t and t["to"] == "active")
check("lifecycle effectif == active", imm2.lifecycle("good_skill") == "active")

print()
print("=== TEST 3 — DÉMOTION : un skill actif qui viole redescend ===")
t_dem = imm2.record("good_skill", VIOLATION)
check("skill actif + violation → démotion", t_dem and t_dem["to"] == "candidate")
check("lifecycle effectif == candidate", imm2.lifecycle("good_skill") == "candidate")

print()
print("=== TEST 4 — ROLLBACK : la dernière transition est annulable ===")
before = imm.lifecycle("bad_skill")  # quarantine
rb = imm.rollback_last()
check("rollback retourne un résultat", rb is not None)
check("lifecycle restauré (quarantine → candidate)",
      imm.lifecycle("bad_skill") == "candidate" and before == "quarantine")

print()
print("=== TEST 5 — JOURNAL : tracé, signé, intègre ===")
imm3, jpath = _fresh_immune()
imm3.record("x", CLEAN)
imm3.record("x", CLEAN)
imm3.record("x", CLEAN)  # promotion → 1 événement transition
events = imm3.journal.read()
check("journal non vide", len(events) >= 1)
check("événement horodaté", all("timestamp" in e for e in events))
check("événement signé", all(e.get("signature", "").startswith("sha256:") for e in events))
ok, bad_id = imm3.journal.verify_integrity()
check("intégrité du journal vérifiée", ok)
# falsification : on corrompt le fichier → l'intégrité doit échouer
raw = jpath.read_text(encoding="utf-8")
jpath.write_text(raw.replace('"active"', '"HACKED"', 1), encoding="utf-8")
ok2, _ = imm3.journal.verify_integrity()
check("altération du journal détectée (signature invalide)", ok2 is False)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
