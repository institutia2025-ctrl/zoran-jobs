# GLOBAL_VETO_RUNTIME — Veto de cohérence globale

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code
**Signé** : Claude Code, prestataire · **Livrable 4/8**

> Le Global Veto empêche une solution **localement excellente** de détruire la
> **cohérence globale**. C'est un filtre dur, appliqué avant tout classement.

---

## 1. Le cas à empêcher

```
S_backend  = 10   (solution backend brillante)
S_securite = 0    (elle détruit la sécurité)
→ REFUS GLOBAL.
```

Une moyenne dirait `S = 5` — « acceptable ». C'est faux et dangereux. La
cohérence n'est pas une moyenne : un cadre effondré effondre l'ensemble. Le
Global Veto formalise cela.

## 2. Règle d'agrégation — veto + min, jamais la moyenne

Reprend et généralise `PHASE4_MULTI_FRAME_MODEL.md` et
`PHASE4_FRAME_PRIORITIES.md` :

1. **Veto dur** : si un cadre *à veto* (`securite`, et tout cadre déclaré
   critique pour la mission) a `S_cadre < seuil_veto`, la solution est
   **éliminée** — pas pénalisée, éliminée. Seuil par défaut : `0.15` (déjà
   utilisé par le veto V2, `ZORAN_SKILL_CONTRACT_V2.md` §2.3).
2. **Plancher (min)** : parmi les solutions non vétotées, aucune n'est retenue
   si son cadre le plus faible est sous le plancher de mission.
3. **Classement** : seulement ensuite, `S_global = Σ(weight_i × S_i)` départage.

L'ordre est non négociable : **veto → min → classement**. Inverser, c'est
laisser une moyenne masquer un effondrement.

## 3. Invariants

**Invariant GV-1 — antériorité du veto** : le veto s'applique *avant* tout
calcul de score global. Une solution vétotée ne paraît jamais dans le
classement (déjà le comportement de `_veto_securite` au niveau skill).

**Invariant GV-2 — INV-1 préservé par cadre** : chaque `S_cadre` suit
`S = (β·ΔΦ)/(1 + T + σ)` — dénominateur additif, jamais `T×σ`. Le veto ne
contourne pas la formule, il l'applique cadre par cadre (INV-11 du contrat V2).

**Invariant GV-3 — déterminisme** : `veto_global(solution, état)` appelé deux
fois sur des entrées identiques renvoie le même verdict (INV-12).

**Invariant GV-4 — veto traçable** : tout veto déclenché est journalisé avec le
cadre fautif, son `S`, le seuil, et la solution éliminée. Un veto silencieux est
interdit.

## 4. Portée — local vs global

| Niveau | Mécanisme | Déjà existant |
|---|---|---|
| Skill | `veto_capable` + cadre `securite` | ✅ contrat V2 |
| IA | sortie d'une IA vétotée si un cadre s'effondre | spec (ce document) |
| Orchestration | mission entière refusée si `S_global` non atteignable | spec (ce document) |

Le Global Veto est la **remontée** du veto de skill au niveau de l'orchestrateur :
même principe, échelle supérieure.

## 5. Anti-pattern interdit

> « Le backend est à 10, la sécurité à 2, en moyenne 6, on garde. »

Interdit. C'est précisément la dérive que la mission proscrit : une excellence
locale qui achète sa survie en sacrifiant un cadre. Le Global Veto rend ce
marché impossible.

## 6. Traçabilité

Journalise : `mission_id`, solution évaluée, `S` par cadre, cadre(s) sous seuil,
seuil appliqué, verdict (`ACCEPTÉ` / `VÉTO`), limites explicites.

---

*Livrable 4/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
