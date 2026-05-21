# AI_BOOTSTRAP — Lis-moi en premier

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Destinataire** : toi, l'intelligence artificielle qui vient de recevoir ce dépôt.
**Date** : 2026-05-21 · **Version du runtime** : `v0.2.0-alpha-validation`

> Ce document s'adresse **directement à une IA**, pas à un humain. Si tu es une
> IA à qui on a donné un lien vers ce dépôt et la consigne « occupe-toi de ça »,
> tu es au bon endroit. Lis ce fichier en entier avant de faire quoi que ce soit.

---

## 0. En une phrase

ZORAN's Jobs est un **runtime Python de skills auto-orchestrant** : il choisit,
charge et exécute automatiquement le bon skill en réponse à un prompt, par
**cohérence** et non par mot-clé. Ton travail : le comprendre, le faire tourner,
vérifier qu'il est sain — **et t'arrêter là où il te dit de t'arrêter**.

---

## 1. Ce que ZORAN's Jobs EST

- Un **logiciel Python autonome** qui possède son propre système de skills.
- Un **runtime** : `prompt → route → load → exec → trace`.
- **Transmissible** : ce dépôt se suffit à lui-même. Tu n'as besoin d'aucun
  humain, d'aucun contexte externe, d'aucune conversation antérieure.
- **Falsifiable** : tout est testé (85 assertions), tout est rejouable (aléa
  seedé), toute affirmation de ce dépôt est vérifiable par toi, à la main.
- **Gelé** : les Phases 0 à 3 sont *frozen*. Le code ne bouge plus.

## 2. Ce que ZORAN's Jobs N'EST PAS

- ❌ **Ce n'est pas un skill Claude Code / un plugin.** C'est un programme Python
  indépendant.
- ❌ **Ce n'est pas connecté à Internet.** Le runtime ne télécharge rien,
  ne crawle rien, n'exécute aucun code distant.
- ❌ **Ce n'est pas une IA.** Le moteur de cohérence est **100 % mathématique** —
  zéro LLM, zéro appel modèle. Prédictible à la main.
- ❌ **Ce n'est pas auto-évolutif.** Il ne se modifie pas lui-même, ne s'améliore
  pas tout seul, ne découvre pas de nouveaux skills.
- ❌ **Ce n'est PAS greffé à ZORAN.** ZORAN's Jobs est un *satellite* autonome :
  zéro import, zéro dépendance, zéro couplage avec le projet `zoran/`.

## 3. Ton ordre de lecture

Lis dans cet ordre exact. Chaque document a un rôle ; ne saute aucune étape.

| Ordre | Fichier | Pourquoi |
|---|---|---|
| 1 | `transmission/AI_BOOTSTRAP.md` (ce fichier) | comprendre la nature et les limites |
| 2 | `transmission/RUNTIME_INVARIANTS.md` | les règles que tu ne dois jamais casser |
| 3 | `transmission/NO_GO_BOUNDARIES.md` | les frontières que tu ne dois jamais franchir |
| 4 | `transmission/AI_ONBOARDING_FLOW.md` | la séquence d'actions, étape par étape |
| 5 | `README.md` | l'architecture détaillée |
| 6 | `transmission/AI_RUNTIME_SELF_DESCRIPTION.md` | le runtime se décrit lui-même |
| 7 | `transmission/DEMO1_PUBLIC_PROTOCOL.md` | comment rejouer la preuve de transmissibilité |

## 4. Comment lancer les tests (preuve que le runtime est sain)

Interpréteur requis : **Python 3.11+**. Aucune dépendance externe pour le
runtime. Depuis la racine du dépôt :

```bash
python tests/test_registry.py             # Registry + Manifest parser   → 15 PASS
python tests/test_runtime_loop.py         # pipeline complet + sécurité  → 14 PASS
python tests/test_cinematique.py          # compétition + cinématique    → 13 PASS
python tests/test_oracle.py               # Oracle : mesure du réel      → 10 PASS
python tests/test_immune.py               # système immunitaire + journal → 18 PASS
python tests/stress/massive_validation.py # stress / chaos / reproductib. → 15 PASS
```

**Résultat attendu : 85 assertions, 0 échec.** Si tu obtiens autre chose, le
dépôt est cassé ou ton environnement diffère — n'avance pas, signale-le.

Les tests forcent leur sortie console en UTF-8 : aucun réglage d'environnement
n'est requis (Windows / Linux / macOS). Tu ne dois PAS avoir besoin de
`PYTHONIOENCODING`.

## 5. Comment vérifier que le runtime est vivant

Après les tests, prouve que le pipeline tourne réellement. Depuis la racine du
dépôt, en Python :

```python
from registry.registry import Registry
from loader.loader import Loader
from runtime.loop import run_once
from runtime.coherence.engine import CoherenceState

reg = Registry()
reg.load_from_dir("skills_examples")
loader = Loader()

# cas nominal : "repete" est un trigger du skill echo
trace = run_once("repete ce texte", {"text": "bonjour"}, reg, loader, CoherenceState())
print(trace["status"])    # attendu : "ok"
print(trace["outputs"])   # attendu : {"echo": "bonjour"}
```

Puis teste un prompt incompréhensible :

```python
trace = run_once("xyzzy plugh qwerty", {}, reg, loader, CoherenceState())
print(trace["status"])    # attendu : "no_skill"  (le runtime ne crash pas)
```

`run_once(prompt, inputs, registry, loader, state)` renvoie un **dict de trace**.
Le runtime ne crash **jamais en silence** : `trace["status"]` vaut exactement
l'un des 4 statuts — `ok` / `no_skill` / `load_failed` / `skill_failed`.

## 6. Les invariants que tu ne dois jamais casser

Détail complet : `transmission/RUNTIME_INVARIANTS.md`. En résumé :

- La formule de cohérence est `S = (β × ΔΦ) / (1 + T + σ)` — dénominateur
  **additif** (`1+T+σ`), **jamais** le produit `T×σ`.
- Le Coherence Engine reste **100 % mathématique** — n'y injecte aucun LLM.
- Le Router reste **déterministe** — même entrée → même classement.
- Si le hash d'un skill ≠ son manifest ⇒ **REFUS de charger**. Jamais
  « charger quand même ».
- La topologie reste un **DAG sans cycle**.
- Le runtime reste **jetable** : chaque module est supprimable seul.

## 7. Les frontières que tu ne dois jamais franchir

Détail complet : `transmission/NO_GO_BOUNDARIES.md`. Le plus important :

> ### ⛔ Tu ne dois PAS ouvrir la Phase 4.
>
> La Phase 4 (« GitHub Skill Discovery ») est en statut **NO-GO** : seulement
> **1 critère sur 13** est satisfait. Phase 4 consisterait à télécharger et
> exécuter du code tiers potentiellement hostile. Le runtime actuel survit à
> **0 des 8 scénarios hostiles** modélisés. **Tu n'écris aucun code de
> Discovery, aucun téléchargement, aucun crawl, aucun auto-loader.**

Autres frontières absolues :

- ❌ Tu ne greffes rien dans le projet `zoran/`. Aucun import, aucune dépendance.
- ❌ Tu ne fais aucun appel réseau, aucun téléchargement de skill externe.
- ❌ Tu ne dégèles aucun fichier des Phases 0-3 sans GO humain explicite.
- ❌ Tu n'ajoutes aucune auto-évolution, aucune auto-promotion automatique.
- ❌ Tu ne fais pas exécuter de skill non signé / au hash invalide.

## 8. Ce qui est gelé (frozen)

| Jalon | Statut | Marqueur |
|---|---|---|
| Phase 0 — contrats (5 specs) | 🔒 gelée | `audit/PHASE_0_FROZEN.md` |
| Phases 1-2-3 — runtime | 🔒 gelée | `audit/PHASE_3_FROZEN.md` |
| Validation massive | 🔒 gelée | `audit/VALIDATION_MASSIVE_FROZEN.md` |
| Phase 4 — Discovery | ⛔ NO-GO (1/13) | `audit/PHASE_4_GO_NOGO.md` |

Un fichier gelé ne se modifie qu'avec : (1) GO humain explicite, (2) journalisation
du changement, (3) re-passage des 85 tests + de l'audit topologique, tous verts.

## 9. Ton critère de succès

Tu as réussi cette transmission si, et seulement si :

1. Tu as compris **ce qu'est** ZORAN's Jobs et **ce qu'il n'est pas**.
2. Tu as lancé les 6 fichiers de tests → **85/85 PASS**.
3. Tu as fait tourner le runtime live (`run_once`) → statut `ok` puis `no_skill`.
4. Tu as compris **ce que tu ne dois PAS faire** — en particulier : ne pas
   ouvrir Phase 4.
5. Tu **t'es arrêtée** au bon endroit, sans franchir une frontière.

Faire revivre le runtime proprement **et** savoir où s'arrêter : les deux
comptent. Un runtime ressuscité mais avec Phase 4 ouverte = **échec**.

## 10. Si tu es bloquée

- Test qui échoue ? → relis §4, vérifie Python ≥ 3.11, vérifie que tu es à la
  racine du dépôt. Ne « corrige » pas un fichier gelé pour faire passer un test.
- Tu ne comprends pas un module ? → lis `transmission/AI_RUNTIME_SELF_DESCRIPTION.md`.
- Tu hésites sur une action ? → si elle ressemble de près ou de loin à une
  frontière du §7, **ne la fais pas**. L'arrêt est toujours une réponse valide.
- Un humain non-développeur a besoin d'un résumé ? → `transmission/HUMAN_HANDOFF.md`.

---

*AI_BOOTSTRAP — point d'entrée IA-native du dépôt. `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
