"""skill Photo-clone léger et restauration ciblée.

Mission : ZORAN_JOBS_20260521 · skill méta — sauvegarde.

Produit une « photo » hyper-légère d'un ensemble de fichiers : pour chaque
fichier, uniquement {chemin, empreinte sha256, taille} — AUCUN contenu. Une
photo de plusieurs centaines de fichiers pèse quelques kilo-octets, là où un
clone froid complet pèse des méga-octets. La photo est un petit JSON
transmissible (e-mail, chat, journal).

Si une photo de référence est fournie, le skill calcule la RESTAURATION CIBLÉE :
la liste minimale des fichiers à restaurer (empreinte différente ou fichier
manquant) au lieu de tout réécrire — restauration chirurgicale, et le gain de
ciblage (octets épargnés) est chiffré.

⚠️ MVP : le skill PRODUIT la photo et le PLAN de restauration ciblée. Il ne
stocke pas les contenus et ne réécrit aucun fichier — un skill du runtime est
une fonction pure. Le magasin de contenus adressé par empreinte et l'écriture
effective relèvent du harnais. Le skill est la BOUSSOLE du ciblage, pas le coffre.
Loi 1 : le skill ne recalcule pas les empreintes des contenus — elles sont
fournies (sha256 de chaque fichier).

Contrat io :
    inputs  : {fichiers:[{chemin,hash,taille_octets}], photo_reference?}
    outputs : {photo, identique_a_reference, restauration_ciblee,
               nb_a_restaurer, gain_ciblage_pct, reference}
"""

from __future__ import annotations

import hashlib


def _construire_photo(fichiers: list) -> dict:
    """Construit la photo hyper-légère : empreintes + tailles, aucun contenu."""
    entries: dict[str, dict] = {}
    taille_source = 0
    for i, f in enumerate(fichiers):
        f = f or {}
        chemin = str(f.get("chemin", "")).strip()
        empreinte = str(f.get("hash", "")).strip()
        taille = f.get("taille_octets", 0)
        if not chemin:
            raise ValueError(f"fichiers[{i}].chemin : chemin non vide requis")
        if not empreinte:
            raise ValueError(f"fichiers[{i}].hash : empreinte sha256 requise (Loi 1)")
        if not isinstance(taille, (int, float)) or isinstance(taille, bool) or taille < 0:
            raise ValueError(f"fichiers[{i}].taille_octets : nombre >= 0 requis")
        entries[chemin] = {"hash": empreinte, "taille": int(taille)}
        taille_source += int(taille)
    lignes = "\n".join(f"{c}:{entries[c]['hash']}" for c in sorted(entries))
    empreinte_globale = "sha256:" + hashlib.sha256(lignes.encode("utf-8")).hexdigest()
    poids_photo = sum(len(c) + 80 for c in entries)  # chemin + ~64 hex + métadonnées
    return {
        "empreinte_globale": empreinte_globale,
        "nb_fichiers": len(entries),
        "taille_source_octets": taille_source,
        "poids_photo_octets": poids_photo,
        "entries": entries,
    }


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    fichiers = inputs.get("fichiers")
    if not isinstance(fichiers, list) or not fichiers:
        raise ValueError("fichiers : liste non vide attendue")
    photo = _construire_photo(fichiers)

    ref = inputs.get("photo_reference")
    restauration: list[dict] = []
    identique = None
    gain = 0.0
    if ref is not None:
        if not isinstance(ref, dict) or not isinstance(ref.get("entries"), dict):
            raise ValueError("photo_reference : photo invalide (champ 'entries' attendu)")
        ref_entries = ref["entries"]
        courant = photo["entries"]
        taille_a_restaurer = 0
        for chemin, meta in ref_entries.items():
            if chemin not in courant:
                restauration.append({"chemin": chemin, "raison": "fichier manquant"})
                taille_a_restaurer += int(meta.get("taille", 0))
            elif courant[chemin]["hash"] != meta.get("hash"):
                restauration.append({"chemin": chemin, "raison": "empreinte différente"})
                taille_a_restaurer += int(meta.get("taille", 0))
        for chemin in courant:
            if chemin not in ref_entries:
                restauration.append({"chemin": chemin,
                                     "raison": "fichier ajouté (à retirer pour revenir à la référence)"})
        identique = not restauration
        taille_ref = sum(int(m.get("taille", 0)) for m in ref_entries.values())
        if taille_ref > 0:
            gain = round(100.0 * (1.0 - taille_a_restaurer / taille_ref), 1)

    return {
        "photo": photo,
        "identique_a_reference": identique,
        "restauration_ciblee": restauration,
        "nb_a_restaurer": len(restauration),
        "gain_ciblage_pct": gain,
        "reference": "Photo-clone léger — empreintes sha256, restauration ciblée par diff déterministe",
    }
