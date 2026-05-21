"""tests/test_zoran_oracle_adaptation.py — Tests du skill zoran_oracle_adaptation_agents.

Mission : ZORAN_JOBS_20260521 · skill méta — orchestration.
Signé : Claude Code, 2026-05-22.

Oracle déterministe : dimensionne les agents (locaux / API) et décide du réveil
ou de l'arrêt. Chargement via le runtime réel (Registry + Loader, hash + V2).

Exécutable : python tests/test_zoran_oracle_adaptation.py
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
_manifest = _reg.get("zoran_oracle_adaptation_agents")
assert _manifest is not None, "zoran_oracle_adaptation_agents absent du registry"
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
print("TESTS zoran_oracle_adaptation_agents")
print("=" * 60)

# --- TERMINE : toutes les étapes faites -------------------------------------
r = run({
    "etapes": [{"id": "e1", "statut": "fait", "charge": 2},
               {"id": "e2", "statut": "fait", "charge": 3}],
    "agents_disponibles": {"api": 2, "local": 2}, "budget_restant": 100,
})
check("TERMINE : verdict + reveil stop",
      r["verdict"] == "TERMINE" and r["reveil"] == "stop")
check("TERMINE : progression 100% et 0 étape restante",
      r["progression_pct"] == 100.0 and r["etapes_restantes"] == 0)
check("TERMINE : 0 cycle restant estimé", r["cycles_restants_estimes"] == 0)

# --- CONTINUER : agents locaux d'abord, puis API ----------------------------
r = run({
    "etapes": [{"id": f"e{i}", "statut": "a_faire", "charge": 1}
               for i in range(4)],
    "agents_disponibles": {"api": 5, "local": 2}, "budget_restant": 100,
    "cout_api_par_agent": 1.0,
})
check("CONTINUER : verdict + reveil continuer",
      r["verdict"] == "CONTINUER" and r["reveil"] == "continuer")
check("CONTINUER : locaux d'abord (2 local, 2 API pour 4 étapes)",
      r["agents_a_mobiliser"] == {"api": 2, "local": 2})
check("CONTINUER : coût du cycle = 2 API × 1.0", r["cout_estime_cycle"] == 2.0)
check("CONTINUER : budget après cycle = 98.0", r["budget_apres_cycle"] == 98.0)
check("CONTINUER : 4 prochaines étapes désignées",
      r["prochaines_etapes"] == ["e0", "e1", "e2", "e3"])
check("CONTINUER : 1 cycle restant estimé (charge 4 / débit 4)",
      r["cycles_restants_estimes"] == 1)

# --- API plafonnée par le budget --------------------------------------------
r = run({
    "etapes": [{"id": f"e{i}", "statut": "a_faire", "charge": 1}
               for i in range(4)],
    "agents_disponibles": {"api": 5, "local": 0}, "budget_restant": 3,
    "cout_api_par_agent": 1.0,
})
check("budget : API plafonnée à 3 agents finançables (budget 3)",
      r["agents_a_mobiliser"] == {"api": 3, "local": 0})
check("budget : budget après cycle = 0.0", r["budget_apres_cycle"] == 0.0)

# --- STOP_INCOHERENCE : prioritaire sur le budget ---------------------------
r = run({
    "etapes": [{"id": "e1", "statut": "a_faire", "charge": 1}],
    "agents_disponibles": {"api": 5, "local": 5}, "budget_restant": 100,
    "coherence_courante": 0.2, "seuil_coherence": 0.3,
})
check("STOP_INCOHERENCE : cohérence sous le seuil → arrêt",
      r["verdict"] == "STOP_INCOHERENCE" and r["reveil"] == "stop")
check("STOP_INCOHERENCE : aucun agent mobilisé",
      r["agents_a_mobiliser"] == {"api": 0, "local": 0})

# --- STOP_BUDGET : enveloppe épuisée ----------------------------------------
r = run({
    "etapes": [{"id": "e1", "statut": "a_faire", "charge": 1}],
    "agents_disponibles": {"api": 5, "local": 5}, "budget_restant": 0,
    "coherence_courante": 1.0,
})
check("STOP_BUDGET : budget à 0 → arrêt",
      r["verdict"] == "STOP_BUDGET" and r["reveil"] == "stop")

# --- STOP_RESSOURCE : travail restant mais 0 agent mobilisable --------------
r = run({
    "etapes": [{"id": "e1", "statut": "a_faire", "charge": 1}],
    "agents_disponibles": {"api": 0, "local": 0}, "budget_restant": 100,
})
check("STOP_RESSOURCE : aucun agent disponible → arrêt",
      r["verdict"] == "STOP_RESSOURCE" and r["reveil"] == "stop")

r = run({
    "etapes": [{"id": "e1", "statut": "a_faire", "charge": 1}],
    "agents_disponibles": {"api": 3, "local": 0}, "budget_restant": 5,
    "cout_api_par_agent": 100.0,
})
check("STOP_RESSOURCE : API non finançable (coût > budget) → arrêt",
      r["verdict"] == "STOP_RESSOURCE")

# --- Progression pondérée par la charge -------------------------------------
r = run({
    "etapes": [{"id": "e1", "statut": "fait", "charge": 3},
               {"id": "e2", "statut": "a_faire", "charge": 1}],
    "agents_disponibles": {"api": 1, "local": 0}, "budget_restant": 10,
})
check("progression : pondérée par la charge (3/4 = 75%)",
      r["progression_pct"] == 75.0)

# --- en_cours sans a_faire : CONTINUER sans mobiliser d'agent neuf ----------
r = run({
    "etapes": [{"id": "e1", "statut": "fait", "charge": 1},
               {"id": "e2", "statut": "en_cours", "charge": 1}],
    "agents_disponibles": {"api": 2, "local": 2}, "budget_restant": 10,
})
check("en_cours : CONTINUER (étape en cours, rien de neuf à lancer)",
      r["verdict"] == "CONTINUER" and r["agents_a_mobiliser"]["api"] == 0
      and r["agents_a_mobiliser"]["local"] == 0)
check("en_cours : 1 étape restante (l'étape en cours)",
      r["etapes_restantes"] == 1)

# --- Journal cumulatif ------------------------------------------------------
etapes_j = [{"id": "e1", "statut": "a_faire", "charge": 1}]
r1 = run({"etapes": etapes_j, "agents_disponibles": {"api": 1, "local": 0},
          "budget_restant": 50, "cycle": 1})
r2 = run({"etapes": etapes_j, "agents_disponibles": {"api": 1, "local": 0},
          "budget_restant": 49, "cycle": 2, "journal": r1["journal"]})
check("journal : cumulatif (séquence 2 au cycle 2)",
      len(r2["journal"]) == 2 and r2["journal"][1]["sequence"] == 2
      and r2["journal"][1]["cycle"] == 2)

# --- Cas négatifs -----------------------------------------------------------
check("négatif : liste d'étapes vide → ValueError",
      raises_value_error({"etapes": [], "agents_disponibles": {"api": 1}}))
check("négatif : statut d'étape invalide → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "peut-etre"}],
                          "agents_disponibles": {"api": 1}}))
check("négatif : charge nulle ou négative → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "a_faire",
                                      "charge": 0}],
                          "agents_disponibles": {"api": 1}}))
check("négatif : cohérence hors [0,1] → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "a_faire"}],
                          "agents_disponibles": {"api": 1},
                          "coherence_courante": 1.5}))
check("négatif : budget négatif → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "a_faire"}],
                          "agents_disponibles": {"api": 1},
                          "budget_restant": -10}))
check("négatif : cycle < 1 → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "a_faire"}],
                          "agents_disponibles": {"api": 1}, "cycle": 0}))
check("négatif : nombre d'agents négatif → ValueError",
      raises_value_error({"etapes": [{"id": "e1", "statut": "a_faire"}],
                          "agents_disponibles": {"api": -1}}))

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
