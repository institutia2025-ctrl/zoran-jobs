# META_ORCHESTRATOR_SPEC — Orchestrateur de cohérence distribuée

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code (invariants en cours de stabilisation)
**Signé** : Claude Code, prestataire · **Livrable 1/8**

> Spec fondatrice. Définit l'orchestrateur, les rôles IA, les scopes, ce que
> chaque IA reçoit, et l'arbitrage des conflits. Aucun code ne s'écrit tant que
> les invariants de cette spec ne sont pas gelés.

---

## 1. Le problème — énoncé exact

Le problème n'est **pas** « faire parler plusieurs IA ». C'est :

> **empêcher plusieurs IA de dériver ensemble.**

Une dérive conjointe survient quand chaque IA est *localement* cohérente mais que
l'ensemble diverge. Ce n'est pas théorique : la conception même de ce dépôt l'a
produit (cf. `audit/INTER_AGENT_CONFLICTS.md`) — deux IA en parallèle sur des
états de dépôt divergents, du travail « livré » jamais poussé, des bases
obsolètes. Le Meta Orchestrator existe pour rendre cette dérive **impossible
par construction, ou détectée immédiatement**.

## 2. Principe central — compression cognitive distribuée

Le noyau ne transmet **jamais** le contexte complet. Il transmet **uniquement le
minimum cohérent utile**. Chaque IA spécialisée reçoit exactement :

- sa **mission** (1 énoncé),
- ses **invariants** (ce qu'elle ne doit jamais casser),
- ses **NO-GO** (frontières),
- ses **skills utiles** (et eux seuls),
- son **budget token** (cf. `TOKEN_BUDGET_MODEL.md`).

Rien d'autre. Pas le contexte des autres IA, pas les cadres qui ne la concernent
pas, pas l'historique global.

## 3. Architecture cible

```
        META ORCHESTRATOR        ← détient la cohérence globale, jamais le détail
              │
        Frame Router             ← distribue les bons cadres (FRAME_ROUTER_SPEC.md)
              │
        IA spécialisées          ← reçoivent un scope minimal, disjoint
              │
        ZORAN Jobs distribués    ← skills routés par IA (ZORAN_JOBS_DISTRIBUTION.md)
              │
        Global Veto              ← refuse toute solution incohérente globalement
```

Le flux descendant transmet du **scope minimal** ; le flux remontant transmet
des **deltas** (`DELTA_TRANSMISSION_PROTOCOL.md`), jamais du contexte massif.

## 4. Rôles IA — scopes disjoints

| Rôle | Reçoit | Ne reçoit PAS |
|---|---|---|
| IA Backend | runtime, providers, infra, tests, rollback | UI, design |
| IA UX | layers, vocal, zero-friction, mobile | sécurité runtime |
| IA Sécurité | sandbox, veto, trust model, threat model | design UI, planning |
| IA Code | invariants, contrats, topologie | exécution métier |
| IA Métier | mission métier, skills du domaine, NO-GO | infra, sécurité runtime |

**Invariant MO-1 — scopes disjoints** : deux IA ne partagent jamais le même
scope intégral. Le recouvrement est réduit au strict point de contact, géré par
l'orchestrateur. (Discipline déjà appliquée dans ce dépôt : préfixes de skills
disjoints, branches séparées, fichiers de tests distincts.)

## 5. Ce que l'orchestrateur garde pour lui

L'orchestrateur est le **seul** à détenir la vue globale. Il ne la diffuse pas.
Il détient : la carte des rôles, les budgets, le journal inter-IA, l'état du
veto global. Une IA omnisciente est **interdite** (NO-GO ci-dessous) : elle
recréerait le bruit que l'architecture supprime.

## 6. Arbitrage des conflits

Quand deux IA produisent des sorties incompatibles (cf.
`audit/INTER_AGENT_CONFLICTS.md`), l'orchestrateur arbitre **sans négociation
inter-IA** (interdite — produit du bavardage et de la dérive) :

1. Chaque sortie est évaluée en **cohérence multi-cadres** (V2 :
   `coherence_multi_frame`).
2. Le **Global Veto** s'applique d'abord (`GLOBAL_VETO_RUNTIME.md`) : toute
   sortie à `S_securite` ou `S_global` sous seuil est éliminée *avant* tout
   classement.
3. Parmi les survivantes, l'orchestrateur retient celle de `S_global` maximal,
   `S_global = Σ(weight_i × S_i)` — agrégation par **veto + min**, jamais par
   moyenne (héritée de `PHASE4_FRAME_PRIORITIES.md`).
4. La décision est **journalisée** (cadre, budget consommé, veto déclenché).

## 7. NO-GO

- ❌ Aucune IA omnisciente (recrée le bruit, la duplication cognitive).
- ❌ Aucun bavardage inter-IA (négociation directe = canal de dérive).
- ❌ Aucune transmission de contexte massif (viole le principe §2).
- ❌ Aucune mission sans NO-GO explicite attaché.
- ❌ Aucune dérive locale non détectée (toute sortie passe le Global Veto).
- ❌ Aucun code tant que cette spec et les 7 autres ne sont pas gelées.

## 8. Traçabilité obligatoire

Chaque cycle d'orchestration journalise : `mission_id`, timestamp, cadres
utilisés, budgets token (alloué / consommé), veto déclenchés, conflits détectés,
rollback conceptuel proposé, limites explicites. Append-only signé — même
discipline que `quarantine/journal.py`.

## 9. Critère de succès

Le succès n'est **pas** « beaucoup d'IA qui parlent ». C'est :

> **plusieurs IA qui restent alignées, à coût cognitif minimal.**

Le système ne cherche pas la puissance brute — il cherche la **cohérence
distribuée à coût minimal**.

---

*Livrable 1/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
