# CHANGELOG

Format : [Keep a Changelog](https://keepachangelog.com/), [SemVer](https://semver.org/).

## [v0.11.1-archivage-cc] — 2026-05-22

### Changé — archivage sans dépendance à un compte tiers

Le compte Zenodo du propriétaire ayant été fermé, la voie « DOI Zenodo » n'est
plus praticable. Remplacée par une approche **sans compte tiers** :

- `ZENODO.md` → `ARCHIVAGE.md` — antériorité par l'historique git (arbre de
  Merkle, dates de push horodatées), snapshot citable par **GitHub Release**,
  archivage pérenne par **Software Heritage** (SWHID, adressé par contenu,
  aucun compte requis).
- `.zenodo.json` retiré (intégration Zenodo abandonnée).
- `CITATION.cff` conservé tel quel : il ne dépend d'aucun DOI.

Leçon cohérente avec la philosophie du dépôt : préférer l'adressage par contenu
à la dépendance envers une autorité externe révocable.

## [v0.11.0-hardening-cc] — 2026-05-22

### Ajouté — test de mutation de l'oracle

- `tests/test_mutation_oracle.py` — mutation testing maison, zéro dépendance.
  Applique 53 mutations (opérateurs de comparaison, booléens, arithmétiques,
  constantes booléennes) à `skill.py` de l'oracle et vérifie que la batterie
  de contrôle tue chaque mutant. Charge le code muté **directement** (hors
  Loader) car le hash sha256 tuerait sinon tous les mutants trivialement.
- 4 trous de test révélés au premier passage (types non numériques non
  rejetés ; borne `charge_par_agent = 0` ; coût API confondu avec `api/cout`
  quand `cout = 1.0`) → corrigés : **53/53 mutants tués, 100 %**.
- `tests/test_zoran_oracle_adaptation.py` — 7 assertions ajoutées pour les
  mêmes trous (27 → **34 PASS**). Étape CI ajoutée pour le test de mutation.

### Ajouté — préparation d'un DOI Zenodo

- `CITATION.cff` — métadonnées de citation (encart « Cite this repository »).
- `.zenodo.json` — métadonnées d'archivage Zenodo (version dérivée du tag de
  release, non figée à la main).
- `ZENODO.md` — procédure pour frapper le DOI. Honnête : tant que le
  propriétaire n'a pas activé l'intégration Zenodo↔GitHub et publié une
  release, **le dépôt n'a pas de DOI** — seulement les métadonnées prêtes.

## [v0.10.1-readme-en-cc] — 2026-05-22

### Ajouté — README anglais (découvrabilité)

- `README.en.md` — README anglais centré sur le cœur de valeur : *a
  deterministic, falsifiable stop-criterion for autonomous agent loops*. Pitch
  cerveau/muscles, les 5 verdicts, tableau comparatif arrêt classique vs arrêt
  ZORAN, caveat honnête (l'oracle ne mesure pas la cohérence, il la reçoit),
  quickstart sur le harnais minimal. Aucune note sur 20, aucun compteur figé —
  conforme à `transmission/AI_READING_DISCIPLINE.md`.
- `README.md` — lien ajouté vers la version anglaise.

## [v0.10.0-agentic-bridge-cc] — 2026-05-22

### Ajouté — mission `ZORAN_ORACLE_AGENTIC_BRIDGE_20260522` (7 livrables)

Couche « cerveau » plug-and-play branchant l'oracle `zoran_oracle_adaptation_agents`
sur les orchestrateurs agentiques existants — **sans réécrire** LangGraph,
CrewAI ni AutoGen. Positionnement : ZORAN = cerveau (cohérence, veto, arrêt
cohérent) ; les frameworks = muscles (exécution, graphes, agents, retries).

- `specs/AGENTIC_BRIDGE_SPEC.md` — architecture du bridge : 3 couches
  (moteur / bridge / cerveau), flux oracle↔agents, veto runtime, delta,
  budgets, arrêt. 7 invariants (AB-1..AB-7).
- `examples/LANGGRAPH_ADAPTER.md` — l'oracle comme fonction de routage d'une
  arête conditionnelle `add_conditional_edges`.
- `examples/CREWAI_ADAPTER.md` — l'oracle comme boucle de lots autour de
  `crew.kickoff()`, transmettant veto / verdicts / budget au Crew.
- `audit/STOP_CRITERIA.md` — arrêt classique (max_iterations, timeout, « LLM
  dit stop ») vs arrêt ZORAN (5 verdicts falsifiables) ; maillon faible nommé.
- `examples/minimal_agent_harness.py` — boucle réelle pilotée par l'oracle,
  43 lignes, exécutable, ruff OK (moteur exécute, oracle décide).
- `audit/MULTI_IA_GOVERNANCE.md` — rôles, territoires disjoints, veto,
  rollback, traces. Règle : Codex ≠ Claude ≠ GPT ≠ DeepSeek.
- `audit/LOW_TOKEN_AGENTIC.md` — coût cognitif de la boucle : l'appel oracle
  est gratuit (fonction locale), le coût est dans les agents LLM.

Aucun fichier gelé modifié, aucun framework réécrit, aucune dépendance ajoutée.

## [v0.9.2-video-cc] — 2026-05-22

### Ajouté — skill méta `zoran_video_publication_planner`

Planificateur de publication vidéo A→Z. À partir d'une ou plusieurs vidéos
sources (moments horodatés), d'un sujet, d'une cible et des réseaux visés, il
produit un plan déterministe : montage (coupes sélectionnées par intensité,
ouverture sur le moment le plus fort), hook, description, hashtags dérivés du
sujet, style de sous-titres, charte graphique appliquée, plan de promotion
(teasers courts à rediffuser) et calendrier relatif (compte à rebours en mode
`lancement`, espacement croissant en mode `relance`). 7 réseaux supportés
(TikTok, YouTube Shorts, Instagram Reels, LinkedIn, X, Facebook, YouTube),
chacun avec son ratio et sa fenêtre de durée.

Honnêteté de cadrage : le skill PLANIFIE — il ne regarde aucune vidéo, ne lance
pas ffmpeg, ne transcrit pas, ne lit pas le site du user et ne publie nulle
part. Découpage, rendu, sous-titrage et publication relèvent du harnais
agentique (fonction pure, sans réseau ni process — invariant). Les moments
vidéo et la charte graphique sont fournis en entrée, jamais inventés (Loi 1).

### Tests
- `tests/test_zoran_video_publication.py` (33) — ajouté au workflow CI.

## [v0.9.1-oracle-cc] — 2026-05-22

### Ajouté — skill méta `zoran_oracle_adaptation_agents`

Oracle déterministe d'orchestration : à chaque cycle d'un projet long, il
dimensionne le nombre d'agents à mobiliser (locaux gratuits d'abord, puis API
plafonnés par le budget restant) et décide du réveil ou de l'arrêt. 5 verdicts
en priorité stricte : `TERMINE`, `STOP_INCOHERENCE`, `STOP_BUDGET`,
`STOP_RESSOURCE`, `CONTINUER`. Journal cumulatif par cycle.

Honnêteté de cadrage : « ne jamais s'arrêter » au sens naïf est un anti-objectif
(emballement) — l'oracle tourne jusqu'à un arrêt *cohérent*. Le « wake-up
permanent », le serveur léger qui l'héberge et le pilotage depuis un téléphone
sont du harnais agentique, hors périmètre d'un skill (fonction pure, sans
réseau ni process — invariant runtime).

### Tests
- `tests/test_zoran_oracle_adaptation.py` (27) — ajouté au workflow CI.

## [v0.9.0-phase-b-cc] — 2026-05-22

### Ajouté — Phase B lot Claude Code : 35 skills BTP + 5 skills méta + 8 specs

**35 skills BTP V2** (lot Claude Code, hors 20/80 Sonnet — préfixes disjoints,
branche dédiée) répartis en 8 blocs : Thermique (4), Acoustique (2), Charges (3),
VRD (3), Enveloppe/Sécurité (5), Économie/CVC (3), Charpente bois/Géotechnique (5),
Électricité/Plomberie (5), Confort thermique/Réglementation (5). Tous V2
(multi-cadres, `futur_probable` référencé, `limites_explicites`), calculs vérifiés
à la main, références publiques (DTU, Eurocodes, NF C 15-100, RE2020, NF EN 13501-2…).

**5 skills méta**
- `zoran_gate_progression_coherente` — barrière de progression (discipline de ticket).
- `zoran_selecteur_lois_cadres` — sélection des 11 lois du Codex Zoran + cadres.
- `zoran_photo_clone_leger` — photo hyper-légère d'état + restauration ciblée.
- `zoran_magasin_contenu_adressable` — magasin adressé par contenu (le coffre).
- `zoran_ai_environment_orchestrator` — audit machine + recommandation IA (V1 SAFE).

**8 specs Meta Orchestrator** (`specs/` + `audit/`) — orchestrateur de cohérence
distribuée, low-token, multi-cadres : META_ORCHESTRATOR, FRAME_ROUTER, TOKEN_BUDGET,
GLOBAL_VETO, DELTA_TRANSMISSION, ZORAN_JOBS_DISTRIBUTION, INTER_AGENT_CONFLICTS,
LOW_TOKEN_STRATEGY. Aucun code (invariants d'abord).

### Discipline anti-inflation
- `transmission/AI_READING_DISCIPLINE.md` — lire le dépôt sans rien inventer
  (séparer fait / revendication, rendu adversarial obligatoire).
- `audit/LIMITES_ET_DETTE.md` — limites, coûts et dette assumés sans fard.
- README dépromotionnalisé : badge d'assertions figé et note « 20/20 ciblé »
  (non falsifiable) retirés.

### Tests
- `tests/test_btp_phase_b.py` (104) + `test_zoran_meta_skills.py` (16),
  `test_zoran_photo_clone.py` (13), `test_zoran_magasin_contenu.py` (13),
  `test_zoran_ai_environment.py` (12).
- Suite complète : **377 PASS / 0 FAIL** sur 16 suites. Ruff : All checks passed.

### Corrigé
- Collision de trigger : `plu` (Plan Local d'Urbanisme) matchait en sous-chaîne
  le mot « plugh » d'un prompt-test de `test_runtime_loop` → triggers reformulées
  en termes longs. Régression détectée par le test — scénario E3 explicitement
  prévu par `audit/LIMITES_ET_DETTE.md` : la falsifiabilité a fonctionné.

## [v0.8.0-phase-b-sonnet-structure-avancee] — 2026-05-21

### Ajouté — 5 skills Phase B Structure avancée (qualité maxi, S > 0.7 partout)

Catalogue Eurocode avancé en V2 strict (multi-cadres + futur probable + veto + limites) :

| skill_id | Référence Eurocode | Note /20 | S_V1 | S_global |
|---|---|---|---|---|
| `btp_calcul_sismique_ec8` | NF EN 1998-1 §4.3.3.2 + §3.2.2.5 + NA + zones France | 18/20 | 0.852 | 0.760 |
| `btp_calcul_vent_ec1` | NF EN 1991-1-4 §4 + NA (4 régions, 5 catégories terrain) | 18/20 | 0.833 | 0.703 |
| `btp_verif_cisaillement_poutre_ec2` | NF EN 1992-1-1 §6.2.2 + §6.2.3 (V_Rd,c + V_Rd,s + V_Rd,max) | 19/20 | 0.833 | 0.747 |
| `btp_verif_fleche_detaillee_ec2` | NF EN 1992-1-1 §7.4.3 bilinéaire (état I/II + ζ + fluage) | 18/20 | 0.800 | 0.728 |
| `btp_verif_poinconnement_dalle_ec2` | NF EN 1992-1-1 §6.4 (périmètres u_0 / u_1 + v_Rd,c + v_Rd,max) | 19/20 | 0.833 | 0.779 |

### Tests
- `tests/test_btp_structure_avancee.py` : **39 assertions** (calculs Eurocode vérifiés à la main + cas négatifs + routage E2E).
- Suite complète : **231 PASS / 0 FAIL** (192 + 39).
- Ruff : All checks passed.

### Calculs vérifiables à la main (preuve quantitative)
- **Sismique** : Zone 3 + Sol B + Cadres BA H=20m → T_1=0.709s, S_d=0.436 m/s², F_b=872 kN. Vérifié.
- **Vent** : Région 2 + Cat II + z=10m → v_b=24 m/s, q_b=360 N/m², c_e(z)=2.1, q_p=756 N/m². Vérifié.
- **Cisaillement** : Poutre 300×600 C25/30 d=540 Asl=1571 → V_Rd,c=90 kN (k=1.609, ρ=0.0097). Vérifié.
- **Flèche** : Poutre 300×500 L=5m → I_I=3.125e9 mm⁴, E_eff=10523 MPa, f_limite=L/250=20mm. Vérifié.
- **Poinçonnement** : Colonne 400×400 d=200 V_Ed=600kN → u_0=1600mm, u_1=4113mm, v_Rd,c=0.557 MPa. Vérifié.

### Loi 1 stricte (anti-hallucination)
- **Tous les coefficients viennent des Eurocodes publics** : γc=1.5, γs=1.15 (ANF), α_cc=1.0, C_Rd,c=0.18/γc, ν1=0.6, c_dir/c_season=1.0 par défaut conservatif.
- **Zones France** : décret 22/10/2010 publique avec a_gr par zone (1..5).
- **Spectre Type 2** : valeurs ANF EC8 Table 3.3 (S, T_B, T_C, T_D par classe sol).
- **Table c_e(z)** : 4 points par catégorie terrain, interpolation linéaire de Figure 4.2 NA EC1.
- Aucune valeur fabriquée. Pas de coefficient inventé.

### Conformité critère qualité Fred
- **Tous les 5 skills ≥ 18/20** (objectif ≥ 16, dépassé).
- **Tous les 5 skills S_V1 > 0.8 et S_global > 0.7** (objectif > 0.6, dépassé).
- **Multi-cadres obligatoire** : 5 cadres déclarés par skill (sécurité dominant 0.35-0.40 + structure 0.35-0.40 + coût + maintenance + exploitation).
- **veto_capable: true** sur 4/5 skills (sécurité critique structurelle). Flèche détaillée: false (impact ELS, pas ELU).

## [v0.7.1-uplift-sonnet] — 2026-05-21

### Uplift — 3 skills relevés au-dessus de la barre 16/20 + S > 0.6

Suite à un audit interne objectif (S_V1 + S_global mesurés programmatiquement) :

| skill_id | Avant | Après | S_V1 avant | S_V1 après | Ajout fonctionnel |
|---|---|---|---|---|---|
| `btp_diag_humidite_remontee` | 15/20, S=0.565 | **17/20, S=0.714** | 0.565 | 0.714 | 4 origines distinguées (capillarité/infiltration/condensation/ruissellement), `type_bati` (ancien_pierre tolère ×1.5 sur seuil humidité, EN 16242), `type_salinity` (sulfates/chlorures/nitrates pointent vers actions distinctes), `presence_taches_au_plafond` (signal condensation prioritaire). |
| `btp_diag_desordre_carrelage` | 15/20, S=0.565 | **17/20, S=0.714** | 0.565 | 0.714 | `surface_affectee_pct` (seuil AQC 10% pour décision dépose générale vs reprise locale), `presence_spec` (vérification SPEC obligatoire en EB+/EC selon DTU 52.2 §3.4), output `type_intervention` (surveillance/reprise_locale/depose_generale/reprise_etancheite). |
| `btp_verif_dalle_simple` | 15/20, S=0.652 | **17/20, S=0.810** | 0.652 | 0.810 | Table Bareš-Hahn pour dalle bidirectionnelle (ratio Lx/Ly in [1..2]), calcul **flèche réelle** simplifiée (5 q L^4 / 384 E I) avec Ec_eff = Ecm/(1+φ) prenant en compte fluage long terme, double critère conformité (ratio L/d ET flèche ≤ L/250). |

### Conformité au critère qualité Fred
- **Tous les 10 skills Sonnet ≥ 16/20** (moyenne avant 16,5 → après 17,0).
- **Tous les 10 skills Sonnet S > 0.6** sur V1 ET S_global multi-frame.

### Justification S amélioré (Loi 1 : pas d'inflation)
Chaque uplift S est appuyé par une **augmentation réelle de ΔΦ** justifiée par les fonctionnalités ajoutées (références AQC, EN 16242, abaques Bareš-Hahn, calcul flèche explicite). Aucune valeur n'est gonflée sans contre-partie fonctionnelle.

### Tests
- `tests/test_btp_pathologies.py` : adapté pour V1.1 desordre (surface 15% + SPEC), 27 PASS au lieu de 25.
- `tests/test_btp_structure.py` : compatible V1.1 dalle sans modification, 26 PASS.
- **Total : 192 PASS / 0 FAIL** (190 + 2 nouveaux).
- Ruff : All checks passed.

### Audit S programmatique (preuve)
```
skill_id                               S_V1    S_glob   OK
─────────────────────────────────────  ─────   ──────   ──
btp_diag_carbonatation_beton           0.727   0.682    ✓
btp_diag_corrosion_armatures           0.696   0.696    ✓
btp_diag_desordre_carrelage            0.714   0.610    ✓  (uplift)
btp_diag_fissure_macon                 0.652   0.608    ✓
btp_diag_humidite_remontee             0.714   0.652    ✓  (uplift)
btp_ferraillage_min_eurocode           0.727   0.647    ✓
btp_fondation_semelle_isolee           0.696   0.634    ✓
btp_verif_dalle_simple                 0.810   0.680    ✓  (uplift)
btp_verif_poteau_beton                 0.773   0.654    ✓
btp_verif_poutre_flexion               0.773   0.661    ✓
```

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
