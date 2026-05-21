"""
registry/registry.py — Skill Registry minimal.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : specs/ZORAN_SKILL_CONTRACT.md
Signé : Claude, prestataire, 2026-05-21

Scanne un dossier de skills, charge + valide chaque manifest.json, indexe.
Un skill dont le manifest est invalide est REFUSÉ (jamais indexé) et ses
erreurs sont conservées pour audit. Pas de skill « à moitié chargé ».

Composant supprimable : le Registry ne dépend que de manifest.py. Le supprimer
ne casse rien d'autre — discipline « sandbox jetable ».
"""

from __future__ import annotations

from pathlib import Path

from registry.manifest import Manifest, load_manifest_file


class Registry:
    """Index en mémoire des skills valides découverts sur disque."""

    def __init__(self) -> None:
        self._skills: dict[str, Manifest] = {}
        self._rejected: dict[str, list[str]] = {}  # nom_dossier -> erreurs

    def load_from_dir(self, skills_dir) -> dict:
        """Scanne `skills_dir/*/manifest.json`. Retourne un rapport explicite."""
        skills_dir = Path(skills_dir)
        loaded: list[str] = []
        rejected: list[str] = []

        if not skills_dir.is_dir():
            return {
                "loaded": [], "rejected": [],
                "n_loaded": 0, "n_rejected": 0,
                "error": f"dossier introuvable : {skills_dir}",
            }

        for sub in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            mpath = sub / "manifest.json"
            if not mpath.exists():
                self._rejected[sub.name] = ["manifest.json absent"]
                rejected.append(sub.name)
                continue
            manifest, errors = load_manifest_file(mpath)
            if errors:
                self._rejected[sub.name] = errors
                rejected.append(sub.name)
                continue
            manifest.source_dir = str(sub)  # le Loader en a besoin
            self._skills[manifest.skill_id] = manifest
            loaded.append(manifest.skill_id)

        return {
            "loaded": loaded,
            "rejected": rejected,
            "n_loaded": len(loaded),
            "n_rejected": len(rejected),
        }

    def get(self, skill_id: str) -> Manifest | None:
        """Retourne le Manifest d'un skill, ou None si inconnu."""
        return self._skills.get(skill_id)

    def list_skills(self) -> list[str]:
        """Liste triée des skill_id valides indexés."""
        return sorted(self._skills.keys())

    def by_domain(self, domain: str) -> list[Manifest]:
        """Tous les skills valides d'un domaine donné."""
        return [m for m in self._skills.values() if m.domain == domain]

    def all_manifests(self) -> list[Manifest]:
        """Tous les manifests valides (utile au Router)."""
        return list(self._skills.values())

    def rejected(self) -> dict[str, list[str]]:
        """Skills refusés et leurs erreurs — pour audit."""
        return dict(self._rejected)


__all__ = ["Registry"]
