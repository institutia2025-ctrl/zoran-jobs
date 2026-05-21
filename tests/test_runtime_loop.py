"""
tests/test_runtime_loop.py — Test d'intégration du runtime MVP.

Mission : ZORAN_JOBS_20260521 · Phase 1 MVP
Signé : Claude, prestataire, 2026-05-21

Répond à LA question de ZORAN : « est-ce que le système charge réellement
le bon skill de manière stable ? » + vérifie que le Coherence Engine est
prédictible à la main (falsifiabilité).

Exécutable directement : `python tests/test_runtime_loop.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# FIX-DEF-1 2026-05-21 : sortie console UTF-8 — portabilité multi-OS.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from loader import Loader  # noqa: E402
from registry import Registry  # noqa: E402
from router import route  # noqa: E402
from runtime.coherence.engine import (  # noqa: E402
    CoherenceState,
    compute_S,
    delta_S,
    dS_dt,
)
from runtime.loop import run_once  # noqa: E402

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


print("=== TEST 1 — Coherence Engine : prédictible à la main (falsifiabilité) ===")
# S = (β×ΔΦ)/(1+T+σ) = (2×3)/(1+1+1) = 6/3 = 2.0
check("compute_S(2,3,1,1) == 2.0", compute_S(2.0, 3.0, 1.0, 1.0) == 2.0)
# état vide → S = 0
st = CoherenceState()
# skill {ΔΦ+0.5} → candidate_S = (1×0.5)/1 = 0.5 ; ΔS = 0.5 − 0 = 0.5
check("delta_S(+0.5 ΔΦ) == 0.5", delta_S(st, {"expected_delta_phi": 0.5}) == 0.5)
# cinématique : S_history [1,2,3] → pente (3−1)/2 = 1.0
st2 = CoherenceState(S_history=[1.0, 2.0, 3.0])
check("dS_dt([1,2,3]) == 1.0", dS_dt(st2) == 1.0)
# trajectoire descendante
st3 = CoherenceState(S_history=[5.0, 3.0, 1.0])
check("dS_dt([5,3,1]) == -2.0", dS_dt(st3) == -2.0)

print()
print("=== TEST 2 — Pipeline complet : charge-t-il le BON skill ? ===")
reg = Registry()
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()
state = CoherenceState()
trace = run_once("fais un echo de ce texte", {"text": "bonjour ZORAN"}, reg, loader, state)
check("status == ok", trace.get("status") == "ok")
check("skill sélectionné == echo", trace.get("selected") == "echo")
check("outputs == {echo: 'bonjour ZORAN'}", trace.get("outputs") == {"echo": "bonjour ZORAN"})
check("echo est chargé dans le Loader", loader.is_loaded("echo"))

print()
print("=== TEST 3 — Déterminisme du Router (même entrée → même classement) ===")
m = reg.all_manifests()
r1 = route("echo test", m, CoherenceState())
r2 = route("echo test", m, CoherenceState())
check("route() déterministe (2 appels identiques)",
      [(c.skill_id, c.score) for c in r1] == [(c.skill_id, c.score) for c in r2])
check("prompt sans trigger → 0 skill routé", route("xyzzy plugh", m, CoherenceState()) == [])

print()
print("=== TEST 4 — Sécurité : hash corrompu ⇒ REFUS de charger ===")
echo_manifest = reg.get("echo")
original_hash = echo_manifest.hash
echo_manifest.hash = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
loader2 = Loader()
mod, err = loader2.load(echo_manifest)
check("hash corrompu → module None", mod is None)
check("hash corrompu → erreur explicite 'mismatch'", "mismatch" in err)
check("hash corrompu → skill NON chargé", not loader2.is_loaded("echo"))
echo_manifest.hash = original_hash  # restaure
# le runtime loop doit reporter load_failed proprement (pas de crash)
echo_manifest.hash = "sha256:deadbeef"
trace_bad = run_once("echo", {"text": "x"}, reg, Loader(), CoherenceState())
check("runtime loop : hash KO → status load_failed (pas de crash)",
      trace_bad.get("status") == "load_failed")
echo_manifest.hash = original_hash

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
