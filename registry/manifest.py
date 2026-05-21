"""
registry/manifest.py — Manifest parser + validator.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Spec source (gelée) : specs/ZORAN_SKILL_CONTRACT.md
Signé : Claude, prestataire, 2026-05-21

Valide un manifest.json de skill contre le contrat gelé SKILL_CONTRACT.
Aucune magie implicite : si un champ manque ou sort d'une énumération fermée,
l'erreur est explicite et le skill est refusé. Pas de valeur devinée.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# --- Énumérations fermées (issues du contrat gelé SKILL_CONTRACT) -----------
SANDBOX_LEVELS = {"none", "isolated", "strict"}
LATENCY_CLASSES = {"fast", "medium", "slow"}
# MVP : 3 états seulement. Phase 2+ ajoutera quarantine/deprecated/revoked.
LIFECYCLE_MVP = {"candidate", "active", "rejected"}
ROLLBACK_STRATEGIES = {"undo_function", "snapshot", "none"}

# --- V2 énumérations ---
GRAVITE_V2 = {"faible", "moyenne", "elevee", "critique"}
FRAMES_V2_RECOMMANDES = {"structure", "cout", "carbone", "maintenance",
                          "exploitation", "securite", "global"}


@dataclass
class Manifest:
    """Représentation typée d'un manifest de skill validé."""
    skill_id: str
    name: str
    version: str
    hash: str
    signature: str
    domain: str
    triggers: list[str]
    description: str
    coherence: dict
    cost: dict
    permissions: list[str]
    sandbox_level: str
    dependencies: dict
    rollback: dict
    providers_compatible: list[str]
    lifecycle_state: str
    # --- V2 champs optionnels (rétro-compatible) ---
    coherence_multi_frame: dict = field(default_factory=dict)
    futur_probable: list = field(default_factory=list)
    veto_capable: bool = False
    limites_explicites: list = field(default_factory=list)
    # ----------------------------------------------
    raw: dict = field(default_factory=dict)
    source_dir: str = ""  # métadonnée runtime (rempli par le Registry, pas dans le json)


def validate_manifest(data: dict) -> list[str]:
    """Retourne la liste des erreurs. Liste vide = manifest valide.

    Ne lève jamais d'exception : un manifest cassé produit des messages
    d'erreur explicites, pas un crash.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest n'est pas un objet JSON"]

    # identity
    ident = data.get("identity") or {}
    for f in ("skill_id", "name", "version", "hash", "signature"):
        if not ident.get(f):
            errors.append(f"identity.{f} manquant ou vide")
    sid = ident.get("skill_id", "")
    if sid and not all(c.islower() or c.isdigit() or c == "_" for c in sid):
        errors.append(f"identity.skill_id '{sid}' : caractères interdits (attendu [a-z0-9_])")

    # routing
    routing = data.get("routing") or {}
    if not routing.get("domain"):
        errors.append("routing.domain manquant")
    triggers = routing.get("triggers")
    if not isinstance(triggers, list) or not triggers:
        errors.append("routing.triggers manquant ou vide")

    # coherence — bornes 0..1, voir SKILL_CONTRACT §4
    coh = data.get("coherence") or {}
    for f in ("expected_delta_phi", "expected_T_added", "expected_sigma_added"):
        v = coh.get(f)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 <= v <= 1.0):
            errors.append(f"coherence.{f} : attendu un nombre dans [0..1]")

    # cost
    cost = data.get("cost") or {}
    rc = cost.get("runtime_cost")
    if not isinstance(rc, int) or isinstance(rc, bool) or not (1 <= rc <= 10):
        errors.append("cost.runtime_cost : attendu un entier dans [1..10]")
    if cost.get("latency_class") not in LATENCY_CLASSES:
        errors.append(f"cost.latency_class : attendu l'un de {sorted(LATENCY_CLASSES)}")

    # sandbox
    if data.get("sandbox_level") not in SANDBOX_LEVELS:
        errors.append(f"sandbox_level : attendu l'un de {sorted(SANDBOX_LEVELS)}")

    # rollback
    rb = data.get("rollback") or {}
    if rb.get("rollback_strategy") not in ROLLBACK_STRATEGIES:
        errors.append(f"rollback.rollback_strategy : attendu l'un de {sorted(ROLLBACK_STRATEGIES)}")

    # lifecycle — MVP uniquement
    if data.get("lifecycle_state") not in LIFECYCLE_MVP:
        errors.append(f"lifecycle_state : attendu l'un de {sorted(LIFECYCLE_MVP)} (MVP)")

    # --- Validation V2 (déclenchée si schema_version >= 2.0 OU champs V2 présents) ---
    _validate_v2_extensions(data, errors)

    return errors


def _validate_v2_extensions(data: dict, errors: list) -> None:
    """Valide les champs V2 (optionnels, rétro-compat). Erreurs accumulees dans `errors`."""
    mf = data.get("coherence_multi_frame")
    if mf is not None:
        if not isinstance(mf, dict) or not mf:
            errors.append("coherence_multi_frame : doit etre un dict non vide si present")
            return
        total_weight = 0.0
        for fname, cfg in mf.items():
            if not isinstance(cfg, dict):
                errors.append(f"coherence_multi_frame.{fname} : doit etre un objet")
                continue
            for k in ("expected_delta_phi", "expected_T_added", "expected_sigma_added"):
                v = cfg.get(k)
                if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 <= v <= 1.0):
                    errors.append(f"coherence_multi_frame.{fname}.{k} : nombre dans [0..1] attendu")
            w = cfg.get("weight")
            if not isinstance(w, (int, float)) or isinstance(w, bool) or not (0.0 <= w <= 1.0):
                errors.append(f"coherence_multi_frame.{fname}.weight : nombre dans [0..1] attendu")
            else:
                total_weight += w
        if mf and abs(total_weight - 1.0) > 0.01:
            errors.append(
                f"coherence_multi_frame : somme des poids = {total_weight:.4f}, attendu 1.0 +/- 0.01"
            )

    fp = data.get("futur_probable")
    if fp is not None:
        if not isinstance(fp, list):
            errors.append("futur_probable : doit etre une liste si present")
        else:
            for i, item in enumerate(fp):
                if not isinstance(item, dict):
                    errors.append(f"futur_probable[{i}] : doit etre un objet")
                    continue
                if not isinstance(item.get("horizon_an"), int) or item["horizon_an"] < 1:
                    errors.append(f"futur_probable[{i}].horizon_an : entier >= 1 requis")
                if not isinstance(item.get("evenement"), str) or not item["evenement"]:
                    errors.append(f"futur_probable[{i}].evenement : str non vide requis")
                pb = item.get("probabilite")
                if not isinstance(pb, (int, float)) or isinstance(pb, bool) or not (0.0 <= pb <= 1.0):
                    errors.append(f"futur_probable[{i}].probabilite : nombre dans [0..1] requis")
                if item.get("gravite") not in GRAVITE_V2:
                    errors.append(f"futur_probable[{i}].gravite : attendu {sorted(GRAVITE_V2)}")
                if not isinstance(item.get("reference"), str) or not item["reference"]:
                    errors.append(f"futur_probable[{i}].reference : source vérifiable requise (Loi 1)")

    vc = data.get("veto_capable")
    if vc is not None and not isinstance(vc, bool):
        errors.append("veto_capable : booleen attendu")

    le = data.get("limites_explicites")
    if le is not None:
        if not isinstance(le, list):
            errors.append("limites_explicites : doit etre une liste de strings")
        else:
            for i, lim in enumerate(le):
                if not isinstance(lim, str) or not lim.strip():
                    errors.append(f"limites_explicites[{i}] : string non vide attendue")


def parse_manifest(data: dict) -> Manifest:
    """Construit un Manifest depuis un dict. À appeler APRÈS validate_manifest()."""
    ident = data["identity"]
    routing = data["routing"]
    return Manifest(
        skill_id=ident["skill_id"],
        name=ident["name"],
        version=ident["version"],
        hash=ident["hash"],
        signature=ident["signature"],
        domain=routing["domain"],
        triggers=list(routing["triggers"]),
        description=routing.get("description", ""),
        coherence=dict(data.get("coherence") or {}),
        cost=dict(data.get("cost") or {}),
        permissions=list(data.get("permissions") or []),
        sandbox_level=data["sandbox_level"],
        dependencies=dict(data.get("dependencies") or {}),
        rollback=dict(data.get("rollback") or {}),
        providers_compatible=list(data.get("providers_compatible") or []),
        lifecycle_state=data["lifecycle_state"],
        coherence_multi_frame=dict(data.get("coherence_multi_frame") or {}),
        futur_probable=list(data.get("futur_probable") or []),
        veto_capable=bool(data.get("veto_capable", False)),
        limites_explicites=list(data.get("limites_explicites") or []),
        raw=data,
    )


def load_manifest_file(path) -> tuple[Manifest | None, list[str]]:
    """Charge + valide un manifest.json. Retourne (Manifest|None, erreurs)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # JSON illisible — erreur explicite, pas de crash
        return None, [f"JSON illisible : {e}"]
    errors = validate_manifest(data)
    if errors:
        return None, errors
    return parse_manifest(data), []


__all__ = ["Manifest", "validate_manifest", "parse_manifest", "load_manifest_file"]
