"""registry — Skill Registry + Manifest parser. Phase 1 MVP — ZORAN's Jobs.

Mission : ZORAN_JOBS_20260521 · Signé Claude, prestataire, 2026-05-21.
"""

from registry.manifest import (
    Manifest,
    load_manifest_file,
    parse_manifest,
    validate_manifest,
)
from registry.registry import Registry

__all__ = [
    "Manifest",
    "validate_manifest",
    "parse_manifest",
    "load_manifest_file",
    "Registry",
]
