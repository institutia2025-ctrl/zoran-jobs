# LANGGRAPH_ADAPTER — Faire piloter un graphe LangGraph par l'oracle ZORAN

**Mission** : `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`
**Date** : 2026-05-22 · **Statut** : EXEMPLE d'intégration — patron, non exécuté ici
**Signé** : Claude Code, prestataire · **Livrable 2/7**

> LangGraph reste le **moteur** : il porte le graphe, les nœuds, les agents,
> les retries. ZORAN reste le **cerveau** : il décide, à chaque tour de boucle,
> s'il faut continuer et avec combien d'agents. L'oracle se branche comme la
> **fonction de routage d'une arête conditionnelle**.

---

## 1. Le point d'ancrage : `add_conditional_edges`

Un graphe LangGraph boucle naturellement via une arête conditionnelle : après
un nœud de travail, une fonction de routage choisit le nœud suivant. C'est
exactement la place de l'oracle — il **est** cette fonction de routage.

```
        ┌──────────────┐
        │  work_node   │  ← LangGraph exécute un lot d'étapes (agents, tools)
        └──────┬───────┘
               │
        add_conditional_edges(work_node, oracle_route)
               │
       ┌───────┴────────┐
       │                │
  "continuer"        "stop"
       │                │
   work_node           END        ← l'oracle a tranché
```

## 2. La correspondance d'état

| État LangGraph (`StateGraph`) | Entrée de l'oracle |
|---|---|
| `state["etapes"]` | `etapes` (liste `{id, statut, charge}`) |
| `state["agents"]` | `agents_disponibles` (`{api, local}`) |
| `state["budget"]` | `budget_restant` |
| `state["coherence"]` | `coherence_courante` (mesurée par le moteur) |
| `state["cycle"]` | `cycle` |
| `state["journal"]` | `journal` (cumulatif) |

| Sortie de l'oracle | Effet LangGraph |
|---|---|
| `reveil == "stop"` | la fonction de routage renvoie `END` |
| `reveil == "continuer"` | renvoie le nom du nœud de travail |
| `prochaines_etapes` | liste d'étapes confiée au prochain `work_node` |
| `agents_a_mobiliser` | nombre d'agents instanciés par le `work_node` |
| `budget_apres_cycle` | réécrit dans `state["budget"]` |

## 3. Patron de code (illustratif)

> ⚠️ Ce bloc illustre l'intégration. `langgraph` n'est **pas** une dépendance
> du dépôt ZORAN's Jobs (zéro dépendance externe — invariant). Le code n'est
> donc pas exécuté par la CI ; il montre la forme du branchement.

```python
from langgraph.graph import StateGraph, END
from loader.loader import Loader
from registry.registry import Registry

reg = Registry(); reg.load_from_dir("skills_examples")
oracle, _ = Loader().load(reg.get("zoran_oracle_adaptation_agents"))

def oracle_route(state: dict) -> str:
    """Fonction de routage = appel à l'oracle ZORAN (cerveau)."""
    decision = oracle.run({
        "etapes": state["etapes"], "agents_disponibles": state["agents"],
        "budget_restant": state["budget"], "coherence_courante": state["coherence"],
        "cycle": state["cycle"], "journal": state["journal"],
    })
    state["journal"] = decision["journal"]
    state["budget"] = decision["budget_apres_cycle"]
    state["_decision"] = decision          # lu par work_node
    return END if decision["reveil"] == "stop" else "work_node"

graph = StateGraph(dict)
graph.add_node("work_node", run_agents)    # run_agents : fourni par LangGraph
graph.set_entry_point("work_node")
graph.add_conditional_edges("work_node", oracle_route)
```

`run_agents` (le nœud de travail) lit `state["_decision"]["prochaines_etapes"]`
et `["agents_a_mobiliser"]`, instancie ce nombre d'agents, exécute, met à jour
`state["etapes"]` et `state["coherence"]`, puis incrémente `state["cycle"]`.

## 4. Frontière de responsabilité — non négociable

- **LangGraph** : porte le graphe, exécute les agents, gère retries et
  parallélisme. Le bridge ne réécrit rien de tout cela.
- **ZORAN** : la fonction `oracle_route` ne contient **aucune** logique de
  décision propre — elle traduit l'état et appelle l'oracle. Tout `if` métier
  ajouté dans `oracle_route` viole l'invariant AB-5 de `AGENTIC_BRIDGE_SPEC.md`.

## 5. Honnêteté

Ce document est un **patron d'intégration**, pas une preuve. Il n'a pas été
exécuté contre une instance LangGraph réelle (pas de dépendance, pas de réseau
dans ce dépôt). Ce qui **est** prouvé et exécuté par la CI : la boucle
minimale `examples/minimal_agent_harness.py` (livrable 5), qui démontre le même
schéma — moteur exécute, oracle décide — sans dépendance externe.

---

*Livrable 2/7 — `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522`. Exemple d'intégration.*
