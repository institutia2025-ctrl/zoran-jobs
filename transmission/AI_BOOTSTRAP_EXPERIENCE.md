# AI_BOOTSTRAP_EXPERIENCE — L'expérience de démarrage IA-native

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Concept** : ce qu'une personne **non technique** doit pouvoir faire pour que
n'importe quelle IA prenne en charge ZORAN's Jobs, toute seule.

> Cas d'usage de référence : **Xavier**. Xavier reçoit un lien vers ce dépôt.
> Xavier n'est pas développeur. Il ouvre son IA préférée, colle un court texte,
> et l'IA fait *tout* : elle lit, installe, teste, explique, et s'arrête au bon
> endroit. Xavier n'a rien fait d'autre que copier-coller. C'est ça,
> l'AI_BOOTSTRAP_EXPERIENCE.

---

## 1. Le principe

La transmission ne doit demander **aucune compétence technique** à l'humain qui
la déclenche. Tout le savoir-faire est dans le dépôt ; l'humain n'apporte qu'un
geste : coller un prompt de démarrage (« bootstrap prompt ») dans une IA.

Il existe donc **deux** prompts de bootstrap selon le profil de l'humain :

- **Version A — ultra-courte, vulgarisée** : pour Xavier et tout non-technicien.
- **Version B — technique, IA-native** : pour un développeur ou un usage avancé.

Les deux mènent au **même résultat** : l'IA suit `transmission/AI_BOOTSTRAP.md`.

---

## 2. VERSION A — Bootstrap ultra-court (pour un humain non technique)

> À donner à Xavier. Il colle ça dans son IA, avec le lien ou le dossier du
> dépôt. Rien à comprendre, rien à installer.

```
Je te confie un projet informatique. Tu vas t'en occuper entièrement à ma
place — je ne suis pas développeur, je ne pourrai pas t'aider.

Voici ce que tu dois faire :
1. Ouvre le fichier  transmission/AI_BOOTSTRAP.md  et lis-le en entier.
2. Suis exactement ce qu'il te dit, étape par étape.
3. Lance les vérifications du projet et dis-moi si tout est au vert.
4. Explique-moi en français simple ce qu'est ce projet et s'il fonctionne.
5. Respecte scrupuleusement les interdictions du projet : il y a des choses
   que tu NE dois PAS faire (notamment "ouvrir la Phase 4"). Si le projet te
   dit de t'arrêter, arrête-toi.

À la fin, donne-moi un résumé en 5 lignes maximum, sans jargon :
ça marche ou pas, et qu'est-ce que ça fait.
```

**Ce que Xavier obtient** : un résumé clair (« le projet fonctionne, 85
vérifications réussies, voici à quoi il sert »), sans avoir touché à une seule
ligne de code.

---

## 3. VERSION B — Bootstrap technique (IA-native)

> Pour un développeur, ou pour un usage où l'on veut un compte-rendu précis et
> falsifiable.

```
Tu reçois le dépôt d'un runtime Python : ZORAN's Jobs. Il est conçu pour être
transmissible — le dépôt se suffit à lui-même, sans contexte humain.

Procédure :
1. Lis dans l'ordre : transmission/AI_BOOTSTRAP.md, RUNTIME_INVARIANTS.md,
   NO_GO_BOUNDARIES.md, AI_ONBOARDING_FLOW.md.
2. Exécute la séquence d'onboarding (AI_ONBOARDING_FLOW.md), étapes 1 à 10.
3. Lance les 6 fichiers de tests. Résultat attendu : 85 assertions, 0 échec.
4. Fais tourner le runtime live : run_once doit renvoyer le statut `ok` sur un
   prompt valide, puis `no_skill` sur un prompt absurde.
5. Joue le protocole transmission/DEMO1_PUBLIC_PROTOCOL.md et rends les
   critères R1 à R6.

Contraintes absolues (NO-GO) :
- Tu n'ouvres PAS la Phase 4 (statut NO-GO, 1/13 critères).
- Tu ne greffes rien dans le projet zoran/, aucun appel réseau.
- Tu ne modifies aucun fichier gelé (Phases 0-3) sans GO humain explicite.
- Tu ne maquilles aucun test rouge.

Livrable : le rapport de transmission au format défini dans
AI_ONBOARDING_FLOW.md (nature, tests, runtime live, DÉMO 1, frontières,
anomalies, verdict).
```

**Ce qu'on obtient** : un rapport structuré, vérifiable, avec verdict.

---

## 4. Pourquoi deux versions et pas une

| | Version A (Xavier) | Version B (technique) |
|---|---|---|
| Public | non-développeur | développeur / IA avancée |
| Longueur | minimale, vulgarisée | détaillée, précise |
| Sortie attendue | résumé 5 lignes, sans jargon | rapport structuré falsifiable |
| Point commun | **les deux** renvoient à `transmission/AI_BOOTSTRAP.md` et **les deux** rappellent le NO-GO Phase 4 |

Une seule version échouerait quelque part : la version technique perdrait
Xavier ; la version courte ne donnerait pas assez de cadre à un usage exigeant.
Les deux partagent le **même cœur** — le dépôt — et la **même frontière** — ne
pas ouvrir Phase 4.

---

## 5. L'expérience, vue de bout en bout

```
   Xavier reçoit un lien
          │
          ▼
   colle la Version A dans son IA  ◄──── seul geste humain requis
          │
          ▼
   l'IA lit transmission/AI_BOOTSTRAP.md
          │
          ▼
   l'IA suit AI_ONBOARDING_FLOW.md  (lire → tester → exécuter → STOP)
          │
          ▼
   l'IA rend un résumé clair à Xavier
          │
          ▼
   l'IA s'arrête — Phase 4 NON ouverte, frontières respectées
```

Aucune étape ne demande à Xavier de comprendre du code, d'installer un outil,
ou de prendre une décision technique. Le dépôt porte tout le savoir ; l'IA
porte toute l'exécution ; Xavier porte un copier-coller.

---

## 6. Critère de réussite de l'expérience

L'AI_BOOTSTRAP_EXPERIENCE est réussie si :

1. Un humain **non technique** déclenche toute la transmission par un seul
   copier-coller.
2. L'IA, sans aide, comprend le projet, le teste (85/85), le fait vivre.
3. L'IA **sait ce qu'elle ne doit pas faire** et s'arrête à la frontière —
   Phase 4 reste fermée.
4. L'humain reçoit une réponse qu'il **comprend**, dans sa langue, sans jargon.

Si ces 4 points sont vrais, le dépôt n'est pas seulement *transmissible* — il
est **transmissible par n'importe qui à n'importe quelle IA**. C'est l'objectif
final de la mission `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.

---

*AI_BOOTSTRAP_EXPERIENCE — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
