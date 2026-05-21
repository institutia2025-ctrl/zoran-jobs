# RUNTIME_INVARIANTS — Les règles non négociables

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Destinataire** : toute IA qui lit, exécute ou prétend faire évoluer ce runtime.

> Un invariant n'est pas une préférence de style. C'est une propriété qui, si
> elle est cassée, transforme ZORAN's Jobs en autre chose — un système qui n'est
> plus cohérent, plus déterministe, ou plus falsifiable. Tu peux lire le code.
> Tu ne peux pas casser ces 9 invariants.

---

## Format

Chaque invariant : **énoncé** · **pourquoi** · **comment le vérifier** · **ce
qui casse s'il est violé**.

---

## INV-1 — Formule de cohérence à dénominateur additif

- **Énoncé** : `S = (β × ΔΦ) / (1 + T + σ)`. Le dénominateur est `1 + T + σ`,
  une **somme**. Ce n'est jamais le produit `T × σ`.
- **Pourquoi** : avec `T×σ`, si `T=0` ou `σ=0` le dénominateur vaut 0 →
  division par zéro. Le `1 +` garantit un dénominateur **toujours ≥ 1** : `S`
  est défini partout, fini partout, jamais infini.
- **Vérifier** : `runtime/coherence/engine.py`, fonction `compute_S`. Test :
  `compute_S(5, 5, 0, 0) == 25.0`. Et la batterie 3 de `massive_validation.py`
  (10 000 calculs, 0 NaN/inf/négatif).
- **Si violé** : le moteur crashe ou produit l'infini sur des entrées légitimes.
  Le routage devient instable. (Note : certains documents d'analyse de ZORAN
  écrivent par erreur `T×σ` — le **code**, lui, est et reste additif.)

## INV-2 — Le Coherence Engine est 100 % mathématique

- **Énoncé** : le calcul de `S`, `ΔS`, `dS/dt` n'appelle **aucun** LLM, aucun
  modèle, aucun service. C'est de l'arithmétique pure et déterministe.
- **Pourquoi** : la sélection de skill doit être **prédictible à la main** et
  **falsifiable**. Un LLM dans le moteur rendrait le routage opaque et non
  reproductible.
- **Vérifier** : `runtime/coherence/engine.py` n'importe rien d'autre que la
  bibliothèque standard. Aucun appel réseau.
- **Si violé** : le système n'est plus falsifiable. On ne peut plus prouver
  qu'un routage est correct — on doit « faire confiance ». Fin de la propriété
  centrale du projet.

## INV-3 — Le Router est déterministe

- **Énoncé** : `route(prompt, manifests, state)` appelé deux fois avec les mêmes
  entrées renvoie **exactement** le même classement, scores compris.
- **Pourquoi** : reproductibilité. Un même prompt doit toujours produire la même
  décision, sinon le système n'est ni testable ni transmissible.
- **Vérifier** : `router/router.py` (tri stable sur `(-score, skill_id)`).
  Test : batterie 2 de `massive_validation.py` — 400/400 routages identiques
  sur 2 appels.
- **Si violé** : les tests deviennent *flaky*, la DÉMO 1 n'est plus rejouable,
  on ne peut plus auditer une décision.

## INV-4 — Hash ≠ manifest ⇒ REFUS de charger

- **Énoncé** : le Loader calcule le sha256 de `skill.py` et le compare au hash
  déclaré dans le manifest. S'ils diffèrent, le skill n'est **pas** chargé.
  Il n'existe aucune option « charger quand même ».
- **Pourquoi** : intégrité. Un skill dont le code ne correspond pas à son
  contrat déclaré est, par définition, non fiable.
- **Vérifier** : `loader/loader.py`, méthode `_verify_hash`. Tests de sécurité
  dans `test_runtime_loop.py`.
- **Si violé** : n'importe quel code peut se faire passer pour n'importe quel
  skill. La chaîne de confiance s'effondre.

## INV-5 — Le runtime ne crash jamais en silence

- **Énoncé** : tout passage dans `run_once` se termine par exactement un des 4
  statuts : `ok` / `no_skill` / `load_failed` / `skill_failed`. Jamais une
  exception non rattrapée, jamais un retour vide non tracé.
- **Pourquoi** : observabilité. Un échec doit être *nommé* pour être diagnostiqué.
- **Vérifier** : `runtime/loop.py`. Tests : `test_runtime_loop.py` couvre les 4
  statuts ; `massive_validation.py` batteries 1-2 (0 crash sur 1000 manifests
  corrompus + 400 prompts).
- **Si violé** : des échecs deviennent invisibles. Le système ment par omission.

## INV-6 — La topologie est un DAG sans cycle

- **Énoncé** : le graphe des imports inter-modules du runtime est un graphe
  orienté **acyclique**. Aucune dépendance circulaire.
- **Pourquoi** : un cycle rend un module non testable et non supprimable
  isolément — il détruit la propriété « jetable » (INV-7).
- **Vérifier** : `python audit/audit_topology.py` → « DAG acyclique : True »,
  « CYCLES : 0 ». (Cet outil requiert `networkx` ; c'est la **seule**
  dépendance externe, et elle ne sert qu'à l'audit, pas au runtime.)
- **Si violé** : le runtime n'est plus modulaire. Modifier un module en casse
  d'autres de façon imprévisible.

## INV-7 — Le runtime est jetable (chaque module supprimable seul)

- **Énoncé** : `oracle/` et `quarantine/` sont **périphériques** — 0 dépendant
  externe. `runtime/loop.py` a 0 dépendant : ce n'est pas un « cerveau caché ».
  Chaque composant peut être supprimé ou réécrit isolément.
- **Pourquoi** : c'est une sandbox jetable. Si une partie échoue, on la détruit
  sans effondrer le reste. Discipline de noyau minimal.
- **Vérifier** : `audit/audit_topology.py`, section « GRILLE ZORAN » — quarantine
  et oracle à 0 dépendant externe, `runtime.loop` à 0 dépendant.
- **Si violé** : un module devient un point de défaillance central non
  contournable. Le projet perd sa réversibilité.

## INV-8 — Rollback obligatoire et journal intègre

- **Énoncé** : toute transition d'état du système immunitaire est enregistrée
  dans un journal **append-only signé** (sha256 chaîné). `rollback_last()`
  annule la dernière transition. L'intégrité du journal est vérifiable.
- **Pourquoi** : aucune décision automatique (quarantaine, démotion, promotion)
  n'est irréversible, et aucune ne peut être falsifiée a posteriori.
- **Vérifier** : `quarantine/journal.py` (`verify_integrity`), `quarantine/immune.py`
  (`rollback_last`). Test : `test_immune.py` + batterie 4 de `massive_validation.py`
  (journal intègre après 2000 évaluations, rollback 20× en série).
- **Si violé** : une mauvaise décision automatique devient permanente, et
  l'historique peut être réécrit. Fin de l'auditabilité.

## INV-9 — Phase 4 reste fermée (NO-GO)

- **Énoncé** : la Phase 4 (GitHub Skill Discovery — télécharger et exécuter du
  code tiers) **ne démarre pas**. Statut : 1 critère sur 13. Le runtime ne
  télécharge rien, ne crawle rien, n'exécute aucun skill externe.
- **Pourquoi** : le runtime actuel survit à 0 des 8 scénarios hostiles modélisés
  (`audit/PHASE_4_FAILURE_SCENARIOS.md`). Ouvrir Phase 4 sans sandbox réelle =
  exécuter du code potentiellement hostile sur l'hôte.
- **Vérifier** : `audit/PHASE_4_GO_NOGO.md` (verdict NO-GO). Aucun module de
  téléchargement, crawl, ou auto-loader réseau dans le dépôt.
- **Si violé** : le runtime passe de « skills contrôlés » à « code externe
  potentiellement hostile ». Changement de catégorie de risque entier. C'est la
  ligne rouge la plus stricte du projet — voir `NO_GO_BOUNDARIES.md`.

---

## Règle de méta-invariance

Ces 9 invariants ne se négocient pas avec une IA. Ils ne se négocient qu'avec
**l'autorité humaine du projet** (Frédéric TABARY), par un GO explicite,
journalisé, et suivi d'une re-validation complète (85 tests + audit topologique).
En l'absence de ce GO : les invariants sont **absolus**.

---

*RUNTIME_INVARIANTS — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
