# PHASE 4 — CRITÈRES GO / NO-GO

**Mission** : `ZORAN_JOBS_PHASE4_PREAUDIT_20260521` · **Doc 7/7**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Ce document fixe la **barrière**. Phase 4 (code réel de Discovery) ne peut
> commencer QUE si TOUS les critères GO sont satisfaits ET prouvés. Un seul
> critère manquant ⇒ **NO-GO**.

---

## 1. Règle terminale (énoncée par ZORAN)

> Si Phase 4 ne peut pas être **contrôlée, sandboxée, rollbackable et
> falsifiable**, elle ne doit **jamais** être développée.

Ce n'est pas un objectif souhaitable — c'est une **condition d'existence**.

---

## 2. Critères GO — tous obligatoires

| # | Critère | Prouvé par | État |
|---|---|---|---|
| G1 | **Sandbox d'exécution** isolée (process/mémoire/FS/réseau) opérationnelle | un skill hostile de test confiné, runtime hôte intact | ⬜ |
| G2 | **Kill-switch** termine tout skill sans sa coopération, enfants compris | test : skill en boucle infinie tué, hôte survit | ⬜ |
| G3 | **Runtime limits** (CPU/RAM/temps/I/O) appliquées et déclenchent le kill | test : dépassement de chaque quota → kill | ⬜ |
| G4 | **Rollback** validé sous attaque — un skill ne peut pas le casser | scénario S6 rejoué → journal intact | ⬜ |
| G5 | **Signatures** obligatoires — skill non signé / hash KO refusé | test : 3 cas de signature invalide → rejet | ⬜ |
| G6 | **Trust model** implémenté — `unknown→active` direct impossible | test : tentative de saut d'étape → bloquée | ⬜ |
| G7 | **Discovery pipeline** : les 8 étapes filtrent, aucune court-circuitable | test : skill malveillant rejeté à chaque étape | ⬜ |
| G8 | **8 failure scenarios** : les 8 lignes de `FAILURE_SCENARIOS` passent de 💀/⚠️ à 🛡️ prouvé | rejouer les 8 scénarios → runtime survit aux 8 | ⬜ |
| G9 | **Clone froid Phase 3 intact** — point de retour garanti | hash du zip vérifié | ✅ |
| G10 | **Décision humaine explicite** de Fred après lecture des 7 docs de pré-audit | — | ⬜ |

État au 2026-05-21 : **1 / 10** (seul G9 acquis). → **NO-GO actuel.**

---

## 3. Verdict

```
╔═══════════════════════════════════════════════╗
║   PHASE 4 — STATUT : NO-GO                     ║
║   1 critère sur 10 satisfait.                  ║
║   Phase 4 NE COMMENCE PAS.                     ║
╚═══════════════════════════════════════════════╝
```

C'est le résultat **attendu et sain** de ce pré-audit. Le pré-audit n'a pas
pour but d'autoriser Phase 4 — il a pour but de **mesurer la distance** qui
sépare le runtime actuel d'un runtime capable d'accueillir du code hostile.
Cette distance = 9 critères. Elle est maintenant **explicite et chiffrée**.

---

## 4. Ordre de travail si Phase 4 est un jour décidée

Aucun code de Discovery (téléchargement, crawl, auto-loader) ne s'écrit avant
que G1→G8 soient verts. L'ordre de construction des défenses :

```
1. Sandbox (G1) ──> 2. Kill-switch (G2) ──> 3. Runtime limits (G3)
        │
        ▼
4. Signatures (G5) ──> 5. Trust model (G6) ──> 6. Rollback sous attaque (G4)
        │
        ▼
7. Discovery pipeline (G7) ──> 8. Rejouer les 8 scénarios (G8)
        │
        ▼
9. GO/NO-GO réévalué ──> 10. Décision Fred (G10)
        │
        ▼
   SEULEMENT ALORS : premier code de Discovery
```

Les défenses se construisent **et se prouvent** dans cet ordre. Chaque critère
a son test ; sans le test vert, le critère n'est pas acquis.

---

## 5. Critère final de succès du pré-audit

Le succès de cette mission n'était **pas** de produire du code, ni d'autoriser
Phase 4. Le succès est atteint : **on comprend désormais précisément pourquoi
Phase 4 peut devenir catastrophique, et ce qu'il faut prouver pour qu'elle ne
le devienne pas.** Les 9 critères manquants sont la feuille de route.

---

## 6. Synthèse des 7 livrables du pré-audit

| Doc | Objet | Conclusion |
|---|---|---|
| 1 THREAT_MODEL | 12 vecteurs de destruction | runtime actuel exposé à tous |
| 2 SANDBOX_MODEL | 9 dimensions d'isolation + kill-switch | `importlib` actuel insuffisant |
| 3 TRUST_MODEL | 5 niveaux, promotion progressive | `unknown→active` interdit |
| 4 DISCOVERY_PIPELINE | 8 étapes de filtrage | rejeter tôt, promotion manuelle |
| 5 ZGNET_SECURITY | ZGNET = protocole, pas sécurité d'exécution | ne pas l'implémenter pour Phase 4 |
| 6 FAILURE_SCENARIOS | 8 skills hostiles simulés | runtime actuel survit à 0/8 |
| 7 GO_NOGO (ce doc) | 10 critères | **NO-GO — 1/10** |

---

*Doc 7/7 — GO_NOGO. Pré-audit Phase 4 COMPLET.
`ZORAN_JOBS_PHASE4_PREAUDIT_20260521`. Aucun code produit — conforme à la mission.*
