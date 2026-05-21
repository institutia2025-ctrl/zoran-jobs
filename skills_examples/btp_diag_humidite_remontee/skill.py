"""skill btp_diag_humidite_remontee — diagnostic humidite (uplift v1.1).

Mission : ZORAN_JOBS_20260521 · Phase A · AXE 4 Patho (2/5, v1.1 uplift).
Sources :
  - NF DTU 14.1 (cuvelage) + NF DTU 20.1 §10 (desordres maconnerie)
  - Cahier CSTB 3848 : Diagnostic et traitement de l'humidite
  - Norme NF EN 16242 : Conservation patrimoine — mesure humidite materiaux

Approche v1.1 : croisement de 3 axes (hauteur, symptomes visuels, mesures)
+ identification origine probable parmi 4 hypotheses concurrentes :
  - remontee capillaire
  - infiltration laterale
  - condensation
  - ruissellement / fuite
+ prise en compte type bati (ancien pierre vs contemporain BA — regulation
  hygrometrique naturelle differente, NF EN 16242).

⚠️ MVP : oriente diagnostic. Confirme sur site par sondage humidite (CM
   carbure ou capacitif) + analyse chimique si salinity_observee.

Contrat io :
    inputs : {
        "hauteur_zone_humide_cm": float,
        "efflorescences_salines": bool,
        "presence_revetement_etanche": bool,
        "type_bati"?: str,                       # "ancien_pierre"|"contemporain_ba"|"mixte"
        "humidite_pct_masse"?: float,
        "seuil_humidite_alerte_pct"?: float,
        "source_seuil"?: str,
        "type_salinity"?: str,                   # "sulfates"|"chlorures"|"nitrates"|"inconnu"
        "presence_taches_au_plafond"?: bool      # signale condensation > capillarite
    }
    outputs : {
        "remontee_capillaire_suspectee": bool,
        "origine_probable": str,                 # "capillarite"|"infiltration"|"condensation"|"ruissellement"|"indeterminee"
        "gravite": str,
        "actions_recommandees": list[str],
        "diagnostic_complementaire": list[str],
        "reference": str
    }
"""
from __future__ import annotations

TYPES_BATI = {"ancien_pierre", "contemporain_ba", "mixte"}
SALINITY_TYPES = {"sulfates", "chlorures", "nitrates", "inconnu"}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    h = inputs.get("hauteur_zone_humide_cm")
    if not isinstance(h, (int, float)) or h < 0:
        raise ValueError("hauteur_zone_humide_cm >= 0 requis")
    eff = inputs.get("efflorescences_salines")
    if not isinstance(eff, bool):
        raise ValueError("efflorescences_salines (bool) requis")
    rev = inputs.get("presence_revetement_etanche")
    if not isinstance(rev, bool):
        raise ValueError("presence_revetement_etanche (bool) requis")

    typ_bati = inputs.get("type_bati")
    if typ_bati is not None and typ_bati not in TYPES_BATI:
        raise ValueError(f"type_bati doit etre dans {sorted(TYPES_BATI)}")

    plafond = inputs.get("presence_taches_au_plafond", False)
    if not isinstance(plafond, bool):
        raise ValueError("presence_taches_au_plafond (bool) requis si fourni")

    # Humidite mesuree + seuil utilisateur (Loi 1)
    hum_mes = inputs.get("humidite_pct_masse")
    seuil = inputs.get("seuil_humidite_alerte_pct")
    source = inputs.get("source_seuil")
    hum_excede = False
    ref_quantitative = ""
    if hum_mes is not None:
        if not isinstance(hum_mes, (int, float)) or hum_mes < 0:
            raise ValueError("humidite_pct_masse >= 0 requis si fourni")
        if seuil is not None:
            if not isinstance(seuil, (int, float)) or seuil <= 0:
                raise ValueError("seuil_humidite_alerte_pct > 0 requis")
            if not isinstance(source, str) or not source.strip():
                raise ValueError("source_seuil obligatoire si seuil fourni (Loi 1)")
            # Bati ancien : tolerance plus large (regulation hygrometrique naturelle)
            seuil_effectif = seuil * (1.5 if typ_bati == "ancien_pierre" else 1.0)
            hum_excede = hum_mes >= seuil_effectif
            ref_quantitative = f" + seuil utilisateur {seuil}% (source: {source})"

    # Salinity
    salinity = inputs.get("type_salinity")
    if salinity is not None and salinity not in SALINITY_TYPES:
        raise ValueError(f"type_salinity doit etre dans {sorted(SALINITY_TYPES)}")

    # === Determination de l'origine probable (raisonnement croise) ===
    # Plafond = condensation prioritaire
    if plafond:
        origine = "condensation"
    # h entre 30-150 cm + efflorescences = signature capillarite
    elif (30 <= h <= 150) and eff:
        origine = "capillarite"
    # h > 150 cm et pas plafond = infiltration laterale ou ruissellement
    elif h > 150:
        origine = "infiltration"
    # Tache localisee sans h significative et sans plafond
    elif h < 30 and (eff or hum_excede):
        # Ruissellement / fuite ponctuelle
        origine = "ruissellement"
    else:
        origine = "indeterminee"

    # Capillarite suspectee = origine capillarite avec confirmation symptomes
    suspectee = (origine == "capillarite") and (eff or hum_excede)

    # Gravite
    if suspectee and (rev or hum_excede):
        gravite = "elevee"
    elif suspectee or origine == "infiltration":
        gravite = "moyenne"
    elif origine == "condensation":
        gravite = "moyenne" if typ_bati == "contemporain_ba" else "faible"
    elif h > 0 and eff:
        gravite = "moyenne"
    else:
        gravite = "faible"

    actions = []
    diag_complementaire = []
    if origine == "capillarite":
        actions.append("Sondage humidite carbure (CM) sur 3 points le long de la zone.")
        actions.append("Inspecter coupure de capillarite (arase etanche) - NF DTU 14.1.")
        diag_complementaire.append("Analyse chimique des sels (sulfates/nitrates/chlorures).")
    elif origine == "infiltration":
        actions.append("Tracer le cheminement de l'eau : facade, defaut etancheite, joints.")
        diag_complementaire.append("Inspection thermographique IR + test fumee si fissures suspectes.")
    elif origine == "condensation":
        actions.append("Mesurer hygrometrie ambiante + temperature paroi (point de rosee).")
        actions.append("Verifier VMC et isolation thermique (RE2020 / NF EN 16798).")
        if typ_bati == "ancien_pierre":
            actions.append("ATTENTION : ne pas etancher un bati ancien — preserver respiration paroi.")
    elif origine == "ruissellement":
        actions.append("Inspection visuelle reseau d'eau et descentes pluviales a proximite.")
        diag_complementaire.append("Test de mise en charge reseau eau si fuite suspectee.")

    if rev:
        actions.append("Deposer revetement etanche au sol si origine capillarite confirmee.")

    if salinity == "sulfates":
        actions.append("ALERTE : attaque sulfatique probable du mortier (NF EN 206-1 XA) — diagnostic mortier urgent.")
    elif salinity == "chlorures":
        actions.append("ALERTE : presence chlorures = corrosion armatures possible (NF EN 1504-9).")
    elif salinity == "nitrates":
        actions.append("Origine nitrates : fuite reseau eaux usees ou activite biologique (cave).")

    if not actions:
        actions.append("Surveillance simple : photographier date + hauteur, reverifier 6 mois.")

    return {
        "remontee_capillaire_suspectee": suspectee,
        "origine_probable": origine,
        "gravite": gravite,
        "actions_recommandees": actions,
        "diagnostic_complementaire": diag_complementaire,
        "type_bati_pris_en_compte": typ_bati,
        "reference": "NF DTU 14.1 + NF DTU 20.1 §10 + Cahier CSTB 3848 + NF EN 16242" + ref_quantitative,
    }
