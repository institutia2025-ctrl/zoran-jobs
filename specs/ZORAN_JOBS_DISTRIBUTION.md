# ZORAN_JOBS_DISTRIBUTION — Distribution des skills aux IA

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code
**Signé** : Claude Code, prestataire · **Livrable 6/8**

> Une IA ne reçoit que les skills utiles à sa mission. Pas le catalogue complet.

---

## 1. Objet

Le dépôt contient des dizaines de skills (`skills_examples/` : BTP, structure,
pathologies, méta, sauvegarde…). Transmettre le catalogue entier à chaque IA est
une duplication cognitive coûteuse et une source de dérive (une IA peut invoquer
un skill hors de son rôle). La distribution résout cela : chaque IA reçoit un
**sous-ensemble disjoint et minimal** de skills.

## 2. Règle de distribution

Pour chaque IA, l'orchestrateur calcule le sous-ensemble de skills tel que :
`domaine(skill) ∈ scope(IA)` **et** `manifest.routing.domain` compatible avec le
rôle. La distribution est **déterministe** : elle s'appuie sur le champ
`routing.domain` du manifest, déjà existant et validé.

## 3. Exemple — distribution par rôle

| IA | Skills reçus (domaines) | Skills NON reçus |
|---|---|---|
| IA Sécurité | threat model, sandbox, veto, `securite` | skills déco, planning chantier, BTP métier |
| IA Backend | runtime, `structure`, `exploitation`, tests | skills UI/UX, design |
| IA Structure (BTP) | `structure` : poteau, poutre, dalle, semelle, charges | pathologies, second œuvre, économie |
| IA Économie (BTP) | `economie` : métré, ratio, DPGF, situation | structure, sécurité runtime |
| IA Gouvernance | skills méta : gate, sélecteur lois/cadres, photo-clone | skills métier BTP |

## 4. Invariants

**Invariant ZD-1 — minimalité** : une IA reçoit le plus petit ensemble de skills
qui rend sa mission réalisable. Tout skill en plus est un NO-GO.

**Invariant ZD-2 — disjonction** : les ensembles de skills de deux IA sont
disjoints, sauf point de contact explicite arbitré par l'orchestrateur. (Déjà
appliqué dans ce dépôt : préfixes de skill_id disjoints entre lots parallèles.)

**Invariant ZD-3 — distribution déterministe** : même rôle + même domaine → même
ensemble de skills. Reproductible, auditable.

**Invariant ZD-4 — hash préservé** : un skill distribué garde son `manifest.hash`
sha256. Une IA ne charge un skill que si l'empreinte correspond — la distribution
ne désarme jamais la vérification du Loader (INV-4 du runtime).

## 5. Anti-pattern interdit

> « Donnons tous les skills à toutes les IA, elles n'utiliseront que les bons. »

Interdit. Une IA qui *voit* un skill hors rôle peut l'invoquer, raisonner dessus,
le citer — c'est du bruit, du coût, et un risque de conflit (cf.
`audit/INTER_AGENT_CONFLICTS.md`). Ce qu'une IA ne reçoit pas, elle ne peut pas
le dévoyer.

## 6. Traçabilité

Journalise : `mission_id`, IA, skills distribués (avec leur hash), skills
volontairement exclus (limites explicites), domaine de référence.

---

*Livrable 6/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
