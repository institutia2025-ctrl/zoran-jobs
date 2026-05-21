# INTER_AGENT_CONFLICTS — Conflits possibles entre IA

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : AUDIT — aucun code
**Signé** : Claude Code, prestataire · **Livrable 7/8**

> Recense les conflits inter-IA. Un conflit non anticipé est une dérive qui
> arrive. Chacun reçoit son mécanisme de prévention.

---

## 1. Conflits de type « excellence locale destructrice »

| # | Conflit | Mécanisme de prévention |
|---|---|---|
| C1 | IA Backend optimise la perf → casse la sécurité | Global Veto : `S_securite < seuil` ⇒ refus, avant tout score (`GLOBAL_VETO_RUNTIME.md`) |
| C2 | IA UX réduit la friction → casse la gouvernance | cadre `global` obligatoire pour l'IA UX (`FRAME_ROUTER_SPEC.md` FR-2) + veto |
| C3 | IA Code modifie un invariant runtime « pour améliorer » | les invariants sont des NO-GO transmis ; toute modif d'invariant = veto |
| C4 | IA Sécurité bloque tout → paralysie du système | arbitrage orchestrateur : un veto doit citer le cadre fautif et son `S` ; un veto non motivé est invalide |

## 2. Conflits de type « dérive de coordination » (observés dans cette session)

Ces conflits ne sont pas théoriques — ils se sont produits pendant la conception
de ce dépôt, entre les sessions IA parallèles :

| # | Conflit observé | Cause | Prévention |
|---|---|---|---|
| C5 | Travail « livré » jamais transmis (lettre de mission, bundle, fondation V2) | « livré dans un chat » ≠ poussé | `DELTA_TRANSMISSION_PROTOCOL.md` DT-2 : un livrable n'existe que delta émis **et** empreinte vérifiée |
| C6 | Deux IA construisant sur des états de dépôt divergents | bases obsolètes non re-synchronisées | empreinte globale d'état vérifiée avant toute mission ; baseline divergente ⇒ stop et rapport |
| C7 | Duplication de périmètre entre lots parallèles | scopes non disjoints | scopes et préfixes disjoints (`META_ORCHESTRATOR_SPEC.md` MO-1, `ZORAN_JOBS_DISTRIBUTION.md` ZD-2) |
| C8 | Numérotation de version divergente entre lots (v0.5 / v0.6 / v0.7) | sections de CHANGELOG concurrentes | sections de journal disjointes par lot, jamais de section commune |

## 3. Conflits de type « bruit cognitif »

| # | Conflit | Prévention |
|---|---|---|
| C9 | Négociation directe inter-IA qui s'éternise | bavardage inter-IA interdit (NO-GO) ; l'orchestrateur arbitre, les IA ne négocient pas |
| C10 | Une IA reçoit des cadres/skills hors rôle et raisonne dessus | distribution minimale (`FRAME_ROUTER_SPEC.md`, `ZORAN_JOBS_DISTRIBUTION.md`) |
| C11 | Retransmission de contexte massif prise pour un delta | `DELTA_TRANSMISSION_PROTOCOL.md` DT-3 : delta ≪ contexte, sinon rejeté |

## 4. Principe d'arbitrage commun

Aucun conflit ne se règle par négociation entre IA. Tout conflit remonte à
l'orchestrateur, qui tranche par : **Global Veto → plancher (min) → `S_global`**.
La décision est journalisée. Les IA ne se parlent pas entre elles : elles
parlent à l'orchestrateur, qui détient seul la cohérence globale.

## 5. Conflit résiduel non couvert (honnêteté)

Un conflit reste hors de portée d'une spec : **deux orchestrateurs concurrents**.
Si deux Meta Orchestrators tournent sans se connaître, on recrée le problème C6
à l'étage du dessus. Règle : **un seul orchestrateur fait autorité par mission**.
Sa désignation est humaine et explicite — elle n'est pas négociée par les IA.

## 6. Traçabilité

Chaque conflit détecté journalise : `mission_id`, type (C1..C11), IA impliquées,
cadre fautif, verdict d'arbitrage, rollback conceptuel proposé.

---

*Livrable 7/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Audit, aucun code.*
