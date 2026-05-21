"""
router/router.py — Skill Router déterministe.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : audit/SKILL_ORACLE_ARCHITECTURE.md §4.4
Signé : Claude, prestataire, 2026-05-21

Le Router NE pense pas, NE prédit pas, NE raisonne pas. Il CLASSE et ROUTE.
Déterministe : même (prompt, registry, état) → même classement, toujours.

INTERDIT : LLM, hasard, embeddings, ranking dynamique appris.

Score de routage (architecture §4.4) :

    skill_score = pertinence_triggers
                × cohérence_phénoménale (ΔS)
                × bonus_cinématique
                ÷ coût_runtime
"""

from __future__ import annotations

from dataclasses import dataclass

from registry.manifest import Manifest
from runtime.coherence.engine import CoherenceState, dS_dt, delta_S


@dataclass
class RoutingCandidate:
    """Un skill candidat et son score décomposé (traçable, falsifiable)."""
    skill_id: str
    score: float
    pertinence: float
    delta_S: float
    bonus_cinematique: float
    cost: int


def _trigger_pertinence(prompt: str, triggers: list[str]) -> float:
    """Fraction des triggers du skill présents dans le prompt (0..1).

    Match littéral, insensible à la casse. Déterministe.
    """
    if not triggers:
        return 0.0
    low = prompt.lower()
    hits = sum(1 for t in triggers if t.lower() in low)
    return hits / len(triggers)


def score_skill(prompt: str, manifest: Manifest, state: CoherenceState) -> RoutingCandidate:
    """Calcule le score d'un skill. Tout est explicite et reproductible."""
    pertinence = _trigger_pertinence(prompt, manifest.triggers)

    # Cohérence phénoménale : gain de S si on chargeait ce skill.
    # Borné à >= 0 — un skill qui dégrade S ne peut pas obtenir un score négatif,
    # il obtient 0 (il ne sera pas routé).
    d_s = delta_S(state, manifest.coherence)
    coherence_gain = max(0.0, d_s)

    # Bonus cinématique : si la cohérence s'effondre (dS/dt < 0) ET que le skill
    # est correcteur, on le privilégie. Sinon neutre.
    slope = dS_dt(state)
    corrective = bool(manifest.coherence.get("corrective", False))
    bonus = 1.5 if (slope < 0 and corrective) else 1.0

    cost = int(manifest.cost.get("runtime_cost", 1)) or 1

    score = (pertinence * coherence_gain * bonus) / cost

    return RoutingCandidate(
        skill_id=manifest.skill_id,
        score=round(score, 6),
        pertinence=round(pertinence, 4),
        delta_S=round(d_s, 4),
        bonus_cinematique=bonus,
        cost=cost,
    )


def route(prompt: str, manifests: list[Manifest], state: CoherenceState) -> list[RoutingCandidate]:
    """Classe tous les skills par score décroissant.

    Les skills de score 0 (aucun trigger OU aucun gain de cohérence) sont
    EXCLUS du résultat — le Router ne route pas un skill non pertinent.
    Tri stable : à score égal, ordre alphabétique du skill_id (déterminisme).
    """
    candidates = [score_skill(prompt, m, state) for m in manifests]
    retained = [c for c in candidates if c.score > 0.0]
    retained.sort(key=lambda c: (-c.score, c.skill_id))
    return retained


__all__ = ["RoutingCandidate", "score_skill", "route"]
