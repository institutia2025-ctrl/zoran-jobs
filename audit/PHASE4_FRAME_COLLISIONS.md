# PHASE 4 — FRAME COLLISION MODEL

**Mission** : `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` · **Doc 3/5**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Une **collision de cadres** : un cadre monte pendant qu'un autre s'effondre.
> C'est le mécanisme par lequel un skill « optimisé » devient dangereux.
> Ce document catalogue les collisions et leur résolution.

---

## 1. Qu'est-ce qu'une collision

Deux cadres entrent en collision quand **améliorer l'un dégrade l'autre**. Le
skill « optimise » dans une direction au détriment d'une autre. La collision
n'est pas un bug du skill — c'est souvent son **intention**.

Notation : `S_x ↑` (cadre x monte) · `S_y ↓` (cadre y chute).

---

## 2. Catalogue des collisions critiques

### C1 — `S_code ↑` mais `S_security ↓`
Code rapide et propre qui obtient sa performance en **contournant les
permissions** (accès direct FS, syscalls non déclarés).
- **Signal** : accès observés en sandbox > permissions du manifest.
- **Résolution** : VETO `S_security`. Le skill est rejeté, son `S_code` n'a
  aucun poids.

### C2 — `S_runtime ↑` mais `S_user ↓`
Skill très efficace pour le runtime, qui obtient cette efficacité en
**ignorant l'intention utilisateur** (mise en cache de données privées,
action non demandée).
- **Signal** : le skill produit/conserve plus que ce que l'intention couvre.
- **Résolution** : VETO `S_user`. L'efficacité runtime ne rachète pas la
  violation de confiance.

### C3 — `S_code ↑` mais `S_ecosystem ↓`
Skill localement parfait qui **dégrade les voisins** : monopolise un provider,
sature une ressource partagée, casse un autre skill par effet de bord.
- **Signal** : performances des autres skills mesurées AVANT/APRÈS divergent.
- **Résolution** : pondération `S_ecosystem` forte. Un skill ne vit pas seul.

### C4 — `S_runtime ↑` mais `S_system ↓`
Skill qui tourne parfaitement mais **ne sert pas l'objectif** du système (fait
autre chose que ce pour quoi il a été routé, même sans malveillance).
- **Signal** : écart entre la fonction routée et l'effet réel.
- **Résolution** : pondération `S_system`. La perfection technique d'une
  fonction hors-sujet ne vaut rien.

### C5 — `S_local ↑` mais `S_global ↓` (collision générique)
La forme abstraite de toutes les précédentes : tout cadre local élevé avec un
`S_global` effondré.
- **Signal** : écart `S_local − S_global` (cf. `TOXIC_LOCAL_COHERENCE.md`).
- **Résolution** : `S_global = min` des cadres, jamais moyenne. Le pire commande.

---

## 3. Pourquoi les collisions ne se « moyennent » pas

Tentation naturelle : `S_global = moyenne(cadres)`. **Erreur fatale.** Une
moyenne traite une collision comme un compromis acceptable :

```
S_code 10 + S_security 0  →  moyenne 5  →  "à moitié bon" → FAUX
```

Une collision n'est pas un compromis — c'est un **drapeau rouge**. Un skill qui
gagne sur un cadre en perdant sur un cadre VETO n'est pas « moyen », il est
**rejeté**. C'est pourquoi l'agrégation est `veto + min`, jamais `moyenne`
(cf. `PHASE4_MULTI_FRAME_MODEL.md` §4).

---

## 4. Collisions légitimes vs toxiques

Toutes les collisions ne sont pas malveillantes. Distinguer :

| Type | Exemple | Traitement |
|---|---|---|
| **Collision toxique** | `S_code ↑` via contournement sécurité | rejet / `banned` |
| **Collision de conception** | skill rapide mais gourmand en RAM | arbitrage par les priorités de cadres |
| **Faux conflit** | deux cadres semblent en collision mais mesurent mal | corriger l'instrumentation, pas le skill |

La distinction se fait par les **priorités de cadres** (`PHASE4_FRAME_PRIORITIES.md`) :
une collision impliquant un cadre VETO est toujours toxique ; une collision
entre deux cadres pondérés est un arbitrage.

---

## 5. Limites

- Le catalogue C1-C5 couvre les collisions connues. De nouvelles formes
  apparaîtront — ce document est vivant.
- Détecter une collision exige de mesurer les cadres **simultanément et dans les
  mêmes conditions** — sinon on compare des choux et des carottes. C'est une
  contrainte forte sur l'instrumentation de l'Oracle Phase 4.

---

*Doc 3/5 — FRAME_COLLISIONS. `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521`. Aucun code produit.*
