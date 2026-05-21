"""skill Planificateur de publication vidéo — montage + diffusion A→Z.

Mission : ZORAN_JOBS_20260521 · skill méta — média / orchestration.

À partir d'une ou plusieurs vidéos sources, d'un sujet, d'une cible et de la
liste des réseaux sociaux visés, ce skill produit un PLAN DE PUBLICATION
complet et déterministe : montage (liste de coupes), hook, description,
hashtags, style de sous-titres, charte graphique appliquée, plan de promotion
(teasers à rediffuser) et calendrier relatif.

⚠️ CADRAGE HONNÊTE — ce que ce skill N'EST PAS.
Un skill du runtime est une FONCTION PURE : ni réseau, ni process, ni système
de fichiers (invariant). Ce skill ne « regarde » donc aucune vidéo, ne lance
pas ffmpeg, ne transcrit pas (Whisper), ne lit pas le site du user et ne
publie sur AUCUN réseau. Il est le CERVEAU qui PLANIFIE ; le découpage réel,
le rendu, la transcription et la publication sont exécutés par le HARNAIS
agentique à partir du plan produit ici.

Conséquence directe : les « moments » de chaque vidéo (segments horodatés avec
une intensité) doivent être fournis en entrée — détectés en amont par le
harnais. Loi 1 : le skill n'invente aucun contenu vidéo. De même, la charte
graphique est fournie en entrée (extraite du site du user par le harnais) ;
si elle manque, le skill le signale au lieu d'inventer des couleurs.

Contrat io :
    inputs  : {videos:[{id,duree_s,moments:[{debut_s,fin_s,intensite,
               description}]}], sujet, cible, reseaux:[...],
               charte_graphique?, objectif?, nb_teasers?}
    outputs : {plans_par_reseau, plan_promotion, calendrier,
               charte_appliquee, avertissements, synthese, reference}
"""

from __future__ import annotations

import unicodedata

# Spécifications publiques et stables des réseaux : ratio d'image et durée
# maximale sont des faits de plateforme ; `duree_ideale_s` est une heuristique
# de format court (déclarée comme telle dans limites_explicites).
RESEAUX: dict[str, dict] = {
    "tiktok":          {"ratio": "9:16", "duree_max_s": 600,  "duree_ideale_s": 34,  "hook_window_s": 3, "hashtags_max": 5},
    "youtube_shorts":  {"ratio": "9:16", "duree_max_s": 60,   "duree_ideale_s": 45,  "hook_window_s": 3, "hashtags_max": 3},
    "instagram_reels": {"ratio": "9:16", "duree_max_s": 90,   "duree_ideale_s": 30,  "hook_window_s": 3, "hashtags_max": 8},
    "linkedin":        {"ratio": "1:1",  "duree_max_s": 600,  "duree_ideale_s": 60,  "hook_window_s": 5, "hashtags_max": 5},
    "x":               {"ratio": "16:9", "duree_max_s": 140,  "duree_ideale_s": 45,  "hook_window_s": 3, "hashtags_max": 2},
    "facebook":        {"ratio": "1:1",  "duree_max_s": 240,  "duree_ideale_s": 60,  "hook_window_s": 3, "hashtags_max": 3},
    "youtube":         {"ratio": "16:9", "duree_max_s": 3600, "duree_ideale_s": 480, "hook_window_s": 8, "hashtags_max": 5},
}
SHORT_FORM = {"tiktok", "youtube_shorts", "instagram_reels", "x"}
OBJECTIFS = {"lancement", "relance"}
TEASER_MAX_S = 15.0

STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "au",
    "aux", "en", "dans", "sur", "pour", "avec", "par", "ce", "ces", "cette",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "qui", "que",
    "quoi", "comment", "est", "sont", "plus", "moins", "tres", "votre", "vos",
    "nos", "notre", "the", "and", "for", "you",
}

HOOK_PATTERNS = (
    "{cible}, ne scrollez pas : {sujet}.",
    "Ce que personne ne vous dit sur {sujet}.",
    "{sujet} — l'essentiel en {duree}s.",
    "Si vous êtes {cible}, regardez ça : {sujet}.",
)


def _slug(mot: str) -> str:
    """Normalise un mot : minuscules, sans accent, alphanumérique seul."""
    decompose = unicodedata.normalize("NFKD", mot)
    sans_accent = "".join(c for c in decompose if not unicodedata.combining(c))
    return "".join(c for c in sans_accent.lower() if c.isalnum())


def _nombre(valeur, nom: str, *, mini=None, maxi=None, strict_mini=False):
    """Convertit en float et vérifie les bornes. Lève ValueError sinon."""
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise ValueError(f"{nom} : nombre attendu")
    v = float(valeur)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError(f"{nom} : nombre fini attendu")
    if mini is not None and (v <= mini if strict_mini else v < mini):
        borne = ">" if strict_mini else ">="
        raise ValueError(f"{nom} : valeur {borne} {mini} attendue")
    if maxi is not None and v > maxi:
        raise ValueError(f"{nom} : valeur <= {maxi} attendue")
    return v


def _texte(valeur, nom: str) -> str:
    """Renvoie une chaîne non vide ou lève ValueError."""
    s = str(valeur or "").strip()
    if not s:
        raise ValueError(f"{nom} : texte non vide attendu")
    return s


def _hashtags(sujet: str, cible: str, maxi: int) -> list[str]:
    """Hashtags DÉRIVÉS du sujet et de la cible — aucune tendance inventée."""
    mots: list[str] = []
    for source in (sujet, cible):
        for brut in source.replace("-", " ").replace("'", " ").split():
            slug = _slug(brut)
            if len(slug) >= 3 and slug not in STOPWORDS and slug not in mots:
                mots.append(slug)
    return ["#" + m for m in mots[:maxi]]


def _valider_videos(videos) -> list[dict]:
    """Normalise et valide la liste des vidéos sources."""
    if not isinstance(videos, list) or not videos:
        raise ValueError("videos : liste non vide attendue")
    norm: list[dict] = []
    for i, v in enumerate(videos):
        v = v or {}
        vid = _texte(v.get("id"), f"videos[{i}].id")
        duree = _nombre(v.get("duree_s"), f"videos[{i}].duree_s",
                        mini=0.0, strict_mini=True)
        moments = v.get("moments")
        if not isinstance(moments, list) or not moments:
            raise ValueError(f"videos[{i}].moments : liste non vide attendue")
        m_norm: list[dict] = []
        for j, m in enumerate(moments):
            m = m or {}
            etq = f"videos[{i}].moments[{j}]"
            debut = _nombre(m.get("debut_s"), f"{etq}.debut_s", mini=0.0)
            fin = _nombre(m.get("fin_s"), f"{etq}.fin_s", mini=0.0)
            if fin <= debut:
                raise ValueError(f"{etq} : fin_s doit être > debut_s")
            if fin > duree:
                raise ValueError(f"{etq} : fin_s dépasse la durée de la vidéo")
            intensite = _nombre(m.get("intensite"), f"{etq}.intensite",
                                mini=0.0, maxi=1.0)
            desc = _texte(m.get("description"), f"{etq}.description")
            m_norm.append({"debut_s": debut, "fin_s": fin,
                           "intensite": intensite, "description": desc})
        norm.append({"id": vid, "duree_s": duree, "moments": m_norm})
    return norm


def _montage(moments: list[dict], spec: dict) -> tuple[list[dict], float]:
    """Sélectionne les segments les plus intenses pour remplir la durée cible.

    Le moment le plus intense devient le segment d'ouverture (hook) ; les
    autres sont remis en ordre chronologique pour une timeline cohérente.
    """
    cible = spec["duree_ideale_s"]
    hard = spec["duree_max_s"]
    par_intensite = sorted(
        moments, key=lambda m: (-m["intensite"], m["video_index"], m["debut_s"]))
    picked: list[dict] = []
    total = 0.0
    for m in par_intensite:
        if total >= cible:
            break
        room = hard - total
        if room <= 0:
            break
        use = min(m["fin_s"] - m["debut_s"], room)
        picked.append({
            "video_id": m["video_id"], "debut_s": m["debut_s"],
            "fin_s": round(m["debut_s"] + use, 3), "duree_s": round(use, 3),
            "intensite": m["intensite"], "description": m["description"],
        })
        total += use
    if not picked:
        return [], 0.0
    # Le segment le plus intense en ouverture, le reste en chronologie.
    ouverture = max(picked, key=lambda s: s["intensite"])
    reste = [s for s in picked if s is not ouverture]
    reste.sort(key=lambda s: (s["video_id"], s["debut_s"]))
    return [ouverture, *reste], round(total, 3)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    videos = _valider_videos(inputs.get("videos"))
    sujet = _texte(inputs.get("sujet"), "sujet")
    cible = _texte(inputs.get("cible"), "cible")

    reseaux = inputs.get("reseaux")
    if not isinstance(reseaux, list) or not reseaux:
        raise ValueError("reseaux : liste non vide attendue")
    reseaux_norm: list[str] = []
    for r in reseaux:
        rid = str(r or "").strip().lower()
        if rid not in RESEAUX:
            raise ValueError(
                f"reseaux : '{rid}' inconnu — attendus {sorted(RESEAUX)}")
        if rid not in reseaux_norm:
            reseaux_norm.append(rid)

    objectif = str(inputs.get("objectif", "lancement")).strip().lower()
    if objectif not in OBJECTIFS:
        raise ValueError(f"objectif : attendu l'un de {sorted(OBJECTIFS)}")

    nb_teasers = inputs.get("nb_teasers", 3)
    if isinstance(nb_teasers, bool) or not isinstance(nb_teasers, int) \
            or nb_teasers < 0:
        raise ValueError("nb_teasers : entier >= 0 attendu")

    avertissements: list[str] = []

    # --- charte graphique (fournie par le harnais, jamais inventée) --------
    charte_in = inputs.get("charte_graphique")
    if charte_in is not None and not isinstance(charte_in, dict):
        raise ValueError("charte_graphique : objet attendu")
    charte_in = charte_in or {}
    charte = {
        "couleur_primaire": charte_in.get("couleur_primaire"),
        "couleur_secondaire": charte_in.get("couleur_secondaire"),
        "police": charte_in.get("police"),
        "ton": charte_in.get("ton"),
    }
    if not any(charte.values()):
        avertissements.append(
            "Charte graphique non fournie : le harnais doit l'extraire du "
            "site du user avant rendu (couleurs, police, ton).")

    # --- moments aplatis (toutes vidéos) -----------------------------------
    tous_moments: list[dict] = []
    for vi, v in enumerate(videos):
        for m in v["moments"]:
            tous_moments.append({"video_index": vi, "video_id": v["id"], **m})

    # --- un plan par réseau ------------------------------------------------
    plans: list[dict] = []
    for reseau in reseaux_norm:
        spec = RESEAUX[reseau]
        montage, duree_montage = _montage(tous_moments, spec)
        if duree_montage < spec["duree_ideale_s"]:
            avertissements.append(
                f"{reseau} : matériel disponible ({duree_montage:.0f}s) "
                f"sous la durée idéale ({spec['duree_ideale_s']}s) — "
                "fournir plus de moments pour un format optimal.")
        idx = sum(ord(c) for c in reseau) % len(HOOK_PATTERNS)
        hook = HOOK_PATTERNS[idx].format(
            cible=cible, sujet=sujet, duree=spec["duree_ideale_s"])
        couvert = ", ".join(s["description"] for s in montage[:3]) or sujet
        hashtags = _hashtags(sujet, cible, spec["hashtags_max"])
        description = (f"{sujet} — pour {cible}. Au programme : {couvert}. "
                       + " ".join(hashtags))
        plans.append({
            "reseau": reseau,
            "format": {"ratio": spec["ratio"],
                       "duree_cible_s": spec["duree_ideale_s"],
                       "duree_max_s": spec["duree_max_s"]},
            "montage": montage,
            "duree_montage_s": duree_montage,
            "hook": hook,
            "hook_window_s": spec["hook_window_s"],
            "description": description,
            "hashtags": hashtags,
            "sous_titres": {
                "actives": True,
                "source": "transcription automatique (harnais — ex. Whisper)",
                "style": {"police": charte["police"],
                          "couleur": charte["couleur_primaire"]},
            },
            "charte_appliquee": dict(charte),
        })

    # --- plan de promotion : teasers (extraits courts à rediffuser) --------
    par_intensite = sorted(
        tous_moments,
        key=lambda m: (-m["intensite"], m["fin_s"] - m["debut_s"],
                       m["video_index"], m["debut_s"]))
    reseaux_court = [r for r in reseaux_norm if r in SHORT_FORM] \
        or list(reseaux_norm)
    teasers: list[dict] = []
    for k, m in enumerate(par_intensite[:nb_teasers]):
        duree_t = min(m["fin_s"] - m["debut_s"], TEASER_MAX_S)
        teasers.append({
            "id": f"teaser_{k + 1}",
            "source_video": m["video_id"],
            "debut_s": m["debut_s"],
            "fin_s": round(m["debut_s"] + duree_t, 3),
            "duree_s": round(duree_t, 3),
            "intensite": m["intensite"],
            "mini_hook": f"{m['description']} — vidéo complète en lien.",
            "reseaux_cibles": list(reseaux_court),
        })
    if nb_teasers > len(par_intensite):
        avertissements.append(
            f"nb_teasers={nb_teasers} demandé mais seulement "
            f"{len(par_intensite)} moment(s) disponible(s).")

    # --- calendrier relatif (jour 0 = publication master) ------------------
    calendrier: list[dict] = []
    for reseau in reseaux_norm:
        calendrier.append({"jour_relatif": 0, "type": "master",
                            "reseau": reseau, "reference": "video_master"})
    if objectif == "lancement":
        # Teasers en compte à rebours AVANT le master.
        n = len(teasers)
        for k, t in enumerate(teasers):
            jour = -(n - k)
            for reseau in t["reseaux_cibles"]:
                calendrier.append({"jour_relatif": jour, "type": "teaser",
                                   "reseau": reseau, "reference": t["id"]})
    else:
        # Relance : teasers APRÈS le master, espacement croissant.
        offsets = [1, 3, 7, 14, 21, 30]
        for k, t in enumerate(teasers):
            jour = offsets[k] if k < len(offsets) \
                else offsets[-1] + (k - len(offsets) + 1) * 7
            for reseau in t["reseaux_cibles"]:
                calendrier.append({"jour_relatif": jour, "type": "teaser",
                                   "reseau": reseau, "reference": t["id"]})
    calendrier.sort(key=lambda e: (e["jour_relatif"], e["type"], e["reseau"]))

    synthese = (
        f"{len(videos)} vidéo(s) source → {len(plans)} plan(s) réseau + "
        f"{len(teasers)} teaser(s) ({objectif}). "
        f"Le skill PLANIFIE ; le découpage, le rendu et la publication sont "
        f"exécutés par le harnais.")

    return {
        "sujet": sujet,
        "cible": cible,
        "objectif": objectif,
        "plans_par_reseau": plans,
        "plan_promotion": {"objectif": objectif, "teasers": teasers},
        "calendrier": calendrier,
        "charte_appliquee": charte,
        "avertissements": avertissements,
        "synthese": synthese,
        "reference": ("Planificateur de publication vidéo ZORAN — montage, "
                      "hook, hashtags, charte, promotion et calendrier "
                      "déterministes ; exécution déléguée au harnais"),
    }
