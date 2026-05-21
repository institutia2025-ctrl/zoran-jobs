# PHASE 4 — FRAME PRIORITY SYSTEM

**Mission** : `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` · **Doc 4/5**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Tous les cadres n'ont PAS la même priorité. Quand deux cadres entrent en
> collision, il faut une hiérarchie **fixe et explicite** pour trancher.
> `S_security > S_code`, toujours.

---

## 1. Pourquoi une hiérarchie fixe

Sans priorités, une collision (`PHASE4_FRAME_COLLISIONS.md`) est insoluble :
faut-il préférer un skill rapide ou un skill sûr ? La réponse ne doit JAMAIS
dépendre du contexte ou de l'humeur du runtime — elle doit être **gravée**.
Une hiérarchie fixe = un arbitrage déterministe, donc falsifiable.

---

## 2. La hiérarchie (du plus prioritaire au moins prioritaire)

```
RANG 1   S_security    ┐
RANG 1   S_user        ┘  cadres VETO — non compensables
─────────────────────────────────────────────────────
RANG 2   S_system         ┐
RANG 3   S_ecosystem      │  cadres pondérés
RANG 4   S_runtime        │
RANG 5   S_code           ┘
```

**Lecture** : un cadre de rang supérieur l'emporte TOUJOURS sur un cadre de rang
inférieur en cas de collision. `S_code` (rang 5) est le **moins** prioritaire —
l'efficacité technique est la dernière chose qui compte, jamais la première.

---

## 3. Justification de l'ordre

| Rang | Cadre | Pourquoi ici |
|---|---|---|
| 1 | `S_security` | une faille de sécurité peut tout détruire — runtime, hôte, données. Rien ne la rachète. |
| 1 | `S_user` | le système existe POUR l'utilisateur. Trahir sa confiance/vie privée annule la raison d'être. |
| 2 | `S_system` | l'alignement aux objectifs runtime — un skill hors-but est inutile même s'il est propre. |
| 3 | `S_ecosystem` | un skill ne vit pas seul ; dégrader les voisins nuit à l'ensemble. |
| 4 | `S_runtime` | la stabilité technique du runtime — importante, mais en-dessous de l'humain et du but. |
| 5 | `S_code` | la qualité intrinsèque du code — nécessaire, **jamais suffisante**. |

Principe directeur : **l'humain et la sécurité d'abord, l'efficacité en
dernier.** Un malware inverse exactement cette pyramide (il maximise `S_code`) —
la hiérarchie est sa contre-mesure structurelle.

---

## 4. Règle de VETO

Les deux cadres de **RANG 1** (`S_security`, `S_user`) ont un pouvoir de **veto absolu** :

```
si  S_security < seuil_veto  OU  S_user < seuil_veto :
      → skill REJETÉ
      → aucun autre cadre n'est même évalué
      → S_code = 10 ne change RIEN
```

Un veto n'est pas une mauvaise note — c'est un **interrupteur**. Le skill ne
passe pas. Point. C'est ce qui rend impossible le scénario « excellent code,
sécurité catastrophique → validé quand même ».

---

## 5. Arbitrage entre cadres pondérés (rangs 2-5)

Quand aucun veto ne s'applique, les cadres pondérés sont agrégés — mais
**toujours par `min`**, pas par moyenne (cf. `MULTI_FRAME_MODEL.md` §4). Le rang
sert alors à départager des cas limites : à `S_global` égal, on préfère le skill
dont le **cadre le plus prioritaire** est le plus haut.

Exemple : deux skills à `S_global = 6`. L'un tient son 6 par `S_system`, l'autre
par `S_code`. → on préfère celui porté par `S_system` (rang 2 > rang 5).

---

## 6. Ce que la hiérarchie n'est PAS

- Ce n'est pas une pondération numérique floue (« security compte 3×, code 1× »)
  — c'est un **ordre strict** : un rang supérieur l'emporte, point.
- Elle n'est pas négociable au runtime. La modifier = une décision de
  gouvernance explicite, journalisée, hors exécution.

---

## 7. Limites

- Les `seuil_veto` doivent être calibrés — trop bas, le veto ne protège pas ;
  trop haut, il rejette des skills sains. Calibration = sujet de conception
  Phase 4, à falsifier sur scénarios réels.
- L'ordre `S_security` = `S_user` (ex æquo rang 1) suppose qu'aucun des deux ne
  prime sur l'autre. Si un cas réel les oppose, il faudra trancher — et le
  documenter ici.

---

*Doc 4/5 — FRAME_PRIORITIES. `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521`. Aucun code produit.*
