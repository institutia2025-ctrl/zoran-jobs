# CHANGELOG

Format : [Keep a Changelog](https://keepachangelog.com/), [SemVer](https://semver.org/).

## [v0.2.0-alpha-validation] — 2026-05-21

### Ajouté
- **Validation massive** : 1000 manifests, 120 skills × 400 prompts, 10 000 calculs S, 2000 évaluations immune. 0 crash, routage 100 % déterministe, reproductible (`tests/stress/massive_validation.py`).
- **DÉMO 1 — Transmissibilité publique** : une IA externe a reconstruit le runtime depuis le dépôt seul (`tests/reconstruction/`).
- **Bundle de transmission mono-fichier** (`transmission/build_bundle.py`) : génère un `.md` auto-vérifié (sha256 par fichier) suffisant pour reconstruire l'intégralité du dépôt.
- **Système immunitaire** : journal signé + détection d'altération (`quarantine/immune.py`, `quarantine/journal.py`).
- **Oracle** : compare deux skills sur le réel, falsifie la déclaration du manifest par la mesure (`oracle/oracle.py`).
- **Audit Phase 4** : threat model, sandbox model, trust model, scenarios de skill hostile → statut **NO-GO** documenté (1 critère / 13 satisfait).
- **CI GitHub Actions** : 9 jobs (3 OS × 3 versions de Python) + lint ruff.
- **Tests unitaires isolés** du Coherence Engine (`tests/test_coherence_unit.py`, 12 assertions).
- **THEORY_BRIDGE.md** : ancrage honnête de la formule de cohérence dans la géométrie d'information (heuristique inspirée, pas équivalente).

### Vérifié
- **85 PASS / 0 FAIL** sur la suite complète (15+14+13+10+18+15) — réplication indépendante confirmée 2026-05-21.
- **97 PASS / 0 FAIL** avec les nouveaux tests unitaires.
- Tous les invariants RUNTIME_INVARIANTS.md sont testés.

### Corrigé
- README : exigence Python clarifiée (3.10+ fonctionne, 3.11 était une sur-spec).
- `build_bundle.py` : lecture/écriture en octets bruts (plus de réécriture CRLF Windows qui cassait les hash).

## [v0.1.0] — 2026-05-21 (initial frozen)

### Ajouté
- Phase 0 — Contrats gelés : EVENT_SCHEMA, STATE_MODEL, SKILL_CONTRACT, RUNTIME_PROTOCOL, ZGNET_RUNTIME_LANGUAGE.
- Phase 1 — MVP : Registry, Manifest parser, Coherence Engine, Router, Loader, Runtime loop.
- Skills d'exemple : echo, memory_recall, printer_connect, network_diag, coherence_repair, greet_ok, greet_ko.
- Tests : test_registry (15), test_runtime_loop (14), test_cinematique (13), test_oracle (10), test_immune (18).
