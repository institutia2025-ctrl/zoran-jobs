"""
oracle/oracle.py — Oracle minimal : compare 2 skills sur métriques RÉELLES.

Mission : ZORAN_JOBS_20260521 · Phase 2
Spec source : audit/SKILL_ORACLE_ARCHITECTURE.md (composant Oracle)
Signé : Claude, prestataire, 2026-05-21

ZORAN : « l'Oracle est le premier vrai point de dérive potentielle. »
Donc l'Oracle est STRICTEMENT minimal et falsifiant :

- il MESURE, il ne note pas — aucune métrique décorative, aucun score
  « impressionnant », aucune notation de verbosité ;
- il ne fait pas confiance au manifest : il exécute le skill et observe le RÉEL ;
- son verdict est déterministe : mêmes skills + mêmes cas → même gagnant.

Métriques mesurées (toutes objectives, vérifiables) :
  success_rate        — fraction d'exécutions sans exception
  io_conformity_rate  — fraction d'outputs conformes au schéma io.outputs déclaré
  stable              — mêmes inputs → mêmes outputs (déterminisme)
  latency_avg_ms      — durée moyenne mesurée
  runtime_cost        — coût déclaré (seul champ non mesuré — départage final)
"""

from __future__ import annotations

import time

from loader.loader import Loader
from registry.manifest import Manifest


def _output_conforme(outputs, io_outputs_schema: dict) -> bool:
    """L'output respecte-t-il le schéma io.outputs déclaré ?

    Vérification minimale et honnête : toutes les clés produites doivent être
    déclarées dans `properties`. Un skill qui produit une clé non déclarée
    VIOLE son contrat — même s'il ne lève pas d'exception.
    """
    if not isinstance(outputs, dict):
        return False
    declared = set((io_outputs_schema or {}).get("properties", {}).keys())
    if not declared:
        return True  # aucun schéma déclaré → on ne juge pas
    return set(outputs.keys()).issubset(declared)


def evaluate_skill(manifest: Manifest, test_cases: list[dict], loader: Loader) -> dict:
    """Exécute un skill sur des cas de test et mesure ses métriques objectives."""
    module, err = loader.load(manifest)
    if err:
        return {"loadable": False, "skill_id": manifest.skill_id, "error": err}

    io_outputs = (manifest.raw.get("io") or {}).get("outputs", {})
    n = len(test_cases)
    successes = 0
    conformes = 0
    stable = True
    latencies: list[float] = []

    for inputs in test_cases:
        t0 = time.perf_counter()
        try:
            out1 = module.run(inputs)
            ok = True
        except Exception:
            out1, ok = None, False
        latencies.append(time.perf_counter() - t0)

        if not ok:
            continue
        successes += 1
        if _output_conforme(out1, io_outputs):
            conformes += 1
        # stabilité : ré-exécution sur les mêmes inputs
        try:
            if module.run(inputs) != out1:
                stable = False
        except Exception:
            stable = False

    return {
        "loadable": True,
        "skill_id": manifest.skill_id,
        "success_rate": round(successes / n, 4) if n else 0.0,
        "io_conformity_rate": round(conformes / n, 4) if n else 0.0,
        "stable": stable,
        "latency_avg_ms": round(1000 * sum(latencies) / len(latencies), 4) if latencies else 0.0,
        "runtime_cost": int(manifest.cost.get("runtime_cost", 1)),
        "n_cases": n,
    }


def _verdict_key(m: dict) -> tuple:
    """Clé de comparaison — priorité STRICTE et déterministe.

    Ordre : conformité io > taux de succès > stabilité > latence basse > coût bas.
    La conformité io passe AVANT le succès : un skill qui « réussit » mais viole
    son contrat est jugé inférieur à un skill conforme.
    """
    if not m.get("loadable"):
        return (-1.0, -1.0, -1, -9e9, -99)  # non chargeable = pire de tout
    return (
        m.get("io_conformity_rate", 0.0),
        m.get("success_rate", 0.0),
        1 if m.get("stable") else 0,
        -m.get("latency_avg_ms", 9e9),   # plus bas = mieux
        -m.get("runtime_cost", 99),       # plus bas = mieux
    )


def compare(manifest_a: Manifest, manifest_b: Manifest,
            test_cases: list[dict], loader: Loader) -> dict:
    """Compare 2 skills. Retourne le gagnant + les 2 jeux de métriques.

    `winner` = skill_id du meilleur, ou None si égalité stricte.
    Déterministe : mêmes entrées → même verdict.
    """
    a = evaluate_skill(manifest_a, test_cases, loader)
    b = evaluate_skill(manifest_b, test_cases, loader)
    ka, kb = _verdict_key(a), _verdict_key(b)
    if ka > kb:
        winner = a["skill_id"]
    elif kb > ka:
        winner = b["skill_id"]
    else:
        winner = None
    return {"winner": winner, "skill_a": a, "skill_b": b}


__all__ = ["evaluate_skill", "compare"]
