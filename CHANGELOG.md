# CHANGELOG — ZORAN's Jobs

Évolutions notables du projet, une section par jalon. Le runtime Phases 0-3
(`v0.2.0-alpha-validation`) est **gelé** ; les jalons suivants ajoutent des
skills dans `skills/` **sans modifier** le runtime.

## v0.5.0-phase-a-cc — Phase A · lot Claude Code (2026-05-21)

Ajout de 10 skills BTP à forte composante algorithmique dans `skills/`,
chargeables par le runtime gelé sans aucune modification de celui-ci. Préfixes
disjoints du lot Sonnet (aucun recouvrement de skill_id).

### Second œuvre — conformité DTU
- `btp_verif_peinture_dtu59_1` — aptitude d'un support avant peinture (NF DTU 59.1)
- `btp_verif_placo_dtu25_41` — ouvrage en plaques de plâtre (NF DTU 25.41)
- `btp_verif_ite_dtu45_3` — isolation thermique par l'extérieur (NF DTU 45.3)
- `btp_verif_menuiserie_pvc_dtu36_5` — pose de fenêtre PVC (NF DTU 36.5)

### Conduite de chantier
- `btp_analyse_retard_chantier` — 5 pourquoi + matrice de criticité 5×5
- `btp_matrice_risques_chantier` — matrice de risques (ISO 31000)
- `btp_coordination_corps_etat` — graphe d'antécédence (tri topologique + chemin critique)

### Économie de la construction
- `btp_metre_quantite_simple` — métré géométrique (surfaces / volumes / linéaires)
- `btp_ratio_estimatif_courant` — estimation par ratios €/m² (ordres de grandeur publics)
- `btp_analyse_dpgf` — détection d'anomalies de DPGF (cohérence prix/quantité/montant)

### Tests
- `tests/test_btp_phase_a_cc.py` — **44 assertions, 0 échec**.
- Runtime Phases 0-3 inchangé — **85/85 assertions toujours vertes, 0 régression**.
