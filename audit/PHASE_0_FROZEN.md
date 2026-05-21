# PHASE 0 — FROZEN_FOUNDATION

**Mission** : `ZORAN_JOBS_20260521`
**Date du gel** : 2026-05-21
**Statut** : 🔒 **FROZEN_FOUNDATION** — fondations gelées
**Autorité de gel** : Frédéric TABARY (GO « A », via ZORAN CC_inst 10.0)

---

## 1. Ce qui est gelé

Les 6 documents fondateurs de Phase 0. Toute modification ultérieure exige un
**GO explicite de Fred** + un nouveau hash + une entrée dans ce journal.

| Document | SHA256 (16 préfixe) | Couche |
|---|---|---|
| `audit/SKILL_ORACLE_ARCHITECTURE.md` | `912535cf27681cb8` | — (doc chapeau) |
| `specs/ZORAN_EVENT_SCHEMA.md` | `bbababe8d0a00f9f` | 0 |
| `specs/ZORAN_SKILL_CONTRACT.md` | `c120d9875484b54d` | 1 |
| `specs/ZORAN_STATE_MODEL.md` | `7a50b842d9bad6cb` | 1 |
| `specs/ZORAN_RUNTIME_PROTOCOL.md` | `7f9a8835074d9a9d` | 2 |
| `specs/ZGNET_RUNTIME_LANGUAGE.md` | `9486bbaf239f1b65` | 3 |

---

## 2. Garanties acquises au gel

| Critère | État | Preuve |
|---|---|---|
| Topologie acyclique | ✅ 0 cycle | détecteur networkx, 2 passes graphify indépendantes |
| Hiérarchie en couches | ✅ DAG strict 0→1→2→3 | chaque spec déclare sa `Couche de dépendance` |
| MVP isolable | ✅ | registry+router+loader+coherence sans Oracle/Quarantine/GitHub/ZGNET |
| STATE_MODEL passif | ✅ | couche 1, zéro logique, état = fold des événements |
| Quarantine hors MVP | ✅ | repoussée Phase 2+, vérifiée par grep |
| Centralisation faible | ✅ | specs à degré réparti 10-12, pas de god node logique |

---

## 3. Historique des corrections (Phase 0)

| Vague | Objet | Résultat |
|---|---|---|
| Audit graphify #1 | détection | 4 cycles + 2 god nodes trouvés |
| Correction vague 1 | hiérarchie en couches (11 edits) | 4 cycles → 0 |
| Audit graphify #2 | re-vérification | DAG acyclique confirmé |
| Correction vague 2 | quarantine sortie du MVP (7 edits) | périmètre MVP réduit, 0 cycle maintenu |

---

## 4. Règle de dégel

Un document gelé ne peut être modifié que si :
1. Fred donne un **GO explicite**
2. La modification est journalisée ici (date, motif, ancien hash → nouveau hash)
3. Un nouvel audit topologique graphify est relancé si la modification touche
   les dépendances inter-specs

---

## 5. Ce qui commence maintenant — Phase 1 MVP

Ordre de construction (recommandé par ZORAN 2026-05-21T03:08) :
1. Registry minimal
2. Manifest parser
3. Router déterministe
4. Loader minimal
5. Coherence Engine phénoménal

Objectif unique : **prouver qu'un runtime de skills minimal reste stable et
falsifiable**. Discipline : chaque composant doit rester supprimable facilement
— le sandbox reste **jetable** tant qu'il n'a pas survécu.

INTERDIT en Phase 1 : Oracle · projection future · GitHub discovery ·
auto-promotion · auto-évolution · ZGNET runtime.

---

*Phase 0 close et gelée. Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.*
