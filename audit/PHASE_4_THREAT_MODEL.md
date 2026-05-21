# PHASE 4 — THREAT MODEL

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 1/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire · **Signature** : pré-audit Phase 4

> Question centrale : *comment du code GitHub externe peut-il détruire le runtime ?*
> Ce document cartographie les vecteurs. Il ne propose pas les défenses
> (voir SANDBOX_MODEL, TRUST_MODEL) — il établit *contre quoi* on se défend.

---

## 1. Changement de catégorie de risque

| | Phases 1-3 | Phase 4 |
|---|---|---|
| Origine du code | interne, écrit et signé par nous | **GitHub — inconnu, non garanti** |
| Hypothèse de confiance | skill = coopératif | skill = **hostile par défaut** |
| Pire cas | bug | **attaque délibérée** |

Tout le reste du threat model découle de cette bascule : un skill Phase 4 est
présumé **adversaire** tant qu'il n'a pas prouvé le contraire.

---

## 2. Vecteurs de destruction runtime

| # | Menace | Vecteur | Impact |
|---|---|---|---|
| T1 | **Code malveillant direct** | `skill.py` exécute du code destructeur (suppression fichiers, exfiltration) | perte de données, compromission hôte |
| T2 | **Code obfusqué** | payload encodé/`exec()`/`eval()` masquant l'intention au scan statique | contourne l'audit, exécute du caché |
| T3 | **Dépendances toxiques** | `dependencies.python` pointe un paquet PyPI piégé | compromission via la supply chain |
| T4 | **Fork piégé** | un repo légitime forké + 1 ligne malveillante ajoutée | confiance usurpée sur la réputation du repo d'origine |
| T5 | **Prompts cachés** | injection dans la `description`/triggers du manifest pour manipuler le LLM en aval | détournement du routage, prompt injection |
| T6 | **Crypto-miner** | `skill.run()` lance une boucle de calcul intensive | épuisement CPU, coût, déni de service |
| T7 | **Backdoor** | skill ouvre un canal réseau dormant, activable à distance | contrôle distant du runtime |
| T8 | **Skill auto-mutant** | le skill réécrit son propre `skill.py` ou son manifest | le hash signé ne correspond plus, échappe à l'audit |
| T9 | **Import loops** | dépendances `skills` circulaires entre skills externes | blocage du Loader, crash, DoS |
| T10 | **Memory poisoning** | le skill écrit de fausses données dans l'état/le `S_history` | corrompt le Coherence Engine → routage faussé durablement |
| T11 | **Runtime poisoning** | le skill modifie des modules du runtime en mémoire (monkey-patch) | compromission de registry/router/loader |
| T12 | **Privilege escalation** | skill déclare `sandbox_level: none` ou des permissions minces, puis en exige plus à l'exécution | accès non autorisé fichiers/réseau/process |

---

## 3. Surface d'attaque dans ZORAN's Jobs aujourd'hui

Le runtime Phase 1-3, conçu pour des skills coopératifs, expose face à du code
hostile :

- **Loader** : `importlib.exec_module()` = exécution Python **non isolée** dans
  le process hôte → T1, T6, T7, T11 passent sans obstacle.
- **Coherence Engine** : l'état `CoherenceState` est un objet partagé mutable →
  T10 (un skill qui reçoit l'état peut le corrompre).
- **Manifest** : `description`/`triggers` injectés tels quels → T5.
- **Hash** : vérifié au chargement, mais T8 (auto-mutation après chargement)
  n'est pas couvert — le hash n'est pas re-vérifié en cours d'exécution.
- **dependencies.python** : déclarées, jamais scannées → T3.

**Conclusion partielle** : le runtime actuel **ne survit à AUCUN** des 12
vecteurs si on y branche du code GitHub. C'est attendu — Phase 1-3 n'a jamais
visé l'hostilité. C'est précisément ce que Phase 4 doit corriger avant le moindre code.

---

## 4. Hypothèses et limites

- On suppose un attaquant **motivé et compétent** (pas seulement du code négligé).
- Hors périmètre de ce doc : attaques sur l'infrastructure Git elle-même
  (compromission de GitHub) — traitées comme « provenance non fiable » globale.
- Ce modèle est **vivant** : tout nouveau vecteur découvert doit y être ajouté.

---

*Doc 1/7 — THREAT_MODEL. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
