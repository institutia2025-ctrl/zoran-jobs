"""
quarantine/journal.py — Journal append-only horodaté et signé.

Mission : ZORAN_JOBS_20260521 · Phase 3
Spec source : specs/ZORAN_EVENT_SCHEMA.md (append-only, signature)
Signé : Claude, prestataire, 2026-05-21

ZORAN Phase 3 : « chaque promotion/démotion/rejet/quarantaine doit être
tracée, horodatée, signée, reconstructible. »

Le journal est append-only : un événement n'est jamais modifié ni supprimé.
Chaque ligne porte une signature (hash) — toute altération est détectable.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _sign(event_without_sig: dict) -> str:
    """Signature = sha256 de l'événement sérialisé (clés triées, déterministe)."""
    blob = json.dumps(event_without_sig, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


class Journal:
    """Journal d'événements de gouvernance runtime. Append-only, signé."""

    def __init__(self, path) -> None:
        self.path = Path(path)

    def append(self, event_type: str, skill_id: str, payload: dict) -> dict:
        """Ajoute un événement signé. Retourne l'événement complet."""
        event = {
            "event_id": f"imm_{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "skill_id": skill_id,
            "payload": payload,
        }
        event["signature"] = _sign(event)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def read(self) -> list[dict]:
        """Relit tous les événements dans l'ordre."""
        if not self.path.exists():
            return []
        out: list[dict] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def verify_integrity(self) -> tuple[bool, str | None]:
        """Vérifie la signature de chaque événement. (True,None) si tout est intègre."""
        for event in self.read():
            sig = event.get("signature")
            unsigned = {k: v for k, v in event.items() if k != "signature"}
            if sig != _sign(unsigned):
                return False, event.get("event_id")
        return True, None


__all__ = ["Journal"]
