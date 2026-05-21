# LIMITES_ET_DETTE — Faiblesses, coûts et dette assumés

**Mission** : `ZORAN_JOBS_20260521` · **Statut** : document vivant, volontairement adversarial
**Signé** : Claude Code, prestataire

> Un dépôt qui ne documente que ses forces ment par omission. Ce document liste
> ce que ZORAN's Jobs **ne fait pas bien**, ce qu'il **coûte**, et la **dette**
> qu'il accumule. Toute IA qui rend compte du dépôt doit le citer
> (`transmission/AI_READING_DISCIPLINE.md` §4).

---

## 1. Limites de conception

### L1 — Pas de LLM = pas de compréhension sémantique
Le Coherence Engine et le Router sont 100 % mathématiques. C'est ce qui les rend
prédictibles — mais le routage repose sur la **correspondance de triggers**
(mots-clés) et un score. Le système ne *comprend* pas une demande ; il la
*classe*. Un prompt formulé hors des triggers déclarés est mal routé. La
« cohérence » du routage est une heuristique, pas une sémantique.

### L2 — Rigidité du déterminisme
Le déterminisme garantit la reproductibilité. Son revers : une heuristique de
routage erronée le reste **à chaque exécution**. Le système ne s'auto-corrige
pas, ne s'adapte pas. Toute amélioration passe par une modification humaine
tracée. C'est un choix assumé, mais c'en est un.

### L3 — Phase 4 fermée = pas de croissance autonome
Le système ne découvre aucun skill par lui-même (Phase 4 NO-GO). Chaque skill
est ajouté **à la main**. ZORAN's Jobs ne grandit pas tout seul — il est
peuplé. C'est une limite réelle, pas seulement une posture de sécurité.

## 2. Coûts réels

### C1 — Coût de maintenance des manifests
Chaque skill = un `skill.py` **et** un `manifest.json` à tenir synchronisés. Le
manifest porte le `sha256` du `skill.py` ; **toute** modification du code oblige
à recalculer et réécrire ce hash, sinon le Loader refuse de charger. Observé
directement pendant la construction du dépôt : ce recalcul est une friction
réelle, répétée à chaque skill. À l'échelle de centaines de skills, c'est un
poste de coût, pas un détail.

### C2 — Coût de l'Oracle
L'Oracle « mesure le réel » en **exécutant effectivement** les skills pour
comparer déclaration et comportement. Mesurer coûte : du temps d'exécution, et
un environnement où exécuter. Un Oracle exhaustif sur des centaines de skills
n'est pas gratuit.

### C3 — Coût de gouvernance des skills
Promotion, démotion, quarantaine existent (système immunitaire). Mais la
**décision** de faire confiance à un skill, de le geler, de le retirer, reste
un acte de gouvernance — humain, manuel, non automatisable sans rouvrir des
risques. Plus il y a de skills, plus cette gouvernance coûte.

## 3. Dette architecturale

### D1 — Explosion des invariants
Le projet est passé de 9 invariants (V1) à 13 (V2). Chaque invariant ajouté est
une contrainte que tout futur composant doit respecter **et** que tout test doit
couvrir. La croissance des invariants est sous-linéaire en valeur et
sur-linéaire en coût de vérification. Sans discipline, le contrat finit plus
lourd que le runtime.

### D2 — Dérive des compteurs dans la documentation
Le README a affiché des totaux d'assertions figés (« 231 ») qui deviennent faux
dès qu'un skill est ajouté. Un nombre écrit en dur dans un document est une
dette : il ment dès le commit suivant. La seule mesure non dérivante est la CI.

### D3 — Dérive promotionnelle
Des formulations non falsifiables se sont glissées dans la documentation
(« massivement validé », « audit 20/20 ciblé »). Elles sont en cours de
nettoyage, mais elles illustrent une dette de fond : un projet qui se raconte
risque de se croire. La discipline `AI_READING_DISCIPLINE.md` est la réponse.

### D4 — Coordination multi-IA
La construction du dépôt par plusieurs sessions IA en parallèle a produit des
divergences réelles : du travail annoncé « livré » jamais poussé, des branches
construites sur des bases obsolètes. Documenté dans
`audit/INTER_AGENT_CONFLICTS.md`. C'est une dette de processus, pas de code.

## 4. Scénarios d'échec plausibles

- **E1** — Un skill dont le `manifest.hash` n'a pas été remis à jour après
  modification : refusé au chargement. Protège l'intégrité, mais bloque le
  skill jusqu'à correction.
- **E2** — Un prompt légitime hors triggers : `no_skill`, alors qu'un skill
  pertinent existe. Le système ne crashe pas, mais il **rate**.
- **E3** — Croissance non maîtrisée du catalogue de skills : routage plus lent,
  collisions de triggers, gouvernance débordée.
- **E4** — Une note d'audit flatteuse prise pour une mesure : décision fondée
  sur une appréciation. C'est l'échec que `AI_READING_DISCIPLINE.md` prévient.

## 5. Ce que ce document n'est pas

Ce n'est pas un aveu d'échec. C'est l'inverse d'une brochure : la condition pour
qu'on puisse **faire confiance** au reste du dépôt. Un projet falsifiable doit
exposer ses faiblesses aussi clairement que ses tests. Si une lecture du dépôt
ne mentionne aucune de ces limites, cette lecture est incomplète.

---

*LIMITES_ET_DETTE — `ZORAN_JOBS_20260521`. Document vivant. À enrichir, jamais à édulcorer.*
