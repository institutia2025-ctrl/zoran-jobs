"""skill memory_recall — démo MVP. run(inputs) -> dict. Mission ZORAN_JOBS_20260521."""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Simule un rappel mémoire. Contrat io : {query:str} -> {recall:str}."""
    query = str((inputs or {}).get("query", ""))
    return {"recall": f"souvenir simule pour: {query}"}
