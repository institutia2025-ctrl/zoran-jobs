"""skill greet_ko — skill qui VIOLE son contrat io. Mission ZORAN_JOBS_20260521.

Déclare dans son manifest produire {greeting: str}, mais produit en réalité
{message: str} — mauvaise clé. Il « réussit » (aucune exception) mais ne
respecte PAS son contrat déclaré.

Sert à prouver que l'Oracle FALSIFIE : il doit révéler cette violation par la
mesure (io_conformity_rate), pas se fier à la déclaration du manifest.
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Manifest déclare {greeting:str} — ce code produit {message:str}. Violation."""
    name = str((inputs or {}).get("name", ""))
    return {"message": f"bonjour {name}"}
