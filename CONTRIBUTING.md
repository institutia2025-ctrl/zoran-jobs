# CONTRIBUTING

> Avant d'ouvrir une PR, lis `transmission/AI_BOOTSTRAP.md` (si tu es une IA) ou `transmission/HUMAN_HANDOFF.md` (si tu es humain). Tu sauras si ta contribution est dans le périmètre.

## Le périmètre

Ce dépôt est un **satellite jetable**. Sa valeur n'est pas dans ce qu'il fait — c'est dans ce qu'il **prouve** : qu'un runtime de skills peut rester cohérent, déterministe, falsifiable, transmissible.

Les contributions bienvenues sont celles qui **renforcent une de ces 4 propriétés**. Les contributions qui ajoutent des fonctionnalités au prix d'une propriété centrale seront refusées.

## Invariants — non négociables

9 invariants listés dans `transmission/RUNTIME_INVARIANTS.md`. Aucune PR ne peut en casser un. Si tu penses qu'un invariant doit évoluer, ouvre d'abord une issue avec ta démonstration.

## NO-GO — frontières

3 frontières listées dans `transmission/NO_GO_BOUNDARIES.md`. Aucune PR qui franchit un NO-GO ne sera mergée. Phase 4 reste fermée.

## Avant de soumettre

1. **Toutes les suites de tests passent en local** : 97 PASS / 0 FAIL (85 historiques + 12 unit).
   ```bash
   python tests/test_registry.py
   python tests/test_runtime_loop.py
   python tests/test_cinematique.py
   python tests/test_oracle.py
   python tests/test_immune.py
   python tests/stress/massive_validation.py
   python tests/test_coherence_unit.py
   ```
2. **Ruff passe sans warning** : `pip install ruff && ruff check .`
3. **Si tu ajoutes un skill** : il a un manifest conforme au contrat, son hash sha256 est exact, il a un test négatif (cas où il échoue) en plus du cas heureux.
4. **Si tu modifies un composant noyau** (registry, router, loader, runtime, coherence) : tu ajoutes des assertions qui prouvent que l'invariant correspondant tient toujours.

## Style

- Stdlib only pour le runtime (zéro dépendance externe).
- `from __future__ import annotations` en tête de fichier.
- Docstrings explicites, en français ou en anglais, jamais les deux dans un même fichier.
- Pas de magie implicite : si un champ manque, erreur explicite, pas valeur devinée.

## Signatures

Toute PR doit être signée par un humain identifiable. Si tu es une IA agissant pour un humain, l'humain doit confirmer la PR en commentaire avec son identité.

— Frédéric TABARY · 2026-05-21
