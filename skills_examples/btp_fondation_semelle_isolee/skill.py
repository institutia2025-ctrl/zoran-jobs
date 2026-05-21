"""skill btp_fondation_semelle_isolee — predimensionnement semelle isolee carree.

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 3 Structure (4/5).
Sources :
  - NF EN 1997-1 (Eurocode 7) : Calcul geotechnique, etat limite ELU GEO.
  - NF DTU 13.1 : Travaux de fondations superficielles.
  - NF EN 1992-1-1 §9.8 : dispositions constructives semelles.

Approche predimensionnement (ELU GEO, approche 2 EC7 §2.4.7.3.4.2) :
    A_semelle >= N_Ed / σ_sol_admissible
    cote_B = √A

avec σ_sol_admissible deja "factorise" par le BET geotechnique (G1/G2)
qui fournit la valeur de calcul. **Loi 1 stricte : aucune valeur de
σ_sol fabriquee — l'utilisateur fournit la contrainte admissible issue
de l'etude G1/G2.**

⚠️ MVP : semelle carree centrale, charge centree, pas de moment, pas de
   chargement excentre. Pas de calcul de tassement (§6.6.2 EC7) ni de
   poinçonnement (§9.8.2 EC2).

Contrat io :
    inputs : {
        "N_Ed_kN": float,                # effort ELU au pied du poteau
        "sigma_sol_kpa": float,          # contrainte admissible sol (G2 fourni)
        "source_etude_sol": str,         # ref rapport etude sols (Loi 1)
        "profondeur_ancrage_mm": int,    # profondeur d'ancrage / hors gel
        "epaisseur_min_mm"?: int         # epaisseur minimum imposee (defaut 250mm)
    }
    outputs : {
        "B_cote_mm": int,                # cote semelle carree
        "h_min_mm": int,                 # epaisseur min recommandee
        "surface_m2": float,
        "contrainte_appliquee_kpa": float,
        "conforme": bool,
        "reference": str
    }
"""
from __future__ import annotations

import math


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    N = inputs.get("N_Ed_kN")
    sig = inputs.get("sigma_sol_kpa")
    src = inputs.get("source_etude_sol")
    prof = inputs.get("profondeur_ancrage_mm")
    e_min = inputs.get("epaisseur_min_mm", 250)

    if not isinstance(N, (int, float)) or N <= 0:
        raise ValueError("N_Ed_kN > 0 requis")
    if not isinstance(sig, (int, float)) or sig <= 0:
        raise ValueError("sigma_sol_kpa > 0 requis (issu etude G1/G2)")
    if not isinstance(src, str) or not src.strip():
        raise ValueError("source_etude_sol requise (Loi 1 : pas d'invention de sigma_sol)")
    if not isinstance(prof, int) or prof < 600:
        raise ValueError("profondeur_ancrage_mm >= 600 mm requis (hors gel zone 1, sinon adapter)")
    if not isinstance(e_min, int) or e_min < 150:
        raise ValueError("epaisseur_min_mm >= 150 (§9.8 EC2)")

    # Surface mini A = N / σ (passage kN -> N et kPa -> Pa : facteur 1)
    # kN / kPa = m² directement
    A_m2 = N / sig
    B_m = math.sqrt(A_m2)
    B_mm = int(math.ceil(B_m * 1000.0 / 50.0) * 50)  # arrondi au 50 mm sup
    A_corrigee = (B_mm / 1000.0) ** 2
    sigma_appliquee = N / A_corrigee  # kPa

    h_recommandee = max(e_min, int(B_mm * 0.5))  # h >= B/2 (regle pratique semelle rigide)

    conforme = sigma_appliquee <= sig

    return {
        "B_cote_mm": B_mm,
        "h_min_mm": h_recommandee,
        "surface_m2": round(A_corrigee, 3),
        "contrainte_appliquee_kpa": round(sigma_appliquee, 2),
        "marge_kpa": round(sig - sigma_appliquee, 2),
        "conforme": conforme,
        "source_etude_sol_tracee": src,
        "reference": "NF EN 1997-1 §2.4.7.3 + NF DTU 13.1 + NF EN 1992-1-1 §9.8",
    }
