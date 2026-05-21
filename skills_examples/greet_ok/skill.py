"""skill greet_ok — skill CONFORME à son contrat io. Mission ZORAN_JOBS_20260521.

Déclare produire {greeting: str} et produit bien {greeting: str}.
Sert de référence honnête pour l'Oracle (Phase 2).
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Contrat io : {name:str} -> {greeting:str}. Respecté."""
    name = str((inputs or {}).get("name", ""))
    return {"greeting": f"bonjour {name}"}
