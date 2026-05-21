"""skill btp_calcul_sismique_ec8 — sismique forces laterales EC8.

Mission : ZORAN_JOBS_20260521 · Phase B Structure avancee (1/5).
Sources :
  - NF EN 1998-1 §4.3.3.2 : methode des forces laterales equivalentes
  - Decret 22 octobre 2010 (zones sismiques France I-V)
  - Annexe Nationale Francaise EC8 (a_gr, categories, spectre Type 2)

Formules (§4.3.3.2 et §3.2.2.5 EC8) :
    T_1 = C_t × H^(3/4)              periode propre approche
    a_g = a_gr × γ_I                 acceleration design site
    S_d(T_1) : spectre de calcul     §3.2.2.5 (4 plages : 0..T_B..T_C..T_D..)
    F_b = S_d(T_1) × m × λ           effort tranchant base
    λ = 0.85 si T_1 < 2×T_C et n ≥ 2, sinon 1.0

Zones France (Decret 22/10/2010, a_gr en m/s²) :
    Zone 1 = 0.4 (tres faible)   Zone 2 = 0.7 (faible)
    Zone 3 = 1.1 (modere)        Zone 4 = 1.6 (moyen)
    Zone 5 = 3.0 (fort, Antilles)

Categorie importance γ_I (NA EC8 Tableau 4.3) :
    I = 0.8 · II = 1.0 · III = 1.2 · IV = 1.4

C_t (§4.3.3.2.2(3)) :
    Cadres BA = 0.075 · Cadres acier = 0.085 · Voile/mixte = 0.050

q (coefficient comportement, simplifie selon ductilite) :
    DCL = 1.5 · DCM = 3.0 · DCH = 4.5

⚠️ MVP : methode forces laterales, valable batiment regulier (§4.2.3.2).
   Pour irreguliers, T > 4×T_C, ou structures speciales : analyse modale
   §4.3.3.3 ou temporelle §4.3.3.4 BET specialise.

Contrat io :
    inputs : {zone_sismique:int 1..5, classe_sol:str A..E,
              categorie_importance:str I..IV, hauteur_batiment_m:float,
              nb_etages:int, type_systeme_resistant:str,
              masse_totale_tonnes:float, classe_ductilite:str DCL/DCM/DCH}
    outputs : {T_1_s, S_d_T1_m_s2, F_b_kN, lambda_correction, a_g_m_s2,
               q_comportement, spectre_type, reference}
"""
from __future__ import annotations

ZONES_A_GR = {1: 0.4, 2: 0.7, 3: 1.1, 4: 1.6, 5: 3.0}
GAMMA_I = {"I": 0.8, "II": 1.0, "III": 1.2, "IV": 1.4}
C_T = {"cadres_ba": 0.075, "cadres_acier": 0.085, "voile_mixte": 0.050}
CLASSES_SOL = {"A", "B", "C", "D", "E"}
CLASSES_DUCT = {"DCL", "DCM", "DCH"}
# Spectre Type 2 (NA EC8 France metropole) — Table 3.3
SPECTRE_T2 = {
    "A": (1.0, 0.05, 0.25, 1.2),
    "B": (1.35, 0.05, 0.25, 1.2),
    "C": (1.5, 0.10, 0.25, 1.2),
    "D": (1.8, 0.10, 0.30, 1.2),
    "E": (1.6, 0.05, 0.25, 1.2),
}
Q_BY_DCL = {"DCL": 1.5, "DCM": 3.0, "DCH": 4.5}
BETA_LOWER = 0.2  # NA EC8


def _S_d(T: float, a_g: float, S: float, T_B: float, T_C: float,
         T_D: float, q: float) -> float:
    """Spectre de calcul §3.2.2.5 EC8 — 4 plages."""
    if T <= T_B:
        return a_g * S * (2.0 / 3.0 + (T / T_B) * (2.5 / q - 2.0 / 3.0))
    if T <= T_C:
        return a_g * S * 2.5 / q
    if T <= T_D:
        return max(a_g * S * 2.5 / q * (T_C / T), BETA_LOWER * a_g)
    return max(a_g * S * 2.5 / q * (T_C * T_D / (T * T)), BETA_LOWER * a_g)


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    z = inputs.get("zone_sismique")
    if not isinstance(z, int) or z not in ZONES_A_GR:
        raise ValueError(f"zone_sismique dans {sorted(ZONES_A_GR)}")
    sol = inputs.get("classe_sol")
    if sol not in CLASSES_SOL:
        raise ValueError(f"classe_sol dans {sorted(CLASSES_SOL)}")
    cat = inputs.get("categorie_importance")
    if cat not in GAMMA_I:
        raise ValueError(f"categorie_importance dans {sorted(GAMMA_I)}")
    H = inputs.get("hauteur_batiment_m")
    if not isinstance(H, (int, float)) or H <= 0:
        raise ValueError("hauteur_batiment_m > 0 requis")
    n = inputs.get("nb_etages")
    if not isinstance(n, int) or n < 1:
        raise ValueError("nb_etages >= 1 requis")
    sysr = inputs.get("type_systeme_resistant")
    if sysr not in C_T:
        raise ValueError(f"type_systeme_resistant dans {sorted(C_T)}")
    m = inputs.get("masse_totale_tonnes")
    if not isinstance(m, (int, float)) or m <= 0:
        raise ValueError("masse_totale_tonnes > 0 requis")
    duct = inputs.get("classe_ductilite")
    if duct not in CLASSES_DUCT:
        raise ValueError(f"classe_ductilite dans {sorted(CLASSES_DUCT)}")

    a_g = ZONES_A_GR[z] * GAMMA_I[cat]
    T1 = C_T[sysr] * (H ** 0.75)
    S, T_B, T_C, T_D = SPECTRE_T2[sol]
    q_coef = Q_BY_DCL[duct]
    Sd = _S_d(T1, a_g, S, T_B, T_C, T_D, q_coef)
    lam = 0.85 if (T1 < 2 * T_C and n >= 2) else 1.0
    F_b_kN = Sd * (m * 1000.0) * lam / 1000.0  # N -> kN

    return {
        "T_1_s": round(T1, 3),
        "S_d_T1_m_s2": round(Sd, 3),
        "F_b_kN": round(F_b_kN, 2),
        "lambda_correction": lam,
        "a_g_m_s2": round(a_g, 3),
        "q_comportement": q_coef,
        "spectre_type": "Type 2 (France metropole)" if z < 5 else "Type 1 a verifier (Antilles)",
        "reference": "NF EN 1998-1 §4.3.3.2 + §3.2.2.5 + Decret 22/10/2010 + Annexe Nationale Francaise",
    }
