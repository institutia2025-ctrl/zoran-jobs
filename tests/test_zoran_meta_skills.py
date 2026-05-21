"""
tests/test_zoran_meta_skills.py — Tests des 2 skills méta de gouvernance ZORAN.

Mission : ZORAN_JOBS_20260521 · skills méta.
Signé : Claude Code, 2026-05-21.

- zoran_gate_progression_coherente : barrière de progression / discipline ticket.
- zoran_selecteur_lois_cadres : sélection des lois (Codex Zoran) + des cadres.

Chargement via le runtime réel (Registry + Loader, hash + validation V2).
Exécutable : python tests/test_zoran_meta_skills.py
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


_reg = Registry()
_reg.load_from_dir(ROOT / "skills_examples")
_loader = Loader()


def run_of(skill_id: str):
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


print("=" * 60)
print("TESTS SKILLS MÉTA ZORAN")
print("=" * 60)

# --- zoran_gate_progression_coherente ---------------------------------------
print("\n[zoran_gate_progression_coherente]")
run = run_of("zoran_gate_progression_coherente")

ok_cl = [{"item": "back", "statut": "ok"}, {"item": "front", "statut": "ok"},
         {"item": "tests_massifs", "statut": "ok"}]
r = run({"ticket": "T-001", "checklist": ok_cl,
         "validations_obligatoires": ["back", "front", "tests_massifs"]})
check("gate : checklist 100% ok → peut_avancer", r["peut_avancer"] is True)
check("gate : journal contient 1 entrée AVANCE",
      len(r["journal"]) == 1 and r["journal"][0]["verdict"] == "AVANCE")

r = run({"ticket": "T-002",
         "checklist": [{"item": "back", "statut": "ok"},
                       {"item": "front", "statut": "pending"}],
         "validations_obligatoires": ["back", "front"]})
check("gate : un item pending → bloqué", r["peut_avancer"] is False)
check("gate : item bloquant 'front' signalé",
      any("front" in b for b in r["items_bloquants"]))

r = run({"ticket": "T-003", "checklist": [{"item": "back", "statut": "ok"}],
         "validations_obligatoires": ["back", "front", "tests_massifs"]})
check("gate : validations obligatoires absentes → bloqué", r["peut_avancer"] is False)
check("gate : 2 validations obligatoires manquantes détectées",
      sum(1 for b in r["items_bloquants"] if "absente" in b) == 2)

journal = run({"ticket": "T-001", "checklist": ok_cl})["journal"]
r = run({"ticket": "T-002", "checklist": ok_cl, "journal": journal})
check("gate : journal cumulatif (séquence 2)",
      len(r["journal"]) == 2 and r["journal"][1]["sequence"] == 2)

check("gate : checklist vide → ValueError",
      raises_value_error(run, {"ticket": "T", "checklist": []}))
check("gate : statut invalide → ValueError",
      raises_value_error(run, {"ticket": "T",
                               "checklist": [{"item": "x", "statut": "peut-etre"}]}))
check("gate : ticket vide → ValueError",
      raises_value_error(run, {"ticket": "", "checklist": ok_cl}))

# --- zoran_selecteur_lois_cadres --------------------------------------------
print("\n[zoran_selecteur_lois_cadres]")
run = run_of("zoran_selecteur_lois_cadres")

r = run({"domaine": "structure"})
check("selecteur : domaine structure → cadre dominant 'structure'",
      r["cadre_dominant"] == "structure")
check("selecteur : lois universelles = Genèse Éthique (0) + ΨΛ-Cohérence (3)",
      [law["numero"] for law in r["lois_universelles"]] == [0, 3])
check("selecteur : structure inclut la Loi 5 (Schwarzschild-Cohérence)",
      any(law["numero"] == 5 for law in r["lois_pertinentes"]))

r = run({"domaine": "securite", "enjeu": "securite_personnes"})
check("selecteur : enjeu sécurité des personnes → cadre dominant 'securite'",
      r["cadre_dominant"] == "securite")

r = run({"domaine": "transmission"})
check("selecteur : transmission inclut la Loi -1 (Ce qui n'existe pas existe)",
      any(law["numero"] == -1 for law in r["lois_pertinentes"]))

check("selecteur : domaine inconnu → ValueError",
      raises_value_error(run, {"domaine": "patisserie"}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
