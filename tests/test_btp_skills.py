"""
tests/test_btp_skills.py — Tests Phase A BTP (5 skills, décorateur → nucléaire).

Mission : ZORAN_JOBS_20260521 · Phase A BTP
Signé : Frederic TABARY + Claude, 2026-05-21.

Pour chaque skill : 1 cas positif (heureux) + 1 cas négatif (erreur attendue).
Plus 1 test end-to-end : le Router doit sélectionner le bon skill BTP via ses triggers.
Falsifiabilité : si un calcul ment, le test négatif tombe.

Total : 11 assertions BTP + 5 assertions de routage = 16 assertions.
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


def get_skill_module(skill_id: str):
    """Charge un skill via le Registry + Loader (chaine de confiance hash)."""
    reg = Registry()
    reg.load_from_dir(ROOT / "skills_examples")
    manifest = reg.get(skill_id)
    assert manifest is not None, f"skill {skill_id} introuvable dans le registry"
    loader = Loader()
    module, err = loader.load(manifest)
    assert module is not None, f"chargement {skill_id} echoue : {err}"
    return module


print("=== TEST 1 — palette_harmonique (decorateur) ===")
mod = get_skill_module("palette_harmonique")
out = mod.run({"hue": 180})
check("3 teintes generees", len(out["palette"]) == 3)
check("harmony = triadique", out["harmony"] == "triadique")
check("teintes equidistantes (180, 300, 60)",
      [c["hue"] for c in out["palette"]] == [180, 300, 60])

# Negatif : teinte hors borne doit lever
err_raised = False
try:
    mod.run({"hue": 500})
except ValueError:
    err_raised = True
check("hue=500 → ValueError leve (negatif)", err_raised)

print()
print("=== TEST 2 — verif_dtu_carrelage (MOE, DTU 52.2) ===")
mod = get_skill_module("verif_dtu_carrelage")
# Cas conforme : seuils respectes
out = mod.run({"planeite_2m_mm": 4.0, "planeite_20cm_mm": 1.5})
check("planeite OK → conforme=True", out["conforme"] is True and out["violations"] == [])

# Cas non-conforme : planéité 2m dépasse 5 mm
out_ko = mod.run({"planeite_2m_mm": 7.0, "planeite_20cm_mm": 1.5})
check("planeite 7mm > 5mm → conforme=False",
      out_ko["conforme"] is False and len(out_ko["violations"]) == 1)
check("reference DTU 52.2 tracee", "DTU 52.2" in out_ko["reference"])

print()
print("=== TEST 3 — planning_gantt_simple (conducteur, CPM) ===")
mod = get_skill_module("planning_gantt_simple")
# Cas type : A→B→C lineaire (durees 2,3,4) ; D parallele de duree 1
tasks = [
    {"id": "A", "duree_j": 2, "depends_on": []},
    {"id": "B", "duree_j": 3, "depends_on": ["A"]},
    {"id": "C", "duree_j": 4, "depends_on": ["B"]},
    {"id": "D", "duree_j": 1, "depends_on": ["A"]},
]
out = mod.run({"tasks": tasks})
check("duree totale = 9 (2+3+4)", out["duree_totale_j"] == 9)
check("chemin critique = [A,B,C]", out["chemin_critique"] == ["A", "B", "C"])

# Negatif : cycle de dependances
err_raised = False
try:
    mod.run({"tasks": [
        {"id": "X", "duree_j": 1, "depends_on": ["Y"]},
        {"id": "Y", "duree_j": 1, "depends_on": ["X"]},
    ]})
except ValueError:
    err_raised = True
check("cycle X↔Y → ValueError (negatif)", err_raised)

print()
print("=== TEST 4 — descente_charges_simple (ingenieur GC, Eurocode) ===")
mod = get_skill_module("descente_charges_simple")
# Cas : poteau central R+5, surface tributaire 25 m2, G=6 kN/m2, Q=2.5 kN/m2
# G_total = 6 * 25 * 5 = 750 kN ; Q_total = 2.5 * 25 * 5 = 312.5 kN
# N_ELU = 1.35*750 + 1.5*312.5 = 1012.5 + 468.75 = 1481.25 kN
out = mod.run({"surface_tributaire_m2": 25, "nb_etages": 5, "g_kn_m2": 6, "q_kn_m2": 2.5})
check("N_ELU = 1481.25 kN (calcul main)", abs(out["N_ELU_kN"] - 1481.25) < 0.01)
check("N_ELS = 1062.5 kN", abs(out["N_ELS_kN"] - 1062.5) < 0.01)

# Negatif : nb_etages 0 doit lever
err_raised = False
try:
    mod.run({"surface_tributaire_m2": 25, "nb_etages": 0, "g_kn_m2": 6, "q_kn_m2": 2})
except ValueError:
    err_raised = True
check("nb_etages=0 → ValueError (negatif)", err_raised)

print()
print("=== TEST 5 — verif_seisme_classe1_asn (ingenieur nucleaire, RFS 2001-01) ===")
mod = get_skill_module("verif_seisme_classe1_asn")
# Cas conforme : PGA dim 0.30g >= SMS calcule (0.20 * 1.4 = 0.28)
out = mod.run({"pga_smhv_g": 0.20, "marge_sms": 1.4,
               "pga_dimensionnement_g": 0.30, "classe_eips": "F1A"})
check("conforme=True, sms=0.28g", out["conforme"] is True and abs(out["sms_calcule_g"] - 0.28) < 0.001)

# Cas non-conforme : PGA dim < SMS
out_ko = mod.run({"pga_smhv_g": 0.25, "marge_sms": 1.5,
                  "pga_dimensionnement_g": 0.20, "classe_eips": "F1B"})
check("PGA dim < SMS → conforme=False", out_ko["conforme"] is False)
check("verdict NON CONFORME trace", "NON CONFORME" in out_ko["verdict"])

# Negatif : marge < 1.0 doit lever (principe RFS)
err_raised = False
try:
    mod.run({"pga_smhv_g": 0.20, "marge_sms": 0.5,
             "pga_dimensionnement_g": 0.30, "classe_eips": "F1A"})
except ValueError:
    err_raised = True
check("marge_sms=0.5 (<1.0) → ValueError (negatif)", err_raised)

print()
print("=== TEST 6 — Routage end-to-end : ZORAN's Jobs choisit le bon skill BTP ===")
reg = Registry()
reg.load_from_dir(ROOT / "skills_examples")
loader = Loader()

prompts_attendus = [
    ("genere moi une palette de couleur harmonie triadique", "palette_harmonique"),
    ("verifie la planeite pour pose collee carrelage selon DTU 52", "verif_dtu_carrelage"),
    ("calcule le planning gantt et chemin critique", "planning_gantt_simple"),
    ("descente de charges sur poteau ELU eurocode", "descente_charges_simple"),
    ("verification seisme EIPS classe F1A selon RFS ASN", "verif_seisme_classe1_asn"),
]
# Pour chaque, on fournit des inputs minimaux pour eviter skill_failed
inputs_par_skill = {
    "palette_harmonique": {"hue": 180},
    "verif_dtu_carrelage": {"planeite_2m_mm": 3.0, "planeite_20cm_mm": 1.0},
    "planning_gantt_simple": {"tasks": [{"id": "T1", "duree_j": 1, "depends_on": []}]},
    "descente_charges_simple": {"surface_tributaire_m2": 10, "nb_etages": 1, "g_kn_m2": 5, "q_kn_m2": 2},
    "verif_seisme_classe1_asn": {"pga_smhv_g": 0.2, "marge_sms": 1.4,
                                  "pga_dimensionnement_g": 0.3, "classe_eips": "F1A"},
}

for prompt, attendu in prompts_attendus:
    state = CoherenceState()
    trace = run_once(prompt, inputs_par_skill[attendu], reg, loader, state)
    actual = trace.get("selected", "<aucun>")
    check(f"'{prompt[:40]}…' → {attendu} (selectionne: {actual})", actual == attendu)

print()
print(f"=== RESULTAT : {PASS} PASS / {FAIL} FAIL ===")
sys.exit(0 if FAIL == 0 else 1)
