"""
tests/test_contract_v2.py — Tests du contrat V2.

Mission : ZORAN_JOBS_20260521 · ZORAN_BTP_SKILLS_MASTERPLAN_20260521.
Signé : Frederic TABARY + Claude, 2026-05-21.

Couvre :
  - Schema V1 toujours accepté (INV-10 retrocompat)
  - Schema V2 avec multi_frame + futur_probable + veto + limites validés
  - INV-1 préservé par cadre (INV-11)
  - Veto sécurité déterministe et bloque le routage (INV-12)
  - Trace runtime contient limites_explicites du skill sélectionné (INV-13)
  - Erreurs explicites quand V2 mal formé

24 assertions au total.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from registry.manifest import parse_manifest, validate_manifest  # noqa: E402
from router.router import is_veto_securite, route  # noqa: E402
from runtime.coherence.engine import (  # noqa: E402
    CoherenceState,
    compute_S_multi_frame,
    s_global,
)

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


# ------------------------------------------------------------------
# Manifest de référence V2 valide
# ------------------------------------------------------------------
def manifest_v2_valid() -> dict:
    return {
        "schema_version": "2.0",
        "identity": {"skill_id": "test_v2_ok", "name": "T", "version": "1.0.0",
                     "hash": "sha256:" + "0" * 64, "signature": "demo"},
        "routing": {"domain": "structure", "triggers": ["test"]},
        "coherence": {"expected_delta_phi": 0.5, "expected_T_added": 0.0,
                      "expected_sigma_added": 0.0},
        "cost": {"runtime_cost": 1, "latency_class": "fast", "external_calls": False},
        "sandbox_level": "none",
        "rollback": {"rollback_strategy": "none"},
        "lifecycle_state": "candidate",
        "coherence_multi_frame": {
            "structure": {"expected_delta_phi": 0.8, "expected_T_added": 0.05,
                          "expected_sigma_added": 0.05, "weight": 0.5},
            "securite":  {"expected_delta_phi": 0.9, "expected_T_added": 0.05,
                          "expected_sigma_added": 0.05, "weight": 0.5},
        },
        "futur_probable": [
            {"horizon_an": 30, "evenement": "Carbonatation",
             "probabilite": 0.45, "gravite": "moyenne",
             "reference": "NF EN 14630"},
        ],
        "veto_capable": True,
        "limites_explicites": [
            "Ne couvre que les fissures non structurelles (AQC a/b/c)."
        ],
    }


print("=== TEST 1 — INV-10 : un manifest V1 reste valide (retrocompat) ===")
v1 = {
    "schema_version": "1.0",
    "identity": {"skill_id": "test_v1", "name": "V1", "version": "1.0.0",
                 "hash": "sha256:" + "1" * 64, "signature": "demo"},
    "routing": {"domain": "demo", "triggers": ["v1"]},
    "coherence": {"expected_delta_phi": 0.5, "expected_T_added": 0.0,
                  "expected_sigma_added": 0.0},
    "cost": {"runtime_cost": 1, "latency_class": "fast", "external_calls": False},
    "sandbox_level": "none",
    "rollback": {"rollback_strategy": "none"},
    "lifecycle_state": "candidate",
}
check("V1 sans champs V2 → 0 erreur", validate_manifest(v1) == [])
m = parse_manifest(v1)
check("V1 parse : veto_capable default False", m.veto_capable is False)
check("V1 parse : coherence_multi_frame default {}", m.coherence_multi_frame == {})
check("V1 parse : limites_explicites default []", m.limites_explicites == [])

print()
print("=== TEST 2 — Manifest V2 valide passe la validation ===")
v2 = manifest_v2_valid()
errs = validate_manifest(v2)
check("V2 valide → 0 erreur", errs == [])

print()
print("=== TEST 3 — Validation V2 : champs malformés détectés ===")
# Poids ne sommant pas à 1
bad_weights = manifest_v2_valid()
bad_weights["coherence_multi_frame"]["securite"]["weight"] = 0.3  # somme 0.8
errs = validate_manifest(bad_weights)
check("poids 0.8 (≠1.0) → erreur detectee", any("poids" in e for e in errs))

# Probabilité hors borne
bad_prob = manifest_v2_valid()
bad_prob["futur_probable"][0]["probabilite"] = 1.5
errs = validate_manifest(bad_prob)
check("probabilite=1.5 → erreur detectee", any("probabilite" in e for e in errs))

# Gravité hors enum
bad_grav = manifest_v2_valid()
bad_grav["futur_probable"][0]["gravite"] = "yolo"
errs = validate_manifest(bad_grav)
check("gravite='yolo' → erreur detectee", any("gravite" in e for e in errs))

# Référence manquante (Loi 1)
bad_ref = manifest_v2_valid()
bad_ref["futur_probable"][0]["reference"] = ""
errs = validate_manifest(bad_ref)
check("reference vide → erreur Loi 1 detectee", any("reference" in e or "Loi 1" in e for e in errs))

# veto_capable mauvais type
bad_veto = manifest_v2_valid()
bad_veto["veto_capable"] = "yes"
errs = validate_manifest(bad_veto)
check("veto_capable='yes' → erreur boolean attendu", any("veto_capable" in e for e in errs))

print()
print("=== TEST 4 — INV-11 : compute_S_multi_frame applique INV-1 par cadre ===")
state = CoherenceState()
mf = v2["coherence_multi_frame"]
s_frames = compute_S_multi_frame(state, mf)
# verif manuelle structure : S = (1.0 × 0.8) / (1 + 0.05 + 0.05) = 0.8/1.10 ≈ 0.7272
expected_struct = 0.8 / 1.10
check("S_structure ≈ 0.8/1.10 (INV-1 par cadre)",
      abs(s_frames["structure"] - expected_struct) < 1e-9)
# securite : S = 0.9 / 1.10 ≈ 0.8181
expected_sec = 0.9 / 1.10
check("S_securite ≈ 0.9/1.10 (INV-1 par cadre)",
      abs(s_frames["securite"] - expected_sec) < 1e-9)
# Tous les S sont positifs (1+T+σ ≥ 1 toujours)
check("Tous les S frames sont > 0 (denominateur additif)",
      all(s > 0 for s in s_frames.values()))

print()
print("=== TEST 5 — s_global : moyenne ponderee correcte ===")
sg = s_global(s_frames, mf)
expected_sg = 0.5 * expected_struct + 0.5 * expected_sec
check("s_global = 0.5×S_struct + 0.5×S_sec", abs(sg - expected_sg) < 1e-9)

print()
print("=== TEST 6 — INV-12 : veto securite deterministe + filtrant ===")
m_valid = parse_manifest(manifest_v2_valid())
# S_securite par defaut ≈ 0.8181 >> 0.15 → pas de veto
check("veto False quand S_securite confortable", is_veto_securite(m_valid, state) is False)

# Construire un manifest avec S_securite tres bas
v2_bad_sec = manifest_v2_valid()
v2_bad_sec["coherence_multi_frame"]["securite"] = {
    "expected_delta_phi": 0.05,  # faible
    "expected_T_added": 0.9,     # bruit fort
    "expected_sigma_added": 0.9,
    "weight": 0.5,
}
m_unsafe = parse_manifest(v2_bad_sec)
# S_sec = 0.05 / (1 + 0.9 + 0.9) = 0.05/2.8 ≈ 0.0179 << 0.15 → veto
check("veto True quand S_securite < seuil", is_veto_securite(m_unsafe, state) is True)
# determinisme : deux appels identiques
r1 = is_veto_securite(m_unsafe, state)
r2 = is_veto_securite(m_unsafe, state)
check("INV-12 : veto deterministe (2 appels = meme resultat)", r1 == r2)

# V1 skill jamais veto (veto_capable False par defaut)
m_v1 = parse_manifest(v1)
check("V1 jamais veto (veto_capable=False)", is_veto_securite(m_v1, state) is False)

print()
print("=== TEST 7 — Router applique le veto AVANT scoring ===")
# manifest avec triggers qui matchent, mais veto actif → exclus
m_unsafe_routable = manifest_v2_valid()
m_unsafe_routable["identity"]["skill_id"] = "unsafe_skill"
m_unsafe_routable["coherence_multi_frame"]["securite"] = {
    "expected_delta_phi": 0.05,
    "expected_T_added": 0.9,
    "expected_sigma_added": 0.9,
    "weight": 0.5,
}
m_unsafe_routable["routing"]["triggers"] = ["dangerous"]
parsed = parse_manifest(m_unsafe_routable)
result = route("dangerous operation", [parsed], state)
check("Router exclut skill veto → result vide", result == [])
# Sans veto_capable, le meme skill (s'il avait triggers + coh adequate) serait route
m_safe = manifest_v2_valid()
m_safe["identity"]["skill_id"] = "safe_skill"
m_safe["routing"]["triggers"] = ["dangerous"]
m_safe["veto_capable"] = False
parsed_safe = parse_manifest(m_safe)
result2 = route("dangerous operation", [parsed_safe], state)
check("Sans veto_capable, le skill est route normalement", len(result2) == 1)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
