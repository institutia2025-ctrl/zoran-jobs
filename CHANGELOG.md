# CHANGELOG

Format : [Keep a Changelog](https://keepachangelog.com/), [SemVer](https://semver.org/).

## [v0.7.0-phase-a-sonnet-structure] — 2026-05-21

### Ajouté — 5 skills Structure simple (AXE 3 du masterplan, 2ème moitié de ma Phase A)

10/10 skills Sonnet livrés sur Phase A (5 pathologies + 5 structure). Catalogue complet en V2 :

| skill_id | Élément | Référence métier |
|---|---|---|
| `btp_verif_poteau_beton` | Poteau BA compression centrée | NF EN 1992-1-1 §6.1 + §5.8.3.1 (ANF γc=1.5, γs=1.15) |
| `btp_verif_poutre_flexion` | Poutre BA flexion simple | NF EN 1992-1-1 §6.1 + §3.1.7 (diagramme rectangle) |
| `btp_verif_dalle_simple` | Dalle BA prédimensionnement | NF EN 1992-1-1 §7.4.2 (ratio L/d limitation flèche) |
| `btp_fondation_semelle_isolee` | Semelle isolée carrée | NF EN 1997-1 §2.4.7.3 + NF DTU 13.1 + EC2 §9.8 |
| `btp_ferraillage_min_eurocode` | As_min poteau/poutre/dalle | NF EN 1992-1-1 §9.2 / §9.3 / §9.5 + §3.1.6 (fctm) |

### Tests
- `tests/test_btp_structure.py` : **26 assertions** (5 calculs Eurocode vérifiés à la main + 5 négatifs + 6 routages E2E).
- Suite complète : **190 PASS / 0 FAIL** (164 + 26).
- Ruff : All checks passed.

### Calculs Eurocode vérifiables
Chaque skill produit un résultat **prédictible à la main** :
- Poteau 300×300 C25/30 4HA20 N_Rd ≈ 2046 kN (testé).
- Poutre 300×600 C25/30 5HA20 d=560 z=0.9d → M_Rd ≈ 344 kNm (testé).
- Dalle L=5m h=250 → ratio 22.2 < 25 conforme prédim (testé).
- Semelle 600 kN sur σ=200 kPa → B=1750 mm σ_appl=195.9 kPa (testé).
- Ferraillage min poteau 300×300 N=600 → As_min = 180 mm² règle 0.002·Ac (testé).

### Veto sécurité activé
Tous les 5 skills structure ont `veto_capable: true` : un skill structure mal renseigné (S_securite < seuil) est **bloqué par le router avant scoring**. C'est la garantie INV-12 testée.

### Loi 1 respectée
- Tous les coefficients (γc, γs, αcc, formule fctm) viennent de l'Eurocode 2 (publique).
- `btp_fondation_semelle_isolee` exige `source_etude_sol` non vide (G1/G2 BET géotechnique) — sinon refus.
- Aucune valeur de σ_sol fabriquée.

## [v0.6.0-phase-a-sonnet-pathologies] — 2026-05-21

### Ajouté — 5 skills Pathologies (AXE 4 du masterplan, ma moitié des 20/80)

Catalogue Pathologies en V2 (multi-cadres + futur probable + veto + limites) :

| skill_id | Pathologie | Référence(s) métier (publiques) |
|---|---|---|
| `btp_diag_fissure_macon` | Fissures maçonnerie | NF DTU 20.1 §10 + grille AQC paramétrable (Loi 1 stricte) |
| `btp_diag_humidite_remontee` | Remontées capillaires | NF DTU 14.1 + NF DTU 20.1 §10 |
| `btp_diag_carbonatation_beton` | Carbonatation béton armé | NF EN 14630 + NF EN 1992-1-1 §4.4 + NF EN 206-1 |
| `btp_diag_corrosion_armatures` | Corrosion armatures + principe EN 1504 | NF EN 1504-9 + NF EN 206-1 |
| `btp_diag_desordre_carrelage` | Désordres carrelage collé | NF DTU 52.2 + Cahier CSTB 3567 |

### Tests
- `tests/test_btp_pathologies.py` : **25 assertions** (positif + négatif + routage end-to-end pour les 5).
- Suite complète : **164 PASS / 0 FAIL** (139 + 25).
- Ruff : All checks passed.

### Conformité Loi 1 (jamais halluciner)
- **`btp_diag_fissure_macon`** : aucun seuil mm AQC hard-codé. Les seuils a/b/c/d sont fournis en input par l'utilisateur avec source. Si absents, classification AQC reste `None` (skill reste utile via le qualitatif DTU 20.1).
- **`btp_diag_humidite_remontee`** : aucun % humidité hard-codé. Seuils en input + source obligatoire.
- **`btp_diag_carbonatation_beton`** : compare deux mesures fournies (carbonatation vs enrobage) ; pas de modèle de progression caché.
- **`btp_diag_corrosion_armatures`** : oriente vers un principe EN 1504-9, ne décide pas du système.
- **`btp_diag_desordre_carrelage`** : checklist visuelle + raisonnement DTU 52.2, aucune fabrication.

### Conformité V2
- 5 skills V2 (schema_version 2.0), tous multi-cadres avec INV-1 par cadre.
- `veto_capable: true` sur fissure, carbonatation, corrosion (impact sécurité bâti).
- Tous ont au moins 1 entrée `futur_probable` avec `reference` publique vérifiable.
- Tous ont `limites_explicites` non vide (Loi 10 : refus partiel explicite).

## [v0.4.0-contract-v2] — 2026-05-21

### Ajouté — Contrat skill V2 (industrialisation)

Évolution majeure du contrat de skill, **rétro-compatible 100%** (les 7 skills V1 + 5 BTP V1 continuent de marcher sans modification).

#### Spec gelée
- `specs/ZORAN_SKILL_CONTRACT_V2.md` — 237 lignes, 4 champs optionnels, 4 nouveaux invariants (INV-10 à INV-13).

#### 4 champs V2 (tous optionnels)
- **`coherence_multi_frame`** — cohérence par cadre métier (`structure`, `cout`, `carbone`, `maintenance`, `exploitation`, `securite`), chaque cadre suivant **INV-1 strict** (`(1 + T + σ)` par cadre).
- **`futur_probable`** — projection à horizon temporel (Loi 2 Zoran : Futur Cohérent). Chaque entrée requiert `horizon_an`, `evenement`, `probabilite`, `gravite`, `reference` (Loi 1 anti-hallucination : pas de prediction sans source).
- **`veto_capable`** — déclare que le skill peut être bloqué par veto sécurité du routeur (pré-filtre AVANT scoring).
- **`limites_explicites`** — liste des choses que le skill ne sait PAS faire (Loi 10 : refus partiel explicite).

#### Implémentation runtime
- `registry/manifest.py` : validation V2 + 4 nouveaux champs sur Manifest dataclass.
- `runtime/coherence/engine.py` : `compute_S_multi_frame()` + `s_global()`. INV-11 : chaque cadre = INV-1 indépendant.
- `router/router.py` : `is_veto_securite()` + `VETO_SECURITE_SEUIL=0.15`. Pré-filtre AVANT scoring (INV-12 déterministe).

#### Tests
- `tests/test_contract_v2.py` : **20 assertions** (rétrocompat V1, validation V2, multi-frame INV-1, veto INV-12).
- Tous tests existants intacts.
- **Total : 139 PASS / 0 FAIL** sur la suite complète.
- Ruff : All checks passed.

#### Migration BTP Phase A
Les 5 skills BTP Phase A migrés vers V2 avec multi-frame + limites + (pour structure/nucléaire) `veto_capable: true` + futur probable horizons 30/50 ans.

### Invariants ajoutés
- **INV-10** : Rétrocompatibilité V1 absolue.
- **INV-11** : INV-1 préservé par cadre (aucun produit `T×σ` caché).
- **INV-12** : Veto déterministe (même état → même verdict).
- **INV-13** : `limites_explicites` traçables dans la trace runtime.

### Conformité Zoran
- INV-1 (additif) **réaffirmé** par cadre, jamais T×σ.
- Loi 1 (jamais halluciner) appliquée aux `futur_probable.reference` (vide → erreur de validation).
- Loi 2 (Futur Cohérent) incarnée par `futur_probable`.
- Loi 10 (Anti-hallucination, refus partiel) incarnée par `limites_explicites`.

## [v0.3.0-phase-a-btp] — 2026-05-21

### Ajouté — 5 skills BTP (Phase A : preuve de méthode)

Catalogue emblématique, un skill par niveau de complexité métier :

| skill_id | Niveau | Domaine | Référence | Triggers |
|---|---|---|---|---|
| `palette_harmonique` | Décorateur | decoration | Théorie HSL (triadique) | palette, couleur, harmonie |
| `verif_dtu_carrelage` | Maître d'œuvre | construction | NF DTU 52.2 (déc. 2009) | dtu 52, carrelage, planéité |
| `planning_gantt_simple` | Conducteur travaux | construction | CPM (Kelley-Walker, ISO 21500) | planning, gantt, chemin critique |
| `descente_charges_simple` | Ingénieur génie civil | structure | NF EN 1990 + NF EN 1991-1-1 | descente, charges, ELU, eurocode |
| `verif_seisme_classe1_asn` | Ingénieur nucléaire | nucléaire | RFS 2001-01 (ASN, mai 2001) | séisme, ASN, RFS, EIPS, SMHV |

### Tests
- `tests/test_btp_skills.py` : **22 assertions** (positif + négatif chaque skill + 5 routages end-to-end)
- Tests existants : intacts, 97 PASS (registry/runtime/cinématique/oracle/immune/stress/coherence_unit)
- **Total : 119 PASS / 0 FAIL** (réplication indépendante confirmée 2026-05-21)
- Ruff : All checks passed.

### Vérifié
- Le Router de ZORAN's Jobs sélectionne le bon skill BTP pour 5/5 prompts métier naturels.
- Aucun NO-GO franchi : skills statiques dans `skills_examples/`, pas de découverte distante.
- Loi 1 (jamais inventer) : toutes les références (DTU 52.2, Eurocodes, RFS 2001-01) sont publiques et vérifiables.

### À noter
- Tous les skills sont marqués MVP démonstratif (calculs simplifiés). Ils prouvent le pattern. Phase B = approfondissement par domaine après audit.
- Le contrat ZORAN_SKILL_CONTRACT.md tient sans modification : 5 skills de 5 niveaux différents l'ont validé.

## [v0.2.0-alpha-validation] — 2026-05-21

### Ajouté
- **Validation massive** : 1000 manifests, 120 skills × 400 prompts, 10 000 calculs S, 2000 évaluations immune. 0 crash, routage 100 % déterministe, reproductible (`tests/stress/massive_validation.py`).
- **DÉMO 1 — Transmissibilité publique** : une IA externe a reconstruit le runtime depuis le dépôt seul (`tests/reconstruction/`).
- **Bundle de transmission mono-fichier** (`transmission/build_bundle.py`) : génère un `.md` auto-vérifié (sha256 par fichier) suffisant pour reconstruire l'intégralité du dépôt.
- **Système immunitaire** : journal signé + détection d'altération (`quarantine/immune.py`, `quarantine/journal.py`).
- **Oracle** : compare deux skills sur le réel, falsifie la déclaration du manifest par la mesure (`oracle/oracle.py`).
- **Audit Phase 4** : threat model, sandbox model, trust model, scenarios de skill hostile → statut **NO-GO** documenté (1 critère / 13 satisfait).
- **CI GitHub Actions** : 9 jobs (3 OS × 3 versions de Python) + lint ruff.
- **Tests unitaires isolés** du Coherence Engine (`tests/test_coherence_unit.py`, 12 assertions).
- **THEORY_BRIDGE.md** : ancrage honnête de la formule de cohérence dans la géométrie d'information (heuristique inspirée, pas équivalente).

### Vérifié
- **85 PASS / 0 FAIL** sur la suite complète (15+14+13+10+18+15) — réplication indépendante confirmée 2026-05-21.
- **97 PASS / 0 FAIL** avec les nouveaux tests unitaires.
- Tous les invariants RUNTIME_INVARIANTS.md sont testés.

### Corrigé
- README : exigence Python clarifiée (3.10+ fonctionne, 3.11 était une sur-spec).
- `build_bundle.py` : lecture/écriture en octets bruts (plus de réécriture CRLF Windows qui cassait les hash).

## [v0.1.0] — 2026-05-21 (initial frozen)

### Ajouté
- Phase 0 — Contrats gelés : EVENT_SCHEMA, STATE_MODEL, SKILL_CONTRACT, RUNTIME_PROTOCOL, ZGNET_RUNTIME_LANGUAGE.
- Phase 1 — MVP : Registry, Manifest parser, Coherence Engine, Router, Loader, Runtime loop.
- Skills d'exemple : echo, memory_recall, printer_connect, network_diag, coherence_repair, greet_ok, greet_ko.
- Tests : test_registry (15), test_runtime_loop (14), test_cinematique (13), test_oracle (10), test_immune (18).
