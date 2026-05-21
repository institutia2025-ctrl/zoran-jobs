# THEORY_BRIDGE — Du scoring de routage à la géométrie d'information

**Mission** : `ZORAN_JOBS_20260521`
**Statut** : document explicatif, **pas** un invariant.
**Auteur** : Frédéric TABARY · 2026-05-21

> Ce document existe pour répondre à une question légitime : *« la formule de cohérence du runtime est-elle la métrique de Fisher ? Est-ce que ZORAN's Jobs incarne `CP^(n-1)` (la variété projective complexe de la cognition optimale) ? »*
>
> Réponse courte : **non**. Réponse longue : ci-dessous, honnête.

---

## 1. Ce que le runtime calcule réellement

Le Coherence Engine évalue, pour chaque skill candidat, un scalaire :

```
S = (β × ΔΦ) / (1 + T + σ)
```

avec `β` la direction structurelle de l'état courant, `ΔΦ` l'information attendue du skill, `T` les contradictions injectées, `σ` le bruit injecté. Le routeur classe ensuite par `ΔS = S_candidat − S_courant`.

C'est une **heuristique de scoring**. Elle est élégante (additive, robuste à la division par zéro, prédictible à la main, déterministe), mais elle est **scalaire** : un seul nombre par skill.

## 2. Ce que prétend la conjecture Zoran sous-jacente

Le cadre théorique plus large dont ZORAN's Jobs est un satellite avance que la cognition optimale d'un modèle de monde se structure comme l'espace projectif complexe **CP^(n−1)**, muni de la métrique **Fubini–Study** — équivalente, par construction Kähler + règle de Born, à la métrique de Fisher sur la sphère statistique.

Sous cette conjecture, la « cohérence » d'un état cognitif n'est pas un scalaire mais une **géométrie** : courbure constante, distances inter-états mesurées par Fisher–Rao, transport parallèle non trivial.

## 3. La différence honnêtement nommée

| Aspect | Formule du runtime | Métrique Fisher / Fubini–Study |
|---|---|---|
| Type | scalaire sur ℝ⁺ | tenseur métrique sur une variété |
| Dimension | 1 valeur par skill | matrice n×n par état |
| Dérivée | différence finie (ΔS, dS/dt) | gradient covariant ∇S |
| Topologie | aucune (juste un ordre) | CP^(n−1), courbure constante |
| Implémentation | 5 lignes Python, stdlib | ferait appel à un système d'autodiff |

La formule additive **n'est pas** la métrique de Fisher. Elle ne s'y ramène pas par changement de variables. Affirmer le contraire serait du *theory laundering* — emprunter la respectabilité de la géométrie d'information sans en porter les contraintes.

## 4. Ce qu'elle est, alors

Une **heuristique inspirée par** la même intuition que la métrique de Fisher : **plus l'information acquise est élevée par rapport au bruit et aux contradictions, plus le système est "stable" dans la direction choisie**. Le rapport `(β × ΔΦ) / (1 + T + σ)` est une projection 1D, grossière mais opératoire, de cette idée.

Concrètement :
- Le numérateur `β × ΔΦ` capture le produit *direction × information*. C'est l'analogue scalaire du produit `g(δ, δ)` de la métrique Fisher dans une direction donnée — sans la structure de variété.
- Le dénominateur `1 + T + σ` joue le rôle d'un *régularisateur* : pénalise le bruit et l'incohérence sans jamais s'annuler. Le `1 +` garantit que la quantité reste finie.

Cette heuristique est **suffisante pour router** un skill parmi quelques dizaines de candidats. Elle ne prétend pas être suffisante pour modéliser la cognition optimale d'un agent.

## 5. Pourquoi le choix est délibéré

Trois raisons :

1. **Falsifiabilité.** Une métrique de Fisher implémentée en Python serait opaque pour un humain (matrices, exponentielle de log-vraisemblance, etc.). La formule scalaire se vérifie à la main avec une calculette. Le contrat de falsifiabilité du projet (INV-2) prime sur l'élégance théorique.

2. **Transmissibilité.** Une IA externe doit pouvoir comprendre et faire revivre le runtime depuis le dépôt seul, sans contexte théorique préalable. Une formule scalaire avec quatre paramètres est transmissible. La géométrie de l'information ne l'est pas, sauf à embarquer un cours.

3. **Sandbox jetable.** Le projet pourrait être détruit si l'architecture échoue. Investir dans une implémentation rigoureuse de Fisher–Rao pour un MVP qui pourrait disparaître serait disproportionné.

## 6. Évolutions possibles (hors MVP)

Une **Phase 5 théorique** (jamais ouverte tant que la Phase 4 reste NO-GO) pourrait :

- Étendre `CoherenceState` en `CoherenceManifold` portant une vraie matrice métrique.
- Remplacer `compute_S` scalaire par un score géométrique `g(δ, δ)` calculé sur le tangent en l'état courant.
- Valider expérimentalement, sur un corpus de routages connus, que le score géométrique strictement domine le score scalaire.
- Comparer les deux par Oracle (`oracle/oracle.py`) — si le score géométrique ne fait pas mieux, on revient au scalaire.

Tant que cette validation n'est pas faite, **le scalaire reste la formule officielle** du runtime, et ce document est la seule passerelle honnête vers le cadre théorique plus ambitieux.

## 7. Référence

- Amari, S. *Information Geometry and Its Applications*, 2016 — pour la métrique de Fisher.
- Brody & Hughston, *Geometric quantum mechanics* — pour CP^(n−1) muni de Fubini–Study.
- `audit/SKILL_ORACLE_ARCHITECTURE.md §4` — pour la dérivation de la formule scalaire actuelle.

---

**TL;DR** : la formule de cohérence du runtime est une heuristique scalaire utile et auditable. Elle n'est pas la métrique de Fisher. Le cadre Zoran propose la métrique comme horizon, le runtime livre une projection 1D opérationnelle. La distinction est dans ce document, pas masquée.
