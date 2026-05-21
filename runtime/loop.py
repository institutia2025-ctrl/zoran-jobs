"""
runtime/loop.py — Runtime loop minimal MVP.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : specs/ZORAN_RUNTIME_PROTOCOL.md §2
Signé : Claude, prestataire, 2026-05-21

Assemble les composants : prompt → cohérence → route → load → execute.
Le runtime est un petit chef d'orchestre : il n'a aucune logique métier.
Chaque cycle retourne une trace complète (reconstructible, falsifiable).
"""

from __future__ import annotations

from loader.loader import Loader
from registry.registry import Registry
from router.router import route
from runtime.coherence.engine import CoherenceState, record_S, state_S


def run_once(
    prompt: str,
    inputs: dict,
    registry: Registry,
    loader: Loader,
    state: CoherenceState,
) -> dict:
    """Un cycle de runtime. Retourne une trace explicite de chaque étape.

    Statuts possibles : ok · no_skill · load_failed · skill_failed.
    Le runtime ne crash jamais en silence : toute erreur est tracée.
    """
    trace: dict = {"prompt": prompt, "S_before": round(state_S(state), 4)}

    # 1. Router (déterministe)
    ranked = route(prompt, registry.all_manifests(), state)
    trace["ranked"] = [(c.skill_id, c.score) for c in ranked]
    if not ranked:
        trace["status"] = "no_skill"
        return trace

    best = ranked[0]
    trace["selected"] = best.skill_id

    # 2. Loader (vérifie le hash, importe)
    manifest = registry.get(best.skill_id)
    if manifest is None:  # ne devrait pas arriver — sécurité
        trace["status"] = "no_skill"
        trace["error"] = f"skill {best.skill_id} absent du registry"
        return trace
    module, err = loader.load(manifest)
    if err:
        trace["status"] = "load_failed"
        trace["error"] = err
        return trace

    # 3. Exécution
    try:
        outputs = module.run(inputs)
    except Exception as e:  # le skill plante — tracé, pas de crash runtime
        trace["status"] = "skill_failed"
        trace["error"] = str(e)
        return trace

    trace["outputs"] = outputs

    # 6. Mesure de cohérence APRÈS (RUNTIME_PROTOCOL §2 étape 6).
    #    On applique l'effet de cohérence DÉCLARÉ par le skill sur l'état,
    #    puis on enregistre le nouveau S dans l'historique (base cinématique).
    #    Note : en MVP l'effet est la valeur déclarée du manifest. L'Oracle
    #    (Phase 2) mesurera l'effet RÉEL et corrigera l'écart déclaration↔mesure.
    coh = manifest.coherence
    state.delta_phi += float(coh.get("expected_delta_phi", 0.0))
    state.T += float(coh.get("expected_T_added", 0.0))
    state.sigma += float(coh.get("expected_sigma_added", 0.0))
    s_after = record_S(state)
    trace["S_after"] = round(s_after, 4)
    trace["delta_S_real"] = round(s_after - trace["S_before"], 4)

    trace["status"] = "ok"
    return trace


__all__ = ["run_once"]
