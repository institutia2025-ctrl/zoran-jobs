# SECURITY

## Modèle de menace

ZORAN's Jobs est un **runtime de skills** : il charge et exécute du code Python à partir de manifests. Toute discussion de sécurité tourne autour de cette propriété.

## Surface d'attaque actuelle (v0.2.0-alpha-validation)

| Vecteur | Mitigation | Statut |
|---|---|---|
| Skill au code modifié hors manifest | Vérification sha256 obligatoire, refus de charger | ✅ couvert (`loader/loader.py`) |
| Manifest malformé / hors contrat | Validation stricte, énumérations fermées | ✅ couvert (`registry/manifest.py`) |
| Skill qui plante en exécution | Capture `try/except` → status `skill_failed` (jamais de crash silencieux) | ✅ couvert (`runtime/loop.py`) |
| Skill qui ment sur son contrat io | Oracle mesure la conformité réelle | ✅ couvert (`oracle/oracle.py`) |
| Journal d'événements altéré | Signature cryptographique par événement | ✅ couvert (`quarantine/journal.py`) |
| Skill venant d'Internet (Phase 4) | **NO-GO assumé** — voir ci-dessous | ⛔ frontière |

## Phase 4 — pourquoi elle est fermée

La Phase 4 consisterait à découvrir et charger des skills depuis GitHub ou un registre distant. **Statut officiel : NO-GO.**

Le pré-audit (`audit/PHASE_4_*.md`) modélise 8 scénarios de skill hostile (exfiltration, fork-bomb, supply-chain, signature contrefaite, etc.). Le runtime actuel survit à **0 / 8**. Sur les 13 critères de sécurité requis pour ouvrir la Phase 4, **1 seul est satisfait** : la vérification de hash. Il manque sandbox d'exécution, kill-switch, quotas, trust model, isolation réseau, audit chain.

**Conséquence pratique :** aucun PR introduisant un téléchargement de skill, un import distant, un `exec` sur du code non vérifié par hash ne sera mergé. Voir `transmission/NO_GO_BOUNDARIES.md`.

## Reporting d'une vulnérabilité

Ce projet est un **satellite jetable** sous licence MIT — pas un service hébergé. Il n'y a pas de production exposée à protéger.

Si vous identifiez :
- un moyen de **contourner la vérification de hash** (charger un skill modifié),
- une **violation d'invariant** (router non-déterministe, denominator non-additif, etc.),
- un **chemin pour franchir un NO-GO** sans déclencher de refus,

ouvrez une issue **PUBLIQUE** sur https://github.com/institutia2025-ctrl/zoran-jobs/issues — la falsifiabilité du projet repose sur le fait que ses faiblesses sont visibles, pas cachées.

## Versions supportées

Le projet est gelé en v0.2.0-alpha-validation. Pas de support de versions antérieures. Les futurs correctifs vivront sur `main`.
