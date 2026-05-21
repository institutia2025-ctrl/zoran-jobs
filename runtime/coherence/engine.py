"""
runtime/coherence/engine.py — Coherence Engine MVP (couche phénoménale).

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : audit/SKILL_ORACLE_ARCHITECTURE.md §4
Signé : Claude, prestataire, 2026-05-21

PUREMENT MATHÉMATIQUE. Aucune magie. Le résultat de chaque fonction est
prédictible à la main — c'est la condition de la falsifiabilité.

INTERDIT dans ce module (discipline ZORAN) : LLM, embeddings, heuristiques
opaques, auto-apprentissage, ranking dynamique. Que du calcul.

Formule canonique ZORAN (additive — JAMAIS le produit T×σ) :

    S = (β × ΔΦ) / (1 + T + σ)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CoherenceState:
    """État de cohérence courant + historique (base de la cinématique)."""
    beta: float = 1.0          # direction / structure
    delta_phi: float = 0.0     # information acquise
    T: float = 0.0             # contradictions
    sigma: float = 0.0         # bruit
    S_history: list[float] = field(default_factory=list)


def compute_S(beta: float, delta_phi: float, T: float, sigma: float) -> float:
    """S = (β × ΔΦ) / (1 + T + σ). Dénominateur additif, jamais nul."""
    denom = 1.0 + max(0.0, T) + max(0.0, sigma)
    return (beta * delta_phi) / denom


def state_S(state: CoherenceState) -> float:
    """S de l'état courant."""
    return compute_S(state.beta, state.delta_phi, state.T, state.sigma)


def candidate_S(state: CoherenceState, skill_coherence: dict) -> float:
    """S projeté SI on chargeait un skill, d'après son bloc `coherence` (manifest).

    Le skill ajoute de l'information (ΔΦ) mais peut injecter T et σ.
    """
    dphi = state.delta_phi + float(skill_coherence.get("expected_delta_phi", 0.0))
    t = state.T + float(skill_coherence.get("expected_T_added", 0.0))
    sig = state.sigma + float(skill_coherence.get("expected_sigma_added", 0.0))
    return compute_S(state.beta, dphi, t, sig)


def delta_S(state: CoherenceState, skill_coherence: dict) -> float:
    """ΔS = S_candidat − S_courant. Positif = le skill améliore la cohérence."""
    return candidate_S(state, skill_coherence) - state_S(state)


def dS_dt(state: CoherenceState, window: int = 3) -> float:
    """Cinématique : pente de S sur les `window` derniers points de l'historique.

    Différence finie simple (dernier − premier de la fenêtre) / nb_intervalles.
    > 0 : la cohérence monte · < 0 : elle s'effondre · 0 : stagne ou pas assez d'historique.
    """
    h = state.S_history
    if len(h) < 2:
        return 0.0
    w = h[-max(2, window):]
    return (w[-1] - w[0]) / (len(w) - 1)


def record_S(state: CoherenceState) -> float:
    """Calcule le S courant ET l'ajoute à l'historique. Retourne ce S."""
    s = state_S(state)
    state.S_history.append(s)
    return s


__all__ = [
    "CoherenceState", "compute_S", "state_S",
    "candidate_S", "delta_S", "dS_dt", "record_S",
    # V2 :
    "compute_S_multi_frame", "s_global",
]


# ============================================================================
# V2 — Cohérence multi-cadres (rétro-compat, INV-1 préservé par cadre)
# ============================================================================

def compute_S_multi_frame(state: CoherenceState, multi_frame: dict) -> dict:
    """Calcule S par cadre. Chaque cadre suit INV-1 strict (1 + T + sigma).

    INV-11 : aucun produit T×σ caché. Chaque cadre est un compute_S indépendant.
    """
    out = {}
    for frame, cfg in multi_frame.items():
        if not isinstance(cfg, dict):
            continue
        out[frame] = compute_S(
            state.beta,
            state.delta_phi + float(cfg.get("expected_delta_phi", 0.0)),
            state.T + float(cfg.get("expected_T_added", 0.0)),
            state.sigma + float(cfg.get("expected_sigma_added", 0.0)),
        )
    return out


def s_global(s_per_frame: dict, multi_frame: dict) -> float:
    """S_global = somme(weight_i × S_i). Somme des poids déjà validée à 1.0 par le manifest."""
    return sum(
        float(multi_frame[f].get("weight", 0.0)) * s
        for f, s in s_per_frame.items()
        if f in multi_frame
    )
