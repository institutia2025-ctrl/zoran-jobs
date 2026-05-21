"""
tests/test_zoran_photo_clone.py — Tests du skill zoran_photo_clone_leger.

Mission : ZORAN_JOBS_20260521 · skill méta — sauvegarde.
Signé : Claude Code, 2026-05-21.

Photo hyper-légère (empreintes seules) + restauration ciblée par diff.
Chargement via le runtime réel (Registry + Loader, hash + validation V2).

Exécutable : python tests/test_zoran_photo_clone.py
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
_manifest = _reg.get("zoran_photo_clone_leger")
assert _manifest is not None, "zoran_photo_clone_leger absent du registry"
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
print("TESTS zoran_photo_clone_leger")
print("=" * 60)

# --- Photo : hyper-légèreté -------------------------------------------------
v1 = [
    {"chemin": "f1.py", "hash": "sha256:aaa", "taille_octets": 100},
    {"chemin": "f2.py", "hash": "sha256:bbb", "taille_octets": 100},
    {"chemin": "f3.py", "hash": "sha256:ccc", "taille_octets": 100},
    {"chemin": "f4.py", "hash": "sha256:ddd", "taille_octets": 100},
    {"chemin": "f5.py", "hash": "sha256:eee", "taille_octets": 100},
]
r = run({"fichiers": v1})
photo_ref = r["photo"]
check("photo : 5 fichiers, 500 octets de source",
      photo_ref["nb_fichiers"] == 5 and photo_ref["taille_source_octets"] == 500)
check("photo : empreinte globale sha256", photo_ref["empreinte_globale"].startswith("sha256:"))
check("photo : hyper-légère (poids photo < taille source)",
      photo_ref["poids_photo_octets"] < photo_ref["taille_source_octets"])
check("photo : sans référence → identique_a_reference None", r["identique_a_reference"] is None)

# --- Restauration ciblée : 1 fichier modifié sur 5 --------------------------
v2 = list(v1)
v2[4] = {"chemin": "f5.py", "hash": "sha256:CHANGED", "taille_octets": 100}
r = run({"fichiers": v2, "photo_reference": photo_ref})
check("restauration : 1 seul fichier à restaurer (f5 modifié)",
      r["nb_a_restaurer"] == 1 and r["restauration_ciblee"][0]["chemin"] == "f5.py")
check("restauration : gain de ciblage = 80% (100/500 octets seulement)",
      abs(r["gain_ciblage_pct"] - 80.0) < 0.1)
check("restauration : état non identique à la référence",
      r["identique_a_reference"] is False)

# --- État identique ---------------------------------------------------------
r = run({"fichiers": v1, "photo_reference": photo_ref})
check("restauration : état identique → rien à restaurer",
      r["identique_a_reference"] is True and r["nb_a_restaurer"] == 0)

# --- Fichier manquant -------------------------------------------------------
r = run({"fichiers": v1[:4], "photo_reference": photo_ref})
check("restauration : fichier manquant détecté",
      any(x["raison"] == "fichier manquant" for x in r["restauration_ciblee"]))

# --- Fichier ajouté ---------------------------------------------------------
v_plus = v1 + [{"chemin": "f6.py", "hash": "sha256:fff", "taille_octets": 100}]
r = run({"fichiers": v_plus, "photo_reference": photo_ref})
check("restauration : fichier ajouté signalé",
      any("ajouté" in x["raison"] for x in r["restauration_ciblee"]))

# --- Cas négatifs -----------------------------------------------------------
check("négatif : liste de fichiers vide → ValueError", raises_value_error({"fichiers": []}))
check("négatif : fichier sans empreinte → ValueError",
      raises_value_error({"fichiers": [{"chemin": "x.py", "taille_octets": 10}]}))
check("négatif : photo_reference invalide → ValueError",
      raises_value_error({"fichiers": v1, "photo_reference": {"pas_entries": 1}}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
