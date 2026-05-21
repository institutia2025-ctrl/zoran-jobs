"""
tests/test_registry.py — Test du Registry + Manifest parser.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Signé : Claude, prestataire, 2026-05-21

Test self-contained : exécutable directement (`python tests/test_registry.py`).
Falsifiable : chaque assertion vérifie un comportement concret du contrat.
Ne valide PAS « tout va bien » — il vérifie que le valide passe ET que
l'invalide est refusé.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Racine du projet dans le path (le test vit dans tests/, registry/ à la racine)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# FIX-DEF-1 2026-05-21 : sortie console en UTF-8 — portabilité multi-OS.
# Sans ça, crash UnicodeEncodeError sur terminal Windows cp1252 (caractères
# non-ASCII dans les print). Un runtime transmissible ne doit pas dépendre
# de l'encodage du terminal de l'hôte.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from registry import Registry, validate_manifest  # noqa: E402

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


print("=== TEST 1 — Registry charge le skill echo valide ===")
reg = Registry()
report = reg.load_from_dir(ROOT / "skills_examples")
check("echo est indexe", "echo" in reg.list_skills())
check("rapport : 1 skill charge", report["n_loaded"] >= 1)
echo = reg.get("echo")
check("manifest echo recupere", echo is not None)
if echo:
    check("echo.domain == demo", echo.domain == "demo")
    check("echo.lifecycle == candidate", echo.lifecycle_state == "candidate")
    check("echo a des triggers", len(echo.triggers) > 0)
    check("echo.sandbox_level valide", echo.sandbox_level == "none")

print()
print("=== TEST 2 — by_domain ===")
demo_skills = reg.by_domain("demo")
check("by_domain('demo') contient echo", any(m.skill_id == "echo" for m in demo_skills))
check("by_domain('inexistant') vide", reg.by_domain("inexistant") == [])

print()
print("=== TEST 3 — un manifest INVALIDE est refuse (falsification) ===")
bad = {
    "identity": {"skill_id": "Bad ID!", "name": "x"},  # id interdit, champs manquants
    "routing": {},                                      # domain + triggers manquants
    "coherence": {"expected_delta_phi": 5.0},           # hors [0..1]
    "cost": {"runtime_cost": 99, "latency_class": "turbo"},  # hors bornes / enum
    "sandbox_level": "yolo",                            # hors enum
    "rollback": {"rollback_strategy": "magic"},         # hors enum
    "lifecycle_state": "quarantine",                    # hors MVP
}
errors = validate_manifest(bad)
check("le manifest invalide produit des erreurs", len(errors) > 0)
check("skill_id interdit detecte", any("skill_id" in e for e in errors))
check("delta_phi hors borne detecte", any("delta_phi" in e for e in errors))
check("lifecycle hors MVP detecte", any("lifecycle_state" in e for e in errors))
check("sandbox_level invalide detecte", any("sandbox_level" in e for e in errors))

print()
print("=== TEST 4 — un manifest valide ne produit AUCUNE erreur ===")
import json  # noqa: E402
good = json.loads((ROOT / "skills_examples" / "echo" / "manifest.json").read_text(encoding="utf-8"))
check("manifest echo : 0 erreur", validate_manifest(good) == [])

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
