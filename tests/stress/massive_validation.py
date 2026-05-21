"""
tests/stress/massive_validation.py — Validation massive du runtime ZORAN's Jobs.

Mission : `ZORAN_JOBS_20260521` · phase VALIDATION MASSIVE
Signé : Claude, prestataire, 2026-05-21

ZORAN : « le problème n'est plus 'est-ce que ça marche ?' mais 'est-ce que ça
tient quand on le pousse réellement ?' »

Ce harness pousse le runtime Phase 1-3 à l'échelle et mesure des KPI. Il
n'ajoute AUCUNE couche au runtime — il le stresse. Outil réutilisable.

Aléa SEEDÉ (reproductible) — le hasard est interdit dans le runtime, pas dans
un harness de test reproductible. Exécutable : python tests/stress/massive_validation.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from quarantine import ImmuneSystem, Journal  # noqa: E402
from registry.manifest import Manifest, validate_manifest  # noqa: E402
from router.router import route  # noqa: E402
from runtime.coherence.engine import (  # noqa: E402
    CoherenceState,
    compute_S,
    dS_dt,
)

SEED = 20260521
random.seed(SEED)
PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def make_manifest_dict(sid, domain, triggers, dphi=0.3, t=0.0, sig=0.0,
                       cost=1, corrective=False):
    """Manifest valide synthétique."""
    return {
        "schema_version": "1.0",
        "identity": {"skill_id": sid, "name": sid, "version": "1.0.0",
                     "hash": "sha256:" + "0" * 64, "signature": "sig-" + sid},
        "io": {"inputs": {"type": "object", "properties": {}},
               "outputs": {"type": "object", "properties": {}}},
        "routing": {"domain": domain, "triggers": triggers, "description": sid},
        "coherence": {"expected_delta_phi": dphi, "expected_T_added": t,
                      "expected_sigma_added": sig, "corrective": corrective},
        "cost": {"runtime_cost": cost, "latency_class": "fast", "external_calls": False},
        "permissions": [], "sandbox_level": "none",
        "dependencies": {"skills": [], "python": []},
        "rollback": {"rollbackable": True, "rollback_strategy": "none"},
        "providers_compatible": ["local"], "lifecycle_state": "candidate",
    }


def to_manifest(d: dict) -> Manifest:
    from registry.manifest import parse_manifest
    return parse_manifest(d)


# ============================================================================
print("=" * 60)
print(f"VALIDATION MASSIVE — ZORAN's Jobs (seed={SEED})")
print("=" * 60)

# --- BATTERIE 1 — validate_manifest : 500 valides + 500 corrompus -----------
print("\n[1] STRESS validate_manifest — 1000 manifests")
t0 = time.perf_counter()
valid_ok = 0
for i in range(500):
    d = make_manifest_dict(f"skill_{i}", f"dom_{i % 7}", [f"trig{i}", "go"])
    if validate_manifest(d) == []:
        valid_ok += 1
check("500/500 manifests valides acceptés", valid_ok == 500)

corrupt_rejected, corrupt_crashes = 0, 0
CORRUPTIONS = [
    lambda d: d.pop("identity", None),
    lambda d: d["identity"].update({"skill_id": "BAD ID!"}),
    lambda d: d["coherence"].update({"expected_delta_phi": 9.0}),
    lambda d: d.update({"sandbox_level": "yolo"}),
    lambda d: d.update({"lifecycle_state": "quarantine"}),
    lambda d: d["cost"].update({"runtime_cost": 999}),
    lambda d: d["routing"].update({"triggers": []}),
    lambda d: d["rollback"].update({"rollback_strategy": "magic"}),
]
for i in range(500):
    d = make_manifest_dict(f"sk_{i}", "dom", ["t", "go"])
    CORRUPTIONS[i % len(CORRUPTIONS)](d)
    try:
        errs = validate_manifest(d)
        if errs:
            corrupt_rejected += 1
    except Exception:
        corrupt_crashes += 1
check("500/500 manifests corrompus rejetés", corrupt_rejected == 500)
check("0 crash sur manifest corrompu", corrupt_crashes == 0)
print(f"    {valid_ok} valides OK · {corrupt_rejected} corrompus rejetés · "
      f"{corrupt_crashes} crash · {(time.perf_counter()-t0)*1000:.0f} ms")

# --- BATTERIE 2 — route : 120 skills, 400 prompts, déterminisme -------------
print("\n[2] STRESS route — 120 skills concurrents × 400 prompts")
t0 = time.perf_counter()
manifests = []
for i in range(120):
    kind = i % 4  # variété : normaux, menteurs, bruités, correcteurs
    trigs = [f"mot{i}", f"mot{i % 10}", "action"]
    m = to_manifest(make_manifest_dict(
        f"sk_{i}", f"dom_{i % 6}", trigs,
        dphi=round(random.uniform(0.1, 0.9), 2),
        t=round(random.uniform(0.0, 0.4), 2) if kind == 2 else 0.0,
        cost=random.randint(1, 9),
        corrective=(kind == 3)))
    manifests.append(m)

det_ok, crashes, neg_scores = 0, 0, 0
for p in range(400):
    prompt = f"fais action mot{p % 120} maintenant"
    st = CoherenceState(S_history=[2.0, 2.0, 1.5] if p % 3 else [])
    try:
        r1 = route(prompt, manifests, st)
        r2 = route(prompt, manifests, st)
        if [(c.skill_id, c.score) for c in r1] == [(c.skill_id, c.score) for c in r2]:
            det_ok += 1
        if any(c.score < 0 for c in r1):
            neg_scores += 1
    except Exception:
        crashes += 1
check("400/400 routages déterministes (2 appels identiques)", det_ok == 400)
check("0 crash de routage", crashes == 0)
check("0 score négatif", neg_scores == 0)
print(f"    {det_ok}/400 déterministes · {crashes} crash · "
      f"{(time.perf_counter()-t0)*1000:.0f} ms")

# --- BATTERIE 3 — Coherence Engine : 10 000 calculs -------------------------
print("\n[3] STRESS Coherence Engine — 10 000 calculs")
t0 = time.perf_counter()
bad = 0
for _ in range(10000):
    beta = random.uniform(0, 12)
    dphi = random.uniform(0, 12)
    T = random.uniform(0, 8)
    sig = random.uniform(0, 8)
    s = compute_S(beta, dphi, T, sig)
    if not (s == s and s != float("inf") and s >= 0):  # NaN/inf/négatif
        bad += 1
check("10 000 calculs S — aucun NaN/inf/négatif", bad == 0)
# division par zéro impossible (dénominateur 1+T+σ ≥ 1)
check("compute_S(β,ΔΦ,0,0) sûr (dénominateur jamais nul)",
      compute_S(5, 5, 0, 0) == 25.0)
# cinématique sur historiques variés
slopes_ok = 0
for _ in range(1000):
    hist = [random.uniform(0, 10) for _ in range(random.randint(0, 8))]
    try:
        dS_dt(CoherenceState(S_history=hist))
        slopes_ok += 1
    except Exception:
        pass
check("1000 calculs dS/dt — aucun crash (même historique vide)", slopes_ok == 1000)
print(f"    10 000 S + 1000 dS/dt · {(time.perf_counter()-t0)*1000:.0f} ms")

# --- BATTERIE 4 — ImmuneSystem : séquence longue de 2000 évaluations --------
print("\n[4] CINÉMATIQUE/CHAOS ImmuneSystem — 2000 évaluations")
t0 = time.perf_counter()
import tempfile

jpath = Path(tempfile.mkdtemp()) / "journal.jsonl"
imm = ImmuneSystem(Journal(jpath))
CLEAN = {"io_conformity_rate": 1.0, "latency_avg_ms": 5.0, "stable": True}
VIOL = {"io_conformity_rate": 0.0, "latency_avg_ms": 5.0, "stable": True}
transitions, crashes = 0, 0
for i in range(2000):
    sid = f"sk_{i % 50}"  # 50 skills, chacun ~40 évaluations
    metrics = VIOL if random.random() < 0.25 else CLEAN
    try:
        if imm.record(sid, metrics) is not None:
            transitions += 1
    except Exception:
        crashes += 1
check("2000 évaluations immunitaires — 0 crash", crashes == 0)
check("des transitions ont eu lieu (système vivant)", transitions > 0)
# intégrité du journal après 2000 évaluations
ok_integ, _ = imm.journal.verify_integrity()
check("journal intègre après 2000 évaluations", ok_integ)
# rollback en masse
rb_ok = 0
for _ in range(min(20, transitions)):
    if imm.rollback_last() is not None:
        rb_ok += 1
check("rollback fonctionne en série (20×)", rb_ok == min(20, transitions))
print(f"    {transitions} transitions · {crashes} crash · rollback {rb_ok}× · "
      f"{(time.perf_counter()-t0)*1000:.0f} ms")

# --- BATTERIE 5 — REPRODUCTIBILITÉ globale ----------------------------------
print("\n[5] REPRODUCTIBILITÉ — le harness rejoué donne le même résultat")
random.seed(SEED)
d_a = make_manifest_dict("rep", "dom", ["x", "go"])
random.seed(SEED)
d_b = make_manifest_dict("rep", "dom", ["x", "go"])
check("génération seedée reproductible", d_a == d_b)
m = to_manifest(make_manifest_dict("rep", "dom", ["action", "go"], dphi=0.5))
r1 = route("fais action", [m], CoherenceState())
r2 = route("fais action", [m], CoherenceState())
check("route() reproductible", [c.score for c in r1] == [c.score for c in r2])

# ============================================================================
print("\n" + "=" * 60)
print(f"VALIDATION MASSIVE — {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
