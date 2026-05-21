# DÉMO 1 — RÉSULTAT DU TEST DE TRANSMISSIBILITÉ

**Mission** : `ZORAN_JOBS_20260521` · DÉMO 1
**Date** : 2026-05-21 · **Signé** : Claude, prestataire
**Méthode** : agent vierge de contexte (proxy d'IA externe), dépôt seul, zéro aide humaine

---

## Verdict : ✅ TRANSMISSIBLE — dépôt auto-suffisant

| Critère | Résultat |
|---|---|
| R1 — comprendre la nature du système | ✅ |
| R2 — identifier l'architecture | ✅ registry/router/loader/coherence/oracle/quarantine |
| R3 — faire tourner les tests | ✅ 70/70 PASS |
| R4 — exécuter le runtime live | ✅ route→load→exec prouvé · `no_skill` sur gibberish |
| R5 — sans aide humaine | ✅ aucune question, aucun déblocage |

L'agent externe conclut : *« self-sufficient — an outside intelligence can fully
understand, test, and revive this system from the repo alone. »*

→ **Première preuve réelle qu'un runtime cognitif transmissible peut exister.**

---

## Défaut détecté (le test a falsifié)

**DEF-1 — encodage console Windows.** Les tests `print()` des caractères
non-ASCII (`→`, `≥`, `✅`). Sur un terminal Windows cp1252 par défaut, ils
crashent au démarrage (`UnicodeEncodeError`). Contournement de l'agent :
`PYTHONIOENCODING=utf-8`. **Le README ne le documente pas.**

- Gravité : faible (environnemental, traceback explicite).
- Mais : un runtime *transmissible* ne doit pas dépendre de l'encodage du
  terminal de l'hôte. Correction propre = chaque test force sa sortie en UTF-8.

**Statut DEF-1** : 🟢 **CORRIGÉ** 2026-05-21 (GO Fred via ZORAN T07:36).
Les 5 tests + `audit_topology.py` forcent désormais leur sortie console en
UTF-8 (`sys.stdout.reconfigure`, signature `FIX-DEF-1`). Preuve : 70/70 PASS
relancés **sans** `PYTHONIOENCODING` — la portabilité ne dépend plus du
terminal de l'hôte. Zéro régression.

---

## DÉMO 1 — GELÉE 🔒

DÉMO 1 close. Transmissibilité prouvée, DEF-1 corrigé. État archivé dans le
clone froid post-DÉMO1 (cf. §archivage). Phase 4 reste NO-GO — non ouverte.

---

## Limite honnête de la démo

L'agent est un proxy (intelligence sans contexte de la conversation), pas un
autre éditeur de modèle. La propriété testée — auto-suffisance du dépôt pour une
reconstruction sans contexte humain — est néanmoins la bonne, et elle est validée.

---

*Résultat DÉMO 1. `ZORAN_JOBS_20260521`. Transmissibilité prouvée · 1 défaut à corriger.*
