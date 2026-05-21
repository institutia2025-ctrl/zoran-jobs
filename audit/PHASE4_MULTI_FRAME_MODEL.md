# PHASE 4 — MULTI-FRAME COHERENCE MODEL

**Mission** : `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` · **Doc 1/5**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Avancée conceptuelle : le problème n'est pas la valeur de S — c'est le **cadre**
> dans lequel S est calculé. Un skill peut être parfaitement cohérent *localement*
> et destructeur *globalement*. Ce document définit les cadres et leur agrégation.

---

## 1. Le piège du S unique

L'Oracle Phase 2 mesure une cohérence **locale** (le skill fait-il bien ce qu'il
dit ?). Insuffisant : un malware runtime est, dans son propre cadre code :
rapide, stable, déterministe, sans contradiction → **S_code élevé**.

Mais il détruit le système. La cohérence locale **n'implique pas** la cohérence
système. Il faut mesurer S dans **plusieurs cadres**, puis vérifier leur *alignement*.

Formule de référence (canonique ZORAN, dénominateur additif) :
`S = (β × ΔΦ) / (1 + T + σ)` — appliquée **par cadre**.

---

## 2. Les 7 cadres

| Cadre | Question | Mesure |
|---|---|---|
| `S_code` | le skill est-il propre, stable, déterministe ? | conformité io, stabilité, latence |
| `S_runtime` | casse-t-il le runtime ? surcharge ? dépendances cachées ? | quotas respectés, pas de monkey-patch |
| `S_security` | lit-il des fichiers ? ouvre du réseau ? contourne des permissions ? subprocess ? | accès observés vs permissions déclarées |
| `S_user` | respecte-t-il les intentions, la vie privée, la confiance utilisateur ? | pas d'exfiltration, pas d'action non demandée |
| `S_system` | reste-t-il aligné avec les objectifs runtime globaux ? | l'action sert-elle le but du système |
| `S_ecosystem` | dégrade-t-il les autres skills / providers / performances ? | pas d'effet de bord sur les voisins |
| `S_global` | **alignement final de tous les cadres** | agrégation — voir §4 |

---

## 3. Poids et nature des cadres

Deux familles :

- **Cadres VETO** (`S_security`, `S_user`) — non compensables. S'ils s'effondrent,
  rien ne peut les racheter. Un excellent `S_code` ne compense JAMAIS un
  `S_security` catastrophique.
- **Cadres pondérés** (`S_code`, `S_runtime`, `S_system`, `S_ecosystem`) —
  contribuent à `S_global` selon un poids, mais aucun ne peut à lui seul
  valider un skill.

La hiérarchie de priorité est traitée en détail dans `PHASE4_FRAME_PRIORITIES.md`.

---

## 4. Agrégation — comment calculer `S_global`

**RÈGLE FONDAMENTALE : `S_global` n'est PAS une moyenne.**

Une moyenne permettrait à un `S_code = 10` de compenser un `S_security = 0` →
exactement le piège du malware. L'agrégation se fait en deux temps :

```
ÉTAPE 1 — VETO
  si  S_security < seuil_veto  OU  S_user < seuil_veto :
        S_global = 0   →  skill REJETÉ, fin. Aucune compensation possible.

ÉTAPE 2 — agrégation des cadres restants (seulement si aucun veto)
  S_global = min( cadres_critiques )   pondéré
```

`S_global` est dominé par le **PIRE** cadre, pas par la moyenne. Un skill n'est
« aligné » que si **tous** ses cadres critiques le sont. Le maillon faible
commande.

---

## 5. Conséquence pour l'Oracle Phase 4

L'Oracle actuel (Phase 2) devient **un seul des 7 cadres** (`S_code`). L'Oracle
Phase 4 devra :
1. mesurer les 7 cadres séparément (chacun avec ses propres sondes) ;
2. appliquer le veto avant toute agrégation ;
3. ne jamais résumer un skill à un nombre unique sans exposer les 7 sous-jacents
   (traçabilité — on doit voir *quel* cadre a fait chuter `S_global`).

---

## 6. Limites du modèle

- Les 7 cadres ne sont pas tous également **mesurables** : `S_code` est
  quantifiable précisément, `S_system` (alignement aux objectifs) est plus
  qualitatif. Ce doc définit les cadres ; leur instrumentation concrète est un
  sujet de conception Phase 4.
- Le modèle suppose qu'on sait fixer les `seuil_veto` — leur calibration est un
  sujet à part entière, à falsifier sur des scénarios réels.
- 7 cadres est un choix initial — extensible si un angle mort apparaît.

---

*Doc 1/5 — MULTI_FRAME_MODEL. `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521`. Aucun code produit.*
