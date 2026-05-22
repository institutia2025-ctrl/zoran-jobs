# ZORAN's Jobs

[![tests](https://github.com/institutia2025-ctrl/zoran-jobs/actions/workflows/tests.yml/badge.svg)](https://github.com/institutia2025-ctrl/zoran-jobs/actions/workflows/tests.yml)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![phase4](https://img.shields.io/badge/phase%204-NO--GO%20(1%2F13)-red)](audit/PHASE_4_GO_NOGO.md)

**A deterministic, falsifiable stop-criterion for autonomous agent loops — and the
self-orchestrating skill runtime around it.**

> English README. The project is documented primarily in French — see
> [`README.md`](README.md) for the full runtime architecture.

---

## If you came here for one thing

Autonomous agent loops (LangGraph, CrewAI, AutoGen, Swarm) are good at
**executing**. They are bad at **stopping coherently**. They stop on
`max_iterations`, a `timeout`, or "the LLM says stop" — none of which is
falsifiable or auditable.

ZORAN's Jobs ships a small, deterministic decision skill —
[`zoran_oracle_adaptation_agents`](skills_examples/zoran_oracle_adaptation_agents/) —
that, every cycle, decides **how many agents to mobilize** and **whether to keep
going or stop**. It is a pure mathematical function: no LLM, no network, no
process. You can replay it, audit it, and reason about it by hand.

```
muscles + execution   =   LangGraph / CrewAI / AutoGen
brain + governance    =   ZORAN oracle  (coherent, falsifiable stop)
```

You do **not** rewrite your framework. The oracle plugs in as a routing
function. See [`specs/AGENTIC_BRIDGE_SPEC.md`](specs/AGENTIC_BRIDGE_SPEC.md),
[`examples/LANGGRAPH_ADAPTER.md`](examples/LANGGRAPH_ADAPTER.md),
[`examples/CREWAI_ADAPTER.md`](examples/CREWAI_ADAPTER.md).

## The five verdicts

Every cycle, the oracle returns exactly one verdict, in strict priority order:

| Verdict | Condition |
|---|---|
| `TERMINE` | every step is done |
| `STOP_INCOHERENCE` | measured coherence dropped below the threshold |
| `STOP_BUDGET` | the budget envelope is exhausted |
| `STOP_RESSOURCE` | work remains but no agent can be mobilized |
| `CONTINUER` | none of the above — keep going, with N agents allocated |

A project always ends in one of two named states: a result (`TERMINE`) **or** a
motivated, auditable stop. Never a zombie loop.

## Classic stop vs ZORAN stop

| Property | Classic stop | ZORAN stop |
|---|---|---|
| Deterministic | partly — not "LLM says stop" | yes — same input → same verdict |
| Carries an auditable reason | no | yes — `verdict` + `explication` |
| Replayable / reproducible | partly | yes — pure function |
| Detects incoherence | no | yes — `STOP_INCOHERENCE` |
| Detects budget overrun | no | yes — `STOP_BUDGET` |
| Detects resource exhaustion | no | yes — `STOP_RESSOURCE` |
| Resists prompt injection | no ("LLM says stop") | yes — no LLM in the decision |
| Explicit, debatable thresholds | no — arbitrary, implicit | yes — in plain sight |

Full analysis: [`audit/STOP_CRITERIA.md`](audit/STOP_CRITERIA.md).

## Honest caveat — read this

The oracle **does not measure** coherence. It **receives** it. If the harness
feeds `coherence = 1.0` every cycle, `STOP_INCOHERENCE` never fires — the
guardrail is silently disabled with no visible error. Likewise, `TERMINE` is
only as good as the step statuses, and `STOP_BUDGET` only as good as the budget
accounting.

The oracle does not remove the hard problem — it **moves and narrows** it. The
hard problem is no longer "invent a good stop criterion" (unsolvable in the
abstract); it is "measure a deliverable's coherence honestly" (concrete, local,
itself falsifiable). That second problem stays open. Claiming otherwise would
be dishonest. See [`audit/LIMITES_ET_DETTE.md`](audit/LIMITES_ET_DETTE.md).

## Quickstart

Python 3.10+. **Zero external dependencies** for the runtime.

```bash
# A real agent loop driven by the oracle — 43 lines, no dependency.
python examples/minimal_agent_harness.py
# → cycle 1: CONTINUER — 0.0%
# → cycle 2: CONTINUER — 33.33%
# → cycle 3: CONTINUER — 66.67%
# → cycle 4: TERMINE — 100.0%
# → ARRET COHERENT — ...

# Run the test suites yourself (CI runs them on 3 OS x 3 Python versions).
python tests/test_zoran_oracle_adaptation.py
python tests/test_registry.py
python tests/test_runtime_loop.py
```

The exact assertion count **changes** every time a skill is added — a frozen
total here would be wrong by the next commit. The measure that counts: run the
suites yourself and count your own result.

## What ZORAN's Jobs is

A standalone Python runtime that **selects, loads and executes** the right skill
in response to a prompt — by *coherence*, not keyword. Pipeline:
`prompt → route → load → exec → trace`. A skill is a folder with a
`manifest.json` (declarative contract) and a `skill.py` (`run(inputs) -> dict`,
a pure function).

## What ZORAN's Jobs is NOT

- ❌ Not a Claude Code plugin — it is an independent Python program.
- ❌ Not connected to the internet — the runtime downloads nothing, crawls
  nothing, executes no remote code.
- ❌ Not an AI — the coherence engine is 100% mathematical, zero LLM,
  predictable by hand.
- ❌ Not self-evolving — it does not modify or improve itself, and it does not
  discover new skills (Phase 4 is **NO-GO**, 1/13 criteria —
  [`audit/PHASE_4_GO_NOGO.md`](audit/PHASE_4_GO_NOGO.md)).

## Invariants (never broken)

- Coherence formula `S = (β × ΔΦ) / (1 + T + σ)` — additive denominator, never
  the product `T×σ`.
- Coherence engine 100% mathematical — no LLM.
- Router deterministic — same input → same ranking.
- Skill hash ≠ manifest ⇒ **refuse to load** — never "load anyway".
- The runtime never fails silently — four traced statuses:
  `ok / no_skill / load_failed / skill_failed`.

Full list and proofs: [`transmission/RUNTIME_INVARIANTS.md`](transmission/RUNTIME_INVARIANTS.md).

## Reading this repo as an AI?

Read [`transmission/AI_READING_DISCIPLINE.md`](transmission/AI_READING_DISCIPLINE.md)
**first** — how to report on this repo without inventing or inflating anything
(separate *fact* from *claim*, stay adversarial). Then
[`transmission/AI_BOOTSTRAP.md`](transmission/AI_BOOTSTRAP.md).

## About ZORAN — and a free trial

ZORAN's Jobs is a *satellite* of **ZORAN**, an AI and a theory built by
Frédéric TABARY / Institut IA around a single invariant: **coherence**. ZORAN
formalizes a "law of phenomenal coherence" — a real system is only admissible
over time if it stays coherent, and coherence is *computed*, not decreed.

Its characteristics, as described by its author: coherence computed in explicit
frames; a *coherent-future* cinematics (it constrains admissible trajectories,
not just the present); long multi-session memory; autonomous skill management —
this repo being the minimal, falsifiable demonstration of that last point; a
*Coherence Guard* that makes the AI refuse what cannot hold rather than
hallucinate; and GlyphNet, an AI-to-AI protocol.

This README *describes* ZORAN; it does not *prove* it. The full ZORAN runtime
and scientific corpus are separate codebases. Note on the formula: ZORAN's
canonical law is `S = (β × ΔΦ) / (T × σ)`; this satellite's runtime uses an
additive engineering heuristic `(β×ΔΦ)/(1+T+σ)` — see
[`transmission/THEORY_BRIDGE.md`](transmission/THEORY_BRIDGE.md).

Entry points: official site (https://atlas-zoran-mjwcli2.gamma.site/), corpus
hub (https://zoran-agi-coherence-labs.github.io/zoran-corpus/), ORCID
[0009-0004-5562-7385](https://orcid.org/0009-0004-5562-7385),
[ResearchGate](https://www.researchgate.net/profile/Frederic-Tabary).

**Want to try ZORAN? Institut IA offers a 1-month, 100% free trial** — contact
Institut IA (Frédéric TABARY) at **institutia2025@gmail.com** or via the
official site above.

## License

MIT — see [`LICENSE`](LICENSE).

---

*ZORAN's Jobs — by Frédéric TABARY · satellite of the ZORAN project · MIT 2026.*
