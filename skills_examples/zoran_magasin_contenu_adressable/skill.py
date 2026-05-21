"""skill Magasin de contenus adressable — le coffre du photo-clone.

Mission : ZORAN_JOBS_20260521 · skill méta — sauvegarde.

Complément de zoran_photo_clone_leger. Si la photo est la BOUSSOLE (elle détecte
et cible), ce magasin est le COFFRE (il stocke et restitue le contenu réel).

Deux modes :
  - "indexer" : transforme une liste de fichiers {chemin, contenu} en magasin
    adressé par empreinte sha256. Les contenus identiques ne sont stockés qu'une
    fois (déduplication). Renvoie le magasin, la photo associée et le taux de
    déduplication.
  - "restaurer" : à partir d'un plan ciblé [{chemin, hash}] et d'un magasin,
    résout le contenu de chaque fichier en VÉRIFIANT son empreinte. Tout contenu
    absent du magasin est signalé, tout contenu corrompu est détecté — la
    restauration n'est jamais silencieuse.

⚠️ MVP : le skill indexe, déduplique et résout en mémoire. La persistance du
magasin sur disque et l'écriture finale des fichiers relèvent du harnais.
Contenus traités comme du texte UTF-8.
Loi 1 : aucune empreinte n'est supposée — elle est recalculée à partir du
contenu réel ; toute restauration vérifie l'empreinte (intégrité falsifiable).

Contrat io :
    inputs  : {mode:"indexer"|"restaurer", fichiers?, a_restaurer?, store?}
    outputs : indexer   -> {store, photo, nb_fichiers, nb_blobs_uniques,
                            ratio_deduplication, reference}
              restaurer -> {restaures, manquants, corrompus, nb_restaures,
                            integrite_ok, reference}
"""

from __future__ import annotations

import hashlib


def _empreinte(contenu: str) -> str:
    return "sha256:" + hashlib.sha256(contenu.encode("utf-8")).hexdigest()


def _indexer(fichiers) -> dict:
    if not isinstance(fichiers, list) or not fichiers:
        raise ValueError("fichiers : liste non vide attendue (mode indexer)")
    store: dict[str, str] = {}
    entries: dict[str, dict] = {}
    for i, f in enumerate(fichiers):
        f = f or {}
        chemin = str(f.get("chemin", "")).strip()
        contenu = f.get("contenu")
        if not chemin:
            raise ValueError(f"fichiers[{i}].chemin : chemin non vide requis")
        if not isinstance(contenu, str):
            raise ValueError(f"fichiers[{i}].contenu : chaîne de caractères requise")
        h = _empreinte(contenu)
        store[h] = contenu  # déduplication : un même contenu = une seule entrée
        entries[chemin] = {"hash": h, "taille": len(contenu.encode("utf-8"))}
    nb_fichiers = len(entries)
    nb_blobs = len(store)
    ratio = round(1.0 - nb_blobs / nb_fichiers, 3) if nb_fichiers else 0.0
    return {
        "store": store,
        "photo": {"nb_fichiers": nb_fichiers, "entries": entries},
        "nb_fichiers": nb_fichiers,
        "nb_blobs_uniques": nb_blobs,
        "ratio_deduplication": ratio,
        "reference": "Magasin adressé par contenu — déduplication par empreinte sha256",
    }


def _restaurer(a_restaurer, store) -> dict:
    if not isinstance(a_restaurer, list) or not a_restaurer:
        raise ValueError("a_restaurer : liste non vide attendue (mode restaurer)")
    if not isinstance(store, dict):
        raise ValueError("store : magasin {empreinte: contenu} attendu")
    restaures: dict[str, str] = {}
    manquants: list[dict] = []
    corrompus: list[dict] = []
    for i, item in enumerate(a_restaurer):
        item = item or {}
        chemin = str(item.get("chemin", "")).strip()
        h = str(item.get("hash", "")).strip()
        if not chemin or not h:
            raise ValueError(f"a_restaurer[{i}] : chemin et hash requis")
        if h not in store:
            manquants.append({"chemin": chemin, "hash": h})
            continue
        contenu = store[h]
        if _empreinte(contenu) != h:
            corrompus.append({"chemin": chemin, "hash": h})
            continue
        restaures[chemin] = contenu
    return {
        "restaures": restaures,
        "manquants": manquants,
        "corrompus": corrompus,
        "nb_restaures": len(restaures),
        "integrite_ok": not manquants and not corrompus,
        "reference": "Restauration adressée par contenu — vérification d'empreinte (Loi 1)",
    }


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    mode = str(inputs.get("mode", "")).lower().strip()
    if mode == "indexer":
        return _indexer(inputs.get("fichiers"))
    if mode == "restaurer":
        return _restaurer(inputs.get("a_restaurer"), inputs.get("store"))
    raise ValueError("mode : attendu 'indexer' ou 'restaurer'")
