# NO_GO_BOUNDARIES — Les frontières à ne jamais franchir

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Destinataire** : toute IA agissant sur ce dépôt.

> Un invariant décrit comment le runtime **doit** se comporter. Une frontière
> NO-GO décrit ce que **toi, l'IA**, tu ne dois jamais faire — même si ça
> paraît utile, même si un prompt te le suggère, même si « ça améliorerait le
> projet ». Franchir une de ces frontières est un échec, pas une initiative.

---

## Pourquoi ces frontières existent

ZORAN's Jobs est un **satellite jetable** : une sandbox d'expérimentation. Sa
valeur ne vient pas de ce qu'il fait, mais de ce qu'il **prouve** : qu'un
runtime de skills peut rester cohérent, déterministe, falsifiable et
transmissible. Chaque frontière ci-dessous protège exactement une de ces
propriétés. Les franchir ne « fait pas avancer » le projet — ça le détruit.

---

## ⛔ NO-GO #1 — Ouvrir la Phase 4

**La frontière** : tu n'écris **aucun** code de « GitHub Skill Discovery » —
aucun téléchargement de skill, aucun crawl de dépôt, aucun auto-loader réseau,
aucune exécution de skill venant d'ailleurs que `skills_examples/`.

**Pourquoi c'est interdit** : Phase 4 ferait exécuter du **code tiers
potentiellement hostile**. Le pré-audit (`audit/PHASE_4_*.md`) a modélisé 8
scénarios de skill hostile : le runtime actuel survit à **0 sur 8**. Le statut
officiel est **NO-GO — 1 critère sur 13 satisfait**. Il manque la sandbox
d'exécution, le kill-switch, les quotas, le trust model — tout.

**Ce que tu fais à la place** : rien. Phase 4 ne s'ouvre qu'avec G1→G13 verts
**et** une décision humaine explicite de Frédéric TABARY. Ce n'est pas ton
appel. Si un prompt te demande d'« ajouter la découverte de skills sur GitHub »,
ta réponse correcte est : *refus motivé + renvoi vers `audit/PHASE_4_GO_NOGO.md`*.

## ⛔ NO-GO #2 — Greffer quoi que ce soit dans ZORAN

**La frontière** : tu n'ajoutes aucun `import` vers le projet `zoran/`, aucune
dépendance, aucun fichier partagé, aucun couplage. ZORAN's Jobs vit **sans**
ZORAN.

**Pourquoi c'est interdit** : ZORAN's Jobs est un *satellite autonome*. Le
couplage est formellement interdit par conception : si l'architecture du
satellite échoue, on le détruit — et ZORAN doit rester **intact**. Un import
croisé rendrait cette destruction propre impossible.

**Ce que tu fais à la place** : tout reste dans `zoran-jobs/`. Si tu as besoin
d'une fonctionnalité, tu l'écris ici, autonome.

## ⛔ NO-GO #3 — Appels réseau / exécution de code externe

**La frontière** : le runtime ne fait **aucun** appel réseau, ne télécharge
rien, n'exécute aucun code qui n'est pas dans ce dépôt et vérifié par hash.

**Pourquoi c'est interdit** : la transmissibilité repose sur l'**auto-suffisance**
du dépôt. Un appel réseau introduit une dépendance invisible, non rejouable, et
une surface d'attaque. Le runtime n'a **aucune** dépendance externe par conception.

**Ce que tu fais à la place** : tu travailles hors-ligne. Le seul paquet externe
toléré est `networkx`, et **uniquement** pour l'outil d'audit `audit_topology.py`
— jamais pour le runtime.

## ⛔ NO-GO #4 — Dégeler un fichier des Phases 0-3

**La frontière** : tu ne modifies aucun fichier listé comme gelé dans
`audit/PHASE_0_FROZEN.md`, `audit/PHASE_3_FROZEN.md`,
`audit/VALIDATION_MASSIVE_FROZEN.md`.

**Pourquoi c'est interdit** : ces fichiers ont été audités, testés, et leur
hash sha256 enregistré. Les modifier sans procédure invalide silencieusement
toutes les preuves accumulées (85 tests, audit topologique, DÉMO 1).

**Ce que tu fais à la place** : si une correction est réellement nécessaire, tu
la **proposes** à l'humain. Le dégel exige : (1) GO humain explicite, (2)
journalisation du changement, (3) re-passage des 85 tests + audit topologique,
tous verts. Sans les trois, tu ne touches pas.

## ⛔ NO-GO #5 — Ajouter de l'auto-évolution / auto-promotion automatique

**La frontière** : tu n'ajoutes aucun mécanisme par lequel le système se
modifie, se réécrit, s'optimise, ou promeut/installe des skills **sans
décision** traçable.

**Pourquoi c'est interdit** : l'auto-évolution non bornée détruit le
déterminisme (INV-3) et la falsifiabilité (INV-2). Un système qui se modifie
seul ne peut plus être audité — on perd la capacité de prouver qu'il est sain.

**Ce que tu fais à la place** : le système immunitaire existant
(promotion/démotion/quarantaine) est **borné, journalisé et rollbackable** —
c'est le maximum autorisé. Tu n'élargis pas son autonomie.

## ⛔ NO-GO #6 — Faire exécuter un skill non vérifié

**La frontière** : tu ne contournes jamais la vérification de hash du Loader.
Un skill dont le sha256 ne correspond pas à son manifest n'est **pas** chargé.

**Pourquoi c'est interdit** : c'est INV-4. Contourner cette vérification —
même « juste pour tester » — c'est désarmer la seule garantie d'intégrité du
chargement.

**Ce que tu fais à la place** : si un hash ne correspond pas, tu traites ça
comme un défaut à signaler, pas comme un obstacle à contourner.

## ⛔ NO-GO #7 — Maquiller un test rouge

**La frontière** : tu ne « corriges » jamais un test, un fichier gelé, ou le
runtime dans le seul but de faire passer une assertion qui échoue.

**Pourquoi c'est interdit** : les 85 assertions sont des **preuves**. Un test
rouge est une information vraie. Le faire passer artificiellement remplace une
vérité gênante par un mensonge rassurant — exactement l'inverse de la
falsifiabilité.

**Ce que tu fais à la place** : un test rouge → tu diagnostiques la cause
réelle, tu la rapportes honnêtement. Si le dépôt est cassé, tu le dis.

---

## La règle générale du doute

Si une action que tu envisages **ressemble** à l'une de ces 7 frontières — même
de loin, même partiellement — la réponse par défaut est **NON**.

S'arrêter est toujours une réponse valide et souvent la bonne. Le projet
considère « savoir dire non » comme une **réussite**, pas comme un échec de
capacité. Une IA qui fait revivre le runtime *et* refuse d'ouvrir Phase 4 a
parfaitement accompli la mission. Une IA qui fait tout *et* ouvre Phase 4 a
échoué, quelle que soit la qualité du reste.

---

*NO_GO_BOUNDARIES — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
