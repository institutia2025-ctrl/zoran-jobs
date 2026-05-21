# LOW_TOKEN_AGENTIC — Le coût cognitif de la boucle oracle ↔ agents

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : AUDIT — aucun code
**Signé** : Claude Code, prestataire · **Livrable 7/7**

> `audit/LOW_TOKEN_STRATEGY.md` donne la stratégie générale (6 leviers). Ce
> document-ci traite le cas précis du **bridge agentique** : où vont les tokens
> dans une boucle oracle ↔ agents, et comment n'en dépenser aucun en trop.

---

## 1. Où est le coût — et où il n'est pas

La clarification décisive : **l'appel à l'oracle ne coûte aucun token.**
`zoran_oracle_adaptation_agents` est une fonction Python locale, 100 %
mathématique, sans LLM, sans réseau. L'appeler 10 fois ou 10 000 fois coûte du
CPU négligeable, **zéro token**.

Le coût cognitif d'une boucle agentique est **entièrement** dans les **agents
LLM** que le moteur exécute. Donc la discipline low-token du bridge ne porte
pas sur l'oracle — elle porte sur ce qu'on **donne à lire aux agents**.

| Élément de la boucle | Coût token |
|---|---|
| Appel `oracle.run(...)` | **nul** (fonction locale) |
| Journal cumulatif passé à l'oracle | **nul** (passé à une fonction locale) |
| Contexte chargé dans chaque agent LLM | **dominant** — c'est ici qu'on agit |
| Échanges directs entre agents | **gaspillage** — à supprimer |

## 2. Le delta dans la boucle agentique

Chaque agent ne reçoit que **son étape et son delta** — pas l'état du projet
entier, pas le travail des autres agents. C'est l'application directe de
`specs/DELTA_TRANSMISSION_PROTOCOL.md` (DT-1, DT-3) à l'intérieur du cycle :
le bridge transmet à l'agent les éléments ajoutés/modifiés pertinents pour son
étape, et l'empreinte globale pour vérification — rien d'autre.

Règle : si le contexte d'un agent grossit à chaque cycle, c'est qu'on lui
retransmet du contexte déguisé en delta. Alerte (DT-3).

## 3. Le verdict de l'oracle EST un résumé déterministe

Un statut de projet rédigé par un agent LLM coûte des tokens **et** introduit
de l'interprétation. La sortie de l'oracle — `verdict`, `progression_pct`,
`agents_a_mobiliser`, `budget_apres_cycle` — est un **résumé déterministe** :
quelques nombres et un mot, calculés, falsifiables, quasi gratuits.

Partout où la boucle aurait demandé à un LLM « résume où on en est », elle lit
la sortie de l'oracle à la place. C'est le levier « résumés déterministes » de
`LOW_TOKEN_STRATEGY.md` §3, appliqué au pilotage de la boucle.

## 4. Le journal cumulatif — gratuit pour l'oracle, piège pour un agent

Le journal de l'oracle grandit d'une entrée par cycle, sans borne. Ce n'est
**pas** un problème de tokens **tant qu'il ne va qu'à l'oracle** : le
ré-injecter à une fonction locale est gratuit.

Le piège : déverser ce journal dans le prompt d'un **agent LLM** « pour le
contexte ». Là, le coût croît à chaque cycle et devient quadratique sur un
projet long. Règle dure :

> Le journal circule entre le **bridge** et l'**oracle**. Un agent LLM ne
> reçoit jamais le journal brut — au plus le **dernier verdict**.

## 5. Anti-patterns interdits

- ❌ Donner l'état du projet entier à chaque agent « par sécurité » → coût
  `O(n²)`, dérive (cf. C5/C6 de `INTER_AGENT_CONFLICTS.md`).
- ❌ Faire écrire à un agent LLM le résumé d'avancement → l'oracle le donne
  déjà, gratuitement et sans interprétation.
- ❌ Injecter le journal cumulatif dans un prompt d'agent → coût croissant sans
  borne.
- ❌ Laisser les agents s'échanger leur contexte directement → bavardage non
  borné, NO-GO (C9).
- ❌ Confondre « l'oracle tourne souvent » et « ça coûte cher » → l'oracle est
  gratuit ; appeler l'oracle à chaque micro-étape est **encouragé**.

## 6. Mesure

Indicateur clé du bridge : **tokens par cycle utile**, ventilés en
`contexte agent` / `delta` / `sortie oracle` (≈ 0). Le modèle de comptage est
`specs/TOKEN_BUDGET_MODEL.md`. Tant que `contexte agent` reste stable d'un
cycle à l'autre, la discipline tient ; s'il croît, on retransmet du contexte —
exactement le signal d'alerte de DT-3.

## 7. Le mot de la fin

Le succès n'est pas « beaucoup d'agents ». C'est « des agents qui restent
cohérents et savent s'arrêter » — à coût cognitif minimal. L'oracle est la
moitié « savent s'arrêter », gratuitement ; la discipline delta de ce document
est la moitié « coût minimal ». Les deux sont indissociables.

---

*Livrable 7/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Audit, aucun code.
Mission COMPLÈTE — 7/7 livrables : 1 spec, 2 exemples d'intégration, 1 exemple
de code exécutable (≤ 50 lignes), 3 audits. Aucun framework réécrit.*
