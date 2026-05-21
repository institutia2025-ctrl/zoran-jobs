"""skill Vérification de la résistance au feu d'un élément de construction.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Sécurité incendie.
Source : NF EN 13501-2 (classement de résistance au feu) ; règlement de sécurité
contre l'incendie.

Compare le classement de résistance au feu d'un élément à l'exigence. Un
classement combine des critères et une durée, par exemple « REI 60 » :
    R = capacité portante,  E = étanchéité au feu,  I = isolation thermique.
L'élément est conforme si :
    - ses critères couvrent tous les critères exigés (REI couvre EI, EI couvre E…),
    - sa durée ≥ durée exigée.

Une protection au feu insuffisante engage la vie des occupants — veto_capable.

⚠️ MVP : comparaison de classement. Ne réalise pas l'essai de résistance au feu
ni le calcul thermomécanique — le classement de l'élément provient d'un PV
d'essai ou d'une appréciation de laboratoire agréé.
Loi 1 : le classement de l'élément et l'exigence sont fournis (PV / règlement).

Contrat io :
    inputs  : {classement_element, exigence}     # ex. "REI 90", "EI 60"
    outputs : {conforme, criteres_manquants, marge_min, verdict, reference}
"""

from __future__ import annotations

CRITERES = {"R", "E", "I"}  # R: portance · E: étanchéité au feu · I: isolation


def _parse(classement: str, nom: str) -> tuple[set, int]:
    """Décompose 'REI 60' en ({'R','E','I'}, 60). Lève ValueError si invalide."""
    parts = str(classement).strip().upper().split()
    if len(parts) != 2:
        raise ValueError(f"{nom} : format attendu '<critères> <durée>' (ex. 'REI 60')")
    lettres = set(parts[0])
    if not lettres or not lettres.issubset(CRITERES):
        raise ValueError(f"{nom} : critères '{parts[0]}' invalides — combinaison de R, E, I")
    try:
        duree = int(parts[1])
    except ValueError:
        raise ValueError(f"{nom} : durée '{parts[1]}' invalide — entier en minutes") from None
    if duree < 0:
        raise ValueError(f"{nom} : durée négative interdite")
    return lettres, duree


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    crit_elem, duree_elem = _parse(inputs.get("classement_element", ""), "classement_element")
    crit_exig, duree_exig = _parse(inputs.get("exigence", ""), "exigence")

    criteres_manquants = sorted(crit_exig - crit_elem)
    duree_ok = duree_elem >= duree_exig
    conforme = not criteres_manquants and duree_ok
    return {
        "conforme": conforme,
        "criteres_manquants": criteres_manquants,
        "duree_element_min": duree_elem,
        "duree_exigee_min": duree_exig,
        "marge_min": duree_elem - duree_exig,
        "verdict": ("Élément conforme à l'exigence de résistance au feu." if conforme
                    else "Élément NON conforme — protection au feu insuffisante."),
        "reference": "NF EN 13501-2 (classement de résistance au feu) + règlement incendie",
    }
