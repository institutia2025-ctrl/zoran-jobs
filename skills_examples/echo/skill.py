"""
skill echo — skill de démonstration MVP.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Point d'entrée standard : run(inputs: dict) -> dict (cf RUNTIME_PROTOCOL §2).

Skill factice volontairement trivial : il sert à prouver que le pipeline
registry -> router -> loader fonctionne, pas à faire un vrai travail.
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Renvoie le texte reçu. Contrat io : {text:str} -> {echo:str}."""
    text = str((inputs or {}).get("text", ""))
    return {"echo": text}
