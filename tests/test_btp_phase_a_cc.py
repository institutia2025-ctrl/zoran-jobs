"""
tests/test_btp_phase_a_cc.py — Tests des 10 skills BTP du lot « Claude Code ».

Mission : ZORAN_JOBS_20260521 · Phase A (second œuvre · conduite · économie)
Signé : Claude Code, prestataire, 2026-05-21

Couvre les 10 skills `skills/btp_verif_peinture/placo/ite/menuiserie*`,
`skills/btp_analyse/matrice/coordination*`, `skills/btp_metre/ratio*` —
préfixes disjoints du lot Sonnet (aucun recouvrement, cf. lettre de mission).

Chaque skill est chargé via le runtime réel (Registry + Loader, vérification de
hash comprise) puis exécuté sur des cas conformes ET non conformes.

Exécutable : python tests/test_btp_phase_a_cc.py
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
print("TESTS BTP PHASE A — lot Claude Code (10 skills)")
print("=" * 60)

# --- Chargement via le runtime réel -----------------------------------------
reg = Registry()
report = reg.load_from_dir(ROOT / "skills")
loader = Loader()

CC_SKILLS = [
    "btp_verif_peinture_dtu59_1", "btp_verif_placo_dtu25_41",
    "btp_verif_ite_dtu45_3", "btp_verif_menuiserie_pvc_dtu36_5",
    "btp_analyse_retard_chantier", "btp_matrice_risques_chantier",
    "btp_coordination_corps_etat", "btp_metre_quantite_simple",
    "btp_ratio_estimatif_courant", "btp_analyse_dpgf",
]

check("0 manifest rejeté dans skills/", report["n_rejected"] == 0)
check("les 10 skills CC sont indexés", set(CC_SKILLS).issubset(set(reg.list_skills())))


def run_of(sid: str):
    """Charge un skill (hash vérifié) et renvoie sa fonction run."""
    manifest = reg.get(sid)
    module, err = loader.load(manifest)
    if module is None:
        raise AssertionError(f"{sid} non chargé : {err}")
    return module.run


for _sid in CC_SKILLS:
    try:
        run_of(_sid)
        check(f"{_sid} : chargé + hash vérifié", True)
    except Exception as e:  # noqa: BLE001
        check(f"{_sid} : chargé + hash vérifié — {e}", False)

# --- 1. btp_verif_peinture_dtu59_1 ------------------------------------------
run = run_of("btp_verif_peinture_dtu59_1")
r = run({"support": "enduit_platre", "humidite_pct": 3.0, "temperature_c": 20.0,
         "hygrometrie_ambiante_pct": 55.0, "support_prepare": True})
check("peinture : cas conforme", r["conforme"] is True and r["non_conformites"] == [])
r = run({"support": "beton", "humidite_pct": 9.0, "temperature_c": 2.0,
         "hygrometrie_ambiante_pct": 85.0, "support_prepare": False})
check("peinture : 4 non-conformités détectées",
      r["conforme"] is False and len(r["non_conformites"]) == 4)

# --- 2. btp_verif_placo_dtu25_41 --------------------------------------------
run = run_of("btp_verif_placo_dtu25_41")
r = run({"epaisseur_plaque_mm": 12.5, "entraxe_montants_mm": 600,
         "entraxe_vis_mm": 250, "type_plaque": "standard", "local_humide": False})
check("placo : cas conforme", r["conforme"] is True)
r = run({"epaisseur_plaque_mm": 10, "entraxe_montants_mm": 700,
         "entraxe_vis_mm": 350, "type_plaque": "standard", "local_humide": True})
check("placo : 4 non-conformités détectées", len(r["non_conformites"]) == 4)
check("placo : local humide exige hydrofuge",
      any("hydrofuge" in nc for nc in r["non_conformites"]))

# --- 3. btp_verif_ite_dtu45_3 -----------------------------------------------
run = run_of("btp_verif_ite_dtu45_3")
r = run({"type_isolant": "pse", "epaisseur_isolant_mm": 120, "nb_chevilles_m2": 6,
         "collage_pct": 50, "support": "beton"})
check("ITE : cas conforme sans avertissement",
      r["conforme"] is True and r["avertissements"] == [])
r = run({"type_isolant": "pse", "epaisseur_isolant_mm": 90, "nb_chevilles_m2": 6,
         "collage_pct": 50, "support": "beton"})
check("ITE : épaisseur limite -> conforme + avertissement",
      r["conforme"] is True and len(r["avertissements"]) == 1)
r = run({"type_isolant": "inconnu", "epaisseur_isolant_mm": 50, "nb_chevilles_m2": 3,
         "collage_pct": 20, "support": "inconnu"})
check("ITE : 5 non-conformités détectées", len(r["non_conformites"]) == 5)

# --- 4. btp_verif_menuiserie_pvc_dtu36_5 ------------------------------------
run = run_of("btp_verif_menuiserie_pvc_dtu36_5")
r = run({"largeur_mm": 1200, "hauteur_mm": 1000, "nb_points_fixation": 4,
         "type_pose": "neuf", "etancheite_realisee": True, "calage_realise": True})
check("menuiserie : cas conforme (4 points requis)",
      r["conforme"] is True and r["nb_points_requis"] == 4)
r = run({"largeur_mm": 1200, "hauteur_mm": 2400, "nb_points_fixation": 2,
         "type_pose": "neuf", "etancheite_realisee": False, "calage_realise": False})
check("menuiserie : grande fenêtre exige 8 points", r["nb_points_requis"] == 8)
check("menuiserie : 3 non-conformités détectées", len(r["non_conformites"]) == 3)

# --- 5. btp_analyse_retard_chantier -----------------------------------------
run = run_of("btp_analyse_retard_chantier")
r = run({"description_retard": "livraison béton retardée",
         "chaine_pourquoi": ["a", "b", "c", "d", "défaut planification appro"],
         "probabilite": 4, "gravite": 4})
check("retard : 5 pourquoi -> analyse complète", r["analyse_complete"] is True)
check("retard : cause racine = dernier pourquoi",
      r["cause_racine"] == "défaut planification appro")
check("retard : criticité 16 -> niveau critique",
      r["criticite"] == 16 and r["niveau_criticite"] == "critique")
r = run({"description_retard": "x", "chaine_pourquoi": ["a", "b"],
         "probabilite": 2, "gravite": 2})
check("retard : chaîne courte -> analyse incomplète",
      r["analyse_complete"] is False and r["niveau_criticite"] == "faible")

# --- 6. btp_matrice_risques_chantier ----------------------------------------
run = run_of("btp_matrice_risques_chantier")
r = run({"risques": [
    {"nom": "R1", "probabilite": 5, "gravite": 5},
    {"nom": "R2", "probabilite": 1, "gravite": 1},
    {"nom": "R3", "probabilite": 3, "gravite": 2}]})
check("matrice : classée par criticité décroissante",
      [m["nom"] for m in r["matrice"]] == ["R1", "R3", "R2"])
check("matrice : risque majeur = R1", r["risque_majeur"] == "R1")
check("matrice : 1 risque inacceptable", r["nb_inacceptables"] == 1)

# --- 7. btp_coordination_corps_etat -----------------------------------------
run = run_of("btp_coordination_corps_etat")
r = run({"taches": [
    {"id": "A", "duree": 2, "predecesseurs": []},
    {"id": "B", "duree": 3, "predecesseurs": ["A"]},
    {"id": "C", "duree": 1, "predecesseurs": ["A"]},
    {"id": "D", "duree": 2, "predecesseurs": ["B", "C"]}]})
check("coordination : aucun cycle", r["cycle_detecte"] is False)
check("coordination : durée totale = 7", r["duree_totale"] == 7.0)
check("coordination : chemin critique A->B->D", r["chemin_critique"] == ["A", "B", "D"])
r = run({"taches": [
    {"id": "X", "duree": 1, "predecesseurs": ["Y"]},
    {"id": "Y", "duree": 1, "predecesseurs": ["X"]}]})
check("coordination : cycle détecté", r["cycle_detecte"] is True)

# --- 8. btp_metre_quantite_simple -------------------------------------------
run = run_of("btp_metre_quantite_simple")
r = run({"elements": [
    {"type": "surface_rect", "dimensions": {"longueur": 4, "largeur": 3}},
    {"type": "surface_triangle", "dimensions": {"base": 6, "hauteur": 4}},
    {"type": "volume_box", "dimensions": {"longueur": 2, "largeur": 2, "hauteur": 2}},
    {"type": "lineaire", "dimensions": {"longueur": 10}}]})
check("métré : surface totale = 24 m²", r["total_surface_m2"] == 24.0)
check("métré : volume total = 8 m³", r["total_volume_m3"] == 8.0)
check("métré : linéaire total = 10 ml", r["total_lineaire_ml"] == 10.0)
r = run({"elements": [{"type": "forme_inconnue", "dimensions": {}}]})
check("métré : type inconnu signalé", len(r["erreurs"]) == 1)

# --- 9. btp_ratio_estimatif_courant -----------------------------------------
run = run_of("btp_ratio_estimatif_courant")
r = run({"type_ouvrage": "maison_individuelle", "surface_m2": 100,
         "niveau_standing": "courant"})
check("ratio : coût estimé = 170 000 €", r["cout_estime_eur"] == 170000)
check("ratio : fourchette encadre l'estimation",
      r["fourchette_basse_eur"] < r["cout_estime_eur"] < r["fourchette_haute_eur"])
r = run({"type_ouvrage": "ouvrage_inconnu", "surface_m2": 100})
check("ratio : ouvrage inconnu -> erreur + coût 0",
      r["cout_estime_eur"] == 0 and len(r["erreurs"]) >= 1)

# --- 10. btp_analyse_dpgf ---------------------------------------------------
run = run_of("btp_analyse_dpgf")
r = run({"lignes": [
    {"designation": "Béton", "quantite": 10, "prix_unitaire": 120, "montant": 1200},
    {"designation": "Acier", "quantite": 5, "prix_unitaire": 200, "montant": 1000}]})
check("DPGF : cas cohérent", r["coherent"] is True and r["total_calcule_eur"] == 2200.0)
r = run({"lignes": [
    {"designation": "Béton", "quantite": 10, "prix_unitaire": 120, "montant": 1200},
    {"designation": "Acier", "quantite": 5, "prix_unitaire": 200, "montant": 1500}]})
check("DPGF : montant incohérent détecté",
      r["coherent"] is False and r["nb_anomalies"] == 1)
r = run({"lignes": [{"designation": "", "quantite": 0, "prix_unitaire": 0}]})
check("DPGF : ligne vide -> plusieurs anomalies", r["nb_anomalies"] >= 3)

# ============================================================================
print()
print("=" * 60)
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
