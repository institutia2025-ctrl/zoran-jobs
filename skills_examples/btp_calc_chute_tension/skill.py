"""skill Calcul de chute de tension d'un circuit électrique.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Électricité.
Source : NF C 15-100 (installations électriques basse tension).

Calcule la chute de tension d'un circuit (approximation résistive) :
    ΔU = b × ρ × (L / S) × I_B × cosφ
avec b = 2 (monophasé) ou √3 (triphasé), ρ = résistivité du conducteur,
L = longueur, S = section, I_B = courant d'emploi.

⚠️ MVP : approximation résistive (terme inductif négligé — valable pour les
sections courantes du logement). Ne traite pas les régimes déséquilibrés.
Loi 1 : la résistivité par défaut 0,023 Ω·mm²/m est la valeur de calcul ΔU du
cuivre (NF C 15-100) ; surchargeable (aluminium ≈ 0,037).

Contrat io :
    inputs  : {type_circuit, longueur_m, section_mm2, courant_a, tension_v,
               cosphi?, resistivite?, limite_pct?}
    outputs : {chute_tension_v, chute_tension_pct, conforme, reference}
"""

from __future__ import annotations

import math

B_FACTEUR = {"monophase": 2.0, "triphase": math.sqrt(3.0)}
RESISTIVITE_CUIVRE = 0.023  # Ω·mm²/m — valeur de calcul ΔU, cuivre (NF C 15-100)
LIMITE_DEFAUT_PCT = 5.0     # limite usuelle (3 % éclairage, 5 % autres usages)


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    type_circuit = str(inputs.get("type_circuit", "")).lower()
    if type_circuit not in B_FACTEUR:
        raise ValueError(f"type_circuit : attendu l'un de {sorted(B_FACTEUR)}")
    for nom in ("longueur_m", "section_mm2", "courant_a", "tension_v"):
        v = inputs.get(nom)
        if not _nombre(v) or v <= 0:
            raise ValueError(f"{nom} : nombre > 0 requis")
    cosphi = inputs.get("cosphi", 1.0)
    resistivite = inputs.get("resistivite", RESISTIVITE_CUIVRE)
    limite = inputs.get("limite_pct", LIMITE_DEFAUT_PCT)
    if not _nombre(cosphi) or not (0.0 < cosphi <= 1.0):
        raise ValueError("cosphi : nombre dans ]0..1] requis")
    if not _nombre(resistivite) or resistivite <= 0:
        raise ValueError("resistivite : nombre > 0 requis")
    if not _nombre(limite) or limite <= 0:
        raise ValueError("limite_pct : nombre > 0 requis")

    b = B_FACTEUR[type_circuit]
    longueur = float(inputs["longueur_m"])
    section = float(inputs["section_mm2"])
    courant = float(inputs["courant_a"])
    tension = float(inputs["tension_v"])

    chute_v = b * float(resistivite) * (longueur / section) * courant * float(cosphi)
    chute_pct = chute_v / tension * 100.0
    conforme = chute_pct <= float(limite)
    return {
        "chute_tension_v": round(chute_v, 3),
        "chute_tension_pct": round(chute_pct, 3),
        "limite_pct": float(limite),
        "conforme": conforme,
        "verdict": ("Chute de tension admissible (NF C 15-100)." if conforme
                    else "Chute de tension excessive — augmenter la section (NF C 15-100)."),
        "reference": "NF C 15-100 (chute de tension des circuits BT)",
    }
