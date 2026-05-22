# ZENODO — Figer une référence citable (DOI)

Ce dépôt est **prêt à être archivé sur Zenodo** : un dépôt archivé reçoit un
**DOI** — un identifiant permanent et citable, qui fige l'antériorité.

## Fichiers de métadonnées (déjà en place)

| Fichier | Rôle |
|---|---|
| `CITATION.cff` | métadonnées de citation — GitHub affiche un encart « Cite this repository » |
| `.zenodo.json` | métadonnées lues par Zenodo lors de l'archivage |

Ni l'un ni l'autre ne fixe de numéro de version : Zenodo le **dérive du tag de
la release** GitHub. C'est volontaire — pas de version à maintenir à la main.

## Frapper le DOI — 3 étapes (réservées au propriétaire du dépôt)

Ces étapes exigent le **compte Zenodo** du propriétaire et une autorisation
OAuth Zenodo↔GitHub. Elles ne peuvent pas être faites par un agent.

1. **Activer l'intégration.** Sur [zenodo.org](https://zenodo.org), se
   connecter avec GitHub, ouvrir *GitHub* dans les réglages du compte, et
   basculer l'interrupteur sur **ON** pour `institutia2025-ctrl/zoran-jobs`.
2. **Créer une release GitHub.** Publier une release avec un tag de version
   (ex. `v0.10.0`). Zenodo détecte la release, archive le code et **frappe le
   DOI** automatiquement.
3. **Afficher le DOI.** Zenodo fournit un badge. L'ajouter à `README.md` /
   `README.en.md`, et renseigner le champ `doi:` de `CITATION.cff`.

> ⚠️ L'intégration (étape 1) doit être active **avant** la release : Zenodo
> n'archive que les releases créées après l'activation.

## Honnêteté

Tant que les étapes ci-dessus ne sont pas faites, **le dépôt n'a pas de DOI** —
seulement les fichiers de métadonnées qui le rendent prêt à en recevoir un. Ne
pas citer de DOI tant que Zenodo ne l'a pas réellement émis (Loi 1 : aucun
identifiant n'est supposé).
