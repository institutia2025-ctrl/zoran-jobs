# ZORAN's JOBS — ARCHITECTURE FONDATRICE

**Mission ID** : `ZORAN_JOBS_20260521`
**Date** : 2026-05-21
**Auteur** : Claude (prestataire)
**Commanditaire** : Frédéric TABARY (Institutia)
**Statut** : Phase 0 — Conception des contrats invariants

---

## 0. CADRE NON NÉGOCIABLE

ZORAN's Jobs est un **satellite de ZORAN** :

- ✅ Projet **100 % autonome** — vit **sans** ZORAN (indépendant) **ou avec** ZORAN (greffe future)
- ❌ **INTERDICTION FORMELLE** de greffer quoi que ce soit dans ZORAN maintenant
- ❌ Zéro import, zéro dépendance, zéro modification du repo `zoran/`
- 🛰️ Conçu **greffe-compatible** : on prévoit les interfaces d'amarrage, on ne les branche pas
- 🗑️ Sandbox **jetable** : si l'architecture est mauvaise, on détruit le satellite — ZORAN reste intact

Emplacement : `C:\Users\frede\Desktop\zoran-jobs\` — **hors** du repo `zoran/`.

---

## 1. CE QUE ZORAN's JOBS RÉSOUT

### Le problème
Les skills (Claude, ou tout système à capacités modulaires) fonctionnent aujourd'hui comme des **modules manuels** : il faut les connaître, les invoquer, les sélectionner soi-même. Avec 50, 500, 5000 skills → plus personne ne sait quoi appeler. **Ça ne scale pas.**

### La réponse
Un **runtime de skills auto-orchestrant** : l'utilisateur parle normalement, le runtime **choisit, charge et utilise** automatiquement les bons skills. Le user ne sélectionne plus rien.

### Ce qui distingue ZORAN's Jobs d'un router générique
Un router banal sélectionne par mots-clés / triggers. **ZORAN's Jobs sélectionne par cohérence** — c'est le cœur ZORAN du satellite (section 4).

---

## 2. PRINCIPE DE SÉPARATION

```
   interaction user          architecture cognitive interne
   ───────────────────  ≠   ──────────────────────────────────
   "connecte mon          registry + router + loader + oracle
    imprimante"           + sandbox + quarantine + coherence engine
```

Le user voit une conversation. Le runtime fait l'orchestration, **sans montrer la technique**.

---

## 3. COMPOSANTS

```
zoran-jobs/
├── runtime/             noyau — lifecycle, orchestration
│   ├── coherence/       ★ MOTEUR DE COHÉRENCE (section 4)
│   └── self-description/  le runtime se décrit lui-même (transmissibilité)
├── registry/            bibliothèque de skills + leurs manifests
├── router/              sélection automatique des skills
├── loader/              chargement dynamique (uniquement l'utile)
├── oracle/              comparaison/évaluation de skills concurrents
├── sandbox/             isolation d'exécution des skills
├── quarantine/          skills suspects mis en quarantaine
├── github/              découverte de skills externes (Phase 4)
├── ranking/             scoring de survie des skills
├── specs/               ★ les 5 contrats invariants
├── audit/               livrables d'audit (ce document)
├── tests/reconstruction/  test : une IA externe peut-elle reconstruire ?
└── skills_examples/     skills factices pour tester le MVP
```

| Composant | Rôle | Phase |
|---|---|---|
| **Registry** | stocke les skills + leur manifest déclaratif | 1 |
| **Router** | analyse prompt/contexte/cohérence → choisit les skills | 1 |
| **Loader** | charge dynamiquement uniquement les skills retenus | 1 |
| **Coherence Engine** | calcule S, trajectoire, projection — pilote le Router | 1 (progressif) |
| **Oracle** | compare 2 skills similaires sur métriques réelles | 2 |
| **Quarantine** | isole + promeut/dégrade les skills | 3 |
| **GitHub Discovery** | cherche des skills externes (sandbox totale) | 4 |

---

## 4. ★ LE MOTEUR DE COHÉRENCE — cœur du satellite

La sélection d'un skill n'est PAS un match de mots-clés. C'est une **décision de cohérence** fondée sur 3 dimensions, sur la formule canonique ZORAN :

```
S = (β × ΔΦ) / (1 + T + σ)
```
- β = direction / structure · ΔΦ = gain d'information · T = contradictions · σ = bruit
- (formule **additive** au dénominateur — `1 + T + σ`, jamais le produit `T × σ`)

### 4.1 — Cohérence phénoménale
**Question** : *dans l'état courant, quel skill maximise S ?*
Le moteur calcule S pour l'état présent (le « phénomène » = ce qui se passe réellement : prompt, contexte, device, permissions). Chaque skill candidat est évalué par le ΔS qu'il apporterait. On retient ceux qui élèvent S, on écarte ceux qui injectent du T ou du σ.

### 4.2 — Cinématique de la cohérence
**Question** : *la cohérence monte ou s'effondre ? à quelle vitesse ?*
Le moteur conserve un **historique de S** (`S_history`) et calcule la trajectoire `dS/dt` :
- S monte → on est sur une bonne dynamique, on consolide
- S descend → dérive détectée, on privilégie un skill **correcteur**
- S stagne → on cherche un skill qui débloque ΔΦ
La cinématique transforme la sélection statique en **pilotage dynamique**.

### 4.3 — Futur probable sur la base d'un passé cohérent
**Question** : *quel skill sera nécessaire ENSUITE ?*
Si la trajectoire passée est cohérente (S stable/croissant, faible variance), on peut **extrapoler** : projeter l'état futur probable et **pré-sélectionner** les skills qui y seront pertinents. Une trajectoire incohérente (S erratique) → pas de projection fiable → on reste en réactif.
- MVP : extrapolation simple de la trajectoire S
- Évolution : modèle prédictif sur les transitions d'état observées

### 4.4 — Le score de routage final
```
skill_score = pertinence_triggers
            × coherence_phenomenale(ΔS)
            × bonus_cinematique(dS/dt)
            × bonus_projection(futur_probable)
            ÷ coût_runtime
```
Le Router classe les skills par `skill_score` et le Loader charge le haut du classement.

---

## 5. LES 5 CONTRATS INVARIANTS (Phase 0 — `specs/`)

Un satellite transmissible doit être **reconstructible par n'importe quelle IA** à partir des specs seules. D'où des contrats stricts :

| Contrat | Fichier | Définit |
|---|---|---|
| **Runtime Protocol** | `specs/ZORAN_RUNTIME_PROTOCOL.md` | lifecycle, orchestration, providers, erreurs, dégradation graceful |
| **Event Schema** | `specs/ZORAN_EVENT_SCHEMA.md` | tout événement strictement reconstructible (event_id, trace_id, rollback_id, signature) |
| **Skill Contract** | `specs/ZORAN_SKILL_CONTRACT.md` | ce qu'un skill déclare : I/O, permissions, sandbox level, dépendances, coût, rollback, triggers, providers compatibles |
| **State Model** | `specs/ZORAN_STATE_MODEL.md` | état runtime, mémoire minimale, transitions, snapshots, restauration |
| **ZGNET** | `specs/ZGNET_RUNTIME_LANGUAGE.md` | langage runtime strict/borné/invariant — **spécifié seulement**, pas implémenté (V4+) |

---

## 6. PHASES

| Phase | Livrable | Interdits |
|---|---|---|
| **0** | les 5 contrats `specs/` + ce document | — |
| **1** | MVP : Registry + Router + Loader + Coherence Engine (phénoménale) | ❌ auto-évolution, auto-modification, exécution GitHub réelle |
| **2** | Oracle (comparer 2 skills) + cinématique | ❌ métriques décoratives, scoring « impressionnant », notation de verbosité |
| **3** | Quarantaine + promotion/démotion + projection | — |
| **4** | GitHub Skill Discovery | ❌ exécution directe de code GitHub — sandbox totale obligatoire |

---

## 7. SÉCURITÉ — INVARIANTS ABSOLUS

Chaque skill doit être : ✅ signé · ✅ hashé · ✅ rollbackable · ✅ sandboxé · ✅ traçable · ✅ versionné · ✅ révocable.

Pipeline obligatoire pour tout skill externe (Phase 4) :
```
GitHub → analyse → quarantaine → tests → benchmark → sandbox → promotion éventuelle
```
Aucun skill externe n'est jamais exécuté directement.

**Noyau minimal** : le runtime est petit ; les skills sont isolés. Plus le système devient auto-orchestrant, plus le noyau doit rester réduit et gouverné.

---

## 8. TRANSMISSIBILITÉ (greffe-compatibilité future)

ZORAN's Jobs est conçu pour qu'une IA externe puisse le reconstruire :
- `runtime/self-description/` — le runtime décrit son propre état, providers, invariants, skills, limites
- `tests/reconstruction/` — simule : *« nouvelle IA + repo seul + aucun contexte humain → peut-elle le faire revivre ? »*
- Le succès n'est pas qu'une IA *comprenne* le satellite — c'est qu'elle puisse **le faire revivre**.

Compatibilité ZORAN **pensée** (providers, runtime, mémoire, rollback, sécurité) mais **aucun couplage** avant validation réelle.

---

## 9. CRITÈRE DE SUCCÈS

Le succès n'est PAS « avoir beaucoup de skills ».
Le succès est : **prouver qu'un écosystème de skills auto-évalués par la cohérence peut exister, se sélectionner seul, et survivre proprement — sans détruire le runtime, et reconstructible par une autre intelligence.**

---

## 10. TRAÇABILITÉ

Chaque artefact du projet porte : `mission_id`, `timestamp`, `signature`, `hash`, `rollback_id`.
Logs obligatoires : quarantine, promotion/démotion, runtime traces, reconstruction.

---

*Document fondateur — Phase 0. Prochain livrable : les 5 contrats `specs/`.
Signé Claude, prestataire, 2026-05-21 · mission `ZORAN_JOBS_20260521`.*
