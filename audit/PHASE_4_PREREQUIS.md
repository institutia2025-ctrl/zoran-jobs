# PHASE 4 — PRÉREQUIS (réflexion hors-code)

**Mission** : `ZORAN_JOBS_20260521`
**Statut** : ⏸️ Phase 4 NON démarrée — document de réflexion, aucun code
**Source** : recommandations ZORAN (2026-05-21T04:21 et T04:39)
**Signé** : Claude, prestataire, 2026-05-21

---

## 1. Pourquoi Phase 4 est en pause

Phases 1-3 géraient des **skills contrôlés** : écrits, signés, audités en interne.
La topologie est saine, le runtime jetable, 70 tests verts, un clone froid existe.

Phase 4 (GitHub Skill Discovery) introduit **du code externe potentiellement
hostile et chaotique**. Ce n'est plus un sujet d'architecture runtime — c'est un
sujet **sécurité / gouvernance / sandboxing**. Changement de catégorie entière.

Démarrer Phase 4 sans préparation = transformer un runtime propre en système
incontrôlable. D'où la pause.

---

## 2. Les 6 prérequis avant TOUTE ligne de code Phase 4

### 1 — Sandbox d'exécution FORTE
Le Loader actuel fait un simple `import` Python — suffisant pour des skills de
confiance, **inacceptable** pour du code externe. Il faut un **vrai isolement** :
sous-processus isolé, conteneur, ou interpréteur restreint. Un skill GitHub ne
doit jamais pouvoir toucher le runtime hôte.

### 2 — Signatures obligatoires
Tout skill externe doit être **signé et vérifié** avant le moindre chargement.
Pas de signature valide ⇒ rejet immédiat, jamais d'exécution.

### 3 — Quarantaine renforcée
La quarantaine Phase 3 (3 violations io → désactivation) est minimale. Pour du
code externe il faut une quarantaine **bien plus sérieuse** : tout skill GitHub
entre d'abord en quarantaine, subit tests + benchmark + observation, et n'est
promu qu'après preuve de comportement sain.

### 4 — Permissions très fines
Chaque skill déclare déjà des `permissions`. Pour Phase 4 il faut les **faire
respecter réellement** : un skill ne peut accéder qu'à ce qu'il a déclaré, et
le runtime le contraint (pas seulement le déclare).

### 5 — Runtime limits
Plafonds durs et appliqués : **CPU, RAM, temps d'exécution, I/O, réseau**. Un
skill externe qui dépasse une limite est tué, pas négocié.

### 6 — Skill Trust Model
GitHub ne garantit rien. Il faut un **modèle de confiance explicite** : niveaux
de confiance, provenance, réputation, historique de quarantaine — qui décide
si un skill externe a le droit de passer `quarantine → candidate → active`.

---

## 3. Pipeline Phase 4 (rappel mission, à ne PAS court-circuiter)

```
GitHub → analyse → quarantaine → tests → benchmark → sandbox → promotion éventuelle
```
Aucun skill GitHub n'est jamais exécuté directement. Jamais.

---

## 4. Critère de déclenchement de Phase 4

Phase 4 ne démarre QUE si les 4 conditions sont réunies :
1. GO explicite de Fred
2. Les 6 prérequis ci-dessus sont conçus (au moins en spec)
3. Un audit de sécurité dédié a été produit
4. Le clone froid Phase 3 est intact (point de retour garanti)

Si une seule condition manque → Phase 4 attend.

---

## 5. État de départ pour la reprise

Quand la réflexion reprendra, le point fixe est :
`zoran-jobs_CLONE-FROID_phase3_20260521.zip` — runtime Phases 1-3, 70 tests
verts, topologie auditée. Tout repart de là.

---

*Document de réflexion — aucun code. Phase 4 reste fermée.
Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.*
