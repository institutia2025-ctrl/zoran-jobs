"""skill Vérification d'une rampe d'accès PMR.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Sécurité / Accessibilité.
Source : arrêté du 8 décembre 2014 (accessibilité des ERP et IOP) — rampes.

Vérifie la conformité d'une rampe d'accès aux personnes à mobilité réduite :
pente, longueur, largeur, présence de paliers de repos.

Règles (rampe aménagée) :
- pente ≤ 5 % : conforme.
- 5 % < pente ≤ 8 % : toléré sur une longueur ≤ 2 m.
- 8 % < pente ≤ 10 % : toléré sur une longueur ≤ 0,50 m.
- pente > 10 % : non conforme.
- largeur ≥ 1,20 m.
- palier de repos requis en haut, en bas, et tous les 10 m.

⚠️ MVP : rampe rectiligne. Ne traite pas les paliers tournants, les ressauts
ni le garde-corps de la rampe (voir btp_verif_garde_corps_hauteur).
Loi 1 : seuils repris de l'arrêté du 8 décembre 2014.

Contrat io :
    inputs  : {pente_pct, longueur_m, largeur_m, paliers_repos_presents}
    outputs : {conforme, non_conformites, verdict, reference}
"""

from __future__ import annotations

LARGEUR_MIN_M = 1.20


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    pente = inputs.get("pente_pct")
    longueur = inputs.get("longueur_m")
    largeur = inputs.get("largeur_m")
    paliers = bool(inputs.get("paliers_repos_presents", False))

    if not _nombre(pente) or pente < 0:
        raise ValueError("pente_pct : nombre >= 0 requis")
    if not _nombre(longueur) or longueur <= 0:
        raise ValueError("longueur_m : nombre > 0 requis")
    if not _nombre(largeur) or largeur <= 0:
        raise ValueError("largeur_m : nombre > 0 requis")

    pente, longueur, largeur = float(pente), float(longueur), float(largeur)
    nc: list[str] = []
    if pente > 10.0:
        nc.append(f"pente {pente}% > 10% : non admissible")
    elif pente > 8.0 and longueur > 0.50:
        nc.append(f"pente {pente}% (8-10%) tolérée seulement sur <= 0,50 m")
    elif pente > 5.0 and longueur > 2.0:
        nc.append(f"pente {pente}% (5-8%) tolérée seulement sur <= 2 m")
    if largeur < LARGEUR_MIN_M:
        nc.append(f"largeur {largeur} m < {LARGEUR_MIN_M} m minimum")
    if longueur > 10.0 and not paliers:
        nc.append("longueur > 10 m sans palier de repos (requis tous les 10 m)")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "verdict": ("Rampe PMR conforme."
                    if conforme else
                    f"{len(nc)} non-conformité(s) — rampe PMR non conforme."),
        "reference": "Arrêté du 8 décembre 2014 (accessibilité ERP/IOP) — rampes",
    }
