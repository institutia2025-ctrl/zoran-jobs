# FRAME_ROUTER_SPEC — Distribution des cadres de cohérence

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code
**Signé** : Claude Code, prestataire · **Livrable 2/8**

> Le Frame Router distribue les **bons cadres de cohérence** aux **bonnes IA**.
> Une IA ne reçoit jamais les cadres qui ne la concernent pas — c'est ce qui
> effondre le coût token et le bruit.

---

## 1. Objet

Les cadres de cohérence (contrat V2, `_validate_v2_extensions`) sont :
`structure`, `cout`, `carbone`, `maintenance`, `exploitation`, `securite`,
`global`. Le Frame Router décide, **de façon déterministe**, quels cadres
chaque IA reçoit. Une IA UX n'a aucune raison de raisonner sur `securite`
runtime ; une IA Sécurité n'a aucune raison de raisonner sur `carbone`.

Distribuer tous les cadres à toutes les IA = duplication cognitive = coût token
qui explose et dérive qui s'installe. Le routage de cadres est une **forme de
compression** : on ne transmet que la dimension d'évaluation pertinente.

## 2. Table de routage des cadres (déterministe)

| IA | Cadres reçus | Cadre dominant |
|---|---|---|
| Backend | `structure`, `exploitation`, `global` | `exploitation` |
| UX | `exploitation`, `cout`, `global` | `exploitation` |
| Sécurité | `securite`, `structure`, `global` | `securite` |
| Code / runtime | `structure`, `global` | `structure` |
| Métier (BTP…) | dépend du domaine, fourni par `zoran_selecteur_lois_cadres` | variable |

Le cadre `global` est le **seul** transmis à toutes les IA : il est le point
d'ancrage commun. Sans lui, aucune IA ne saurait que sa cohérence locale doit
servir une cohérence d'ensemble.

## 3. Règle de routage

**Invariant FR-1 — minimalité** : une IA reçoit le plus petit ensemble de cadres
qui rend sa mission évaluable. Tout cadre en plus est un NO-GO.

**Invariant FR-2 — `global` obligatoire** : toute IA reçoit le cadre `global`.
C'est la garantie que le Global Veto (`GLOBAL_VETO_RUNTIME.md`) a une prise.

**Invariant FR-3 — déterminisme** : même rôle + même domaine → même jeu de
cadres. Le routage des cadres est reproductible, comme le Router de skills
(`router/router.py`).

## 4. Lien avec le skill existant

Le skill `zoran_selecteur_lois_cadres` (déjà livré, `skills_examples/`) est le
**moteur déterministe** de cette spec côté métier : `domaine → cadres
pertinents + lois du Codex`. Le Frame Router en est l'usage à l'échelle
orchestrateur : il applique ce moteur par IA, pas par évaluation isolée.

## 5. Anti-pattern explicitement interdit

> « Par sécurité, donnons tous les cadres à toutes les IA. »

Interdit. C'est exactement la duplication cognitive que la mission proscrit.
Donner `securite` à l'IA UX ne la rend pas plus sûre — ça la fait raisonner sur
une dimension qu'elle ne maîtrise pas, produire du bruit, et coûter des tokens.
La sécurité est garantie par le **Global Veto**, pas par la diffusion du cadre.

## 6. Traçabilité

Chaque routage journalise : `mission_id`, IA cible, cadres attribués, cadre
dominant, justification (rôle + domaine), limites explicites (cadres
volontairement non transmis).

---

*Livrable 2/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
