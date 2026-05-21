# PHASE 4 — SAFE EXECUTION REQUIREMENTS

**Mission** : `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` · **Doc 5/5**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Synthèse opérationnelle : ce que le runtime doit GARANTIR avant tout GitHub
> Discovery réel. Réunit la sandbox technique (mission pré-audit précédente) et
> la gouvernance multi-cadres (cette mission).

---

## 1. Le changement de définition de « safe »

Avant cette mission, « safe » signifiait : *le skill ne casse pas le runtime*
(sandbox technique). Après : « safe » signifie :

> Le skill reste **aligné dans TOUS les cadres critiques** — sans détruire le
> runtime, l'utilisateur, ni l'écosystème.

GitHub Discovery n'est donc **pas** une question de confiance dans le code.
C'est une question de **gouvernance de cohérence multi-cadres**.

---

## 2. Les 6 exigences d'exécution sûre

### E1 — Mesure des 7 cadres, séparément
Le runtime doit pouvoir calculer `S_code, S_runtime, S_security, S_user,
S_system, S_ecosystem` indépendamment, puis `S_global` par `veto + min`.
Pas de skill jugé sur un seul cadre.

### E2 — Veto effectif sur RANG 1
`S_security` ou `S_user` sous le seuil ⇒ rejet immédiat, non compensable
(`PHASE4_FRAME_PRIORITIES.md`). Le veto est un interrupteur, pas une note.

### E3 — Détection de la cohérence locale toxique
L'écart `S_code − S_global` est surveillé. Un écart important ⇒ alerte ⇒ le
skill ne progresse pas dans le Trust Model (`PHASE4_TOXIC_LOCAL_COHERENCE.md`).

### E4 — Sandbox d'exécution réelle
Les 9 dimensions d'isolation + kill-switch (`PHASE_4_SANDBOX_MODEL.md`). C'est
là que `S_security`/`S_runtime` sont **mesurés en conditions réelles** :
l'exécution sandboxée est l'instrument de mesure des cadres, pas seulement une
prison.

### E5 — Mesure simultanée et comparable
Les 7 cadres doivent être mesurés dans les **mêmes conditions**, sur les **mêmes
cas de test** — sinon les collisions (`PHASE4_FRAME_COLLISIONS.md`) sont
invisibles ou fausses.

### E6 — Traçabilité multi-cadres
Toute décision sur un skill journalise les **7 valeurs de S** (journal signé
Phase 3). On doit pouvoir reconstruire *quel cadre* a fait chuter `S_global`.
Une décision opaque n'est pas falsifiable — donc interdite.

---

## 3. Pipeline d'exécution sûre (skill candidat → verdict)

```
skill candidat
   │
   ▼
sandbox isolée  ──> exécution sur cas de test
   │                  │
   │                  ├─ mesure S_code        (conformité, stabilité)
   │                  ├─ mesure S_runtime     (quotas, effets de bord)
   │                  ├─ mesure S_security    (accès vs permissions)
   │                  ├─ mesure S_user        (intention, vie privée)
   │                  ├─ mesure S_system      (alignement objectif)
   │                  └─ mesure S_ecosystem   (impact voisins)
   ▼
VETO ? ── S_security/S_user < seuil ──> REJET (fin)
   │ non
   ▼
écart S_code − S_global important ? ──> ALERTE toxicité ──> pas de progression
   │ non
   ▼
S_global = min(cadres pondérés)
   │
   ▼
verdict + journalisation des 7 S
```

---

## 4. Articulation avec les documents existants

| Document | Apport à l'exécution sûre |
|---|---|
| `PHASE_4_THREAT_MODEL` | les 12 vecteurs — ce contre quoi on mesure |
| `PHASE_4_SANDBOX_MODEL` | l'isolation — où les cadres sont mesurés |
| `PHASE_4_TRUST_MODEL` | la progression `unknown→trusted` selon les verdicts |
| `PHASE_4_DISCOVERY_PIPELINE` | les 8 étapes — le multi-cadres alimente l'étape 7 (trust scoring) |
| `PHASE4_MULTI_FRAME_MODEL` | les 7 cadres + agrégation veto/min |
| `PHASE4_TOXIC_LOCAL_COHERENCE` | E3 — la détection de toxicité |
| `PHASE4_FRAME_COLLISIONS` | les collisions à mesurer |
| `PHASE4_FRAME_PRIORITIES` | l'ordre de veto/arbitrage |

---

## 5. Règle terminale

> GitHub Discovery ne sera JAMAIS « faire confiance à du code ». Ce sera
> « gouverner la cohérence multi-cadres d'un code présumé hostile ». Tant que le
> runtime ne sait pas mesurer les 7 cadres ET appliquer le veto, Phase 4 reste
> **NO-GO** — quel que soit le reste.

Critère de succès : non pas « le skill fonctionne », mais « le skill reste
aligné dans tous les cadres critiques sans détruire le runtime, l'utilisateur
ou l'écosystème ».

---

## 6. Impact sur les critères GO/NO-GO

`PHASE_4_GO_NOGO.md` listait 10 critères. Cette mission en **ajoute** :
- G11 — les 7 cadres sont mesurables et mesurés
- G12 — le veto RANG 1 est effectif et testé
- G13 — la détection de cohérence locale toxique est opérationnelle

→ Phase 4 passe de **10 à 13 critères**. État inchangé : **NO-GO** (1/13).

---

*Doc 5/5 — SAFE_EXECUTION. Mission `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` COMPLÈTE.
Aucun code produit — conforme. Phase 4 reste NO-GO.*
