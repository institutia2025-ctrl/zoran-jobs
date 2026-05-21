# LOW_TOKEN_STRATEGY — Réduction massive du coût cognitif

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : AUDIT — aucun code
**Signé** : Claude Code, prestataire · **Livrable 8/8**

> Le système ne cherche pas la puissance brute. Il cherche la **cohérence
> distribuée à coût minimal**. Ce document liste comment.

---

## 1. Les 6 leviers

| Levier | Principe | Spec liée |
|---|---|---|
| Delta-only | transmettre ce qui change, jamais le contexte entier | `DELTA_TRANSMISSION_PROTOCOL.md` |
| Mémoire condensée | une photo d'empreintes (~80 o/élément), pas les contenus | `zoran_photo_clone_leger` |
| Contexte minimal | chaque IA reçoit mission + invariants + NO-GO + skills + budget, rien d'autre | `META_ORCHESTRATOR_SPEC.md` §2 |
| Cadres filtrés | une IA ne reçoit que ses cadres de cohérence | `FRAME_ROUTER_SPEC.md` |
| Résumés déterministes | un résumé calculé (hash, diff, compte), pas un résumé rédigé par une IA | ce document §3 |
| Suppression du bruit inter-agent | pas de négociation directe entre IA | `INTER_AGENT_CONFLICTS.md` C9 |

## 2. Pourquoi le coût s'effondre

Sans stratégie, `n` IA qui voient tout : coût `≈ O(n²)` (chacune porte le
contexte de toutes). Avec scopes disjoints + delta : coût `≈ O(n)` (chacune
porte son scope + ses deltas). Le facteur dominant n'est pas la vitesse du
modèle — c'est **ce qu'on refuse de transmettre**.

## 3. Résumés déterministes plutôt que rédigés

Un résumé rédigé par une IA coûte des tokens **et** introduit de l'interprétation
(donc de la dérive potentielle). Un résumé déterministe — une empreinte, un
diff, un compte d'items, un verdict de veto — coûte presque rien **et** est
falsifiable. Règle : partout où un résumé déterministe suffit, il remplace le
résumé rédigé. (C'est déjà la discipline du runtime : le Coherence Engine est
100 % mathématique, zéro LLM.)

## 4. Ce qu'on NE fait jamais (anti-patterns)

- ❌ « Par sécurité, on transmet tout le contexte. » → coût `O(n²)`, dérive.
- ❌ « Chaque IA résume la conversation pour les autres. » → coût + interprétation.
- ❌ « On garde l'historique complet en mémoire de travail. » → la photo suffit.
- ❌ « On laisse les IA discuter pour s'accorder. » → bavardage non borné.
- ❌ « On retransmet le contexte à chaque tour, c'est plus sûr. » → faux : c'est
  exactement ce qui désynchronise (C5/C6 de `INTER_AGENT_CONFLICTS.md`).

## 5. Mesure — le budget rend la stratégie falsifiable

`TOKEN_BUDGET_MODEL.md` fournit les compteurs. La stratégie low-token n'est pas
une intention : c'est un budget mesuré. Indicateur clé : le ratio
`delta / scope` par mission. Tant qu'il reste bas, la compression cognitive
fonctionne. S'il grimpe, on retransmet du contexte déguisé — alerte.

## 6. Lien avec le critère de succès de la mission

Le succès n'est pas « beaucoup d'IA qui parlent », mais « plusieurs IA alignées
à coût cognitif minimal ». La stratégie low-token **est** la moitié « coût
minimal » de ce critère ; le Global Veto et les scopes disjoints en sont la
moitié « alignées ». Les deux sont indissociables.

## 7. Traçabilité

Journalise par mission : tokens transmis (scope / delta / rollback /
orchestration), ratio `delta/scope`, leviers actifs, anti-patterns détectés,
limites explicites.

---

*Livrable 8/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Audit, aucun code.
Mission de spécification COMPLÈTE — 8/8 livrables. Aucun code produit, conforme.*
