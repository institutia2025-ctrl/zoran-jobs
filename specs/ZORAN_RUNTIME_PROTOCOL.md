# ZORAN_RUNTIME_PROTOCOL

**Mission** : `ZORAN_JOBS_20260521` · **Spec 4/5** · **Date** : 2026-05-21
**Statut** : Phase 0 — contrat invariant · **Priorité** : 4
**Couche de dépendance** : **2** — orchestrateur. Référence les couches 0-1 (event/state/skill). C'est voulu : il n'existe qu'UN seul orchestrateur, et il est le seul à avoir le droit de référencer vers le bas.

> Discipline : le runtime est un **petit noyau**. Il orchestre, il ne fait pas.
> Tout comportement est explicite, tracé, reconstructible.

---

## 1. Rôle du runtime

Le runtime est le **chef d'orchestre minimal**. Il ne contient aucune logique
métier — celle-ci vit dans les skills. Le runtime :
1. reçoit une requête,
2. mesure la cohérence,
3. fait router → charger → exécuter,
4. mesure le ΔS réel,
5. trace tout, gère les erreurs.

---

## 2. Cycle de vie d'une requête

```
1. request_received
       │   émet l'événement, crée trace_id
       ▼
2. MESURE COHÉRENCE (avant)
       │   coherence engine → S_avant, dS/dt, projection
       │   émet coherence_measured
       ▼
3. ROUTER
       │   pour chaque skill candidat :
       │     skill_score = pertinence × cohérence_phénoménale
       │                   × bonus_cinématique × bonus_projection ÷ coût
       │   émet skill_candidates_ranked, puis skill_selected
       ▼
4. LOADER
       │   vérifie hash == manifest.hash  (sinon REFUS → skill_failed + log)
       │   vérifie permissions, sandbox_level
       │   émet skill_loaded
       ▼
5. EXÉCUTION (dans le sandbox du niveau déclaré)
       │   valide inputs (JSON Schema), exécute run(), valide outputs
       │   émet skill_executed  ou  skill_failed
       ▼
6. MESURE COHÉRENCE (après)
       │   S_après, ΔS_mesuré = S_après − S_avant
       │   émet coherence_delta  → alimente S_history et le ranking
       ▼
7. retour idle
```

Chaque étape émet ≥ 1 événement (spec 2). Le `trace_id` les corrèle.

---

## 3. Providers

Un **provider** = un environnement d'exécution d'un skill.

| Provider MVP | Description |
|---|---|
| `local` | exécution Python locale (process courant ou subprocess sandboxé) |
| `zoran` | **réservé** — interface d'amarrage future à ZORAN. Déclarée, non implémentée. |

Abstraction obligatoire : le runtime appelle `provider.execute(skill, inputs)`.
Ajouter un provider = implémenter cette interface, **sans toucher au noyau**.
C'est ce qui rend le runtime portable (transmissibilité).

**Dépendance unidirectionnelle (anti-cycle)** : le kernel appelle
`provider.execute()` ; un provider n'appelle JAMAIS le kernel. `kernel` et
`providers` sont des composants *définis par ce protocole* — pas des modules
mutuellement dépendants. Le sens de dépendance est strict : `kernel → provider`.

---

## 4. Gestion des erreurs — dégradation graceful

| Situation | Réaction | Jamais |
|---|---|---|
| Hash skill ≠ manifest | refus de charger → `skill_failed` + log | ❌ charger quand même |
| Skill échoue à l'exécution | `skill_failed` + rollback si `rollback_id` | ❌ crash silencieux |
| Inputs/outputs invalides (schéma) | refus + `skill_failed` | ❌ exécuter avec données floues |
| Aucun skill pertinent trouvé | réponse honnête « aucune capacité » | ❌ inventer / forcer un skill |
| Cohérence s'effondre (`dS/dt` très négatif) | bascule `degraded`, attend rollback | ❌ continuer la dérive |

**Principe** : le runtime ne ment jamais, n'invente jamais, ne crash jamais en
silence. En cas de doute → `degraded` + trace + attente.

---

## 5. Lifecycle du runtime

```
boot ──> reconstruire l'état (fold events.jsonl) ──> idle
idle ──> [cycle requête §2] ──> idle
idle ──> shutdown (flush events, snapshot final)
n'importe quel état ──> degraded (sur erreur) ──> idle (après rollback)
```

Au **boot** : le runtime rejoue `events.jsonl`, reconstruit `S_history` et l'état.
Aucune perte de cohérence après redémarrage.

---

## 6. Le noyau reste petit

Ce que le runtime fait : orchestrer, mesurer la cohérence, tracer, gérer erreurs.
Ce que le runtime NE fait PAS : logique métier (→ skills), routage intelligent
(→ router), évaluation (→ oracle), isolation (→ sandbox).

Règle : si une fonctionnalité peut vivre dans un skill ou un composant, elle
**n'entre pas dans le noyau**. Plus le système devient auto-orchestrant, plus le
noyau doit rester réduit et gouvernable.

---

## 7. Hors-scope MVP

- Orchestration multi-skills parallèle — MVP = un skill à la fois
- Provider distant / réseau — MVP = `local` uniquement
- Auto-réinstanciation — Phase transmissibilité ultérieure

---

*Spec 4/5 — RUNTIME_PROTOCOL. Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.
Prochain : ZGNET (spécification minimaliste).*
