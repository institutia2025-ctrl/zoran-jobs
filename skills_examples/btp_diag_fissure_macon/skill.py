"""skill btp_diag_fissure_macon — diagnostic fissure maçonnerie.

Mission : ZORAN_JOBS_20260521 · Phase A BTP · AXE 4 Pathologies.
Niveau metier : ingenieur pathologies / expert structure.

Source qualitative : NF DTU 20.1 §10 (désordres en maçonnerie de petits éléments).
Source quantitative : grille AQC (Agence Qualité Construction) FOURNIE EN INPUT
                      par l'utilisateur. Loi 1 stricte : aucun seuil mm fabriqué
                      par le skill — la grille AQC varie selon l'édition et la
                      fiche AQC consultée par l'utilisateur.

⚠️ MVP démonstratif : oriente le diagnostic, ne remplace pas une expertise in
   situ (sondage, monitoring, jauges, témoin Saugnac).

Approche en 3 axes (chacun renforce le suivant) :
  1. Caractérisation qualitative (DTU 20.1) : structurelle / non structurelle /
     traversante, active / stabilisée.
  2. Classification quantitative AQC (si grille fournie) : a / b / c / d
     d'après la largeur visible en mm.
  3. Verdict combiné + actions recommandees + référence tracée.

Contrat io :
    inputs : {
        "largeur_mm": float,                    # largeur visible
        "traversante": bool,                    # fissure visible des deux côtés du mur
        "localisation": str,                    # "mur_porteur" | "cloison" | "facade" | "linteau"
        "evolution_active": bool,               # progression observee (temoin > 0)
        "seuils_aqc_mm"?: {                     # optionnel : grille AQC utilisateur
            "a_max": float,
            "b_max": float,
            "c_max": float
            # > c_max => classe d
        },
        "source_seuils_aqc"?: str               # obligatoire si seuils_aqc_mm fourni
    }
    outputs : {
        "classe_aqc": str | None,
        "structurelle_suspectee": bool,
        "gravite": str,                          # "faible"/"moyenne"/"elevee"/"critique"
        "actions_recommandees": list[str],
        "reference": str
    }
"""

from __future__ import annotations

LOCALISATIONS_VALIDES = {"mur_porteur", "cloison", "facade", "linteau"}
GRAVITES = ("faible", "moyenne", "elevee", "critique")


def _classer_aqc(largeur_mm: float, seuils: dict) -> str:
    """Classe en a/b/c/d selon la grille AQC FOURNIE PAR L'UTILISATEUR."""
    if largeur_mm <= seuils["a_max"]:
        return "a"
    if largeur_mm <= seuils["b_max"]:
        return "b"
    if largeur_mm <= seuils["c_max"]:
        return "c"
    return "d"


def run(inputs: dict) -> dict:
    inputs = inputs or {}

    largeur = inputs.get("largeur_mm")
    if not isinstance(largeur, (int, float)) or largeur < 0:
        raise ValueError("largeur_mm requis (nombre >= 0, en mm)")

    traversante = inputs.get("traversante")
    if not isinstance(traversante, bool):
        raise ValueError("traversante (bool) requis : visible des deux cotes du mur ?")

    loc = inputs.get("localisation")
    if loc not in LOCALISATIONS_VALIDES:
        raise ValueError(f"localisation doit etre dans {sorted(LOCALISATIONS_VALIDES)}")

    evol = inputs.get("evolution_active")
    if not isinstance(evol, bool):
        raise ValueError("evolution_active (bool) requis : progression observee ?")

    # Classification quantitative AQC — seulement si grille fournie (Loi 1)
    seuils = inputs.get("seuils_aqc_mm")
    source = inputs.get("source_seuils_aqc")
    classe = None
    ref_quantitative = ""
    if seuils is not None:
        if not isinstance(seuils, dict):
            raise ValueError("seuils_aqc_mm doit etre un dict {a_max, b_max, c_max} si fourni")
        for k in ("a_max", "b_max", "c_max"):
            v = seuils.get(k)
            if not isinstance(v, (int, float)) or v <= 0:
                raise ValueError(f"seuils_aqc_mm.{k} doit etre un nombre > 0")
        if not (seuils["a_max"] < seuils["b_max"] < seuils["c_max"]):
            raise ValueError("seuils_aqc_mm doivent etre strictement croissants (a < b < c)")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source_seuils_aqc obligatoire quand seuils fournis (Loi 1)")
        classe = _classer_aqc(largeur, seuils)
        ref_quantitative = f" + grille AQC utilisateur : {source}"

    # Verdict qualitatif (DTU 20.1, raisonnement metier)
    structurelle = (loc in {"mur_porteur", "linteau"}) or traversante

    # Gravite combinee qualitatif + quantitatif (si dispo)
    if structurelle and evol:
        gravite = "critique"
    elif structurelle:
        gravite = "elevee"
    elif classe == "d" or evol:
        gravite = "elevee"
    elif classe == "c":
        gravite = "moyenne"
    elif classe in ("a", "b"):
        gravite = "faible"
    elif loc == "cloison" and not evol:
        gravite = "faible"
    else:
        # Pas de classe AQC et pas structurelle et pas evolutive
        gravite = "faible"

    # Actions recommandees
    actions = []
    if structurelle:
        actions.append("Saisir un BET structure pour expertise in situ (sondage, calculs Eurocode 2).")
    if evol:
        actions.append("Poser temoins (Saugnac ou jauges electroniques) : releve mensuel sur 6 mois minimum.")
    if classe == "d":
        actions.append("Reprise immediate : injection resine epoxy ou agrafage selon nature.")
    if loc == "facade" and traversante:
        actions.append("Verifier etancheite et risque infiltration : DTU 20.1 §10 + DTU 42.1.")
    if not actions:
        actions.append("Surveillance simple : photographier date + largeur, reverifier dans 3 mois.")

    return {
        "classe_aqc": classe,
        "structurelle_suspectee": structurelle,
        "gravite": gravite,
        "actions_recommandees": actions,
        "reference": "NF DTU 20.1 §10" + ref_quantitative,
    }
