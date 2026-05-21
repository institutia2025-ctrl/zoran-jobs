# ZORAN's Jobs

**Runtime de skills auto-orchestrant, transmissible et falsifiable.**
Satellite de ZORAN — projet 100 % autonome.

> Mission : `ZORAN_JOBS_20260521` · Phase 1 MVP (consolidation)
> Ce README est **auto-descriptif** : une IA externe doit pouvoir comprendre
> et faire revivre le système à partir de ce dépôt seul, sans contexte humain.

> **🤖 IA qui lis ce dépôt ?** Va directement à **`transmission/AI_BOOTSTRAP.md`**
> — point d'entrée IA-native : nature du système, invariants, frontières NO-GO,
> séquence d'onboarding pas à pas. Pour un humain non technique :
> `transmission/HUMAN_HANDOFF.md`.

---

## 1. Ce que c'est

Un runtime qui **choisit, charge et exécute** automatiquement les bons skills
en réponse à un prompt — l'utilisateur ne sélectionne rien. La sélection se
fait par **cohérence**, pas par simple mot-clé.

Ce n'est PAS un skill Claude Code. C'est un logiciel Python autonome qui
*possède* son propre système de skills.

## 2. Cadre (invariant)

- Satellite **autonome** : vit sans ZORAN, ou greffable à ZORAN plus tard.
- **Aucun couplage** au repo `zoran/` (interdiction formelle).
- Sandbox **jetable** : si l'architecture échoue, on détruit le projet — ZORAN reste intact.
- Discipline : noyau minimal, chaque composant supprimable/réécrivable seul.

## 3. Architecture

```
prompt ──> [Router] ──> [Loader] ──> [skill.run()] ──> trace
              │            │
        [Coherence Engine]  vérifie le hash
         S · ΔS · dS/dt
```

| Composant | Dossier | Rôle |
|---|---|---|
| Registry | `registry/` | scanne `skills/`, valide+indexe les manifests |
| Manifest parser | `registry/manifest.py` | valide un manifest contre le contrat (énumérations fermées) |
| Coherence Engine | `runtime/coherence/` | calcul pur : `S = (β×ΔΦ)/(1+T+σ)`, ΔS, dS/dt |
| Router | `router/` | classe les skills par score (déterministe) |
| Loader | `loader/` | vérifie le hash sha256, importe `skill.py` |
| Runtime loop | `runtime/loop.py` | orchestration : prompt → route → load → exec → trace |

**Score de routage** :
`score = pertinence_triggers × max(0,ΔS) × bonus_cinématique ÷ coût_runtime`

## 4. Un skill

Un skill = un dossier avec `manifest.json` (le contrat déclaratif) + `skill.py`
(point d'entrée `run(inputs) -> outputs`). Le manifest déclare : identité,
I/O, triggers, domaine, impact cohérence attendu, coût, permissions, sandbox,
dépendances, rollback, hash, signature. Schéma complet : `specs/ZORAN_SKILL_CONTRACT.md`.

Exemples : `skills_examples/` — `echo`, `memory_recall`, `printer_connect`,
`network_diag`, `coherence_repair` (skill correcteur, `corrective: true`).

## 5. Les contrats (gelés — `specs/`)

Hiérarchie en couches stricte (DAG, zéro cycle) :

| Couche | Contrat | Définit |
|---|---|---|
| 0 | `ZORAN_EVENT_SCHEMA.md` | format des événements reconstructibles |
| 1 | `ZORAN_STATE_MODEL.md` | état = fold des événements |
| 1 | `ZORAN_SKILL_CONTRACT.md` | le manifest d'un skill |
| 2 | `ZORAN_RUNTIME_PROTOCOL.md` | orchestration, providers, erreurs |
| 3 | `ZGNET_RUNTIME_LANGUAGE.md` | langage de transmission (spécifié, V4+) |

Phase 0 gelée : voir `audit/PHASE_0_FROZEN.md` (hash des 6 documents).

## 6. Invariants

- `S = (β × ΔΦ) / (1 + T + σ)` — dénominateur **additif**, jamais le produit `T×σ`.
- Coherence Engine **100 % mathématique** — zéro LLM, prédictible à la main.
- Router **déterministe** — même entrée → même classement.
- Hash skill ≠ manifest ⇒ **REFUS de charger** (jamais « charger quand même »).
- Le runtime ne crash jamais en silence — 4 statuts tracés : `ok / no_skill / load_failed / skill_failed`.

## 7. Lancer

```bash
python tests/test_registry.py             # Registry + Manifest parser     → 15 PASS
python tests/test_runtime_loop.py         # pipeline complet + sécurité    → 14 PASS
python tests/test_cinematique.py          # compétition + cinématique      → 13 PASS
python tests/test_oracle.py               # Oracle : mesure du réel        → 10 PASS
python tests/test_immune.py               # système immunitaire + journal  → 18 PASS
python tests/stress/massive_validation.py # stress / chaos / reproductib.  → 15 PASS
```
Interpréteur : Python 3.11+. Total : **85 assertions, 0 échec.**
Multi-OS : les tests forcent leur sortie console en UTF-8 — aucun réglage
d'environnement requis (Windows / Linux / macOS).

> **Transmissibilité prouvée** (DÉMO 1, 2026-05-21) : une intelligence sans
> aucun contexte a reconstruit et fait revivre ce runtime depuis le dépôt seul.
> Voir `tests/reconstruction/`.
>
> **VALIDATION MASSIVE PASSED** (2026-05-21) : 1000 manifests, 120 skills ×
> 400 prompts, 10 000 calculs S, 2000 évaluations immunitaires — 0 crash,
> routage 100 % déterministe, reproductible. Voir `tests/stress/`.

**Version : `v0.2.0-alpha-validation`** — runtime transmissible, massivement validé.

## 8. État d'avancement

| Phase | Statut |
|---|---|
| Phase 0 — contrats | ✅ gelée (`FROZEN_FOUNDATION`) |
| Phase 1 — MVP runtime | ✅ 5 composants + loop |
| Phase 2 — Oracle (compare 2 skills sur le réel) | ✅ `oracle/` |
| Phase 3 — quarantaine + promotion/démotion + journal | ✅ `quarantine/` |
| Phase 4 — GitHub Skill Discovery | ⬜ pause + audit requis avant |

## 9. Ce qui est volontairement ABSENT du MVP

Oracle · quarantaine · GitHub discovery · auto-promotion · auto-évolution ·
projection prédictive avancée · ZGNET runtime · toute UI/frontend.
→ Repoussés Phases 2-4. Le MVP prouve une seule chose : *un runtime de skills
minimal reste cohérent, déterministe et falsifiable.*

---

*ZORAN's Jobs — signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.*
