"""skill Orchestrateur d'environnement IA — recommandation zéro-friction.

Mission : ZORAN_JOBS_20260521 · skill méta — accès à l'intelligence.

Transforme la description d'une machine (ordinateur ou téléphone) en une
recommandation claire : quelles IA elle peut faire tourner en local, lesquelles
refuser, quel moteur local et quel repli en ligne — sans vocabulaire technique
pour l'utilisateur. Il s'attaque à la vraie friction d'aujourd'hui : non pas le
manque d'IA, mais la complexité d'accès.

⚠️ VERSION V1 SAFE : ce skill AUDITE et RECOMMANDE uniquement. Il N'INSTALLE
RIEN. Un skill du runtime est une fonction pure : ni accès matériel, ni réseau,
ni installation. Le scan réel du matériel et l'installation GUIDÉE — étape par
étape, avec validation de l'utilisateur — relèvent du harnais. Le skill est le
cerveau qui décide ce qui est cohérent ; il ne touche pas la machine.
Loi 1 : les caractéristiques de la machine sont fournies (résultat du scan) ;
les seuils de mémoire par taille de modèle sont des ordres de grandeur
(quantification Q4 + marge d'exécution), à confirmer selon le modèle exact. Le
skill ne consulte pas Internet : il recommande des FAMILLES de moteurs, pas une
liste à jour d'API gratuites — disponibilité et quotas du moment sont à vérifier.

Contrat io :
    inputs  : {type_appareil, ram_go, stockage_libre_go, vram_go?, batterie_pct?, reseau?}
    outputs : {capacite, modeles_recommandes, modeles_refuses, moteur_local,
               repli_en_ligne, conseils, reference}
"""

from __future__ import annotations

# Classes de modèles : (nom lisible, mémoire utile mini Go, stockage mini Go).
# Ordres de grandeur pour un modèle quantifié Q4, marge d'exécution comprise.
CLASSES = [
    ("IA nano (~1 à 2 milliards de paramètres)", 1.5, 2.0),
    ("IA légère (~3 à 4 milliards)", 3.0, 4.0),
    ("IA moyenne (~7 à 8 milliards)", 6.0, 6.0),
    ("IA grande (~13 à 14 milliards)", 10.0, 10.0),
    ("IA très grande (~30 à 34 milliards)", 22.0, 22.0),
    ("IA massive (~70 milliards et plus)", 45.0, 45.0),
]
RESERVE_OS = {"ordinateur": 4.0, "telephone": 3.0}  # Go laissés au système
PLAFOND_TELEPHONE = 1  # indice de classe maximal sur téléphone (charge soutenue)
RESEAUX = {"offline", "faible", "correct"}


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    appareil = str(inputs.get("type_appareil", "")).lower()
    if appareil not in RESERVE_OS:
        raise ValueError("type_appareil : attendu 'ordinateur' ou 'telephone'")
    ram = inputs.get("ram_go")
    stockage = inputs.get("stockage_libre_go")
    if not _nombre(ram) or ram <= 0:
        raise ValueError("ram_go : nombre > 0 requis")
    if not _nombre(stockage) or stockage < 0:
        raise ValueError("stockage_libre_go : nombre >= 0 requis")
    vram = inputs.get("vram_go", 0.0)
    batterie = inputs.get("batterie_pct", 100.0)
    reseau = str(inputs.get("reseau", "correct")).lower()
    if not _nombre(vram) or vram < 0:
        raise ValueError("vram_go : nombre >= 0 requis")
    if not _nombre(batterie) or not (0.0 <= batterie <= 100.0):
        raise ValueError("batterie_pct : nombre dans [0..100] requis")
    if reseau not in RESEAUX:
        raise ValueError(f"reseau : attendu l'un de {sorted(RESEAUX)}")

    # Mémoire réellement utilisable : la plus grande des deux voies possibles.
    mem_gpu = float(vram) if (appareil == "ordinateur" and vram >= 4.0) else 0.0
    mem_cpu = max(0.0, float(ram) - RESERVE_OS[appareil])
    memoire_utile = max(mem_gpu, mem_cpu)
    voie = "carte graphique" if mem_gpu > mem_cpu else "mémoire vive"

    recommandes: list[str] = []
    refuses: list[dict] = []
    for i, (nom, ram_mini, stock_mini) in enumerate(CLASSES):
        if appareil == "telephone" and i > PLAFOND_TELEPHONE:
            refuses.append({"modele": nom,
                            "raison": "trop lourd pour un téléphone "
                                      "(chauffe, batterie, charge soutenue)"})
        elif ram_mini > memoire_utile:
            refuses.append({"modele": nom,
                            "raison": f"mémoire insuffisante ({memoire_utile:.1f} Go utiles)"})
        elif stock_mini > float(stockage):
            refuses.append({"modele": nom,
                            "raison": f"stockage insuffisant ({stockage} Go libres)"})
        else:
            recommandes.append(nom)

    capacite = recommandes[-1] if recommandes else "insuffisante pour une IA en local"

    if not recommandes:
        moteur_local = None
    elif appareil == "ordinateur":
        moteur_local = "un lanceur d'IA local simple (par exemple Ollama ou LM Studio)"
    else:
        moteur_local = "une application d'IA mobile à modèle embarqué"

    repli = (None if reseau == "offline"
             else "une IA en ligne (API gratuite type OpenRouter / Mistral) "
                  "pour les demandes trop lourdes pour la machine")

    conseils: list[str] = []
    if not recommandes:
        conseils.append(
            "Cet appareil ne peut pas faire tourner d'IA en local, et il est "
            "hors ligne : aucune IA disponible pour l'instant."
            if reseau == "offline" else
            "Cet appareil est trop juste pour une IA en local — passe par une IA en ligne.")
    if appareil == "telephone" and batterie < 20.0:
        conseils.append("Batterie faible : privilégie l'IA en ligne pour ne pas "
                        "vider la batterie.")
    if reseau == "faible":
        conseils.append("Réseau faible : garde une IA locale prête pour les coupures.")
    if recommandes:
        conseils.append(f"Recommandation : démarre avec « {recommandes[-1]} » en local"
                        + (f", et garde {repli} en secours." if repli else "."))

    return {
        "type_appareil": appareil,
        "capacite": capacite,
        "memoire_utile_go": round(memoire_utile, 1),
        "voie_execution": voie,
        "modeles_recommandes": recommandes,
        "modeles_refuses": refuses,
        "moteur_local": moteur_local,
        "repli_en_ligne": repli,
        "conseils": conseils,
        "reference": "Recommandation d'environnement IA — V1 audit + conseil (aucune installation)",
    }
