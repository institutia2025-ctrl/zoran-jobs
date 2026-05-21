"""skill Calcul de flèche d'une solive bois.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Charpente bois.
Source : NF EN 1995-1-1 (Eurocode 5) §7.2 (états limites de service — flèche).

Calcule la flèche d'une solive bois sous charge répartie, travée isostatique :
    I = b·h³/12                          (moment d'inertie)
    f = 5·q·L⁴ / (384·E·I)               (flèche à mi-travée)
et la compare à une limite admissible (par défaut L/300, usage courant).

⚠️ MVP : flèche instantanée sous charge répartie uniforme, travée sur deux
appuis. Ne traite pas la flèche différée (fluage, kdef) ni les charges
ponctuelles. Limite L/300 par défaut — un CCTP peut imposer L/500.
Loi 1 : le module d'élasticité E dépend de la classe de bois — il est fourni.

Contrat io :
    inputs  : {b_mm, h_mm, entraxe_m, portee_m, charge_surfacique_kn_m2,
               module_e_mpa, limite_fleche_denominateur?}
    outputs : {fleche_mm, fleche_limite_mm, conforme, reference}
"""

from __future__ import annotations

LIMITE_DENOMINATEUR_DEFAUT = 300.0  # flèche admissible L/300 — usage courant


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    for nom in ("b_mm", "h_mm", "entraxe_m", "portee_m",
                "charge_surfacique_kn_m2", "module_e_mpa"):
        v = inputs.get(nom)
        if not _nombre(v) or v <= 0:
            raise ValueError(f"{nom} : nombre > 0 requis")
    denom = inputs.get("limite_fleche_denominateur", LIMITE_DENOMINATEUR_DEFAUT)
    if not _nombre(denom) or denom <= 0:
        raise ValueError("limite_fleche_denominateur : nombre > 0 requis")

    b = float(inputs["b_mm"])
    h = float(inputs["h_mm"])
    portee_mm = float(inputs["portee_m"]) * 1000.0
    module_e = float(inputs["module_e_mpa"])
    # 1 kN/m = 1 N/mm : q_lineique en N/mm = charge surfacique x entraxe.
    q = float(inputs["charge_surfacique_kn_m2"]) * float(inputs["entraxe_m"])

    inertie = b * h ** 3 / 12.0  # mm⁴
    fleche = 5.0 * q * portee_mm ** 4 / (384.0 * module_e * inertie)  # mm
    limite = portee_mm / float(denom)
    conforme = fleche <= limite
    return {
        "fleche_mm": round(fleche, 3),
        "fleche_limite_mm": round(limite, 3),
        "limite_appliquee": f"L/{denom:.0f}",
        "conforme": conforme,
        "verdict": ("Flèche admissible (EC5 §7.2)." if conforme
                    else "Flèche excessive — dépasse la limite admissible (EC5 §7.2)."),
        "reference": "NF EN 1995-1-1 §7.2 (flèche, états limites de service)",
    }
