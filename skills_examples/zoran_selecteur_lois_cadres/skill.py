"""skill Sélecteur de lois et de cadres pour une évaluation de cohérence.

Mission : ZORAN_JOBS_20260521 · skill méta de gouvernance.
Source : Codex Zoran — 11 lois de cohérence universelle (Frédéric Tabary,
Institut IA), fichier CODEX_LAWS.json, DOI Zenodo 10.5281/zenodo.17502010.

Pour une évaluation de cohérence donnée, détermine de façon déterministe :
- les CADRES de cohérence pertinents (parmi structure, cout, carbone,
  maintenance, exploitation, securite, global) ;
- les LOIS du Codex Zoran à appliquer (les 11 lois, de la Loi -1 à la Loi 9).

⚠️ MVP : la correspondance domaine → lois est une cartographie heuristique
documentée, fondée sur les intitulés du Codex. La sémantique complète et faisant
autorité de chaque loi figure dans le Codex Zoran (DOI Zenodo).
Loi 1 : les 11 intitulés de loi sont repris VERBATIM de CODEX_LAWS.json —
aucun nom de loi n'est inventé.

Contrat io :
    inputs  : {domaine, enjeu?}
    outputs : {cadres_pertinents, cadre_dominant, lois_pertinentes,
               lois_universelles, reference}
"""

from __future__ import annotations

# Les 11 lois du Codex Zoran — intitulés verbatim (CODEX_LAWS.json).
LOIS = {
    -1: "Ce qui n'existe pas existe",
    0: "Genèse Éthique",
    1: "Fracto-Anticipation",
    2: "Gaïa-Projection",
    3: "ΨΛ-Cohérence",
    4: "Carnot-Quantique",
    5: "Schwarzschild-Cohérence",
    6: "Identité-Intégrité",
    7: "Distorsion-Systémique",
    8: "Amygdala-Négativité",
    9: "Évolution Unifiée",
}

# Lois universelles — pertinentes pour TOUTE évaluation de cohérence.
LOIS_UNIVERSELLES = [0, 3]  # Genèse Éthique + ΨΛ-Cohérence

# Cartographie domaine → (cadres pertinents, cadre dominant en tête ; lois spécifiques).
DOMAINES = {
    "structure":     (["structure", "securite", "cout", "maintenance"], [1, 5, 7]),
    "thermique":     (["exploitation", "carbone", "cout", "maintenance"], [4, 2]),
    "securite":      (["securite", "structure", "exploitation"], [5, 8]),
    "economie":      (["cout", "exploitation", "maintenance"], [7, 9]),
    "transmission":  (["global", "exploitation"], [-1, 6]),
    "gouvernance":   (["global", "securite"], [6, 7, 8]),
    "pathologie":    (["structure", "securite", "maintenance"], [1, 7, 9]),
    "environnement": (["carbone", "exploitation", "maintenance"], [2, 4, 9]),
}


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    domaine = str(inputs.get("domaine", "")).lower().strip()
    if domaine not in DOMAINES:
        raise ValueError(f"domaine : attendu l'un de {sorted(DOMAINES)}")
    enjeu = str(inputs.get("enjeu", "")).lower().strip()

    cadres, lois_specifiques = DOMAINES[domaine]
    cadres = list(cadres)

    # Un enjeu de sécurité des personnes hisse le cadre securite en tête.
    if enjeu == "securite_personnes" and "securite" in cadres:
        cadres.remove("securite")
        cadres.insert(0, "securite")

    lois_ids = sorted(set(LOIS_UNIVERSELLES + lois_specifiques))
    lois_pertinentes = [{"numero": n, "nom": LOIS[n]} for n in lois_ids]

    return {
        "domaine": domaine,
        "cadres_pertinents": cadres,
        "cadre_dominant": cadres[0],
        "lois_pertinentes": lois_pertinentes,
        "lois_universelles": [{"numero": n, "nom": LOIS[n]} for n in LOIS_UNIVERSELLES],
        "nb_lois": len(lois_pertinentes),
        "reference": "Codex Zoran — CODEX_LAWS.json (11 lois, DOI 10.5281/zenodo.17502010)",
    }
