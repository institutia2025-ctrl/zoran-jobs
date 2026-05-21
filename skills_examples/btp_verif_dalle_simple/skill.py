"""skill btp_verif_dalle_simple — verification dalle BA portee simple.

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Structure (3/5).
Source : NF EN 1992-1-1 §7.4.2 (limitation fleche) + §9.3 (dispositions dalles).

Verification rapide d'epaisseur dalle pleine BA, portee simple (appui-appui),
sous chargement statique modere. Methode predimensionnement via rapport l/d :

    l/d <= K × [11 + 1.5×√fck × (ρ0/ρ) + 3.2×√fck × (ρ0/ρ - 1)^1.5] (EC2 §7.4.2)

⚠️ MVP : on utilise le ratio L/d limite SIMPLIFIE typique habitat courant :
   - dalle pleine portee simple : L/d = 25 (EC2 tableau 7.4N adapte K=1.0, ρ=ρ0)
   - dalle pleine portee multiple : L/d = 32

Cas couvert : dalle pleine BA, portee uniaxiale ou bidirectionnelle ratio < 2,
chargement habitat courant (G+Q). Verifie h_min predimensionnement.

Contrat io :
    inputs : {
        "portee_l_m": float,
        "epaisseur_h_mm": int,
        "enrobage_mm": int,
        "type_appui": str,           # "simple" | "continu"
        "fck_mpa": float
    }
    outputs : {
        "h_min_mm": int,
        "conforme": bool,
        "ratio_l_d": float,
        "ratio_l_d_max": float,
        "marge_mm": int,
        "reference": str
    }
"""
from __future__ import annotations

L_SUR_D_MAX = {"simple": 25.0, "continu": 32.0}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    L = inputs.get("portee_l_m")
    h = inputs.get("epaisseur_h_mm")
    c = inputs.get("enrobage_mm")
    typ = inputs.get("type_appui")
    fck = inputs.get("fck_mpa")

    if not isinstance(L, (int, float)) or L <= 0:
        raise ValueError("portee_l_m > 0 requis")
    for nom, val in [("epaisseur_h_mm", h), ("enrobage_mm", c)]:
        if not isinstance(val, int) or val <= 0:
            raise ValueError(f"{nom} entier > 0 requis (mm)")
    if typ not in L_SUR_D_MAX:
        raise ValueError(f"type_appui doit etre dans {sorted(L_SUR_D_MAX)}")
    if not isinstance(fck, (int, float)) or fck <= 0:
        raise ValueError("fck_mpa > 0 requis")

    if c >= h:
        raise ValueError("enrobage >= epaisseur : section impossible")

    d = h - c  # hauteur utile mm
    L_mm = L * 1000.0
    ratio_actuel = L_mm / d
    ratio_max = L_SUR_D_MAX[typ]

    # epaisseur min predimensionnement
    d_min = L_mm / ratio_max
    h_min = int(d_min + c + 0.5)  # arrondi au mm superieur

    marge = h - h_min  # mm

    return {
        "h_min_mm": h_min,
        "conforme": ratio_actuel <= ratio_max,
        "ratio_l_d": round(ratio_actuel, 2),
        "ratio_l_d_max": ratio_max,
        "marge_mm": marge,
        "reference": "NF EN 1992-1-1 §7.4.2 (limitation fleche par L/d) + §9.3 (dispositions dalles)",
    }
