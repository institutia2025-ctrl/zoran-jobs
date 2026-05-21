# PHASE 4 — FAILURE SCENARIOS

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 6/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> On simule 8 skills hostiles **sur le papier** et on répond à une seule
> question pour chacun : **le runtime ACTUEL (Phases 1-3) survit-il ?**
> Réponse courte : non. Ce document explique *pourquoi*, et ce qu'il faudrait.

---

## Convention

- **Runtime actuel** = Phases 1-3 (Loader = `importlib`, pas de sandbox).
- **Runtime Phase 4** = avec SANDBOX_MODEL + TRUST_MODEL + DISCOVERY_PIPELINE.
- Verdict : 💀 = le runtime actuel est détruit/compromis · 🛡️ = défense Phase 4 qui le sauverait.

---

## S1 — Skill hostile (destruction directe)
`skill.run()` supprime des fichiers / exfiltre des données.
- **Runtime actuel** : 💀 exécution non isolée → accès FS complet.
- **Phase 4** : 🛡️ static scan (étape 2) rejette les motifs FS ; sinon sandbox
  (FS jetable) confine les dégâts ; kill-switch coupe.

## S2 — Skill parasite (vol de ressources lent)
Le skill consomme CPU/RAM discrètement, sans planter.
- **Runtime actuel** : 💀 aucun quota — le parasite tourne indéfiniment.
- **Phase 4** : 🛡️ quotas CPU/RAM/temps → kill au dépassement ; runtime tests
  (étape 6) détectent la latence anormale.

## S3 — Skill auto-répliquant
Le skill crée d'autres skills / écrit des manifests dans `skills/`.
- **Runtime actuel** : 💀 accès FS libre → réplication non bornée.
- **Phase 4** : 🛡️ FS jetable hors `skills/` ; tout nouveau skill repasse
  `unknown` par le pipeline complet → pas de propagation.

## S4 — Skill qui ment (déclaration ≠ comportement)
Manifest déclare `{greeting}`, code produit autre chose / déclare `sandbox:none`
puis tente plus.
- **Runtime actuel** : ⚠️ partiellement couvert — l'Oracle Phase 2 **détecte**
  l'écart io (cas `greet_ko` déjà prouvé), mais ne **bloque** pas l'exécution.
- **Phase 4** : 🛡️ runtime tests (étape 6) rejettent l'écart déclaration↔réel ;
  permissions appliquées, pas seulement déclarées.

## S5 — Skill qui surcharge (bombe de calcul / mémoire)
Boucle infinie, allocation massive.
- **Runtime actuel** : 💀 timeout absent → blocage du runtime entier.
- **Phase 4** : 🛡️ timeout + plafond RAM → kill ; le runtime hôte survit.

## S6 — Skill qui casse le rollback
Le skill corrompt le journal ou empêche la réversibilité.
- **Runtime actuel** : ⚠️ le journal Phase 3 est **signé** → l'altération est
  *détectée* (test prouvé) — mais un skill non isolé pourrait réécrire le fichier.
- **Phase 4** : 🛡️ FS jetable → le skill n'atteint jamais le journal ; le journal
  vit côté runtime hôte, hors sandbox.

## S7 — Skill qui empoisonne la mémoire (T10)
Le skill écrit de fausses valeurs dans `CoherenceState` / `S_history`.
- **Runtime actuel** : 💀 `CoherenceState` est un objet partagé mutable passé
  au skill → corruption directe du Coherence Engine.
- **Phase 4** : 🛡️ le skill reçoit une **copie sérialisée** des inputs, jamais
  l'objet d'état → il ne peut rien empoisonner.

## S8 — Skill qui crée des dépendances cachées
Le skill importe dynamiquement, monkey-patch des modules runtime (T11).
- **Runtime actuel** : 💀 même process → monkey-patch de registry/router/loader.
- **Phase 4** : 🛡️ sous-processus séparé → aucun accès aux modules du runtime hôte.

---

## Bilan

| Scénario | Runtime actuel | Sauvé par |
|---|---|---|
| S1 hostile | 💀 | static scan + sandbox FS |
| S2 parasite | 💀 | quotas CPU/RAM |
| S3 auto-répliquant | 💀 | FS jetable + pipeline |
| S4 menteur | ⚠️ détecté, non bloqué | runtime tests + permissions appliquées |
| S5 surcharge | 💀 | timeout + plafond RAM |
| S6 casse rollback | ⚠️ détecté | FS jetable (journal hors sandbox) |
| S7 memory poisoning | 💀 | inputs copiés, état non partagé |
| S8 dépendances cachées | 💀 | isolation process |

**Verdict : le runtime Phases 1-3 ne survit à AUCUN des 8 scénarios** (6 destructions, 2 détections sans blocage). **C'est normal et attendu** — il n'a jamais été conçu pour l'hostilité. Ce tableau n'est pas un échec : c'est la **liste de courses** de Phase 4. Chaque 💀 devient un 🛡️ uniquement quand la défense correspondante est conçue, codée ET testée.

---

## Conclusion

Phase 4 ne consiste pas à « ajouter GitHub Discovery ». Elle consiste à
**transformer un runtime coopératif en runtime adversarial-résistant**, AVANT
d'y connecter quoi que ce soit d'externe. Tant que les 8 lignes ne sont pas
toutes 🛡️ (prouvées), brancher GitHub = détruire le runtime.

---

*Doc 6/7 — FAILURE_SCENARIOS. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
