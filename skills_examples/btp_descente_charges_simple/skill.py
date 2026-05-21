"""skill descente_charges_simple — ingénieur génie civil.

Mission : ZORAN_JOBS_20260521 · Phase A BTP.
Calcul simplifié de descente de charges sur poteau central.
Référence : NF EN 1991-1-1 (Eurocode 1) charges permanentes/exploitation
            NF EN 1990 (Eurocode 0) coefficients de combinaison ELU.

Hypothèses simplificatrices (MVP DEMONSTRATIF) :
- Bâtiment courant, poteau central, contributions des étages additives.
- ELU fondamental : 1,35 G + 1,5 Q (Eurocode 0 §6.4.3.2)
- Charges permanentes G (poids propre dalle + cloisons + finitions)
- Charges d'exploitation Q (par catégorie d'usage, Eurocode 1-1-1 tableau 6.1)

⚠️ MVP : ne remplace PAS une note de calcul BET. Skill démonstratif.

Contrat io :
    inputs : {
        "surface_tributaire_m2": float,        # surface reprise par le poteau
        "nb_etages": int,                       # nombre d'étages supportés
        "g_kn_m2": float,                       # charge permanente surfacique (kN/m²)
        "q_kn_m2": float                        # charge d'exploitation surfacique (kN/m²)
    }
    outputs : {
        "N_ELU_kN": float,                      # effort normal ELU au pied
        "N_ELS_kN": float,                      # effort normal ELS au pied
        "detail": dict,
        "reference": "NF EN 1990 §6.4.3.2 + NF EN 1991-1-1"
    }
"""

from __future__ import annotations

# Coefficients partiels ELU fondamental (Eurocode 0 tableau A1.2(B))
GAMMA_G = 1.35
GAMMA_Q = 1.50


def run(inputs: dict) -> dict:
    inputs = inputs or {}

    surf = inputs.get("surface_tributaire_m2")
    nb = inputs.get("nb_etages")
    g = inputs.get("g_kn_m2")
    q = inputs.get("q_kn_m2")

    for nom, val in [("surface_tributaire_m2", surf), ("g_kn_m2", g), ("q_kn_m2", q)]:
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"{nom} doit etre un nombre >= 0")
    if not isinstance(nb, int) or nb < 1:
        raise ValueError("nb_etages doit etre un entier >= 1")

    # Sommation par étage (surface constante hypothèse MVP)
    G_total = g * surf * nb
    Q_total = q * surf * nb

    N_ELU = GAMMA_G * G_total + GAMMA_Q * Q_total
    N_ELS = G_total + Q_total

    return {
        "N_ELU_kN": round(N_ELU, 2),
        "N_ELS_kN": round(N_ELS, 2),
        "detail": {
            "G_total_kN": round(G_total, 2),
            "Q_total_kN": round(Q_total, 2),
            "gamma_G": GAMMA_G,
            "gamma_Q": GAMMA_Q,
            "combinaison": "1,35*G + 1,5*Q (ELU fondamental)",
        },
        "reference": "NF EN 1990 §6.4.3.2 + NF EN 1991-1-1",
    }
