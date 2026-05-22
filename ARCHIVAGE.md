# ARCHIVAGE — Référence citable et antériorité, sans compte tiers

> Une référence qui dépend d'un compte que l'on peut perdre est fragile.
> Ce document décrit comment ZORAN's Jobs établit une référence permanente et
> citable **sans dépendre d'aucun compte tiers** — Zenodo compris.

---

## 1. L'antériorité est déjà établie

Git est un arbre de Merkle : chaque commit est un hash de son contenu et de son
parent. Poussé sur GitHub, chaque commit porte une date enregistrée côté
serveur. L'historique du dépôt **est** la preuve d'antériorité — cryptographique
et horodatée. Il n'y a rien à « frapper » pour cela : c'est déjà fait, à chaque
push.

## 2. Snapshot citable — GitHub Release

Une release GitHub (tag de version) est un instantané permanent et citable :
`https://github.com/institutia2025-ctrl/zoran-jobs/releases/tag/<tag>`.
Gratuit, sous notre seul contrôle, sans tiers à qui demander l'autorisation.

## 3. Archivage pérenne — Software Heritage

[archive.softwareheritage.org](https://archive.softwareheritage.org) archive
n'importe quel dépôt public et émet un **SWHID** — identifiant permanent,
adressé par contenu, reconnu académiquement. **Aucun compte requis** : « Save
code now », coller l'URL du dépôt, valider. C'est le remplaçant réel d'un DOI
Zenodo, sans le point de défaillance « compte ».

## 4. Citation — `CITATION.cff`

`CITATION.cff` fournit les métadonnées de citation (encart « Cite this
repository » de GitHub). Il ne dépend d'**aucun** DOI : une citation reste
valide avec l'URL du dépôt et le tag de release.

## 5. Honnêteté

Tant qu'une release n'est pas publiée et que le dépôt n'est pas soumis à
Software Heritage, ces identifiants **n'existent pas** — seul l'historique git
fait foi. Ne citer un SWHID ou une release que lorsqu'ils existent réellement
(Loi 1 : aucun identifiant n'est supposé).

## Pourquoi plus Zenodo

Zenodo reste un service valable, mais il lie la référence à un **compte**. Un
compte fermé, et la référence n'est plus gérable. La leçon est cohérente avec la
philosophie du dépôt : préférer l'**adressage par contenu** — déjà incarné par
le skill `zoran_magasin_contenu_adressable` et par le hash sha256 de chaque
skill — à la dépendance envers une autorité externe.
