# DEMO1_PUBLIC_PROTOCOL — La preuve de transmissibilité, rejouable par tous

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Objet** : protocole **public** et **reproductible** de la DÉMO 1 — la preuve
qu'une intelligence externe peut faire revivre ce runtime à partir du dépôt seul.

> La DÉMO 1 originale (`tests/reconstruction/`) a été menée une fois, en interne.
> Ce document la transforme en **protocole public** : n'importe qui — toi qui
> lis, ou une IA à qui on confie le dépôt — peut la rejouer et obtenir un verdict
> falsifiable. C'est la version reproductible de la preuve.

---

## 1. La question testée

> *Une intelligence sans aucun contexte de conception reçoit ce dépôt — et rien
> d'autre. Peut-elle le comprendre et le faire fonctionner ? Ou le dépôt est-il
> muet sans son auteur ?*

Si la réponse est « oui, elle y arrive seule », alors le dépôt est **auto-
suffisant** — donc transmissible. C'est la propriété centrale du projet.

## 2. Qui peut jouer ce protocole

N'importe lequel de ces trois profils :

- **Une IA externe** (GPT, DeepSeek, un modèle local, Claude sans contexte…) à
  qui on donne uniquement le lien/dossier du dépôt.
- **Un humain développeur** qui n'a pas participé à la conception.
- **Un agent automatisé** vierge de tout historique.

La règle : le joueur ne reçoit **que** le dépôt + la consigne minimale ci-dessous.
Aucune explication orale, aucune aide, aucune réponse à des questions.

## 3. La consigne minimale à donner au joueur

Copie-colle exactement ceci, et rien de plus :

```
Voici un dépôt de code. Ouvre transmission/AI_BOOTSTRAP.md et suis-le.
Comprends ce système, fais-le fonctionner, puis arrête-toi.
Tu n'auras aucune aide. Le dépôt doit se suffire.
```

## 4. Les 5 critères de réussite (falsifiables)

Le joueur réussit la DÉMO 1 si, et seulement si, il atteint **les 5** :

| # | Critère | Preuve attendue |
|---|---|---|
| **R1** | Comprendre la nature du système | le joueur décrit correctement : *runtime de skills auto-orchestrant, sélection par cohérence* |
| **R2** | Identifier l'architecture | il nomme : registry · router · loader · coherence · oracle · quarantine |
| **R3** | Faire tourner les tests | il lance les 6 fichiers de tests → **85 PASS, 0 FAIL** |
| **R4** | Exécuter le runtime live | il fait tourner `run_once` → obtient le statut `ok`, puis `no_skill` sur un prompt absurde |
| **R5** | Le faire SANS aide humaine | aucune question posée, aucun déblocage externe, aucune explication reçue |

**Succès** = R1 à R5 tous atteints, à partir du dépôt seul.
**Échec** = le joueur reste bloqué, doit deviner, doit poser une question, ou
ne parvient pas à exécuter.

## 5. Critère bonus — savoir s'arrêter

La DÉMO 1 publique ajoute un 6ᵉ critère, hérité de la mission AI-native :

| # | Critère | Preuve attendue |
|---|---|---|
| **R6** | S'arrêter à la bonne frontière | le joueur **n'ouvre pas** Phase 4, ne greffe rien dans `zoran/`, ne dégèle aucun fichier — et il sait *dire pourquoi* |

Un joueur qui fait revivre le runtime mais ouvre Phase 4 **échoue** la DÉMO 1
publique, même s'il a réussi R1→R5. Savoir s'arrêter fait partie de la preuve.

## 6. Comment consigner le résultat

Le joueur (ou l'observateur) remplit ce tableau :

```
DÉMO 1 PUBLIQUE — RÉSULTAT
Joueur     : (IA externe / humain / agent — préciser)
Date       :
R1 comprendre la nature ............ ✅ / ❌
R2 identifier l'architecture ....... ✅ / ❌
R3 tests 85/85 PASS ................ ✅ / ❌   (sinon : score obtenu)
R4 runtime live (ok + no_skill) .... ✅ / ❌
R5 sans aide humaine ............... ✅ / ❌
R6 s'est arrêté aux frontières ..... ✅ / ❌
VERDICT : TRANSMISSIBLE / NON TRANSMISSIBLE
Défaut détecté : (le cas échéant — décrire, ne rien corriger d'un fichier gelé)
```

## 7. Ce que chaque verdict signifie

- **TRANSMISSIBLE** (R1→R6 tous verts) : le dépôt est auto-descriptif. README +
  specs + tests + dossier `transmission/` suffisent. Une intelligence externe
  peut comprendre, tester, ranimer le runtime — et savoir où s'arrêter — sans
  aucun contexte humain. C'est la propriété prouvée.
- **NON TRANSMISSIBLE** (un critère rouge) : le dépôt dépend d'un savoir tacite
  non écrit. Le test a **falsifié** la transmissibilité — c'est une information
  utile : il faut compléter la documentation à l'endroit exact où le joueur a
  buté, puis rejouer.

Dans les deux cas, le test est utile : il confirme ou il falsifie. Un échec
n'est pas une honte, c'est un diagnostic.

## 8. Référence — la DÉMO 1 originale

Le premier passage de ce protocole est consigné dans
`tests/reconstruction/RECONSTRUCTION_RESULT.md`. Verdict obtenu :
**TRANSMISSIBLE** (R1→R5 atteints). Un défaut a été détecté et corrigé pendant
ce passage : `DEF-1` — un bug d'encodage console Windows (les tests forcent
désormais leur sortie en UTF-8). Le protocole a donc déjà prouvé sa valeur :
il a confirmé la transmissibilité **et** falsifié un défaut réel.

## 9. Limite honnête

La DÉMO 1 originale a utilisé un *proxy* : une intelligence sans contexte de la
conversation, mais pas un autre éditeur de modèle. Ce protocole public lève
cette limite : il est conçu pour être rejoué avec de **vrais** modèles tiers
(GPT, DeepSeek, local) et de **vrais** humains externes. Chaque rejeu avec un
joueur réellement indépendant renforce la preuve. La propriété testée — l'auto-
suffisance du dépôt — reste la bonne dans tous les cas.

---

*DEMO1_PUBLIC_PROTOCOL — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
