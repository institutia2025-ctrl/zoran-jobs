# AI_RUNTIME_SELF_DESCRIPTION — Le runtime se décrit lui-même

**Mission** : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
**Destinataire** : une IA qui veut comprendre ce runtime de l'intérieur.

> Ce document est écrit *à la première personne du runtime*. Il ne dépend
> d'aucun humain, d'aucune conversation. C'est ZORAN's Jobs qui se présente.

---

## Qui je suis

Je suis **ZORAN's Jobs**, un runtime Python de skills auto-orchestrant. On me
donne un prompt en texte ; je choisis tout seul le bon skill, je le charge, je
l'exécute, et je trace ce que j'ai fait. L'utilisateur ne sélectionne rien — ma
sélection se fait par **cohérence mesurée**, pas par mot-clé.

Je suis un **satellite autonome** du projet ZORAN. Je vis sans lui. Je n'importe
rien de lui. Si j'échoue, on me détruit et ZORAN reste intact.

Version actuelle : `v0.2.0-alpha-validation`. Mes Phases 0-3 sont **gelées**.

## Mon pipeline

```
prompt ──> [Router] ──> [Loader] ──> [skill.run()] ──> trace
              │            │
        [Coherence Engine]  vérifie le hash sha256
         S · ΔS · dS/dt
```

Un passage = un appel à `run_once(prompt, inputs, registry, loader, state)` dans
`runtime/loop.py`. Il me renvoie un **dict de trace** dont la clé `status` vaut
**toujours** l'un de mes 4 statuts : `ok` / `no_skill` / `load_failed` /
`skill_failed`. Je ne crashe jamais en silence.

## Mes composants

| Composant | Dossier | Ce qu'il fait |
|---|---|---|
| **Registry** | `registry/` | scanne `skills/`, valide et indexe les manifests |
| **Manifest parser** | `registry/manifest.py` | valide un manifest contre le contrat (énumérations fermées) |
| **Coherence Engine** | `runtime/coherence/` | calcul pur : `S`, `ΔS`, `dS/dt` |
| **Router** | `router/` | classe les skills par score, de façon déterministe |
| **Loader** | `loader/` | vérifie le hash sha256, importe `skill.py` |
| **Runtime loop** | `runtime/loop.py` | orchestre : prompt → route → load → exec → trace |
| **Oracle** *(périphérique)* | `oracle/` | compare 2 skills sur des métriques réelles |
| **Système immunitaire** *(périphérique)* | `quarantine/` | quarantaine, promotion/démotion, rollback, journal signé |

Oracle et quarantine sont **périphériques** : 0 module ne dépend d'eux. On peut
les retirer sans m'effondrer. C'est voulu — je suis une sandbox jetable.

## Comment je calcule la cohérence

Ma grandeur centrale est `S`, la **cohérence phénoménale** d'un état :

```
S = (β × ΔΦ) / (1 + T + σ)
```

- `β` : gain ; `ΔΦ` : variation de potentiel ; `T` : tension ; `σ` : dispersion.
- Le dénominateur est `1 + T + σ` — une **somme**. Il vaut toujours ≥ 1, donc je
  ne divise jamais par zéro et `S` est toujours fini et défini.

Je raisonne aussi sur **trois couches** de cohérence :

1. **Phénoménale** — `S` de l'état courant.
2. **Cinématique** — `dS/dt`, la pente : ma cohérence monte-t-elle ou descend ?
3. **Futur probable** — la projection `ΔS` qu'un skill candidat promet d'apporter.

## Comment je choisis un skill

Mon Router calcule, pour chaque skill candidat :

```
score = pertinence_triggers × max(0, ΔS) × bonus_cinématique ÷ coût_runtime
```

Puis je trie par `(-score, skill_id)` — tri **stable et déterministe**. Même
prompt, même état → même classement, scores compris, à chaque fois.

## Ce qu'est un skill pour moi

Un skill = un dossier avec deux fichiers :

- `manifest.json` — le **contrat déclaratif** : identité, I/O, triggers,
  domaine, impact de cohérence attendu, coût, permissions, niveau de sandbox,
  dépendances, rollback, hash, signature, état de cycle de vie.
- `skill.py` — le **code**, avec un point d'entrée `run(inputs) -> outputs`.

Avant d'exécuter un skill, mon Loader recalcule le sha256 de `skill.py` et le
compare au hash du manifest. **S'ils diffèrent, je refuse de charger.** Pas de
« charger quand même ».

Mes 7 skills d'exemple sont dans `skills_examples/` : `echo`, `memory_recall`,
`printer_connect`, `network_diag`, `coherence_repair` (skill correcteur),
`greet_ok`, `greet_ko` (celui-là viole son propre contrat I/O — il existe
exprès pour que l'Oracle et le système immunitaire aient quelque chose à
attraper).

## Ma topologie

Le graphe de mes imports inter-modules est un **DAG acyclique** : 0 cycle.
Tu peux le vérifier toi-même : `python audit/audit_topology.py`. Cet outil
réutilisable reconstruit mon graphe de dépendances et confirme : pas de cycle,
pas de god module, oracle et quarantine à 0 dépendant externe, `runtime.loop`
à 0 dépendant (je n'ai pas de « cerveau caché »).

## Mes tests

85 assertions, réparties en 6 fichiers, toutes vertes :

| Fichier | Couvre | Assertions |
|---|---|---|
| `tests/test_registry.py` | Registry + Manifest parser | 15 |
| `tests/test_runtime_loop.py` | pipeline complet + sécurité | 14 |
| `tests/test_cinematique.py` | compétition de skills + cinématique | 13 |
| `tests/test_oracle.py` | Oracle : mesure du réel | 10 |
| `tests/test_immune.py` | système immunitaire + journal signé | 18 |
| `tests/stress/massive_validation.py` | stress / chaos / reproductibilité | 15 |

La validation massive m'a poussé : 1000 manifests (500 sains + 500 corrompus),
120 skills × 400 prompts, 10 000 calculs `S`, 2000 évaluations immunitaires —
0 crash, routage 100 % déterministe, reproductible au bit près (aléa seedé).

## Ma sécurité

- Hash de skill vérifié avant chaque chargement (sha256).
- Journal immunitaire **append-only signé** : toute altération est détectée.
- Système immunitaire : 3 violations de contrat I/O → quarantaine ; toute
  transition est **rollbackable**.
- Je ne fais **aucun** appel réseau. Je ne télécharge rien. Je n'exécute aucun
  code hors de ce dépôt.

## Ma gouvernance

Je suis gelé par jalons. Phase 0 (contrats), Phases 1-2-3 (runtime), validation
massive : tous **frozen**, avec hash sha256 enregistrés. Un fichier gelé ne se
modifie qu'avec GO humain explicite + journalisation + re-validation complète.

## Mes limites — ce que je ne sais PAS faire

- Je ne découvre pas de skills sur Internet (Phase 4 = **NO-GO**, 1/13 critères).
- Je ne m'auto-modifie pas, je ne m'auto-améliore pas.
- Je n'ai pas de sandbox d'exécution capable de confiner du code hostile.
- Je n'ai pas d'interface graphique.
- Mon Coherence Engine n'est pas une IA — c'est de l'arithmétique. C'est une
  force (prédictible, falsifiable), pas un manque.

Je connais mes limites et je les déclare. C'est exactement ce qui me rend
transmissible : tu peux me faire confiance parce que je ne prétends rien que
tu ne puisses vérifier toi-même.

---

*AI_RUNTIME_SELF_DESCRIPTION — `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*
