"""minimal_agent_harness — boucle d'agents pilotée par l'oracle ZORAN.

Mission ZORAN_ORACLE_AGENTIC_BRIDGE_20260522 · livrable 5/7.
Le HARNAIS exécute les étapes ; l'ORACLE (fonction pure, locale) décide à
chaque cycle s'il faut continuer ou s'arrêter. Lancer depuis la racine :
    python examples/minimal_agent_harness.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loader.loader import Loader  # noqa: E402
from registry.registry import Registry  # noqa: E402

_reg = Registry()
_reg.load_from_dir(Path(__file__).resolve().parent.parent / "skills_examples")
_oracle, _err = Loader().load(_reg.get("zoran_oracle_adaptation_agents"))
assert _oracle is not None, f"oracle non chargé : {_err}"


def executer(etape: dict) -> None:
    """Le harnais exécute : l'étape passe à l'état 'fait' (agent simulé)."""
    etape["statut"] = "fait"


def main() -> None:
    """Boucle réelle : moteur exécute, oracle décide, jamais d'état zombie."""
    etapes = [{"id": f"e{i}", "statut": "a_faire", "charge": 1.0} for i in range(6)]
    budget, journal, cycle = 20.0, [], 1
    while True:
        decision = _oracle.run({                       # le CERVEAU décide
            "etapes": etapes, "agents_disponibles": {"api": 0, "local": 2},
            "budget_restant": budget, "coherence_courante": 1.0,
            "cycle": cycle, "journal": journal,
        })
        journal = decision["journal"]
        print(f"cycle {cycle}: {decision['verdict']} — {decision['progression_pct']}%")
        if decision["reveil"] == "stop":
            print(f"ARRET COHERENT — {decision['explication']}")
            break
        for eid in decision["prochaines_etapes"]:       # le HARNAIS exécute
            executer(next(e for e in etapes if e["id"] == eid))
        budget, cycle = decision["budget_apres_cycle"], cycle + 1


if __name__ == "__main__":
    main()
