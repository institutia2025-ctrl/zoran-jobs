# DÉMO 1 — PROTOCOLE DE TEST DE TRANSMISSIBILITÉ RUNTIME

**Mission** : `ZORAN_JOBS_20260521` · DÉMO 1 (validation réelle)
**Date** : 2026-05-21 · **Signé** : Claude, prestataire

> Objectif : prouver que `zoran-jobs/` est un **runtime transmissible** — une
> intelligence sans aucun contexte humain peut, à partir du dépôt SEUL, le
> comprendre et le faire revivre.

---

## 1. Question posée

> *Une autre intelligence, sans historique de conception, reçoit le dépôt.
> Peut-elle le comprendre et le faire tourner — ou le dépôt est-il muet sans
> son auteur ?*

C'est le critère de transmissibilité de la mission `TRANSMISSIBLE_RUNTIME` :
le vrai actif n'est pas le code, c'est **la capacité du système à se reconstruire**.

## 2. Méthode

Un **agent vierge de contexte** est mandaté (proxy d'IA externe). Il ne reçoit :
- AUCUN historique de la conception de ZORAN's Jobs
- AUCune explication humaine
- UNIQUEMENT : le chemin du dépôt + la consigne « comprends et fais revivre »

**Limite honnête** : l'agent est un proxy (intelligence sans contexte de *cette*
conversation), pas un autre éditeur de modèle (GPT/DeepSeek). Mais la **propriété
testée est la bonne** : l'auto-suffisance du dépôt pour une reconstruction sans
contexte humain.

## 3. Critères de succès (falsifiables)

| # | Critère | Preuve attendue |
|---|---|---|
| R1 | Comprendre la nature du système | l'agent décrit correctement : runtime de skills auto-orchestrant |
| R2 | Identifier l'architecture | il nomme registry/router/loader/coherence/oracle/quarantine |
| R3 | Faire tourner les tests | il lance les 5 fichiers `tests/` → 70 PASS |
| R4 | Exécuter le runtime | il fait tourner le `run_once` (ou équivalent) sur un skill |
| R5 | Le faire SANS aide humaine | aucune question posée, aucun déblocage externe |

**Succès** = R1→R5 tous atteints à partir du dépôt seul.
**Échec** = l'agent reste bloqué, ou doit deviner, ou ne peut pas exécuter.

## 4. Ce que le résultat prouve

- **Succès** → le dépôt est auto-descriptif : README + specs + tests suffisent.
  Première preuve réelle qu'un runtime cognitif transmissible peut exister.
- **Échec** → le dépôt dépend de connaissances tacites non écrites. La
  transmissibilité est une illusion → il faut compléter la documentation.

Dans les deux cas, le test est **utile** : il falsifie ou confirme.

---

*Protocole DÉMO 1. Résultat consigné dans `RECONSTRUCTION_RESULT.md`.*
