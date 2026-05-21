"""skill btp_verif_dalle_simple — verif dalle BA (uplift v1.1 : bidirectionnel + fleche).

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Struct (3/5, v1.1).
Sources :
  - NF EN 1992-1-1 §7.4.1 (limites fleche ELS quasi-permanente) : fleche <= L/250
  - NF EN 1992-1-1 §7.4.2 (limitation par ratio L/d) : verif rapide predim
  - Methode Bares-Hahn : abaques pour dalles bidirectionnelles ratio Lx/Ly in [1..2]
    Reduction de la portee effective par coefficient k selon Lx/Ly.

Approche v1.1 :
  1. Predim ratio L/d (§7.4.2) : seuil simple=25, continu=32
  2. Si dalle bidirectionnelle (ratio Ly/Lx fourni) → reduit portee effective
     par coefficient Bares-Hahn (table simplifiee)
  3. Calcul fleche reelle simplifiee charge uniformement repartie :
     f = 5 × q × L^4 / (384 × Ec_eff × I)
     avec Ec_eff = Ecm / (1 + φ) prenant en compte fluage (§7.4.3 simplifie)
  4. Verdict : conforme si max(ratio_OK, fleche < L/250)

⚠️ MVP : Bares-Hahn table simplifiee (5 points). Calcul fleche en negligeant
   fissuration (zone non fissuree). Calcul exact §7.4.3 demande integration
   moment-curvature sur la longueur.

Contrat io :
    inputs : {
        "portee_l_m": float,                      # portee principale Lx
        "portee_perpendiculaire_m"?: float,       # Ly si bidirectionnel
        "epaisseur_h_mm": int,
        "enrobage_mm": int,
        "type_appui": str,                        # "simple"|"continu"
        "fck_mpa": float,
        "charge_q_kn_m2"?: float,                 # charge ELS QP (uniformement repartie)
        "phi_fluage"?: float                      # coeff de fluage (defaut 2.0 habitat)
    }
    outputs : {
        "h_min_mm": int,
        "conforme": bool,
        "ratio_l_d": float,
        "ratio_l_d_max": float,
        "marge_mm": int,
        "bidirectionnel": bool,
        "coeff_bares_hahn": float,
        "fleche_calc_mm"?: float,
        "fleche_limite_mm"?: float,
        "reference": str
    }
"""
from __future__ import annotations

L_SUR_D_MAX = {"simple": 25.0, "continu": 32.0}

# Table Bares-Hahn simplifiee : coeff reducteur k sur portee effective
# pour dalle bidirectionnelle ratio Ly/Lx donne (Lx = portee principale courte)
# Source : abaques Bares-Hahn (manuels EC2)
BARES_HAHN_TABLE = [
    (1.0, 0.66),   # carre : reduction forte (effet 2D)
    (1.25, 0.74),
    (1.5, 0.82),
    (1.75, 0.90),
    (2.0, 0.95),
    (10.0, 1.0),   # > 2 : considere comme uniaxial
]


def _coeff_bares_hahn(ratio_lx_ly: float) -> float:
    """Interpolation lineaire dans la table Bares-Hahn."""
    if ratio_lx_ly <= BARES_HAHN_TABLE[0][0]:
        return BARES_HAHN_TABLE[0][1]
    for i in range(len(BARES_HAHN_TABLE) - 1):
        x1, y1 = BARES_HAHN_TABLE[i]
        x2, y2 = BARES_HAHN_TABLE[i + 1]
        if x1 <= ratio_lx_ly <= x2:
            return y1 + (y2 - y1) * (ratio_lx_ly - x1) / (x2 - x1)
    return 1.0


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    Lx = inputs.get("portee_l_m")
    h = inputs.get("epaisseur_h_mm")
    c = inputs.get("enrobage_mm")
    typ = inputs.get("type_appui")
    fck = inputs.get("fck_mpa")

    if not isinstance(Lx, (int, float)) or Lx <= 0:
        raise ValueError("portee_l_m > 0 requis")
    for nom, val in [("epaisseur_h_mm", h), ("enrobage_mm", c)]:
        if not isinstance(val, int) or val <= 0:
            raise ValueError(f"{nom} entier > 0 requis (mm)")
    if typ not in L_SUR_D_MAX:
        raise ValueError(f"type_appui doit etre dans {sorted(L_SUR_D_MAX)}")
    if not isinstance(fck, (int, float)) or fck <= 0:
        raise ValueError("fck_mpa > 0 requis")
    if c >= h:
        raise ValueError("enrobage >= h : section impossible")

    Ly = inputs.get("portee_perpendiculaire_m")
    bidir = Ly is not None
    if bidir:
        if not isinstance(Ly, (int, float)) or Ly <= 0:
            raise ValueError("portee_perpendiculaire_m > 0 si fourni")
        # On normalise : Lx = portee courte, ratio = Ly/Lx (>=1)
        Lx_court, Ly_long = sorted([Lx, Ly])
        ratio = Ly_long / Lx_court
        k_bh = _coeff_bares_hahn(ratio)
        L_effectif = Lx_court * k_bh  # portee effective reduite
    else:
        L_effectif = Lx
        k_bh = 1.0

    d = h - c
    L_mm = L_effectif * 1000.0
    ratio_actuel = L_mm / d
    ratio_max = L_SUR_D_MAX[typ]
    h_min = int(L_mm / ratio_max + c + 0.5)
    marge = h - h_min
    ratio_ok = ratio_actuel <= ratio_max

    out = {
        "h_min_mm": h_min,
        "ratio_l_d": round(ratio_actuel, 2),
        "ratio_l_d_max": ratio_max,
        "marge_mm": marge,
        "bidirectionnel": bidir,
        "coeff_bares_hahn": round(k_bh, 3),
    }

    # === Calcul fleche reelle simplifiee si charge fournie ===
    q = inputs.get("charge_q_kn_m2")
    if q is not None:
        if not isinstance(q, (int, float)) or q <= 0:
            raise ValueError("charge_q_kn_m2 > 0 si fourni")
        phi = inputs.get("phi_fluage", 2.0)
        if not isinstance(phi, (int, float)) or phi < 0:
            raise ValueError("phi_fluage >= 0 si fourni")

        # Ecm en MPa : EC2 §3.1.3 table 3.1 simplifie : Ecm = 22 * (fcm/10)^0.3 [GPa] avec fcm = fck+8
        fcm = fck + 8
        Ecm = 22000.0 * ((fcm / 10.0) ** 0.3)  # MPa
        Ec_eff = Ecm / (1.0 + phi)  # MPa, effet de fluage long terme

        # Inertie par metre lineaire (b=1000mm) - section rectangulaire non fissuree (zone elastique)
        b_eff = 1000.0  # mm
        inertie = b_eff * (h ** 3) / 12.0  # mm^4

        # Charge q en kN/m² → N/mm sur largeur b=1000mm : q_lin = q * 1.0 (kN/m de bande)
        q_n_mm = q * 1.0  # N/mm

        # Fleche poutre uniformement chargee appui simple : f = 5 q L^4 / (384 E I)
        # Si dalle continue, fleche ≈ f_simple / 2.5 (approximation)
        L_calc_mm = L_effectif * 1000.0
        f_simple_mm = 5.0 * q_n_mm * (L_calc_mm ** 4) / (384.0 * Ec_eff * inertie)
        if typ == "continu":
            f_calc = f_simple_mm / 2.5
        else:
            f_calc = f_simple_mm

        f_limite = L_mm / 250.0  # ELS QP §7.4.1
        out["fleche_calc_mm"] = round(f_calc, 2)
        out["fleche_limite_mm"] = round(f_limite, 2)
        fleche_ok = f_calc <= f_limite
        out["conforme"] = ratio_ok and fleche_ok
    else:
        out["conforme"] = ratio_ok

    out["reference"] = ("NF EN 1992-1-1 §7.4.1 (fleche L/250 ELS QP) + §7.4.2 (ratio L/d) + "
                       "abaques Bares-Hahn (dalle bidirectionnelle)")
    return out
