# AGENTIC_BRIDGE_SPEC — Brancher l'oracle ZORAN sur un orchestrateur agentique

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : SPEC — aucun code de runtime
**Signé** : Claude Code, prestataire · **Livrable 1/7**

> Les frameworks agentiques (LangGraph, CrewAI, AutoGen) savent **exécuter**.
> Ils ne savent pas **s'arrêter de façon cohérente**. Le bridge branche le
> cerveau qui le sait — `zoran_oracle_adaptation_agents` — sans réécrire un
> seul de ces frameworks.

---

## 0. En une phrase

Le bridge est un **traducteur mince** : il convertit l'état d'avancement d'un
orchestrateur agentique en entrées de l'oracle ZORAN, et le verdict de l'oracle
en contrôle de flux du framework. Il ne décide rien lui-même, il n'exécute rien
lui-même.

## 1. Le problème

Un framework agentique boucle jusqu'à `max_iterations`, un `timeout`, ou
« le LLM dit stop ». Aucun de ces trois critères n'est falsifiable ni auditable
(détail : `audit/STOP_CRITERIA.md`). Conséquence : un projet long s'emballe
(runaway) ou s'arrête sur un seuil arbitraire. Il manque un **critère d'arrêt
cohérent**. C'est exactement ce que l'oracle fournit.

## 2. Architecture — trois couches strictement séparées

| Couche | Rôle | Qui |
|---|---|---|
| **Moteur** | exécute : graphes, agents, tools, retries, parallélisme | LangGraph / CrewAI / AutoGen |
| **Bridge** | traduit : état moteur ↔ entrées/verdict oracle | ce document |
| **Cerveau** | décide : dimensionne les agents, dit quand s'arrêter | `zoran_oracle_adaptation_agents` |

Le moteur reste le moteur. Le cerveau reste le cerveau. Le bridge ne fait que
les relier — il n'est pas un quatrième composant intelligent.

## 3. Le flux d'un cycle (oracle ↔ agents)

```
1. le MOTEUR termine un lot d'étapes
2. le BRIDGE collecte l'état réel : étapes (fait/en_cours/a_faire),
   budget consommé, cohérence mesurée du livrable courant
3. le BRIDGE appelle  oracle.run(inputs)        ← fonction pure, locale
4. l'ORACLE renvoie   {verdict, reveil, agents_a_mobiliser,
                       prochaines_etapes, budget_apres_cycle, journal}
5. le BRIDGE applique :
     reveil == "stop"      → le MOTEUR s'arrête, le verdict est remonté
     reveil == "continuer" → le MOTEUR lance agents_a_mobiliser agents
                             sur prochaines_etapes
```

Le contrat d'entrée/sortie de l'oracle est figé par le skill lui-même
(`skills_examples/zoran_oracle_adaptation_agents/`). Le bridge s'y conforme ;
il ne le contourne pas.

## 4. Veto runtime

`STOP_INCOHERENCE` **est** le veto du bridge. Quand la cohérence mesurée passe
sous le seuil, l'oracle rend ce verdict et le bridge **doit** arrêter le
moteur — il n'existe pas de « continuer quand même ». C'est la remontée de
`specs/GLOBAL_VETO_RUNTIME.md` au niveau de l'orchestrateur agentique : un veto
silencieux ou contourné est interdit (GV-1, GV-4).

La cohérence n'est **pas** mesurée par l'oracle — l'oracle la reçoit. Sa mesure
est la responsabilité du moteur/harnais. C'est le maillon faible réel et il est
nommé comme tel (cf. `audit/STOP_CRITERIA.md` §5).

## 5. Delta transmission

Le bridge ne renvoie pas tout le contexte au moteur ni aux agents à chaque
cycle : il transmet le **delta** d'état (`specs/DELTA_TRANSMISSION_PROTOCOL.md`).
Précision importante : l'appel à l'oracle, lui, est **local et mathématique** —
zéro token, zéro réseau. Le coût cognitif d'une boucle agentique est dans les
**agents LLM**, pas dans l'oracle (détail : `audit/LOW_TOKEN_AGENTIC.md`).

## 6. Budgets

Le bridge tient `budget_restant` et le décrémente de `cout_estime_cycle` à
chaque cycle, à partir de la sortie de l'oracle. Le modèle de comptage des
tokens est `specs/TOKEN_BUDGET_MODEL.md`. Quand le budget atteint 0, l'oracle
rend `STOP_BUDGET` : la bascule silencieuse en exécution locale illimitée est
interdite — elle exige une re-décision humaine.

## 7. Arrêt — les 5 verdicts

`TERMINE` · `STOP_INCOHERENCE` · `STOP_BUDGET` · `STOP_RESSOURCE` ·
`CONTINUER`, en priorité stricte. Chaque verdict porte une `explication`
auditable. La comparaison avec les critères d'arrêt classiques est l'objet du
livrable 4 (`audit/STOP_CRITERIA.md`).

## 8. Invariants du bridge

**AB-1 — le bridge n'exécute pas.** Aucun agent, aucun tool, aucun appel
modèle n'est lancé par le bridge. Le moteur exécute. Un bridge qui exécute est
un bug.

**AB-2 — l'oracle reste pur.** Toute entrée/sortie (réseau, process, fichiers,
mesure de cohérence) est faite par le bridge ou le moteur. L'oracle reste une
fonction pure (invariant runtime).

**AB-3 — le verdict est contraignant.** Si `reveil == "stop"`, le bridge
arrête le moteur. Il n'existe aucun chemin « ignorer le verdict ».

**AB-4 — déterminisme de bout en bout.** Même état moteur → mêmes entrées
oracle → même verdict. Le bridge n'introduit aucun aléa.

**AB-5 — le bridge ne décide rien.** Toute décision appartient à l'oracle,
toute exécution au moteur. Tout fragment de logique décisionnelle dans le
bridge est un défaut à retirer.

**AB-6 — delta-only.** Le bridge transmet des deltas d'état, jamais le contexte
entier (DT-1, DT-3).

**AB-7 — un seul oracle fait autorité par mission.** Deux oracles concurrents
recréent le conflit C6 de `audit/INTER_AGENT_CONFLICTS.md` à l'étage du dessus.

## 9. Ce que le bridge n'est PAS

- ❌ Ce n'est **pas** un framework agentique — il ne remplace ni LangGraph,
  ni CrewAI, ni AutoGen.
- ❌ Ce n'est **pas** un « super-orchestrateur » monolithique. Réécrire ces
  frameworks est explicitement hors mission.
- ❌ Ce n'est **pas** un garant de succès. L'oracle garantit qu'un projet ne
  s'emballe pas — pas qu'il aboutisse.
- ❌ Ce n'est **pas** un mesureur de cohérence. Il transmet une cohérence
  mesurée ailleurs ; si cette mesure est fausse, le verdict l'est aussi.

## 10. Traçabilité

Journalise par cycle : `mission_id`, cycle, état moteur transmis, entrées
oracle, verdict, agents mobilisés, `cout_estime_cycle`, `budget_apres_cycle`,
cohérence mesurée et sa source. Le journal de l'oracle est cumulatif et
ré-injecté à chaque cycle (le ré-injecter à une fonction locale ne coûte aucun
token).

---

*Livrable 1/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Spec ; le seul code de
la mission est l'exemple `examples/minimal_agent_harness.py` (livrable 5).*
