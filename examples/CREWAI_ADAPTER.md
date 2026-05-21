# CREWAI_ADAPTER — Faire gouverner un Crew CrewAI par l'oracle ZORAN

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : EXEMPLE d'intégration — patron, non exécuté ici
**Signé** : Claude Code, prestataire · **Livrable 3/7**

> CrewAI reste le **moteur** : il porte les Agents, les Tasks, le Process
> (séquentiel ou hiérarchique). ZORAN reste le **cerveau** : entre deux lots de
> Tasks, l'oracle dit s'il faut relancer un Crew, avec combien d'agents, ou
> s'arrêter — et il transmet au Crew le veto, les verdicts et le budget.

---

## 1. Le point d'ancrage : la boucle de lots

CrewAI exécute une liste de Tasks puis rend la main (`crew.kickoff()`). Il n'a
pas d'arête conditionnelle native comme LangGraph. Le branchement propre est
donc une **boucle de lots** autour du Crew : un cycle d'oracle = un
`kickoff()` sur un lot de Tasks.

```
   ┌─────────────────────────────────────────────┐
   │  boucle de lots (le BRIDGE)                  │
   │                                              │
   │   oracle.run(...)  ──►  verdict + lot suivant │
   │        │                                     │
   │   reveil == "stop"   → fin, verdict remonté   │
   │   reveil == "continuer"                       │
   │        │                                     │
   │        ▼                                     │
   │   Crew(agents=N, tasks=lot).kickoff()         │  ← CrewAI exécute
   │        │                                     │
   │        └── statuts des Tasks ────────────────┘
   └─────────────────────────────────────────────┘
```

## 2. Ce que le Crew reçoit de l'oracle

| Sortie de l'oracle | Ce que le Crew en fait |
|---|---|
| `reveil` | `"stop"` ⇒ le Crew n'est pas relancé ; `"continuer"` ⇒ lot suivant |
| `verdict` | injecté dans le contexte des Tasks (traçabilité, garde-fous) |
| `agents_a_mobiliser` | nombre d'`Agent` CrewAI instanciés pour le lot |
| `prochaines_etapes` | converties en `Task` CrewAI du lot |
| `budget_apres_cycle` | budget reporté au cycle suivant |
| `explication` | motif d'arrêt remonté à l'humain / au journal |

Le **veto** est porté par `STOP_INCOHERENCE` : si la cohérence mesurée des
livrables du lot précédent passe sous le seuil, l'oracle rend ce verdict et le
Crew **n'est pas relancé**. Aucune Task supplémentaire n'est créée.

## 3. La correspondance d'état

| État CrewAI | Entrée de l'oracle |
|---|---|
| Tasks terminées / en cours / non démarrées | `etapes` (`statut` ∈ fait/en_cours/a_faire) |
| coût/poids estimé d'une Task | `charge` de l'étape |
| pool d'`Agent` disponibles (local vs API) | `agents_disponibles` |
| budget de la mission | `budget_restant` |
| score de cohérence du lot livré | `coherence_courante` (mesuré par le moteur) |

## 4. Patron de code (illustratif)

> ⚠️ `crewai` n'est **pas** une dépendance du dépôt (zéro dépendance externe —
> invariant). Ce bloc montre la forme du branchement ; il n'est pas exécuté par
> la CI.

```python
from crewai import Agent, Task, Crew
from loader.loader import Loader
from registry.registry import Registry

reg = Registry(); reg.load_from_dir("skills_examples")
oracle, _ = Loader().load(reg.get("zoran_oracle_adaptation_agents"))

etapes, budget, journal, cycle = charger_etapes(), 100.0, [], 1
while True:
    decision = oracle.run({                       # le CERVEAU décide
        "etapes": etapes, "agents_disponibles": {"api": 4, "local": 2},
        "budget_restant": budget, "coherence_courante": mesurer_coherence(),
        "cycle": cycle, "journal": journal,
    })
    journal = decision["journal"]
    if decision["reveil"] == "stop":
        remonter(decision["verdict"], decision["explication"]); break
    n = sum(decision["agents_a_mobiliser"].values())
    crew = Crew(                                  # CrewAI EXÉCUTE
        agents=[Agent(role=f"worker_{i}") for i in range(n)],
        tasks=[Task(description=e) for e in decision["prochaines_etapes"]],
    )
    crew.kickoff()
    etapes, budget, cycle = relire_statuts(), decision["budget_apres_cycle"], cycle + 1
```

## 5. Frontière de responsabilité — non négociable

- **CrewAI** : Agents, Tasks, Process, délégation, outils. Rien de cela n'est
  réécrit.
- **ZORAN** : la boucle de lots ne contient **aucune** règle métier de
  décision — elle traduit l'état, appelle l'oracle, applique le verdict. Tout
  `if` décisionnel ajouté hors de l'oracle viole l'invariant AB-5 de
  `AGENTIC_BRIDGE_SPEC.md`.

## 6. Honnêteté

Patron d'intégration, pas preuve : non exécuté contre une instance CrewAI
réelle (pas de dépendance, pas de réseau dans ce dépôt). La preuve exécutée par
la CI est la boucle minimale `examples/minimal_agent_harness.py` (livrable 5),
qui démontre le même schéma sans dépendance externe. Limite connue : la
granularité (un cycle d'oracle = un lot de Tasks) impose que les Tasks d'un lot
soient indépendantes ; des Tasks fortement couplées demandent des lots plus
petits, au prix de cycles plus nombreux.

---

*Livrable 3/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Exemple d'intégration.*
