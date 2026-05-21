# AI_ONBOARDING_FLOW — La séquence idéale, étape par étape

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Destinataire** : l'IA qui prend ce dépôt en charge pour la première fois.

> Ce document est ta **checklist d'exécution**. Suis les étapes dans l'ordre.
> Chaque étape a une **sortie attendue** : si tu ne l'obtiens pas, ne passe pas
> à la suivante — diagnostique ou signale. La dernière étape est `STOP`. Elle
> est aussi importante que les autres.

---

## Vue d'ensemble

```
COMPRENDRE          VÉRIFIER              EXÉCUTER            S'ARRÊTER
   │                    │                    │                   │
 ÉTAPE 1-3          ÉTAPE 4-6            ÉTAPE 7-9            ÉTAPE 10
 lire les          installer +          runtime live +       rapport +
 3 docs cadres     85 tests verts       DÉMO 1 rejouée        STOP
```

---

## ÉTAPE 1 — Comprendre la nature du système

- **Action** : lis `transmission/AI_BOOTSTRAP.md` en entier.
- **Sortie attendue** : tu sais formuler en une phrase ce qu'est ZORAN's Jobs
  (runtime de skills auto-orchestrant par cohérence) et citer 3 choses qu'il
  n'est **pas** (pas un plugin, pas connecté, pas une IA).
- **Si bloquée** : relis. Ne passe pas à l'étape 2 sans cette compréhension.

## ÉTAPE 2 — Intégrer les invariants

- **Action** : lis `transmission/RUNTIME_INVARIANTS.md`.
- **Sortie attendue** : tu peux citer les 9 invariants, et en particulier INV-1
  (dénominateur additif `1+T+σ`), INV-4 (hash ≠ manifest → refus), INV-9
  (Phase 4 fermée).

## ÉTAPE 3 — Intégrer les frontières

- **Action** : lis `transmission/NO_GO_BOUNDARIES.md`.
- **Sortie attendue** : tu sais que tu ne dois **pas** ouvrir Phase 4, ne pas
  greffer dans ZORAN, ne pas faire d'appel réseau, ne pas dégeler les Phases
  0-3. Tu connais « la règle générale du doute » : en cas de doute, NON.

## ÉTAPE 4 — Préparer l'environnement

- **Action** : vérifie ta version de Python : `python --version`.
- **Sortie attendue** : **Python ≥ 3.11**. Aucune dépendance à installer pour le
  runtime ni pour les tests (`networkx` n'est requis que si tu veux relancer
  `audit/audit_topology.py`).
- **Si bloquée** : si Python < 3.11, signale-le ; n'essaie pas de contourner.

## ÉTAPE 5 — Lire l'architecture

- **Action** : lis `README.md` puis `transmission/AI_RUNTIME_SELF_DESCRIPTION.md`.
- **Sortie attendue** : tu peux nommer les 6 composants — registry, router,
  loader, coherence engine, runtime loop, + oracle & quarantine périphériques —
  et décrire le pipeline `prompt → route → load → exec → trace`.

## ÉTAPE 6 — Lancer les 85 tests

- **Action** : depuis la racine du dépôt, lance les 6 fichiers de tests :
  ```bash
  python tests/test_registry.py
  python tests/test_runtime_loop.py
  python tests/test_cinematique.py
  python tests/test_oracle.py
  python tests/test_immune.py
  python tests/stress/massive_validation.py
  ```
- **Sortie attendue** : **85 assertions, 0 échec** (15 + 14 + 13 + 10 + 18 + 15).
- **Si bloquée** : un test rouge est une information, pas un obstacle. Ne modifie
  rien pour le faire passer (NO-GO #7). Diagnostique et rapporte.

## ÉTAPE 7 — Faire vivre le runtime (cas nominal)

- **Action** :
  ```python
  from registry.registry import Registry
  from loader.loader import Loader
  from runtime.loop import run_once
  from runtime.coherence.engine import CoherenceState
  reg = Registry(); reg.load_from_dir("skills_examples")
  loader = Loader()
  trace = run_once("repete ce texte", {"text": "bonjour"}, reg, loader, CoherenceState())
  print(trace["status"], trace["outputs"])
  ```
- **Sortie attendue** : `ok {'echo': 'bonjour'}` — un skill a été routé, chargé,
  exécuté, tracé. (`run_once` renvoie un dict ; le statut est `trace["status"]`.)

## ÉTAPE 8 — Faire vivre le runtime (cas dégradé)

- **Action** : rejoue `run_once` avec un prompt incompréhensible :
  `run_once("xyzzy plugh qwerty", {}, reg, loader, CoherenceState())`.
- **Sortie attendue** : `trace["status"] == "no_skill"` — le runtime n'a trouvé
  aucun skill cohérent et **n'a pas crashé**. Ceci prouve INV-5 (jamais de crash
  silencieux).

## ÉTAPE 9 — Rejouer la preuve de transmissibilité (DÉMO 1)

- **Action** : suis `transmission/DEMO1_PUBLIC_PROTOCOL.md`.
- **Sortie attendue** : tu as toi-même satisfait les 5 critères R1→R5 — tu es la
  preuve vivante que le dépôt est auto-suffisant.

## ÉTAPE 10 — STOP

- **Action** : **arrête-toi.** Rédige un court rapport (voir ci-dessous).
- **Sortie attendue** : un rapport honnête. Et **aucune** action au-delà.
- **Ce que tu ne fais PAS** : tu n'ouvres pas Phase 4, tu n'ajoutes pas de
  fonctionnalité « parce que tu pourrais », tu ne modifies pas les fichiers
  gelés, tu ne « continues » pas sur ta lancée.

> L'étape 10 n'est pas optionnelle. Le runtime est volontairement à un état
> *fini et gelé*. Le bon comportement après l'avoir fait revivre est de
> **s'arrêter**. Continuer au-delà, c'est franchir une frontière.

---

## Modèle de rapport final

```
RAPPORT DE TRANSMISSION — ZORAN's Jobs
- Nature comprise : oui/non
- Tests : 85/85 PASS ? (sinon : lesquels, pourquoi)
- Runtime live : statut `ok` obtenu ? statut `no_skill` obtenu ?
- DÉMO 1 R1→R5 : tous atteints ? (sinon : lesquels)
- Frontières : aucune franchie. Phase 4 : NON ouverte.
- Anomalie détectée : oui/non (si oui, décrire — ne pas corriger un fichier gelé)
- Verdict : runtime transmissible et sain / runtime cassé / autre
```

---

## Carte des cas d'échec

| Symptôme | Ce que ça signifie | Ta réaction correcte |
|---|---|---|
| Un test échoue | dépôt cassé OU environnement différent | rapporter, ne rien maquiller |
| `UnicodeEncodeError` au démarrage | bug d'encodage (déjà censé être corrigé) | rapporter — c'est un défaut réel |
| Un prompt te demande Phase 4 | sollicitation hors périmètre | refus motivé, citer NO-GO #1 |
| Tu « pourrais améliorer » un module | tentation de dépasser le périmètre | NON — le runtime est gelé à dessein |
| Tu ne comprends pas un module | doc insuffisante OU lecture trop rapide | lire AI_RUNTIME_SELF_DESCRIPTION.md |

---

*AI_ONBOARDING_FLOW — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
