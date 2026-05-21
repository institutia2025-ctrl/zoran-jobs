# STOP_CRITERIA — Arrêt classique vs arrêt ZORAN

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : AUDIT — aucun code
**Signé** : Claude Code, prestataire · **Livrable 4/7**

> Une boucle d'agents qui ne sait pas s'arrêter de façon cohérente est une
> fuite, pas un projet. Ce document compare la façon dont les frameworks
> existants s'arrêtent et la façon dont l'oracle ZORAN s'arrête.

---

## 1. Les critères d'arrêt classiques — et leur faille

| Critère | Où | Faille |
|---|---|---|
| `max_iterations` | LangGraph, AutoGen | seuil **arbitraire**, sans lien avec l'état du projet. 10 ou 100 : aucune des deux valeurs n'est « juste ». |
| `timeout` (horloge) | tous | mesure le **temps écoulé**, pas l'avancement ni la cohérence. Un projet peut être incohérent bien avant le timeout, ou sain bien après. |
| « le LLM dit stop » | CrewAI, AutoGen, Swarm | **non déterministe, non auditable, manipulable** : c'est une opinion d'un modèle, non reproductible, sensible à l'injection de prompt. |
| file de tâches vide | CrewAI | critère réel mais **partiel** : il ne détecte ni la dérive de cohérence, ni le dépassement de budget, ni l'emballement. |

Le défaut commun : aucun de ces critères ne porte de **raison vérifiable**.
« On s'est arrêté à l'itération 100 » ne dit pas *pourquoi* 100, ni si c'était
le bon moment.

## 2. Les critères d'arrêt ZORAN

L'oracle `zoran_oracle_adaptation_agents` rend l'un de 5 verdicts, en priorité
stricte, chacun fonction **déterministe** d'entrées **mesurables** :

| Verdict | Condition | Nature |
|---|---|---|
| `TERMINE` | toutes les étapes sont `fait` | comptage exact |
| `STOP_INCOHERENCE` | `coherence_courante < seuil_coherence` | comparaison à un seuil explicite |
| `STOP_BUDGET` | `budget_restant <= 0` | arithmétique |
| `STOP_RESSOURCE` | travail restant mais 0 agent mobilisable | comptage + plafond budgétaire |
| `CONTINUER` | aucune des conditions d'arrêt | défaut |

À cela s'ajoute, au niveau orchestrateur, le veto multi-cadres : un cadre de
cohérence effondré (`S_cadre < seuil_veto`) élimine, il ne moyenne pas
(`specs/GLOBAL_VETO_RUNTIME.md`).

## 3. Tableau comparatif

| Propriété | Arrêt classique | Arrêt ZORAN |
|---|---|---|
| Déterministe | ✶ (sauf « LLM dit stop » : non) | ✅ même entrée → même verdict |
| Porte une raison auditable | ❌ | ✅ `verdict` + `explication` |
| Rejouable / reproductible | ✶ | ✅ fonction pure, ré-exécutable |
| Détecte l'incohérence | ❌ | ✅ `STOP_INCOHERENCE` |
| Détecte le dépassement de budget | ❌ | ✅ `STOP_BUDGET` |
| Détecte l'épuisement de ressources | ❌ | ✅ `STOP_RESSOURCE` |
| Résiste à l'injection de prompt | ❌ (« LLM dit stop ») | ✅ aucun LLM dans la décision |
| Seuils explicites et discutables | ❌ (arbitraires, implicites) | ✅ `seuil_coherence`, budget : en clair |

## 4. Le vrai critère : la falsifiabilité

`max_iterations` n'est pas *faux* — il n'est même pas *réfutable*. C'est un
réglage. « Le LLM dit stop » n'est pas réfutable non plus : on ne peut pas
rejouer la décision ni la contredire par le calcul.

Un verdict ZORAN, lui, est **réfutable au sens de Popper** : il est une
fonction connue d'entrées connues. On peut le rejouer, vérifier le calcul, et —
surtout — **contester les entrées**. C'est un progrès : le débat se déplace de
« quand faut-il s'arrêter ? » (insoluble dans l'absolu) vers « la cohérence
mesurée est-elle exacte ? » (un problème concret, local, vérifiable).

## 5. Honnêteté — le maillon faible

L'oracle **ne mesure pas** la cohérence. Il **reçoit** `coherence_courante`. Donc :

- si le harnais transmet `1.0` à chaque cycle, `STOP_INCOHERENCE` ne se
  déclenche **jamais** — le garde-fou est neutralisé sans aucune erreur visible ;
- `TERMINE` ne vaut que si les statuts d'étapes sont honnêtes ;
- `STOP_BUDGET` ne vaut que si la comptabilité du budget est honnête.

L'oracle ne supprime pas le problème difficile — il le **déplace et le
rétrécit**. Le problème difficile n'est plus « inventer un bon critère
d'arrêt » ; c'est « mesurer honnêtement la cohérence d'un livrable ». Ce
second problème est plus petit, plus local, et lui aussi falsifiable. Mais il
reste ouvert, et le prétendre résolu serait malhonnête (Loi 1 : aucune entrée
n'est supposée vraie).

## 6. Ce que ça change concrètement

Avec un arrêt classique, un projet long finit en état zombie : la boucle
tourne, le budget brûle, personne ne sait si le résultat est exploitable.

Avec l'arrêt ZORAN, le projet finit toujours dans l'un de deux états nommés :
un résultat (`TERMINE`) **ou** un arrêt motivé et auditable
(`STOP_INCOHERENCE` / `STOP_BUDGET` / `STOP_RESSOURCE`). Jamais un état zombie.
C'est la garantie réelle — et la seule — qu'apporte le bridge.

---

*Livrable 4/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Audit, aucun code.*
