"""skill btp_diag_corrosion_armatures — diagnostic corrosion armatures.

Mission : ZORAN_JOBS_20260521 · Phase A BTP · AXE 4 Pathologies (4/5).
Sources :
  - NF EN 1504 : Produits et systemes pour la protection et la reparation des
    structures en beton. Partie 9 = principes generaux d'utilisation.
  - NF EN 206-1 : classes d'exposition (XC carbonatation, XS chlorures marins,
    XD chlorures non marins, XF gel).

Approche : combine perte de section (mesure ou estimee), classe d'exposition
et fissuration eventuelle pour orienter vers principe de reparation EN 1504.

⚠️ MVP : oriente vers un PRINCIPE EN 1504 (1 a 11). Le CHOIX du systeme de
   reparation (mortier, revetement, anode sacrificielle, protection cathodique)
   demande etude approfondie BET + diagnostic complementaire.

Contrat io :
    inputs : {
        "perte_section_pct": float,              # % de section perdue (0..100)
        "classe_exposition": str,                # XC1..XC4, XS1..XS3, XD1..XD3, XF1..XF4
        "fissuration_visible": bool,             # fissures longitudinales sur traces armature
        "epaufrures_visibles": bool              # eclats de beton par expansion rouille
    }
    outputs : {
        "severite": str,                          # "minime"/"moderee"/"avancee"/"critique"
        "principe_en1504_recommande": int | None, # 1 a 11 (None si donnees insuffisantes)
        "actions_recommandees": list[str],
        "reference": str
    }
"""
from __future__ import annotations

CLASSES_VALIDES = {f"X{lett}{n}" for lett in "CSDF" for n in range(1, 5)}


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    perte = inputs.get("perte_section_pct")
    if not isinstance(perte, (int, float)) or not (0.0 <= perte <= 100.0):
        raise ValueError("perte_section_pct doit etre un nombre dans [0..100]")
    classe = inputs.get("classe_exposition")
    if classe not in CLASSES_VALIDES:
        raise ValueError(f"classe_exposition doit etre dans {sorted(CLASSES_VALIDES)} (NF EN 206-1)")
    fiss = inputs.get("fissuration_visible")
    eppa = inputs.get("epaufrures_visibles")
    if not isinstance(fiss, bool):
        raise ValueError("fissuration_visible (bool) requis")
    if not isinstance(eppa, bool):
        raise ValueError("epaufrures_visibles (bool) requis")

    # Severite combinee perte + symptomes visibles
    if perte >= 25 or eppa:
        severite = "critique"
    elif perte >= 10 or fiss:
        severite = "avancee"
    elif perte >= 3:
        severite = "moderee"
    else:
        severite = "minime"

    # Orientation Principe EN 1504-9 (selon symptomes principaux)
    # Principle 7 : preservation ou restauration de la passivite
    # Principle 8 : augmentation de la resistivite
    # Principle 10 : protection cathodique
    # Principle 11 : controle des zones anodiques
    if severite == "critique":
        principe = 10  # protection cathodique recommandee
    elif severite == "avancee":
        principe = 7  # restauration passivite + reparation
    elif severite == "moderee":
        principe = 8  # augmentation resistivite (revetement, hydrofuge)
    else:
        principe = 1  # protection contre la penetration

    actions = []
    if severite in ("critique", "avancee"):
        actions.append("Inspection visuelle exhaustive + cartographie potentiel d'electrode (EN 1504-9).")
        actions.append(f"Etude BET specialisee corrosion. Principe {principe} EN 1504-9 indicatif.")
    if eppa:
        actions.append("Decapage local jusqu'a beton sain + traitement armature + remplacement (EN 1504-3 R3 ou R4).")
    if classe.startswith("XS"):
        actions.append("Environnement chlorures marin (XS) — inhibiteurs ou protection cathodique a evaluer.")
    if not actions:
        actions.append("Surveillance reguliere — inspection visuelle annuelle minimum.")

    return {
        "severite": severite,
        "principe_en1504_recommande": principe,
        "classe_exposition": classe,
        "actions_recommandees": actions,
        "reference": "NF EN 1504-9 (principes) + NF EN 206-1 (classes exposition)",
    }
