# MULTI_IA_GOVERNANCE — Gouverner plusieurs IA sans les confondre

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : AUDIT — aucun code
**Signé** : Claude Code, prestataire · **Livrable 6/7**

> Brancher l'oracle sur un framework agentique, c'est faire travailler
> plusieurs IA ensemble. La règle fondatrice n'est pas « combien d'IA » mais
> « chaque IA à sa place, et personne ne confond les rôles ».

---

## 1. La règle fondatrice — les modèles ne sont pas interchangeables

```
Codex  ≠  Claude  ≠  GPT  ≠  DeepSeek.   Toujours.
```

Ce n'est pas un détail d'étiquette. Des modèles différents ont des
entraînements, des forces, des angles morts et des modes d'échec **différents**.
Les traiter comme des ouvriers fongibles est l'erreur de gouvernance majeure :

- on n'attribue plus une régression à un modèle précis ;
- on confie un territoire à un modèle qui y est faible ;
- on perd la possibilité de croiser les regards (la valeur d'avoir plusieurs IA
  vient justement de leur **non-équivalence**).

Une IA est donc toujours identifiée par son **modèle** et son **territoire**.
Jamais « un agent » anonyme.

## 2. Territoires disjoints

Chaque IA reçoit un **territoire** : un périmètre de fichiers / de
responsabilités **disjoint** de celui des autres. Deux IA ne modifient jamais
le même territoire dans la même mission.

L'affectation des territoires est **humaine et explicite** — elle n'est pas
négociée entre les IA. C'est la même discipline que les scopes et préfixes
disjoints de `specs/ZORAN_JOBS_DISTRIBUTION.md` (ZD-2), appliquée aux acteurs
et non plus aux livrables.

| Rôle (illustratif) | Territoire type | Pourquoi disjoint |
|---|---|---|
| IA runtime / infra | cœur d'exécution, providers, perf | une régression cœur doit être attribuable |
| IA satellites / conception | modules périphériques, recherche, bac à sable | l'isolement protège le cœur |
| IA front / UX | interface, rendu | le front ne touche pas le runtime |
| IA gouvernance | specs, audits, journaux | arbitre, ne code pas le cœur |

Ce tableau est un **patron**, pas une prescription : la grille réelle est
fixée par l'humain responsable de la mission.

## 3. Veto — par territoire, puis arbitrage

- **Dans son territoire**, une IA a autorité, veto compris : elle peut refuser
  une modification entrante incohérente avec son périmètre.
- **Entre territoires**, aucune IA ne véto une autre directement. Le conflit
  remonte à l'orchestrateur, qui tranche par **Global Veto → plancher → S_global**
  (`specs/GLOBAL_VETO_RUNTIME.md`). Les IA ne négocient pas entre elles : le
  bavardage inter-IA est un NO-GO (`audit/INTER_AGENT_CONFLICTS.md`, C9).

Tout veto **cite** le cadre fautif, son `S` et le seuil. Un veto non motivé est
invalide (GV-4).

## 4. Rollback indépendant

La contribution de chaque IA doit être **annulable seule**, sans défaire le
travail des autres : branches dédiées, tags de jalon, scopes disjoints. C'est la
contrepartie directe des territoires disjoints — si les périmètres se
chevauchent, le rollback devient impossible et la gouvernance s'effondre.

## 5. Traces — chaque action porte l'identité du modèle

Toute action (commit, manifeste de skill, entrée de journal) porte l'identité
du **modèle** qui l'a produite, pas un pseudonyme générique : signature de
manifeste, `Co-Authored-By` de commit, champ `author`. Critère de réussite :
toute régression doit pouvoir être rattachée à un couple **(modèle, territoire,
jalon)** précis. Si ce n'est pas possible, la traçabilité a échoué.

## 6. Conflits — renvoi au catalogue

Les conflits concrets entre IA (excellence locale destructrice, dérive de
coordination, bruit cognitif) et leurs mécanismes de prévention sont catalogués
dans `audit/INTER_AGENT_CONFLICTS.md` (C1–C11). Ce document-ci en est le volet
**gouvernance** : qui fait quoi, où, et comment on l'annule — pas le détail des
conflits eux-mêmes.

## 7. Honnêteté — le conflit résiduel

Un risque ne se règle pas par une règle écrite : **deux orchestrateurs
concurrents** qui s'ignorent recréent la désynchronisation à l'étage du dessus
(conflit C6). Règle terminale : **un seul orchestrateur fait autorité par
mission**, et un seul oracle (AB-7 de `specs/AGENTIC_BRIDGE_SPEC.md`). Leur
désignation est humaine, explicite, et hors du pouvoir des IA.

Et un rappel de cadrage : cette gouvernance organise des IA — elle ne les rend
pas correctes. Une IA bien gouvernée sur un territoire propre peut toujours se
tromper. La gouvernance rend l'erreur **attribuable et annulable**, pas
impossible.

---

*Livrable 6/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Audit, aucun code.*
