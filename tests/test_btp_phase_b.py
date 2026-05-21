"""
tests/test_btp_phase_b.py — Tests Phase B, lot Claude Code (skills V2).

Mission : ZORAN_JOBS_20260521 · Phase B · lot Claude Code.
Signé : Claude Code, prestataire, 2026-05-21.

Skills hors 20/80 (zéro collision avec les lots Sonnet) — domaines : thermique,
acoustique, charges, VRD, enveloppe, sécurité, économie, CVC.

Chaque skill : 1 cas positif vérifié à la main + 1 cas négatif (ValueError).
Chargement via le runtime réel (Registry + Loader, hash sha256 + validation V2).

Exécutable : python tests/test_btp_phase_b.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from loader.loader import Loader  # noqa: E402
from registry.registry import Registry  # noqa: E402

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


print("=" * 60)
print("TESTS BTP PHASE B — lot Claude Code")
print("=" * 60)

_reg = Registry()
_reg.load_from_dir(ROOT / "skills_examples")
_loader = Loader()


def run_of(skill_id: str):
    """Charge un skill via le runtime (hash + validation V2) et renvoie run."""
    manifest = _reg.get(skill_id)
    if manifest is None:
        raise AssertionError(f"{skill_id} absent du registry")
    module, err = _loader.load(manifest)
    if module is None:
        raise AssertionError(f"{skill_id} non chargé : {err}")
    return module.run


def raises_value_error(fn, payload) -> bool:
    try:
        fn(payload)
        return False
    except ValueError:
        return True
    except Exception:
        return False


def manifest_v2_ok(skill_id: str) -> bool:
    """Vérifie que le skill est bien V2 : multi-frame présent, poids = 1.0."""
    m = _reg.get(skill_id)
    if m is None or not m.coherence_multi_frame:
        return False
    total = sum(c.get("weight", 0.0) for c in m.coherence_multi_frame.values())
    return abs(total - 1.0) <= 0.01


# ===========================================================================
# BLOC THERMIQUE — 4 skills
# ===========================================================================
print("\n[Bloc Thermique]")

# --- btp_calc_resistance_thermique ---
run = run_of("btp_calc_resistance_thermique")
# béton 0.20 m / λ=1.75  →  R=0.11429 ; laine 0.14 m / λ=0.035 → R=4.0
# R_total = Rsi 0.13 + 0.11429 + 4.0 + Rse 0.04 = 4.2843 ; U = 1/4.2843 = 0.2334
r = run({"couches": [{"materiau": "beton", "epaisseur_m": 0.20, "lambda_w_mk": 1.75},
                     {"materiau": "laine", "epaisseur_m": 0.14, "lambda_w_mk": 0.035}]})
check("resistance_thermique : R ≈ 4.2843 m²K/W (calcul main)",
      abs(r["resistance_totale_m2k_w"] - 4.2843) < 0.001)
check("resistance_thermique : U ≈ 0.2334 W/m²K", abs(r["coefficient_u_w_m2k"] - 0.2334) < 0.001)
check("resistance_thermique : couches vides → ValueError",
      raises_value_error(run, {"couches": []}))
check("resistance_thermique : manifest V2 valide", manifest_v2_ok("btp_calc_resistance_thermique"))

# --- btp_calc_deperdition_paroi ---
run = run_of("btp_calc_deperdition_paroi")
# U=0.5, S=10 m², ΔT=20 K → Φ = 0.5 × 10 × 20 = 100 W
r = run({"coefficient_u_w_m2k": 0.5, "surface_m2": 10, "delta_temperature_k": 20})
check("deperdition_paroi : Φ = 100 W (calcul main)", abs(r["deperdition_w"] - 100.0) < 0.01)
# via R = 2.0 → U = 0.5 → même résultat
r2 = run({"resistance_m2k_w": 2.0, "surface_m2": 10, "delta_temperature_k": 20})
check("deperdition_paroi : R=2.0 → Φ = 100 W (U dérivé)", abs(r2["deperdition_w"] - 100.0) < 0.01)
check("deperdition_paroi : surface nulle → ValueError",
      raises_value_error(run, {"coefficient_u_w_m2k": 0.5, "surface_m2": 0,
                               "delta_temperature_k": 20}))

# --- btp_classe_dpe_estimatif ---
run = run_of("btp_classe_dpe_estimatif")
check("dpe : 150 kWh_ep/m².an → classe C", run({"consommation_kwh_ep_m2_an": 150})["classe_dpe"] == "C")
check("dpe : 50 → classe A", run({"consommation_kwh_ep_m2_an": 50})["classe_dpe"] == "A")
check("dpe : 500 → classe G", run({"consommation_kwh_ep_m2_an": 500})["classe_dpe"] == "G")
check("dpe : conso négative → ValueError",
      raises_value_error(run, {"consommation_kwh_ep_m2_an": -10}))

# --- btp_calc_pont_thermique_lineaire ---
run = run_of("btp_calc_pont_thermique_lineaire")
# ψ=0.5 × L=10 + ψ=0.2 × L=5  =  5.0 + 1.0 = 6.0 W/K
r = run({"ponts": [{"type": "plancher", "psi_w_mk": 0.5, "longueur_m": 10},
                   {"type": "refend", "psi_w_mk": 0.2, "longueur_m": 5}]})
check("pont_thermique : déperdition = 6.0 W/K (calcul main)",
      abs(r["deperdition_ponts_w_k"] - 6.0) < 0.001)
check("pont_thermique : liste vide → ValueError", raises_value_error(run, {"ponts": []}))
check("pont_thermique : manifest V2 valide", manifest_v2_ok("btp_calc_pont_thermique_lineaire"))

# ===========================================================================
# BLOC ACOUSTIQUE — 2 skills
# ===========================================================================
print("\n[Bloc Acoustique]")

# --- btp_calc_affaiblissement_acoustique ---
run = run_of("btp_calc_affaiblissement_acoustique")
# m=250 kg/m², f=500 Hz → R = 20·log10(125000) − 47 = 54.9 dB
r = run({"masse_surfacique_kg_m2": 250, "frequence_hz": 500})
check("affaiblissement : R ≈ 54.9 dB (calcul main)", abs(r["affaiblissement_db"] - 54.9) < 0.1)
check("affaiblissement : masse nulle → ValueError",
      raises_value_error(run, {"masse_surfacique_kg_m2": 0, "frequence_hz": 500}))

# --- btp_verif_isolement_acoustique_reglementaire ---
run = run_of("btp_verif_isolement_acoustique_reglementaire")
check("isolement : mur 55 dB >= 53 → conforme",
      run({"type_paroi": "mur_entre_logements", "isolement_mesure_db": 55})["conforme"] is True)
check("isolement : choc 60 dB > 58 → non conforme",
      run({"type_paroi": "plancher_choc", "isolement_mesure_db": 60})["conforme"] is False)
check("isolement : choc 50 dB <= 58 → conforme",
      run({"type_paroi": "plancher_choc", "isolement_mesure_db": 50})["conforme"] is True)
check("isolement : type de paroi inconnu → ValueError",
      raises_value_error(run, {"type_paroi": "xxx", "isolement_mesure_db": 55}))

# ===========================================================================
# BLOC CHARGES / ENVELOPPE — 3 skills
# ===========================================================================
print("\n[Bloc Charges / Enveloppe]")

# --- btp_calc_charge_neige ---
run = run_of("btp_calc_charge_neige")
# sk=0.65, angle=20° → μ1=0.8 → s = 0.8 × 1 × 1 × 0.65 = 0.52 kN/m²
r = run({"charge_sol_sk_kn_m2": 0.65, "angle_toiture_deg": 20})
check("charge_neige : s = 0.52 kN/m² (calcul main, μ1=0.8)",
      abs(r["charge_neige_kn_m2"] - 0.52) < 0.001 and abs(r["mu_forme"] - 0.8) < 0.001)
# angle=45° → μ1 = 0.8 × (60−45)/30 = 0.4 → s = 0.26
r2 = run({"charge_sol_sk_kn_m2": 0.65, "angle_toiture_deg": 45})
check("charge_neige : angle 45° → μ1=0.4, s=0.26", abs(r2["charge_neige_kn_m2"] - 0.26) < 0.001)
check("charge_neige : sk négatif → ValueError",
      raises_value_error(run, {"charge_sol_sk_kn_m2": -1, "angle_toiture_deg": 20}))
check("charge_neige : veto_capable (skill structure)",
      _reg.get("btp_calc_charge_neige").veto_capable is True)

# --- btp_calc_charge_exploitation_plancher ---
run = run_of("btp_calc_charge_exploitation_plancher")
# catégorie B (bureaux) qk=2.5 kN/m², surface 20 m² → total = 50 kN
r = run({"categorie": "B", "surface_m2": 20})
check("charge_exploitation : B → qk=2.5, total=50 kN (calcul main)",
      r["charge_repartie_qk_kn_m2"] == 2.5 and abs(r["charge_totale_repartie_kn"] - 50.0) < 0.01)
check("charge_exploitation : catégorie inconnue → ValueError",
      raises_value_error(run, {"categorie": "Z", "surface_m2": 20}))

# --- btp_verif_etancheite_air_re2020 ---
run = run_of("btp_verif_etancheite_air_re2020")
check("etancheite : maison Q4=0.5 <= 0.6 → conforme",
      run({"type_batiment": "maison_individuelle", "q4pa_surf_mesure": 0.5})["conforme"] is True)
check("etancheite : maison Q4=0.8 > 0.6 → non conforme",
      run({"type_batiment": "maison_individuelle", "q4pa_surf_mesure": 0.8})["conforme"] is False)
check("etancheite : type de bâtiment inconnu → ValueError",
      raises_value_error(run, {"type_batiment": "bureau", "q4pa_surf_mesure": 0.5}))

# ===========================================================================
# BLOC VRD — 3 skills
# ===========================================================================
print("\n[Bloc VRD]")

# --- btp_calc_volume_terrassement ---
run = run_of("btp_calc_volume_terrassement")
# 10 × 2 × 1.5 = 30 m³ en place ; × 1.25 = 37.5 m³ foisonné
r = run({"longueur_m": 10, "largeur_m": 2, "profondeur_m": 1.5})
check("volume_terrassement : 30 m³ en place, 37.5 m³ foisonné (calcul main)",
      abs(r["volume_en_place_m3"] - 30.0) < 0.001
      and abs(r["volume_foisonne_m3"] - 37.5) < 0.001)
check("volume_terrassement : coefficient < 1.0 → ValueError",
      raises_value_error(run, {"longueur_m": 10, "largeur_m": 2, "profondeur_m": 1.5,
                               "coefficient_foisonnement": 0.8}))

# --- btp_calc_pente_evacuation_ep ---
run = run_of("btp_calc_pente_evacuation_ep")
# dénivelé 0.30 m sur 10 m → pente 3.0 % → conforme (>= 1 %)
r = run({"denivele_m": 0.30, "longueur_m": 10})
check("pente_evacuation : 3.0 % → conforme",
      abs(r["pente_pct"] - 3.0) < 0.001 and r["conforme"] is True)
# 0.05 m sur 10 m → 0.5 % → non conforme
r2 = run({"denivele_m": 0.05, "longueur_m": 10})
check("pente_evacuation : 0.5 % → non conforme", r2["conforme"] is False)
check("pente_evacuation : longueur nulle → ValueError",
      raises_value_error(run, {"denivele_m": 0.3, "longueur_m": 0}))

# --- btp_dimensionnement_collecteur_eu ---
run = run_of("btp_dimensionnement_collecteur_eu")
# ΣUV=100, K=0.5 → Q = 0.5 × √100 = 5.0 l/s → DN 100
r = run({"unites_vidange_total": 100, "coef_frequentation_k": 0.5})
check("collecteur_eu : Q = 5.0 l/s, DN 100 (calcul main)",
      abs(r["debit_pointe_l_s"] - 5.0) < 0.001 and r["dn_minimal_indicatif"] == "DN 100")
check("collecteur_eu : unités de vidange négatives → ValueError",
      raises_value_error(run, {"unites_vidange_total": -1}))

# ===========================================================================
# BLOC ENVELOPPE / SECURITE — 5 skills
# ===========================================================================
print("\n[Bloc Enveloppe / Sécurité]")

# --- btp_verif_pente_toiture_couverture ---
run = run_of("btp_verif_pente_toiture_couverture")
r = run({"pente_posee_pct": 40, "pente_min_dtu_pct": 35, "materiau": "tuile"})
check("pente_toiture : 40% >= 35% → conforme (marge 5)",
      r["conforme"] is True and abs(r["marge_pct"] - 5.0) < 0.01)
check("pente_toiture : 20% < 35% → non conforme",
      run({"pente_posee_pct": 20, "pente_min_dtu_pct": 35})["conforme"] is False)
check("pente_toiture : pente min nulle → ValueError",
      raises_value_error(run, {"pente_posee_pct": 40, "pente_min_dtu_pct": 0}))

# --- btp_calc_evacuation_eaux_pluviales ---
run = run_of("btp_calc_evacuation_eaux_pluviales")
# 100 m² × 0.05 l/s/m² = 5.0 l/s
r = run({"surface_toiture_m2": 100})
check("evacuation_ep : Q = 5.0 l/s (calcul main)", abs(r["debit_ep_l_s"] - 5.0) < 0.001)
check("evacuation_ep : surface nulle → ValueError",
      raises_value_error(run, {"surface_toiture_m2": 0}))

# --- btp_verif_accessibilite_pmr_rampe ---
run = run_of("btp_verif_accessibilite_pmr_rampe")
check("pmr_rampe : pente 4% largeur 1.4 m → conforme",
      run({"pente_pct": 4, "longueur_m": 5, "largeur_m": 1.4,
           "paliers_repos_presents": True})["conforme"] is True)
check("pmr_rampe : pente 12% → non conforme",
      run({"pente_pct": 12, "longueur_m": 1, "largeur_m": 1.4})["conforme"] is False)
check("pmr_rampe : pente 7% sur 5 m → non conforme (tolérance 2 m)",
      run({"pente_pct": 7, "longueur_m": 5, "largeur_m": 1.4})["conforme"] is False)
check("pmr_rampe : longueur nulle → ValueError",
      raises_value_error(run, {"pente_pct": 4, "longueur_m": 0, "largeur_m": 1.4}))

# --- btp_verif_garde_corps_hauteur ---
run = run_of("btp_verif_garde_corps_hauteur")
check("garde_corps : h=1050 mm, écart 100 mm → conforme",
      run({"hauteur_mm": 1050, "ecartement_barreaux_mm": 100})["conforme"] is True)
check("garde_corps : h=900 mm → non conforme",
      run({"hauteur_mm": 900, "ecartement_barreaux_mm": 100})["conforme"] is False)
check("garde_corps : écartement 150 mm → non conforme",
      run({"hauteur_mm": 1050, "ecartement_barreaux_mm": 150})["conforme"] is False)
check("garde_corps : hauteur nulle → ValueError",
      raises_value_error(run, {"hauteur_mm": 0, "ecartement_barreaux_mm": 100}))
check("garde_corps : veto_capable (sécurité chute)",
      _reg.get("btp_verif_garde_corps_hauteur").veto_capable is True)

# --- btp_verif_degagement_incendie ---
run = run_of("btp_verif_degagement_incendie")
# 2 UP → largeur réglementaire 1.40 m (article CO 36)
check("degagement : largeur 1.5 m pour 2 UP → conforme",
      run({"largeur_degagement_m": 1.5, "unites_passage_requises": 2})["conforme"] is True)
check("degagement : largeur 1.0 m pour 2 UP (1.40 requis) → non conforme",
      run({"largeur_degagement_m": 1.0, "unites_passage_requises": 2})["conforme"] is False)
check("degagement : 3 UP → largeur min 1.80 m (3 × 0.60)",
      abs(run({"largeur_degagement_m": 2.0, "unites_passage_requises": 3})["largeur_min_requise_m"]
          - 1.80) < 0.01)
check("degagement : UP = 0 → ValueError",
      raises_value_error(run, {"largeur_degagement_m": 1.5, "unites_passage_requises": 0}))
check("degagement : veto_capable (sécurité évacuation)",
      _reg.get("btp_verif_degagement_incendie").veto_capable is True)

# ===========================================================================
# BLOC ECONOMIE / CVC — 3 skills
# ===========================================================================
print("\n[Bloc Économie / CVC]")

# --- btp_calc_revision_prix ---
run = run_of("btp_calc_revision_prix")
# P0=100000, a=0.125, I0=100, I=110 → coef = 0.125 + 0.875×1.1 = 1.0875 → 108750
r = run({"prix_initial_eur": 100000, "terme_fixe": 0.125,
         "index_initial": 100, "index_courant": 110})
check("revision_prix : prix révisé = 108 750 € (calcul main)",
      abs(r["prix_revise_eur"] - 108750.0) < 0.01)
check("revision_prix : terme fixe hors [0,1] → ValueError",
      raises_value_error(run, {"prix_initial_eur": 100000, "terme_fixe": 1.5,
                               "index_initial": 100, "index_courant": 110}))

# --- btp_calc_situation_travaux ---
run = run_of("btp_calc_situation_travaux")
# marché 200000, avancement 40%, RG 5% → travaux 80000, retenue 4000, dû 76000
r = run({"montant_marche_ht": 200000, "avancement_pct": 40})
check("situation : travaux 80 000 €, retenue 4 000 €, acompte 76 000 € (calcul main)",
      abs(r["travaux_realises_ht"] - 80000.0) < 0.01
      and abs(r["retenue_garantie_ht"] - 4000.0) < 0.01
      and abs(r["acompte_periode_ht"] - 76000.0) < 0.01)
check("situation : avancement > 100 → ValueError",
      raises_value_error(run, {"montant_marche_ht": 200000, "avancement_pct": 150}))

# --- btp_calc_debit_ventilation_vmc ---
run = run_of("btp_calc_debit_ventilation_vmc")
check("vmc : 4 pièces → 90 m³/h",
      run({"nb_pieces_principales": 4})["debit_global_minimal_m3h"] == 90)
check("vmc : 1 pièce → 35 m³/h",
      run({"nb_pieces_principales": 1})["debit_global_minimal_m3h"] == 35)
check("vmc : 7 pièces → 135 m³/h",
      run({"nb_pieces_principales": 7})["debit_global_minimal_m3h"] == 135)
check("vmc : 0 pièce → ValueError",
      raises_value_error(run, {"nb_pieces_principales": 0}))

# ===========================================================================
# BLOC CHARPENTE BOIS / GEOTECHNIQUE — 5 skills
# ===========================================================================
print("\n[Bloc Charpente bois / Géotechnique]")

# --- btp_verif_solive_bois_flexion ---
run = run_of("btp_verif_solive_bois_flexion")
# b=75 h=200 entraxe=0.5 portée=4 charge=2.5 → q=1.25, M=2.5 kN·m, W=5e5, σ=5.0 MPa
r = run({"b_mm": 75, "h_mm": 200, "entraxe_m": 0.5, "portee_m": 4.0,
         "charge_surfacique_kn_m2": 2.5, "fm_d_mpa": 14})
check("solive bois : σ = 5.0 MPa, M = 2.5 kN·m (calcul main)",
      abs(r["contrainte_flexion_mpa"] - 5.0) < 0.01
      and abs(r["moment_max_kn_m"] - 2.5) < 0.01)
check("solive bois : conforme (5.0 <= 14 MPa)", r["conforme"] is True)
check("solive bois : section nulle → ValueError",
      raises_value_error(run, {"b_mm": 0, "h_mm": 200, "entraxe_m": 0.5, "portee_m": 4.0,
                               "charge_surfacique_kn_m2": 2.5, "fm_d_mpa": 14}))

# --- btp_calc_fleche_solive_bois ---
run = run_of("btp_calc_fleche_solive_bois")
# même solive, E=11000 → f ≈ 7.576 mm, limite L/300 = 13.33 mm
r = run({"b_mm": 75, "h_mm": 200, "entraxe_m": 0.5, "portee_m": 4.0,
         "charge_surfacique_kn_m2": 2.5, "module_e_mpa": 11000})
check("flèche solive : f ≈ 7.576 mm (calcul main)", abs(r["fleche_mm"] - 7.576) < 0.01)
check("flèche solive : conforme (7.58 < L/300 = 13.33 mm)", r["conforme"] is True)

# --- btp_calc_compression_poteau_bois ---
run = run_of("btp_calc_compression_poteau_bois")
# b=150 h=150 N=100 kN → A=22500, σ = 100000/22500 = 4.444 MPa
r = run({"b_mm": 150, "h_mm": 150, "N_Ed_kN": 100, "fc_0_d_mpa": 21})
check("poteau bois : σ ≈ 4.444 MPa (calcul main)",
      abs(r["contrainte_compression_mpa"] - 4.444) < 0.01)
check("poteau bois : conforme (4.44 <= 21 MPa)", r["conforme"] is True)
check("poteau bois : N nul → ValueError",
      raises_value_error(run, {"b_mm": 150, "h_mm": 150, "N_Ed_kN": 0, "fc_0_d_mpa": 21}))

# --- btp_calc_poussee_terres_rankine ---
run = run_of("btp_calc_poussee_terres_rankine")
# H=3 γ=18 φ=30° → Ka = tan²(30°) = 0.3333, P = 0.5×0.3333×18×9 = 27.0 kN/ml
r = run({"hauteur_ecran_m": 3, "poids_volumique_kn_m3": 18, "angle_frottement_deg": 30})
check("poussée Rankine : Ka ≈ 0.333, P = 27.0 kN/ml (calcul main)",
      abs(r["coefficient_ka"] - 0.3333) < 0.001
      and abs(r["poussee_resultante_kn_ml"] - 27.0) < 0.05)
check("poussée Rankine : point d'application à H/3 = 1.0 m",
      abs(r["point_application_m"] - 1.0) < 0.001)
check("poussée Rankine : angle de frottement invalide → ValueError",
      raises_value_error(run, {"hauteur_ecran_m": 3, "poids_volumique_kn_m3": 18,
                               "angle_frottement_deg": 100}))

# --- btp_verif_angle_talus ---
run = run_of("btp_verif_angle_talus")
# talus 20°, φ=33° → FS = tan(33°)/tan(20°) ≈ 1.784 ≥ 1.5 → stable
r = run({"angle_talus_deg": 20, "angle_frottement_deg": 33})
check("talus : FS ≈ 1.784, conforme (>= 1.5)",
      abs(r["facteur_securite_calcule"] - 1.784) < 0.01 and r["conforme"] is True)
check("talus : 40° avec φ=30° → instable",
      run({"angle_talus_deg": 40, "angle_frottement_deg": 30})["conforme"] is False)
check("talus : angle > 90 → ValueError",
      raises_value_error(run, {"angle_talus_deg": 95, "angle_frottement_deg": 30}))

# ===========================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
