"""quarantine — système immunitaire runtime + journal. Mission ZORAN_JOBS_20260521 · Phase 3."""

from quarantine.immune import (
    PROMOTION_MAX_LATENCY_MS,
    PROMOTION_MIN_CLEAN_EVALS,
    QUARANTINE_THRESHOLD,
    ImmuneSystem,
)
from quarantine.journal import Journal

__all__ = [
    "ImmuneSystem", "Journal",
    "QUARANTINE_THRESHOLD", "PROMOTION_MIN_CLEAN_EVALS", "PROMOTION_MAX_LATENCY_MS",
]
