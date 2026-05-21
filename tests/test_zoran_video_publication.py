"""tests/test_zoran_video_publication.py — Tests zoran_video_publication_planner.

Mission : ZORAN_JOBS_20260521 · skill méta — média / orchestration.
Signé : Claude Code, 2026-05-22.

Planificateur de publication vidéo : montage, hook, hashtags, charte, teasers,
calendrier. Chargement via le runtime réel (Registry + Loader, hash + V2).

Exécutable : python tests/test_zoran_video_publication.py
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
_manifest = _reg.get("zoran_video_publication_planner")
assert _manifest is not None, "zoran_video_publication_planner absent du registry"
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


VIDEOS = [
    {"id": "intro", "duree_s": 120, "moments": [
        {"debut_s": 0,   "fin_s": 12,  "intensite": 0.9,  "description": "ouverture punchy"},
        {"debut_s": 30,  "fin_s": 50,  "intensite": 0.6,  "description": "demo produit"},
        {"debut_s": 80,  "fin_s": 95,  "intensite": 0.75, "description": "temoignage"},
        {"debut_s": 100, "fin_s": 118, "intensite": 0.4,  "description": "conclusion"},
    ]},
    {"id": "bonus", "duree_s": 60, "moments": [
        {"debut_s": 5,  "fin_s": 18, "intensite": 0.85, "description": "reaction"},
        {"debut_s": 40, "fin_s": 55, "intensite": 0.5,  "description": "technique"},
    ]},
]
BASE = {"videos": VIDEOS, "sujet": "renovation energetique maison",
        "cible": "proprietaires", "reseaux": ["tiktok", "youtube"],
        "charte_graphique": {"couleur_primaire": "#1B5E20", "police": "Inter",
                             "ton": "expert rassurant"}}

print("=" * 60)
print("TESTS zoran_video_publication_planner")
print("=" * 60)

# --- Structure : un plan par réseau, formats adaptés -----------------------
r = run(BASE)
check("plans : un plan par réseau (2)", len(r["plans_par_reseau"]) == 2)
plans = {p["reseau"]: p for p in r["plans_par_reseau"]}
check("format : tiktok en 9:16, youtube en 16:9",
      plans["tiktok"]["format"]["ratio"] == "9:16"
      and plans["youtube"]["format"]["ratio"] == "16:9")

# --- Montage : sélection par intensité, ouverture = moment le plus fort ----
tk = plans["tiktok"]
check("montage tiktok : 3 segments pour ~34s idéal (40s de matériel pris)",
      len(tk["montage"]) == 3 and tk["duree_montage_s"] == 40.0)
check("montage : segment d'ouverture = moment le plus intense (intro@0)",
      tk["montage"][0]["video_id"] == "intro"
      and tk["montage"][0]["debut_s"] == 0
      and tk["montage"][0]["intensite"] == 0.9)
yt = plans["youtube"]
check("montage youtube : long format → les 6 moments retenus (93s)",
      len(yt["montage"]) == 6 and yt["duree_montage_s"] == 93.0)
check("avertissement : youtube sous la durée idéale signalé",
      any("youtube" in a for a in r["avertissements"]))

# --- Hook + description ----------------------------------------------------
check("hook : présent et non vide sur chaque plan",
      all(p["hook"].strip() for p in r["plans_par_reseau"]))
check("description : mentionne le sujet",
      "renovation energetique maison" in tk["description"])

# --- Hashtags : dérivés du sujet et de la cible ----------------------------
check("hashtags : dérivés du sujet (#renovation, #maison présents)",
      "#renovation" in tk["hashtags"] and "#maison" in tk["hashtags"])
check("hashtags : plafonnés au maximum du réseau",
      len(tk["hashtags"]) <= 5)

# --- Sous-titres + charte appliquée ----------------------------------------
check("sous-titres : actifs, style issu de la charte",
      tk["sous_titres"]["actives"] is True
      and tk["sous_titres"]["style"]["police"] == "Inter")
check("charte : couleur primaire appliquée",
      tk["charte_appliquee"]["couleur_primaire"] == "#1B5E20")

# --- Plan de promotion : teasers -------------------------------------------
teasers = r["plan_promotion"]["teasers"]
check("teasers : 3 teasers par défaut", len(teasers) == 3)
check("teaser : le plus intense en premier (intro@0, 12s)",
      teasers[0]["id"] == "teaser_1"
      and teasers[0]["source_video"] == "intro"
      and teasers[0]["duree_s"] == 12.0)
check("teaser : ne cible que les formats courts (tiktok, pas youtube)",
      teasers[0]["reseaux_cibles"] == ["tiktok"])

# --- Teaser : durée plafonnée à 15s ----------------------------------------
r2 = run({**BASE, "videos": [{"id": "long", "duree_s": 100, "moments": [
    {"debut_s": 10, "fin_s": 60, "intensite": 0.95,
     "description": "longue sequence"}]}], "nb_teasers": 1})
check("teaser : extrait long plafonné à 15s",
      r2["plan_promotion"]["teasers"][0]["duree_s"] == 15.0
      and r2["plan_promotion"]["teasers"][0]["fin_s"] == 25.0)

# --- Calendrier : lancement → teasers AVANT le master ----------------------
cal = r["calendrier"]
check("calendrier : master au jour 0 sur chaque réseau",
      sum(1 for e in cal if e["type"] == "master" and e["jour_relatif"] == 0)
      == 2)
check("calendrier lancement : teasers en compte à rebours (jours < 0)",
      all(e["jour_relatif"] < 0 for e in cal if e["type"] == "teaser")
      and any(e["type"] == "teaser" for e in cal))

# --- Calendrier : relance → teasers APRÈS le master ------------------------
r3 = run({**BASE, "objectif": "relance"})
check("calendrier relance : teasers planifiés après le master (jours > 0)",
      all(e["jour_relatif"] > 0 for e in r3["calendrier"]
          if e["type"] == "teaser"))

# --- Charte absente → signalée, jamais inventée ----------------------------
r4 = run({"videos": VIDEOS, "sujet": "sujet test", "cible": "cible test",
          "reseaux": ["tiktok"]})
check("charte absente : avertissement émis",
      any("harte" in a for a in r4["avertissements"]))
check("charte absente : aucune couleur inventée",
      r4["charte_appliquee"]["couleur_primaire"] is None)

# --- Cas négatifs -----------------------------------------------------------
check("négatif : videos vide → ValueError",
      raises_value_error({**BASE, "videos": []}))
check("négatif : durée de vidéo nulle → ValueError",
      raises_value_error({**BASE, "videos": [
          {"id": "v", "duree_s": 0, "moments": VIDEOS[0]["moments"]}]}))
check("négatif : moment fin <= debut → ValueError",
      raises_value_error({**BASE, "videos": [{"id": "v", "duree_s": 50,
          "moments": [{"debut_s": 20, "fin_s": 10, "intensite": 0.5,
                       "description": "x"}]}]}))
check("négatif : moment fin > durée vidéo → ValueError",
      raises_value_error({**BASE, "videos": [{"id": "v", "duree_s": 50,
          "moments": [{"debut_s": 10, "fin_s": 80, "intensite": 0.5,
                       "description": "x"}]}]}))
check("négatif : intensité hors [0,1] → ValueError",
      raises_value_error({**BASE, "videos": [{"id": "v", "duree_s": 50,
          "moments": [{"debut_s": 10, "fin_s": 20, "intensite": 1.5,
                       "description": "x"}]}]}))
check("négatif : vidéo sans moments → ValueError",
      raises_value_error({**BASE, "videos": [
          {"id": "v", "duree_s": 50, "moments": []}]}))
check("négatif : sujet vide → ValueError",
      raises_value_error({**BASE, "sujet": ""}))
check("négatif : cible vide → ValueError",
      raises_value_error({**BASE, "cible": "   "}))
check("négatif : liste de réseaux vide → ValueError",
      raises_value_error({**BASE, "reseaux": []}))
check("négatif : réseau inconnu → ValueError",
      raises_value_error({**BASE, "reseaux": ["myspace"]}))
check("négatif : objectif invalide → ValueError",
      raises_value_error({**BASE, "objectif": "buzz"}))
check("négatif : nb_teasers négatif → ValueError",
      raises_value_error({**BASE, "nb_teasers": -1}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
