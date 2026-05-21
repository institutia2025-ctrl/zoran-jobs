"""
tests/test_zoran_magasin_contenu.py — Tests du skill zoran_magasin_contenu_adressable.

Mission : ZORAN_JOBS_20260521 · skill méta — sauvegarde.
Signé : Claude Code, 2026-05-21.

Le « coffre » : magasin adressé par contenu (indexation + déduplication +
restauration vérifiée). Chargement via le runtime réel (Registry + Loader).

Exécutable : python tests/test_zoran_magasin_contenu.py
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
_manifest = _reg.get("zoran_magasin_contenu_adressable")
assert _manifest is not None, "zoran_magasin_contenu_adressable absent du registry"
_module, _err = _loader.load(_manifest)
assert _module is not None, f"chargement échoué : {_err}"
run = _module.run


def raises_value_error(payload) -> bool:
    try:
        run(payload)
        return False
    except ValueError:
        return True
    except Exception:
        return False


print("=" * 60)
print("TESTS zoran_magasin_contenu_adressable")
print("=" * 60)

# --- Mode indexer : déduplication -------------------------------------------
idx = run({"mode": "indexer", "fichiers": [
    {"chemin": "a.py", "contenu": "CONTENU_X"},
    {"chemin": "b.py", "contenu": "CONTENU_X"},
    {"chemin": "c.py", "contenu": "CONTENU_Y"},
]})
check("indexer : 3 fichiers indexés", idx["nb_fichiers"] == 3)
check("indexer : 2 blobs uniques (CONTENU_X dédupliqué)", idx["nb_blobs_uniques"] == 2)
check("indexer : ratio de déduplication = 0.333",
      abs(idx["ratio_deduplication"] - 0.333) < 0.01)
check("indexer : photo produite avec 3 entrées",
      idx["photo"]["nb_fichiers"] == 3 and len(idx["photo"]["entries"]) == 3)

# --- Mode restaurer : round-trip --------------------------------------------
store = idx["store"]
entries = idx["photo"]["entries"]
r = run({"mode": "restaurer", "store": store, "a_restaurer": [
    {"chemin": "a.py", "hash": entries["a.py"]["hash"]},
    {"chemin": "c.py", "hash": entries["c.py"]["hash"]},
]})
check("restaurer : 2 fichiers restitués", r["nb_restaures"] == 2)
check("restaurer : contenu de a.py correctement résolu",
      r["restaures"]["a.py"] == "CONTENU_X")
check("restaurer : intégrité OK", r["integrite_ok"] is True)

# --- Restaurer : contenu manquant -------------------------------------------
r = run({"mode": "restaurer", "store": store, "a_restaurer": [
    {"chemin": "z.py", "hash": "sha256:emprdunte_absente_du_magasin"},
]})
check("restaurer : empreinte absente → signalée dans manquants",
      r["nb_restaures"] == 0 and len(r["manquants"]) == 1 and r["integrite_ok"] is False)

# --- Restaurer : contenu corrompu -------------------------------------------
faux = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
r = run({"mode": "restaurer", "store": {faux: "CONTENU_X"}, "a_restaurer": [
    {"chemin": "a.py", "hash": faux},
]})
check("restaurer : contenu ne correspondant pas à son empreinte → corrompu",
      len(r["corrompus"]) == 1 and r["integrite_ok"] is False)

# --- Cas négatifs -----------------------------------------------------------
check("négatif : mode inconnu → ValueError",
      raises_value_error({"mode": "archiver", "fichiers": []}))
check("négatif : indexer sans fichiers → ValueError",
      raises_value_error({"mode": "indexer", "fichiers": []}))
check("négatif : restaurer sans store → ValueError",
      raises_value_error({"mode": "restaurer", "a_restaurer": [{"chemin": "a", "hash": "h"}]}))
check("négatif : contenu non textuel → ValueError",
      raises_value_error({"mode": "indexer", "fichiers": [{"chemin": "a", "contenu": 123}]}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
