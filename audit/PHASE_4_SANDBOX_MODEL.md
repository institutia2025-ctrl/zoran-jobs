# PHASE 4 — SANDBOX EXECUTION MODEL

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 2/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Principe fondateur : **un skill externe est hostile par défaut.** La sandbox
> n'est pas une option de confort — c'est la frontière entre le code inconnu et
> le runtime. Si la sandbox tombe, tout tombe.

---

## 1. Pourquoi le Loader actuel ne suffit pas

Le Loader Phase 1 fait `importlib.exec_module()` : le code du skill s'exécute
**dans le process hôte**, avec **les mêmes droits que le runtime**. Acceptable
pour des skills internes signés — inacceptable pour du code GitHub.

→ Phase 4 exige une **couche d'exécution séparée**. Le Loader ne charge plus le
skill : il le confie à la sandbox.

---

## 2. Les 9 dimensions d'isolation

| # | Dimension | Exigence Phase 4 |
|---|---|---|
| 1 | **Process** | le skill tourne dans un **sous-processus distinct**, jamais dans le process runtime |
| 2 | **Mémoire** | aucune référence partagée — le skill ne reçoit qu'une **copie sérialisée** des inputs, jamais l'objet `CoherenceState` |
| 3 | **Filesystem** | accès limité à un **répertoire jetable** dédié ; lecture/écriture hors de là = refus |
| 4 | **Réseau** | **coupé par défaut** ; un skill qui veut le réseau doit le déclarer ET être en niveau de confiance suffisant |
| 5 | **CPU** | quota dur ; dépassement → kill |
| 6 | **RAM** | plafond dur ; dépassement → kill |
| 7 | **Temps** | timeout d'exécution ; dépassement → kill |
| 8 | **Syscalls** | restriction des appels système dangereux (exec, fork récursif, accès devices) |
| 9 | **Quotas I/O** | limite de débit/volume disque ; dépassement → kill |

---

## 3. Le kill-switch

Tout skill sandboxé doit être **terminable instantanément et inconditionnellement**
par le runtime — sans coopération du skill. Le kill-switch :
- ne dépend d'aucun code du skill (pas de « demande poliment de s'arrêter »)
- s'applique aussi aux sous-processus enfants que le skill aurait lancés
- est déclenché par : timeout, dépassement quota, comportement anormal détecté, ou ordre manuel
- laisse le runtime hôte **intact** après le kill

---

## 4. Modèle d'exécution cible

```
runtime hôte                    │  sandbox (sous-processus isolé)
─────────────────────────────── │ ──────────────────────────────────
Loader                          │
  └─ prépare inputs (copie)      │
  └─ lance la sandbox ───────────┼──> skill.run(inputs_copiés)
  └─ surveille quotas/temps      │      (FS jetable, réseau coupé,
  └─ kill-switch armé            │       CPU/RAM/temps plafonnés)
  └─ reçoit outputs sérialisés <─┼──< (ou : kill si dépassement)
  └─ valide outputs vs schéma    │
```

Le skill ne **voit jamais** le runtime. Il reçoit des données, rend des données.
Toute communication passe par une frontière sérialisée — pas d'objets vivants.

---

## 5. Options techniques (à arbitrer en conception Phase 4)

| Option | Isolation | Coût | Note |
|---|---|---|---|
| `subprocess` + `resource` limits | moyenne | faible | minimum viable, isolation FS/réseau imparfaite |
| Conteneur (Docker/podman) | forte | moyen | isolation réelle, dépendance externe |
| microVM (Firecracker, gVisor) | très forte | élevé | isolation maximale, complexité |
| Interpréteur restreint (WASM) | forte | moyen | le skill doit être compilable WASM |

**Recommandation pré-audit** : ne PAS choisir maintenant. Le choix dépend du
modèle de menace retenu et des contraintes de déploiement. À trancher dans la
conception Phase 4, jamais par défaut.

---

## 6. Invariant non négociable

> Si un skill ne peut pas être **exécuté en isolation, plafonné, et tué à tout
> instant sans coopération de sa part**, il ne s'exécute pas. Pas d'exception.

---

## 7. Limites de ce document

- Ne traite pas la confiance (qui a le droit d'être sandboxé) → `TRUST_MODEL`.
- Ne traite pas la détection comportementale fine (un skill « lent » vs « miner »)
  → c'est un sujet de runtime tests, Phase 4 conception.
- L'isolation parfaite n'existe pas — l'objectif est de **rendre le coût d'évasion
  supérieur au gain**, pas de garantir l'inviolable.

---

*Doc 2/7 — SANDBOX_MODEL. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
