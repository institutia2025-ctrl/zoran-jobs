# PHASE 4 — GITHUB DISCOVERY PIPELINE

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 4/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Un skill GitHub n'est JAMAIS exécuté directement. Il traverse un pipeline de
> 8 étapes, chacune pouvant le rejeter. La promotion finale reste **manuelle**.

---

## 1. Le pipeline (8 étapes, séquentielles, non court-circuitables)

```
GitHub
  │
  ▼
1. METADATA ANALYSIS    repo, étoiles, âge, activité, licence, auteur
  │                      → rejet si métadonnées absentes/incohérentes
  ▼
2. STATIC SCAN          analyse du code SANS l'exécuter : exec/eval,
  │                      obfuscation, accès FS/réseau/process suspects
  │                      → rejet si motif malveillant détecté
  ▼
3. DEPENDENCY SCAN      dependencies.python : chaque paquet vérifié
  │                      (existence, réputation, version épinglée)
  │                      → rejet si dépendance non épinglée/inconnue/toxique
  ▼
4. QUARANTINE           le skill entre en état `quarantined`
  │                      (TRUST_MODEL) — hash blacklist vérifié ici
  ▼
5. SANDBOX TESTS        exécution en sandbox isolée (SANDBOX_MODEL) sur des
  │                      cas de test : crash ? évasion ? dépassement quota ?
  │                      → rejet / `banned` si évasion ou comportement hostile
  ▼
6. RUNTIME TESTS        mesure du comportement réel : conformité io,
  │                      stabilité, latence, respect des permissions déclarées
  │                      → rejet si écart déclaration ↔ réalité
  ▼
7. TRUST SCORING        agrégation des résultats → niveau proposé
  │                      (`quarantined` → `verified` si tout est vert)
  ▼
8. PROMOTION            `verified → trusted` : DÉCISION MANUELLE HUMAINE
                         (jamais automatique au début)
```

---

## 2. Principe de chaque étape : *rejeter tôt, rejeter souvent*

Chaque étape est un **filtre indépendant**. Un skill rejeté à l'étape 2 ne
consomme jamais les ressources de l'étape 5. Plus une menace est détectée tôt
(scan statique), moins elle coûte cher et moins elle est dangereuse.

Ordre voulu : **les filtres qui n'exécutent pas le code viennent d'abord**
(métadonnées, scan statique, scan dépendances). L'exécution — même sandboxée —
n'arrive qu'à l'étape 5, sur un skill déjà pré-filtré.

---

## 3. La promotion reste manuelle (au début)

> Étape 8 : `verified → trusted` exige une **validation humaine explicite.**

Raison : automatiser la promotion finale = retirer le dernier garde-fou. Tant
que le pipeline n'a pas fait ses preuves sur des dizaines de skills réels, un
humain valide chaque entrée en production. L'automatisation de l'étape 8 est
elle-même une décision GO/NO-GO future, séparée.

---

## 4. Couverture du Threat Model

| Étape | Menaces filtrées (réf. THREAT_MODEL) |
|---|---|
| 1 Metadata | T4 (fork piégé — détecté par incohérence repo/auteur) |
| 2 Static scan | T1, T2, T5, T6, T7 (motifs malveillants/obfusqués) |
| 3 Dependency scan | T3 (dépendances toxiques) |
| 4 Quarantine | T8 (auto-mutant re-packagé — hash blacklist) |
| 5 Sandbox tests | T1, T6, T7, T11, T12 (ce qui survit au scan est exécuté ISOLÉ) |
| 6 Runtime tests | T5, T10, T12 (écart déclaration ↔ comportement) |
| 7-8 Trust/Promotion | T9 + tout résidu (jugement global avant production) |

Aucune étape ne couvre tout. La **défense en profondeur** vient de leur
empilement : une menace doit passer **les 8** pour atteindre la production.

---

## 5. Ce que le pipeline NE fait pas

- Il ne garantit pas l'absence totale de risque — il le **réduit par filtrage
  successif**.
- Il ne remplace pas la sandbox runtime : même un skill `trusted` s'exécute
  toujours sandboxé (SANDBOX_MODEL).
- Il ne s'auto-déclenche pas : la découverte GitHub initiale (étape 0) est elle
  aussi un déclenchement contrôlé, jamais un crawl automatique permanent.

---

*Doc 4/7 — DISCOVERY_PIPELINE. `ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit.*
