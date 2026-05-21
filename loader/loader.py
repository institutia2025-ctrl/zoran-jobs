"""
loader/loader.py — Skill Loader minimal.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : specs/ZORAN_RUNTIME_PROTOCOL.md §4
Signé : Claude, prestataire, 2026-05-21

Le Loader fait EXACTEMENT trois choses : vérifier le hash, charger, décharger.
Il NE connaît PAS : Oracle, Ranking, GitHub, Quarantine, Projection.
Il est volontairement réécrivable/supprimable en quelques minutes — discipline
« sandbox jetable ».

RUNTIME_PROTOCOL §4 : hash skill ≠ manifest ⇒ REFUS de charger + skill_failed.
Jamais « charger quand même ».
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from registry.manifest import Manifest


class Loader:
    """Charge/décharge dynamiquement des modules skill, après vérification du hash."""

    def __init__(self) -> None:
        self._loaded: dict[str, object] = {}  # skill_id -> module

    @staticmethod
    def _verify_hash(manifest: Manifest) -> tuple[bool, str]:
        """Recalcule le sha256 du skill.py et le compare au manifest. Falsifiable."""
        skill_py = Path(manifest.source_dir) / "skill.py"
        if not skill_py.exists():
            return False, f"skill.py absent : {skill_py}"
        actual = "sha256:" + hashlib.sha256(skill_py.read_bytes()).hexdigest()
        if actual != manifest.hash:
            return False, (
                f"hash mismatch — manifest={manifest.hash[:23]}… "
                f"fichier={actual[:23]}… → REFUS de charger"
            )
        return True, ""

    def load(self, manifest: Manifest) -> tuple[object | None, str]:
        """Vérifie le hash puis importe skill.py. Retourne (module|None, erreur)."""
        ok, err = self._verify_hash(manifest)
        if not ok:
            return None, err

        skill_py = Path(manifest.source_dir) / "skill.py"
        try:
            spec = importlib.util.spec_from_file_location(
                f"zoran_skill_{manifest.skill_id}", skill_py
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            return None, f"import échoué : {e}"

        if not hasattr(module, "run") or not callable(module.run):
            return None, "skill.py n'expose pas une fonction run(inputs)"

        self._loaded[manifest.skill_id] = module
        return module, ""

    def unload(self, skill_id: str) -> bool:
        """Décharge un skill. Retourne True s'il était chargé."""
        return self._loaded.pop(skill_id, None) is not None

    def is_loaded(self, skill_id: str) -> bool:
        return skill_id in self._loaded

    def loaded_skills(self) -> list[str]:
        return sorted(self._loaded.keys())


__all__ = ["Loader"]
