"""
tests/test_zoran_ai_environment.py — Tests du skill zoran_ai_environment_orchestrator.

Mission : ZORAN_JOBS_20260521 · skill méta — accès à l'intelligence.
Signé : Claude Code, 2026-05-22.

V1 SAFE : audit machine + recommandation IA, aucune installation.
Chargement via le runtime réel (Registry + Loader, hash + validation V2).

Exécutable : python tests/test_zoran_ai_environment.py
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
_manifest = _reg.get("zoran_ai_environment_orchestrator")
assert _manifest is not None, "zoran_ai_environment_orchestrator absent du registry"
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
print("TESTS zoran_ai_environment_orchestrator")
print("=" * 60)

# --- Gros PC : RAM 32, GPU 12, stockage 200 --------------------------------
# mémoire utile = max(12, 32-4=28) = 28 Go → IA très grande (22) OK, massive (45) refusée
r = run({"type_appareil": "ordinateur", "ram_go": 32, "vram_go": 12,
         "stockage_libre_go": 200})
check("gros PC : capacité 'IA très grande'", "très grande" in r["capacite"])
check("gros PC : IA massive refusée (mémoire)",
      any("massive" in x["modele"] for x in r["modeles_refuses"]))
check("gros PC : moteur local recommandé", r["moteur_local"] is not None)

# --- Téléphone correct : RAM 8, stockage 64 --------------------------------
# mémoire utile = 8-3 = 5 Go ; plafond téléphone = IA légère
r = run({"type_appareil": "telephone", "ram_go": 8, "stockage_libre_go": 64,
         "batterie_pct": 70})
check("téléphone : plafonné à 'IA légère'", "légère" in r["capacite"])
check("téléphone : IA moyenne refusée (trop lourd pour téléphone)",
      any("téléphone" in x["raison"] for x in r["modeles_refuses"]))

# --- Téléphone batterie faible ---------------------------------------------
r = run({"type_appareil": "telephone", "ram_go": 8, "stockage_libre_go": 64,
         "batterie_pct": 10})
check("téléphone batterie 10% : conseil de privilégier l'IA en ligne",
      any("batterie" in c.lower() for c in r["conseils"]))

# --- Machine trop juste, hors ligne ----------------------------------------
r = run({"type_appareil": "ordinateur", "ram_go": 4, "vram_go": 0,
         "stockage_libre_go": 10, "reseau": "offline"})
check("PC faible + offline : aucune IA recommandée",
      r["modeles_recommandes"] == [] and r["moteur_local"] is None)
check("PC faible + offline : pas de repli en ligne", r["repli_en_ligne"] is None)
check("PC faible : capacité 'insuffisante'", "insuffisante" in r["capacite"])

# --- Cas négatifs -----------------------------------------------------------
check("négatif : type d'appareil inconnu → ValueError",
      raises_value_error({"type_appareil": "tablette", "ram_go": 8,
                          "stockage_libre_go": 64}))
check("négatif : RAM nulle → ValueError",
      raises_value_error({"type_appareil": "ordinateur", "ram_go": 0,
                          "stockage_libre_go": 64}))
check("négatif : réseau invalide → ValueError",
      raises_value_error({"type_appareil": "ordinateur", "ram_go": 8,
                          "stockage_libre_go": 64, "reseau": "wifi"}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
