"""skill Section minimale d'un câble pour respecter la chute de tension.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Électricité.
Source : NF C 15-100 (installations électriques basse tension).

Calcule la section minimale d'un conducteur pour que la chute de tension reste
sous une limite, puis recommande la première section normalisée suffisante :
    ΔU_max = limite_pct × U / 100
    S_min  = b × ρ × L × I_B × cosφ / ΔU_max

⚠️ MVP : critère « chute de tension » uniquement. La section finale doit AUSSI
satisfaire le critère d'échauffement (courant admissible I_z selon mode de pose
et isolant, tableaux NF C 15-100) — non traité ici. Retenir la plus grande des
deux sections.
Loi 1 : résistivité du cuivre par défaut 0,023 Ω·mm²/m (NF C 15-100).

Contrat io :
    inputs  : {type_circuit, longueur_m, courant_a, tension_v, cosphi?,
               resistivite?, limite_pct?}
    outputs : {section_min_mm2, section_normalisee_recommandee_mm2, reference}
"""

from __future__ import annotations

import math

B_FACTEUR = {"monophase": 2.0, "triphase": math.sqrt(3.0)}
RESISTIVITE_CUIVRE = 0.023
LIMITE_DEFAUT_PCT = 5.0
# Séries de sections normalisées de conducteurs (mm²).
SECTIONS_NORMALISEES = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0]


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    type_circuit = str(inputs.get("type_circuit", "")).lower()
    if type_circuit not in B_FACTEUR:
        raise ValueError(f"type_circuit : attendu l'un de {sorted(B_FACTEUR)}")
    for nom in ("longueur_m", "courant_a", "tension_v"):
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
    courant = float(inputs["courant_a"])
    tension = float(inputs["tension_v"])

    chute_max_v = float(limite) * tension / 100.0
    section_min = b * float(resistivite) * longueur * courant * float(cosphi) / chute_max_v
    recommandee = next((s for s in SECTIONS_NORMALISEES if s >= section_min), None)
    return {
        "section_min_mm2": round(section_min, 3),
        "section_normalisee_recommandee_mm2": recommandee,
        "avertissement": ("Section au-delà de la série courante — étude spécifique requise."
                          if recommandee is None else
                          "Vérifier aussi le critère d'échauffement (I_z, NF C 15-100)."),
        "reference": "NF C 15-100 (section minimale, critère de chute de tension)",
    }
