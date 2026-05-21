"""skill btp_verif_fleche_detaillee_ec2 — fleche bilineaire EC2 §7.4.3.

Mission : ZORAN_JOBS_20260521 · Phase B Structure avancee (4/5).
Source : NF EN 1992-1-1 §7.4.3 (calcul fleche par interpolation bilineaire).

Methode bilineaire EC2 §7.4.3(3) :
    α = ζ × α_II + (1 - ζ) × α_I
    avec :
        α_I  : valeur en section non fissuree (etat I, beton elastique)
        α_II : valeur en section fissuree (etat II, beton tendu neglige)
        ζ    : coefficient de distribution
                = 1 - β × (σ_sr/σ_s)²
                = 0 si M < M_cr (pas fissure)
        β = 1.0 (chargement court) ou 0.5 (chargement long terme, fluage)

Etat I (non fissure) - inertie homogeneisee :
    f_I = 5 × q × L^4 / (384 × E_eff × I_I)
    I_I ≈ b × h^3 / 12 (section rectangulaire neglige acier)

Etat II (fissure) - inertie fissuree :
    Approximation EC2 : I_II ≈ I_I × 0.3 (typique habitat BA)
    f_II = 5 × q × L^4 / (384 × E_eff × I_II)

E_eff = E_cm / (1 + φ)  (fluage long terme)
E_cm = 22000 × ((fck+8)/10)^0.3  (§3.1.3 Table 3.1)

Limite ELS QP (§7.4.1(4)) : f ≤ L/250

⚠️ MVP : approche bilineaire EC2. Pour calcul rigoureux, integration moment-
   curvature sur la longueur (§7.4.3) avec section fissuree exacte (axe neutre
   y_II reel, moment d'inertie II homogeneise).

Contrat io :
    inputs : {portee_l_m, b_mm, h_mm, enrobage_mm, fck_mpa, fyk_mpa,
              Asl_mm2, charge_q_kn_m2, phi_fluage?, M_Ed_kNm?, M_cr_kNm?}
    outputs : {f_I_mm, f_II_mm, zeta_distribution, f_total_mm,
               f_limite_mm, conforme, etat_fissure, reference}
"""
from __future__ import annotations

GAMMA_S = 1.15


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    L = inputs.get("portee_l_m")
    if not isinstance(L, (int, float)) or L <= 0:
        raise ValueError("portee_l_m > 0 requis")
    for nom in ("b_mm", "h_mm", "enrobage_mm"):
        v = inputs.get(nom)
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nom} entier > 0 requis")
    for nom in ("fck_mpa", "fyk_mpa", "Asl_mm2", "charge_q_kn_m2"):
        v = inputs.get(nom)
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"{nom} > 0 requis")

    b = inputs["b_mm"]
    h = inputs["h_mm"]
    c = inputs["enrobage_mm"]
    fck = inputs["fck_mpa"]
    fyk = inputs["fyk_mpa"]
    Asl = inputs["Asl_mm2"]
    q = inputs["charge_q_kn_m2"]
    phi = inputs.get("phi_fluage", 2.0)
    M_Ed = inputs.get("M_Ed_kNm")
    M_cr_user = inputs.get("M_cr_kNm")

    if c >= h:
        raise ValueError("enrobage >= h : section impossible")
    if not isinstance(phi, (int, float)) or phi < 0:
        raise ValueError("phi_fluage >= 0 requis")

    d = h - c
    L_mm = L * 1000.0

    # Modules
    fcm = fck + 8
    Ecm = 22000.0 * ((fcm / 10.0) ** 0.3)  # MPa
    E_eff = Ecm / (1.0 + phi)  # MPa, prise en compte fluage long terme
    _fyd = fyk / GAMMA_S  # non utilise actuellement (sigma_s pour zeta exact futur)

    # Inertie etat I (non fissure, simplifie)
    I_I = b * (h ** 3) / 12.0  # mm^4
    # Inertie etat II (fissure, approche typique habitat BA = 30% de I_I)
    # Valeur plus realiste : I_II depend de ρ et α_e = E_s/E_eff
    rho_l = Asl / (b * d)
    alpha_e = 200000.0 / E_eff  # E_s acier = 200 GPa = 200000 MPa
    # Position axe neutre fissure (en mm)
    x_II = d * (-alpha_e * rho_l + ((alpha_e * rho_l) ** 2 + 2 * alpha_e * rho_l) ** 0.5)
    # Inertie fissuree
    I_II = b * (x_II ** 3) / 3.0 + alpha_e * Asl * (d - x_II) ** 2  # mm^4

    # Charge en N/mm
    q_n_mm = q * b / 1000.0  # kN/m × b en m → N/mm (b en mm → q est sur largeur b)
    # Fleche appui simple poutre uniformement chargee
    f_I = 5.0 * q_n_mm * (L_mm ** 4) / (384.0 * E_eff * I_I)
    f_II = 5.0 * q_n_mm * (L_mm ** 4) / (384.0 * E_eff * I_II)

    # Distribution ζ
    # M_cr ≈ f_ctm × W (W = b h² / 6 pour rectangulaire)
    fctm = 0.30 * (fck ** (2.0 / 3.0)) if fck <= 50 else 2.12 * (1 + (fcm / 10)) ** 0.5
    W = b * (h ** 2) / 6.0  # mm³
    M_cr_calc = fctm * W / 1.0e6  # kNm (Nmm -> kNm)
    M_cr = M_cr_user if M_cr_user is not None else M_cr_calc

    if M_Ed is None:
        # Sans M_Ed fourni, on prend etat I + fluage (charge ELS QP)
        # mais on signale qu'on ne sait pas si fissure
        zeta = 0.5  # hypothese conservative habitat courant
        etat_fissure = "indetermine_sans_M_Ed"
    elif M_Ed <= M_cr:
        zeta = 0.0
        etat_fissure = "non_fissure"
    else:
        # ζ = 1 - β × (M_cr/M_Ed)² (analogue σ_sr/σ_s sous chargement constant)
        beta = 0.5  # chargement long terme
        zeta = 1.0 - beta * ((M_cr / M_Ed) ** 2)
        zeta = max(0.0, min(1.0, zeta))
        etat_fissure = "fissure"

    f_total = zeta * f_II + (1.0 - zeta) * f_I
    f_limite = L_mm / 250.0  # §7.4.1(4)

    return {
        "f_I_mm": round(f_I, 2),
        "f_II_mm": round(f_II, 2),
        "zeta_distribution": round(zeta, 3),
        "f_total_mm": round(f_total, 2),
        "f_limite_mm": round(f_limite, 2),
        "M_cr_kNm": round(M_cr, 2),
        "etat_fissure": etat_fissure,
        "conforme": f_total <= f_limite,
        "ratio_utilisation": round(f_total / f_limite, 3),
        "I_I_mm4": round(I_I, 0),
        "I_II_mm4": round(I_II, 0),
        "E_eff_mpa": round(E_eff, 0),
        "reference": "NF EN 1992-1-1 §7.4.3 + §3.1.3 + §7.4.1(4) (limite L/250 ELS QP)",
    }
