"""skill btp_diag_humidite_remontee — diagnostic remontees capillaires.

Mission : ZORAN_JOBS_20260521 · Phase A BTP · AXE 4 Pathologies (2/5).
Source qualitative : NF DTU 14.1 (cuvelage) + DTU 20.1 §10 (desordres maconnerie).
Source quantitative : seuils d'humidite a la masse fournis en input (Loi 1).

⚠️ MVP : oriente diagnostic. Confirme sur site par sondage humidite (carbure
   ou capacitif) + analyse origine (capillarite vs infiltration vs condensation).

Contrat io :
    inputs : {
        "hauteur_zone_humide_cm": float,        # hauteur visible depuis le sol
        "efflorescences_salines": bool,         # depots blanchatres
        "presence_revetement_etanche": bool,    # peinture/carrelage etanche au sol
        "humidite_pct_masse"?: float,           # mesure sondage (optionnel)
        "seuil_humidite_alerte_pct"?: float,    # seuil utilisateur (defaut 5%)
        "source_seuil"?: str                    # obligatoire si seuil fourni
    }
    outputs : {
        "remontee_capillaire_suspectee": bool,
        "gravite": str,
        "actions_recommandees": list[str],
        "reference": str
    }
"""
from __future__ import annotations


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    h = inputs.get("hauteur_zone_humide_cm")
    if not isinstance(h, (int, float)) or h < 0:
        raise ValueError("hauteur_zone_humide_cm requis (nombre >= 0)")
    eff = inputs.get("efflorescences_salines")
    if not isinstance(eff, bool):
        raise ValueError("efflorescences_salines (bool) requis")
    rev = inputs.get("presence_revetement_etanche")
    if not isinstance(rev, bool):
        raise ValueError("presence_revetement_etanche (bool) requis")

    hum_mes = inputs.get("humidite_pct_masse")
    seuil = inputs.get("seuil_humidite_alerte_pct")
    source = inputs.get("source_seuil")
    hum_excede = False
    ref_quantitative = ""
    if hum_mes is not None:
        if not isinstance(hum_mes, (int, float)) or hum_mes < 0:
            raise ValueError("humidite_pct_masse doit etre un nombre >= 0 si fourni")
        if seuil is not None:
            if not isinstance(seuil, (int, float)) or seuil <= 0:
                raise ValueError("seuil_humidite_alerte_pct doit etre un nombre > 0")
            if not isinstance(source, str) or not source.strip():
                raise ValueError("source_seuil obligatoire si seuil fourni (Loi 1)")
            hum_excede = hum_mes >= seuil
            ref_quantitative = f" + seuil utilisateur {seuil}% (source: {source})"

    # Critère qualitatif : remontée capillaire suspectée
    # - hauteur entre 30 et 150 cm = signature typique capillarite
    # - efflorescences salines = forte presomption
    # - revetement etanche au sol = aggrave (eau ne s'evapore plus)
    suspectee = (30 <= h <= 150) and (eff or hum_excede)

    if suspectee and (rev or hum_excede):
        gravite = "elevee"
    elif suspectee:
        gravite = "moyenne"
    elif h > 0 and eff:
        gravite = "moyenne"  # autre origine probable, a investiguer
    else:
        gravite = "faible"

    actions = []
    if suspectee:
        actions.append("Sondage humidite carbure (CM) ou capacitif pour mesurer % a la masse.")
        actions.append("Inspecter coupure de capillarite (arase etanche) selon DTU 20.1.")
    if rev:
        actions.append("Deposer revetement etanche au sol — l'eau doit pouvoir s'evaporer (NF DTU 14.1).")
    if eff:
        actions.append("Analyse chimique des efflorescences (sulfates, chlorures) pour identifier l'origine.")
    if not actions:
        actions.append("Surveillance simple : photographier date + hauteur, reverifier dans 6 mois.")

    return {
        "remontee_capillaire_suspectee": suspectee,
        "gravite": gravite,
        "actions_recommandees": actions,
        "reference": "NF DTU 14.1 + NF DTU 20.1 §10" + ref_quantitative,
    }
