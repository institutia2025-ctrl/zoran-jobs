# TOKEN_BUDGET_MODEL — Modèle de budget cognitif

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code
**Signé** : Claude Code, prestataire · **Livrable 3/8**

> Le coût token est un budget, pas une externalité. Ce modèle le rend explicite,
> alloué, mesuré, et opposable — comme un coût `runtime_cost` de skill.

---

## 1. Pourquoi un budget

Sans budget, chaque IA tend à demander « tout le contexte, par sécurité ». Le
coût croît en `O(n²)` avec le nombre d'IA (chacune voit tout le monde). Le
budget inverse la logique : une IA reçoit un **plafond**, et doit tenir sa
mission dedans. La rareté force la compression.

## 2. Unités de budget

Le budget se découpe en quatre postes mesurables :

| Poste | Définition | Vise à limiter |
|---|---|---|
| `budget_scope` | tokens du scope initial transmis à l'IA | le contexte d'entrée |
| `budget_delta` | tokens des deltas échangés en cours de mission | les allers-retours |
| `budget_rollback` | tokens d'un retour arrière conceptuel | le coût de l'erreur |
| `budget_orchestration` | tokens consommés par l'orchestrateur lui-même | le méta-coût |

`budget_total_IA = budget_scope + budget_delta + budget_rollback`.
`budget_mission = Σ(budget_total_IA) + budget_orchestration`.

## 3. Règles d'allocation

**Invariant TB-1 — plafond dur** : une IA qui atteint son `budget_total_IA`
n'obtient pas d'extension automatique. Elle rend un **delta partiel + état**, et
l'orchestrateur décide (rallonge tracée, ou re-découpage de la mission).

**Invariant TB-2 — le scope domine le budget** : `budget_scope` doit être le
plus petit poste. Si le scope coûte plus que le travail, le découpage des rôles
est mauvais (cf. `META_ORCHESTRATOR_SPEC.md` §4).

**Invariant TB-3 — delta ≪ scope** : le coût cumulé des deltas d'une mission
doit rester inférieur au `budget_scope`. Au-delà, on retransmet du contexte
déguisé en delta — anti-pattern (cf. `DELTA_TRANSMISSION_PROTOCOL.md`).

**Invariant TB-4 — rollback budgété d'avance** : `budget_rollback` est réservé
avant le démarrage. Une mission sans budget de rollback est un NO-GO : on ne
démarre pas un travail qu'on ne peut pas défaire à coût connu.

## 4. Coût d'une erreur

Une dérive détectée tard coûte : le travail dérivé + le rollback + la
re-transmission. Le modèle rend ce coût visible *avant* : si
`budget_rollback` d'une mission est élevé, c'est un signal que la mission est
mal bornée — la re-découper coûte moins que la subir.

## 5. Mesure et traçabilité

Chaque mission journalise, par IA : `budget_*` alloué, consommé, dépassements,
ratio `delta/scope`. Un tableau de bord déterministe (pas une estimation IA)
agrège le `budget_mission`. La mesure est falsifiable : on compte des tokens,
on ne les devine pas.

## 6. Lien avec l'existant

Le champ `cost.runtime_cost` du contrat de skill (entier 1..10) est l'ancêtre
de ce modèle, à l'échelle d'un skill. `TOKEN_BUDGET_MODEL` l'étend à l'échelle
d'une IA et d'une mission. Même esprit : le coût est déclaré, borné, vérifié.

---

*Livrable 3/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
