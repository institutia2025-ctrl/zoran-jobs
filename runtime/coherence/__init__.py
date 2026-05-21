"""runtime.coherence — Coherence Engine MVP. Mission ZORAN_JOBS_20260521."""

from runtime.coherence.engine import (
    CoherenceState,
    candidate_S,
    compute_S,
    dS_dt,
    delta_S,
    record_S,
    state_S,
)

__all__ = [
    "CoherenceState", "compute_S", "state_S",
    "candidate_S", "delta_S", "dS_dt", "record_S",
]
