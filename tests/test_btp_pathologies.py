"""
tests/test_btp_pathologies.py — Tests Phase A Pathologies (5 skills V2).

Mission : ZORAN_JOBS_20260521 · ZORAN_BTP_PARALLEL_SONNET_20260521.
Signé : Frederic TABARY + Claude Sonnet, 2026-05-21.

Pour chaque skill : positif + négatif minimum + routage end-to-end.
Loi 1 : tests rédigés à partir de valeurs publiques sourcées,
        AUCUN seuil mm/% fabriqué.
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
from runtime.coherence.engine import CoherenceState  # noqa: E402
from runtime.loop import run_once  # noqa: E402

PASS, FAIL = 0, 0


def check(label: str, condition: bool) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def get_mod(skill_id: str):
    reg = Registry()
    reg.load_from_dir(ROOT / "skills_examples")
    m = reg.get(skill_id)
    assert m is not None, f"{skill_id} introuvable"
    loader = Loader()
    mod, err = loader.load(m)
    assert mod is not None, f"chargement {skill_id} : {err}"
    return mod


# =========================================================
# 1 — btp_diag_fissure_macon
# =========================================================
print("=== TEST 1 — btp_diag_fissure_macon ===")
mod = get_mod("btp_diag_fissure_macon")

# Cas non-structurel, cloison, faible
out = mod.run({"largeur_mm": 0.3, "traversante": False,
               "localisation": "cloison", "evolution_active": False})
check("cloison non traversante stabilisee → non structurelle, faible",
      out["structurelle_suspectee"] is False and out["gravite"] == "faible")

# Cas structurel critique : mur porteur + traversante + active
out_crit = mod.run({"largeur_mm": 5.0, "traversante": True,
                    "localisation": "mur_porteur", "evolution_active": True})
check("mur porteur + traversante + active → critique",
      out_crit["structurelle_suspectee"] is True and out_crit["gravite"] == "critique")
check("reference DTU 20.1 tracee", "DTU 20.1" in out_crit["reference"])

# Avec grille AQC fournie (Loi 1 : utilisateur)
out_aqc = mod.run({"largeur_mm": 3.0, "traversante": False, "localisation": "cloison",
                   "evolution_active": False,
                   "seuils_aqc_mm": {"a_max": 0.2, "b_max": 2.0, "c_max": 10.0},
                   "source_seuils_aqc": "Fiche AQC exemple utilisateur 2024"})
check("largeur 3.0 + grille → classe c", out_aqc["classe_aqc"] == "c")
check("source utilisateur tracee dans reference", "Fiche AQC" in out_aqc["reference"])

# Négatif : seuils fournis sans source = Loi 1 violee
err = False
try:
    mod.run({"largeur_mm": 1.0, "traversante": False, "localisation": "cloison",
             "evolution_active": False,
             "seuils_aqc_mm": {"a_max": 0.2, "b_max": 2.0, "c_max": 10.0}})
except ValueError:
    err = True
check("seuils sans source → ValueError (Loi 1)", err)

# =========================================================
# 2 — btp_diag_humidite_remontee
# =========================================================
print()
print("=== TEST 2 — btp_diag_humidite_remontee ===")
mod = get_mod("btp_diag_humidite_remontee")

out_pos = mod.run({"hauteur_zone_humide_cm": 80, "efflorescences_salines": True,
                   "presence_revetement_etanche": True})
check("h=80cm + efflorescences + rev etanche → suspectee + elevee",
      out_pos["remontee_capillaire_suspectee"] is True and out_pos["gravite"] == "elevee")

out_neg = mod.run({"hauteur_zone_humide_cm": 0, "efflorescences_salines": False,
                   "presence_revetement_etanche": False})
check("aucun symptome → non suspectee + faible",
      out_neg["remontee_capillaire_suspectee"] is False and out_neg["gravite"] == "faible")

err = False
try:
    mod.run({"hauteur_zone_humide_cm": -5, "efflorescences_salines": False,
             "presence_revetement_etanche": False})
except ValueError:
    err = True
check("hauteur negative → ValueError", err)

# =========================================================
# 3 — btp_diag_carbonatation_beton
# =========================================================
print()
print("=== TEST 3 — btp_diag_carbonatation_beton ===")
mod = get_mod("btp_diag_carbonatation_beton")

# Cas OK : enrobage 30 mm, carbonatation 5 mm, XC1
out_ok = mod.run({"profondeur_carbonatation_mm": 5, "enrobage_nominal_mm": 30,
                  "classe_exposition": "XC1"})
check("marge confortable → pas de depassivation, marge 25 mm",
      out_ok["depassivation_atteinte"] is False and out_ok["marge_mm"] == 25.0)

# Cas KO : carbonatation > enrobage
out_ko = mod.run({"profondeur_carbonatation_mm": 35, "enrobage_nominal_mm": 30,
                  "classe_exposition": "XC4"})
check("carbonatation > enrobage → depassivation True, marge -5",
      out_ko["depassivation_atteinte"] is True and out_ko["marge_mm"] == -5.0)
check("verdict mentionne DEPASSIVATION", "DEPASSIVATION" in out_ko["verdict"])

# Négatif : classe inconnue
err = False
try:
    mod.run({"profondeur_carbonatation_mm": 5, "enrobage_nominal_mm": 30, "classe_exposition": "XX9"})
except ValueError:
    err = True
check("classe_exposition XX9 → ValueError (NF EN 206-1)", err)

# =========================================================
# 4 — btp_diag_corrosion_armatures
# =========================================================
print()
print("=== TEST 4 — btp_diag_corrosion_armatures ===")
mod = get_mod("btp_diag_corrosion_armatures")

# Cas critique : 30% perte + epaufrures
out_crit = mod.run({"perte_section_pct": 30, "classe_exposition": "XS2",
                    "fissuration_visible": True, "epaufrures_visibles": True})
check("perte 30% + epaufrures → severite critique + principe 10",
      out_crit["severite"] == "critique" and out_crit["principe_en1504_recommande"] == 10)

# Cas modere : 5% perte, fissuration
out_mod = mod.run({"perte_section_pct": 5, "classe_exposition": "XC3",
                   "fissuration_visible": True, "epaufrures_visibles": False})
check("perte 5% + fissuration → severite avancee",
      out_mod["severite"] == "avancee")

# Cas minime
out_min = mod.run({"perte_section_pct": 1, "classe_exposition": "XC1",
                   "fissuration_visible": False, "epaufrures_visibles": False})
check("perte 1% + rien → severite minime", out_min["severite"] == "minime")

# Négatif : perte hors borne
err = False
try:
    mod.run({"perte_section_pct": 150, "classe_exposition": "XC1",
             "fissuration_visible": False, "epaufrures_visibles": False})
except ValueError:
    err = True
check("perte_section_pct=150 → ValueError", err)

# =========================================================
# 5 — btp_diag_desordre_carrelage
# =========================================================
print()
print("=== TEST 5 — btp_diag_desordre_carrelage ===")
mod = get_mod("btp_diag_desordre_carrelage")

# Cas RAS
out_ras = mod.run({"decollement_localise": False, "sonnant_creux": False,
                   "faiencage_joints": False, "fissures_carreaux": False,
                   "taches_humidite": False})
check("aucun desordre → nb=0, faible", out_ras["nb_desordres"] == 0 and out_ras["gravite"] == "faible")

# Cas eleve : fissures dans carreaux
out_hi = mod.run({"decollement_localise": False, "sonnant_creux": True,
                  "faiencage_joints": False, "fissures_carreaux": True,
                  "taches_humidite": False, "classe_local": "EB"})
check("fissures + sonnant creux → elevee",
      out_hi["gravite"] == "elevee" and len(out_hi["origine_probable"]) >= 1)

# Négatif : type bool manquant
err = False
try:
    mod.run({"decollement_localise": "non", "sonnant_creux": False,
             "faiencage_joints": False, "fissures_carreaux": False,
             "taches_humidite": False})
except ValueError:
    err = True
check("decollement_localise='non' → ValueError (bool requis)", err)

# =========================================================
# 6 — Routage end-to-end : ZORAN's Jobs choisit le bon skill
# =========================================================
print()
print("=== TEST 6 — Routage E2E sur les 5 pathologies ===")
reg = Registry()
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()

prompts = [
    ("fissure traversante dans mur porteur lezarde DTU 20.1",
     "btp_diag_fissure_macon",
     {"largeur_mm": 1.0, "traversante": True, "localisation": "mur_porteur",
      "evolution_active": False}),
    ("humidite remontee capillaire salpetre efflorescence",
     "btp_diag_humidite_remontee",
     {"hauteur_zone_humide_cm": 50, "efflorescences_salines": True,
      "presence_revetement_etanche": False}),
    ("carbonatation beton enrobage armature depassivation EN 14630",
     "btp_diag_carbonatation_beton",
     {"profondeur_carbonatation_mm": 10, "enrobage_nominal_mm": 25,
      "classe_exposition": "XC3"}),
    ("corrosion armature rouille epaufrure principe EN 1504",
     "btp_diag_corrosion_armatures",
     {"perte_section_pct": 10, "classe_exposition": "XC4",
      "fissuration_visible": False, "epaufrures_visibles": False}),
    ("carrelage decollement sonnant creux faiencage DTU 52.2 desordre",
     "btp_diag_desordre_carrelage",
     {"decollement_localise": True, "sonnant_creux": True,
      "faiencage_joints": False, "fissures_carreaux": False,
      "taches_humidite": False}),
]

for prompt, attendu, inps in prompts:
    state = CoherenceState()
    trace = run_once(prompt, inps, reg, loader, state)
    actual = trace.get("selected", "<none>")
    check(f"'{prompt[:50]}…' → {attendu}", actual == attendu)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
