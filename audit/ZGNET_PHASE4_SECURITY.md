# ZGNET — ANALYSE DE SÉCURITÉ POUR PHASE 4

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 5/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> ⚠️ ZGNET reste **purement théorique** (cf. `specs/ZGNET_RUNTIME_LANGUAGE.md`,
> couche 3, V4+). Ce document évalue *si* ZGNET pourrait réduire les risques
> Phase 4 — il ne propose AUCUNE implémentation.

---

## 1. Rappel — ce qu'est ZGNET

Un langage runtime **strict, borné, invariant, non-ambigu** : vocabulaire fini
et fermé pour les échanges entre composants/skills. Pensé pour que toute
intelligence interprète une instruction de façon identique.

## 2. La question posée

ZGNET peut-il réduire : injections · ambiguïtés · skill chaos · protocol drift ?

---

## 3. Analyse, risque par risque

### Injections (T5 — prompts cachés)
- **Apport potentiel** : un langage à vocabulaire **fermé** rejette par
  construction tout ce qui n'est pas une instruction connue. Un prompt caché
  glissé dans un champ ZGNET ne serait pas *interprétable* → inerte.
- **Limite** : ne protège QUE les échanges exprimés en ZGNET. Le `skill.py`
  lui-même reste du Python — ZGNET ne sécurise pas le code, seulement le
  protocole de communication. **Gain réel : partiel.**

### Ambiguïtés
- **Apport potentiel** : fort. C'est la raison d'être de ZGNET — une
  instruction = une seule interprétation. Élimine la classe de bugs « deux
  composants comprennent différemment le même message ».
- **Limite** : aucune si ZGNET est réellement non-ambigu. **Gain réel : élevé**
  — mais sur le *protocole*, pas sur le *comportement du code skill*.

### Skill chaos (skills qui interagissent de façon imprévue)
- **Apport potentiel** : moyen. Un protocole borné réduit les couplages
  sauvages, mais le chaos vient surtout du *code exécuté*, pas du langage de
  communication. **Gain réel : indirect.**

### Protocol drift (le protocole runtime dérive avec le temps/les versions)
- **Apport potentiel** : fort. Un langage **invariant et versionné** est par
  définition une défense contre le drift. **Gain réel : élevé.**

---

## 4. Verdict honnête

| Risque | ZGNET aide ? | Force |
|---|---|---|
| Injections (T5) | partiellement | ★★☆ |
| Ambiguïtés | oui | ★★★ |
| Skill chaos | indirectement | ★☆☆ |
| Protocol drift | oui | ★★★ |

**ZGNET est un bon outil de discipline de PROTOCOLE — pas un outil de sécurité
d'EXÉCUTION.** Il ne remplace ni la sandbox, ni le scan statique, ni le trust
model. Contre un skill hostile, la vraie défense reste : isolation + filtrage +
confiance progressive (docs 2-3-4).

---

## 5. Recommandation

- **NE PAS** implémenter ZGNET pour Phase 4. Ce serait confondre « discipline de
  protocole » et « sécurité d'exécution » — et faire de ZGNET un prérequis
  bloquant alors qu'il ne couvre pas le risque principal.
- ZGNET reste **V4+**, déclenchable seulement si le besoin de transmission
  inter-IA devient réel (cf. critères dans `specs/ZGNET_RUNTIME_LANGUAGE.md`).
- Pour Phase 4, l'`EVENT_SCHEMA` JSON strict (couche 0, déjà gelé) **suffit**
  comme protocole — il est déjà borné et signé.

---

## 6. Limites de cette analyse

- ZGNET n'existant pas, cette évaluation est **spéculative par nature** — elle
  raisonne sur les propriétés *visées*, pas mesurées.
- Si ZGNET était un jour conçu, cette analyse devrait être refaite sur la spec
  réelle, pas sur l'intention.

---

*Doc 5/7 — ZGNET_PHASE4_SECURITY. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
