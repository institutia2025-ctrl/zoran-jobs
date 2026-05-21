# PHASE 4 — SKILL TRUST MODEL

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 3/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> GitHub ne garantit RIEN. La confiance ne se déclare pas — elle **se gagne par
> la preuve**, étape par étape. Ce document définit les niveaux et les passages.

---

## 1. Les 5 niveaux de confiance

| Niveau | Définition | Droits |
|---|---|---|
| `banned` | skill jugé hostile (échec sandbox, code malveillant avéré) | **aucun** — bloqué définitivement, hash mémorisé |
| `unknown` | skill juste découvert sur GitHub, jamais évalué | aucun — ne peut PAS s'exécuter hors sandbox de test |
| `quarantined` | skill en cours d'évaluation OU ayant échoué une règle réversible | exécution **sandbox de test uniquement** |
| `verified` | a passé scans + tests sandbox + benchmark, sans incident | exécution sandbox, **pas encore** routable en production |
| `trusted` | `verified` + observation prolongée + promotion **manuelle** | routable comme un skill interne |

---

## 2. La règle absolue

```
Aucun skill ne passe  unknown ──> active/trusted  directement.  JAMAIS.
```

Le seul chemin légal est **monotone et progressif** :

```
unknown ──> quarantined ──> verified ──> trusted
              │                │
              └── banned       └── retour quarantined si incident
```

Chaque flèche = un franchissement qui exige une **preuve mesurée** (voir
`DISCOVERY_PIPELINE`). On ne saute jamais une étape.

---

## 3. Conditions de passage

| Transition | Condition |
|---|---|
| `unknown → quarantined` | metadata analysée, static scan + dependency scan passés (rien de bloquant) |
| `quarantined → verified` | tests sandbox OK + benchmark OK + 0 violation io + respect des quotas |
| `verified → trusted` | observation prolongée sans incident + **décision manuelle d'un humain** |
| `* → banned` | code malveillant avéré, évasion de sandbox, ou auto-mutation détectée |
| `verified/trusted → quarantined` | toute violation io / dépassement quota / comportement anormal → **rétrogradation immédiate** |

**La rétrogradation est toujours automatique et immédiate. La promotion est
toujours lente et, pour `trusted`, manuelle.** Asymétrie volontaire : il est
facile de perdre la confiance, lent de la gagner.

---

## 4. Articulation avec le système immunitaire Phase 3

Le `quarantine/immune.py` actuel gère déjà `candidate/active/quarantine` pour
des skills internes. Phase 4 **n'écrase pas** ce système — il l'**englobe** :

- les niveaux Phase 4 (`unknown/quarantined/verified/trusted/banned`)
  s'appliquent aux skills **externes** ;
- un skill externe `trusted` rejoint le cycle interne `candidate→active` ;
- `banned` est un état terminal **nouveau** — irréversible, hash blacklisté.

→ Le trust model est une **couche amont** ; le système immunitaire reste la
couche runtime. Les deux journalisent (journal signé Phase 3).

---

## 5. Mémoire de défiance

Un skill `banned` ne doit **jamais pouvoir revenir** sous un autre nom :
- le **hash** du code banni est conservé dans une liste noire persistante ;
- un skill dont le hash matche un hash banni → `banned` d'office, sans ré-évaluation ;
- protège contre T4 (fork piégé re-soumis) et T8 (auto-mutant re-packagé).

---

## 6. Limites

- Le modèle suppose qu'on sait **identifier** un skill de façon stable (hash du
  code). Un attaquant qui change 1 octet change le hash — d'où l'importance des
  **scans de comportement**, pas seulement du hash (voir `DISCOVERY_PIPELINE`).
- `trusted` repose sur une **décision humaine** : c'est volontaire. Automatiser
  la promotion vers `trusted` = recréer le risque qu'on cherche à éviter.

---

*Doc 3/7 — TRUST_MODEL. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
