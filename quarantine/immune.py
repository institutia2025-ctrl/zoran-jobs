"""
quarantine/immune.py — Système immunitaire runtime minimal.

Mission : ZORAN_JOBS_20260521 · Phase 3
Signé : Claude, prestataire, 2026-05-21

ZORAN Phase 3 — « minimalisme radical ». Ce module fait EXACTEMENT ceci :
  - QUARANTAINE : 3 violations io → désactivation (lifecycle → quarantine)
  - DÉMOTION    : un skill `active` qui viole → retour `candidate`
  - PROMOTION   : `candidate` propre (N évals, 0 violation, stable, latence OK) → `active`
  - ROLLBACK    : annuler la dernière transition, immédiatement

INTERDIT (discipline ZORAN) : auto-réparation, auto-réécriture, auto-évolution,
auto-fusion, machine learning, heuristique opaque. Que des règles explicites,
chacune prédictible à la main. Toute transition est journalisée + réversible.
"""

from __future__ import annotations

from quarantine.journal import Journal

# --- Règles explicites (seuils ; modifiables, mais jamais « appris ») --------
QUARANTINE_THRESHOLD = 3        # 3 violations io cumulées → quarantaine
PROMOTION_MIN_CLEAN_EVALS = 3   # nb d'évals propres consécutives pour promouvoir
PROMOTION_MAX_LATENCY_MS = 50.0  # au-delà, pas de promotion


class ImmuneSystem:
    """Gouvernance du cycle de vie des skills, pilotée par les mesures de l'Oracle."""

    def __init__(self, journal: Journal) -> None:
        self.journal = journal
        # skill_id -> {lifecycle, violations, clean_evals, last_latency}
        self._state: dict[str, dict] = {}

    def _ensure(self, skill_id: str, lifecycle: str = "candidate") -> dict:
        if skill_id not in self._state:
            self._state[skill_id] = {
                "lifecycle": lifecycle,
                "violations": 0,
                "clean_evals": 0,
                "last_latency": 0.0,
            }
        return self._state[skill_id]

    def lifecycle(self, skill_id: str) -> str:
        """État de cycle de vie courant d'un skill."""
        return self._state.get(skill_id, {}).get("lifecycle", "candidate")

    def state(self, skill_id: str) -> dict:
        """Copie de l'état interne d'un skill (audit)."""
        return dict(self._ensure(skill_id))

    def record(self, skill_id: str, oracle_metrics: dict) -> dict | None:
        """Enregistre une évaluation Oracle et applique au plus UNE transition.

        Retourne la transition appliquée (dict) ou None si aucun changement.
        Ordre des règles : quarantaine > démotion > promotion. Déterministe.
        """
        st = self._ensure(skill_id)
        io_conf = float(oracle_metrics.get("io_conformity_rate", 0.0))
        latency = float(oracle_metrics.get("latency_avg_ms", 9e9))
        stable = bool(oracle_metrics.get("stable", False))
        st["last_latency"] = latency

        violation = io_conf < 1.0
        if violation:
            st["violations"] += 1
            st["clean_evals"] = 0
        else:
            st["clean_evals"] += 1

        # Règle 1 — QUARANTAINE (priorité absolue)
        if st["violations"] >= QUARANTINE_THRESHOLD and st["lifecycle"] != "quarantine":
            return self._transition(skill_id, "quarantine",
                                    f"{st['violations']} violations io cumulées")

        # Règle 2 — DÉMOTION : un skill actif qui viole redescend candidate
        if violation and st["lifecycle"] == "active":
            return self._transition(skill_id, "candidate",
                                    "violation io en état active")

        # Règle 3 — PROMOTION : candidate propre et performant → active
        if (st["lifecycle"] == "candidate"
                and st["violations"] == 0
                and st["clean_evals"] >= PROMOTION_MIN_CLEAN_EVALS
                and stable
                and latency < PROMOTION_MAX_LATENCY_MS):
            return self._transition(skill_id, "active",
                                    f"{st['clean_evals']} évals propres, latence {latency} ms")

        return None

    def _transition(self, skill_id: str, to_state: str, reason: str) -> dict:
        """Applique une transition de lifecycle + la journalise (signée)."""
        st = self._state[skill_id]
        from_state = st["lifecycle"]
        st["lifecycle"] = to_state
        event = self.journal.append("transition", skill_id, {
            "from": from_state, "to": to_state, "reason": reason,
        })
        return {
            "skill_id": skill_id, "from": from_state, "to": to_state,
            "reason": reason, "event_id": event["event_id"],
        }

    def rollback_last(self) -> dict | None:
        """Annule la DERNIÈRE transition. Réversible immédiat (exigence ZORAN).

        Le rollback est lui-même journalisé — l'historique reste append-only.
        """
        transitions = [e for e in self.journal.read() if e.get("type") == "transition"]
        if not transitions:
            return None
        last = transitions[-1]
        skill_id = last["skill_id"]
        restored = last["payload"]["from"]
        st = self._ensure(skill_id)
        st["lifecycle"] = restored
        event = self.journal.append("rollback", skill_id, {
            "undid_event": last["event_id"],
            "restored_to": restored,
        })
        return {
            "skill_id": skill_id, "restored_to": restored,
            "undid_event": last["event_id"], "event_id": event["event_id"],
        }


__all__ = ["ImmuneSystem", "QUARANTINE_THRESHOLD",
           "PROMOTION_MIN_CLEAN_EVALS", "PROMOTION_MAX_LATENCY_MS"]
