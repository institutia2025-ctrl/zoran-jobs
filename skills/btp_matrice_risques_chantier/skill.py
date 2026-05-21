"""
skill btp_matrice_risques_chantier — Matrice de risques de chantier.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (conduite)
Référence méthodologique : ISO 31000 (management du risque).
Point d'entrée : run(inputs: dict) -> dict.

Évalue une liste de risques (probabilité x gravité, échelles 1..5), construit
la matrice de criticité, classe les risques et identifie les inacceptables.
"""

from __future__ import annotations


def _niveau(criticite: int) -> str:
    """Niveau d'acceptabilité du risque (criticité = probabilité x gravité)."""
    if criticite <= 4:
        return "acceptable"
    if criticite <= 9:
        return "tolerable"
    if criticite <= 14:
        return "indesirable"
    return "inacceptable"


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    risques = inp.get("risques") or []

    matrice: list[dict] = []
    for r in risques:
        r = r or {}
        nom = str(r.get("nom", "risque"))
        p = min(5, max(1, int(r.get("probabilite", 1))))
        g = min(5, max(1, int(r.get("gravite", 1))))
        c = p * g
        matrice.append({"nom": nom, "probabilite": p, "gravite": g,
                        "criticite": c, "niveau": _niveau(c)})

    # Classement déterministe : criticité décroissante, puis nom.
    matrice.sort(key=lambda x: (-x["criticite"], x["nom"]))
    nb_inacceptables = sum(1 for m in matrice if m["criticite"] >= 15)
    moyenne = (round(sum(m["criticite"] for m in matrice) / len(matrice), 2)
               if matrice else 0.0)

    return {
        "matrice": matrice,
        "nb_risques": len(matrice),
        "risque_majeur": matrice[0]["nom"] if matrice else None,
        "nb_inacceptables": nb_inacceptables,
        "criticite_moyenne": moyenne,
        "verdict": (f"{len(matrice)} risque(s) évalué(s), "
                    f"{nb_inacceptables} inacceptable(s)."),
    }
