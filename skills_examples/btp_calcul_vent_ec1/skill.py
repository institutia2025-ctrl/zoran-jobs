"""skill btp_calcul_vent_ec1 — pression vent EC1-1-4.

Mission : ZORAN_JOBS_20260521 · Phase B Structure avancee (2/5).
Sources :
  - NF EN 1991-1-4 §4 : actions du vent
  - Annexe Nationale Francaise EC1-1-4 : carte des regions, v_b,0 par region
  - NF EN 1991-1-4 §4.5 Table 4.1 : categories terrain 0..IV

Formules :
    v_b = c_dir × c_season × v_b,0 (§4.2)   (c_dir = c_season = 1.0 simplifie)
    q_b = 0.5 × ρ × v_b²              (§4.5(1)) - pression dynamique de base
    c_e(z) : coefficient d'exposition  (§4.5 Figure 4.2 par categorie)
    q_p(z) = c_e(z) × q_b              (§4.5(1))

Regions France (Annexe NA EC1, v_b,0 en m/s) :
    Region 1 = 22 m/s  Region 2 = 24 m/s
    Region 3 = 26 m/s  Region 4 = 28 m/s

Categorie terrain (Table 4.1) :
    0  = mer ou zone cotiere exposee
    I  = lacs, zones avec vegetation rare
    II = zones campagne, vegetation moderee
    III = zones suburbaines, foret, banlieue
    IV = zones urbaines avec >15% surface batie h>15m

⚠️ MVP : c_dir = c_season = 1.0 (conservatif). Tabulation c_e(z) simplifiee
   par interpolation lineaire sur Figure 4.2 NA. Pour ouvrages tres exposes
   (>200 m) ou formes complexes, calcul exact §4.5 + études CFD.

Contrat io :
    inputs : {region:int 1..4, categorie_terrain:str "0"/"I"/"II"/"III"/"IV",
              hauteur_z_m:float, c_dir?:float, c_season?:float}
    outputs : {v_b_m_s, q_b_n_m2, c_e_z, q_p_z_n_m2, q_p_z_kn_m2, reference}
"""
from __future__ import annotations

# v_b,0 par region NA EC1-1-4
V_B0 = {1: 22.0, 2: 24.0, 3: 26.0, 4: 28.0}
CATEGORIES_TERRAIN = {"0", "I", "II", "III", "IV"}
RHO_AIR = 1.25  # kg/m³ EC1-1-4 §4.5(1) NA

# Tabulation simplifiee c_e(z) — Figure 4.2 NA EC1 (interpolation par z)
# Valeurs typiques pour terrain de reference (z_min selon categorie)
CE_TABLE = {
    "0":  [(2, 2.4), (10, 3.0), (50, 3.8), (200, 4.5)],
    "I":  [(2, 1.9), (10, 2.5), (50, 3.3), (200, 4.0)],
    "II": [(4, 1.7), (10, 2.1), (50, 2.9), (200, 3.6)],
    "III":[(8, 1.4), (15, 1.8), (50, 2.4), (200, 3.1)],
    "IV": [(16, 1.1), (30, 1.5), (50, 1.9), (200, 2.6)],
}


def _interp_ce(z: float, table: list) -> float:
    if z <= table[0][0]:
        return table[0][1]
    if z >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        z1, c1 = table[i]
        z2, c2 = table[i + 1]
        if z1 <= z <= z2:
            return c1 + (c2 - c1) * (z - z1) / (z2 - z1)
    return table[-1][1]


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    r = inputs.get("region")
    if not isinstance(r, int) or r not in V_B0:
        raise ValueError(f"region doit etre dans {sorted(V_B0)} (NA EC1-1-4)")
    cat = inputs.get("categorie_terrain")
    if cat not in CATEGORIES_TERRAIN:
        raise ValueError(f"categorie_terrain dans {sorted(CATEGORIES_TERRAIN)}")
    z = inputs.get("hauteur_z_m")
    if not isinstance(z, (int, float)) or z <= 0:
        raise ValueError("hauteur_z_m > 0 requis")

    c_dir = inputs.get("c_dir", 1.0)
    c_season = inputs.get("c_season", 1.0)
    for nom, v in [("c_dir", c_dir), ("c_season", c_season)]:
        if not isinstance(v, (int, float)) or v <= 0 or v > 1.0:
            raise ValueError(f"{nom} dans (0..1.0] requis")

    v_b = c_dir * c_season * V_B0[r]
    q_b = 0.5 * RHO_AIR * v_b * v_b  # N/m²
    c_e = _interp_ce(z, CE_TABLE[cat])
    q_p = c_e * q_b  # N/m²

    return {
        "v_b_m_s": round(v_b, 2),
        "q_b_n_m2": round(q_b, 2),
        "c_e_z": round(c_e, 3),
        "q_p_z_n_m2": round(q_p, 2),
        "q_p_z_kn_m2": round(q_p / 1000.0, 4),
        "region": r,
        "categorie_terrain": cat,
        "reference": "NF EN 1991-1-4 §4 + Annexe Nationale Francaise (regions, c_e(z) Figure 4.2)",
    }
