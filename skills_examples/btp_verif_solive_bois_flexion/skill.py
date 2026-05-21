"""skill Vérification d'une solive bois en flexion.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Charpente bois.
Source : NF EN 1995-1-1 (Eurocode 5) §6.1.6 + NF DTU 31.1 (charpente bois).

Vérifie une solive en flexion simple sous charge répartie :
    q = charge_surfacique × entraxe   (charge linéique)
    M = q × L² / 8                    (moment maximal, travée sur 2 appuis)
    σ = M / W,  avec W = b·h²/6        (contrainte de flexion)
    conforme si σ ≤ fm,d              (résistance de flexion de calcul)

⚠️ MVP : flexion simple, travée isostatique sur deux appuis. Ne traite ni le
cisaillement, ni le déversement, ni la flèche (voir btp_calc_fleche_solive_bois).
Loi 1 : fm,d (résistance de flexion de calcul) dépend de la classe de bois et
des coefficients EC5 (kmod, γM) — elle est fournie par l'appelant.

Contrat io :
    inputs  : {b_mm, h_mm, entraxe_m, portee_m, charge_surfacique_kn_m2, fm_d_mpa}
    outputs : {contrainte_flexion_mpa, moment_max_kn_m, conforme, marge_mpa, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    champs = ("b_mm", "h_mm", "entraxe_m", "portee_m",
              "charge_surfacique_kn_m2", "fm_d_mpa")
    for nom in champs:
        v = inputs.get(nom)
        if not _nombre(v) or v <= 0:
            raise ValueError(f"{nom} : nombre > 0 requis")

    b = float(inputs["b_mm"])
    h = float(inputs["h_mm"])
    q = float(inputs["charge_surfacique_kn_m2"]) * float(inputs["entraxe_m"])  # kN/m
    portee = float(inputs["portee_m"])
    fm_d = float(inputs["fm_d_mpa"])

    moment = q * portee ** 2 / 8.0          # kN·m
    module_w = b * h ** 2 / 6.0             # mm³
    contrainte = moment * 1.0e6 / module_w  # MPa
    conforme = contrainte <= fm_d
    return {
        "moment_max_kn_m": round(moment, 3),
        "contrainte_flexion_mpa": round(contrainte, 3),
        "fm_d_mpa": fm_d,
        "marge_mpa": round(fm_d - contrainte, 3),
        "conforme": conforme,
        "verdict": ("Solive conforme en flexion (EC5)." if conforme
                    else "Solive NON conforme — contrainte de flexion dépassée (EC5)."),
        "reference": "NF EN 1995-1-1 §6.1.6 + NF DTU 31.1 (flexion solive bois)",
    }
