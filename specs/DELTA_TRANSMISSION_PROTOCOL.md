# DELTA_TRANSMISSION_PROTOCOL — Transmettre uniquement ce qui a changé

**Mission** : `ZORAN_META_ORCHESTRATOR_20260521`
**Date** : 2026-05-21 · **Statut** : SPEC — aucun code
**Signé** : Claude Code, prestataire · **Livrable 5/8**

> Entre deux échanges, le système ne retransmet pas le contexte. Il transmet le
> **delta** : ce qui a changé, et rien d'autre.

---

## 1. L'interdit fondateur

> ❌ **INTERDIT** : renvoyer tout le contexte à chaque IA, à chaque tour.

C'est le premier poste de coût token, et le premier vecteur de dérive : si on
retransmet tout, chaque IA recharge un état qu'elle croit neuf, et les versions
divergent silencieusement. La règle inverse :

> ✅ On transmet l'**état initial une fois**, puis uniquement des **deltas**.

## 2. Le delta — définition

Un delta est la **différence vérifiable** entre l'état connu d'une IA et l'état
courant. Il contient exactement :

- les éléments **ajoutés**,
- les éléments **modifiés** (avec leur ancienne et nouvelle empreinte),
- les éléments **retirés**,
- une **empreinte globale** de l'état résultant, pour que l'IA réceptrice
  vérifie qu'elle a bien reconstruit le même état.

Un delta ne contient **jamais** les éléments inchangés.

## 3. Mécanisme — réutilise le skill existant

Le skill `zoran_photo_clone_leger` (livré, `skills_examples/`) **est** le moteur
de ce protocole :

1. Chaque IA détient une **photo** de son état (empreintes seules, ~80 o/élément).
2. Avant un échange, l'orchestrateur compare photo connue ↔ photo courante.
3. Il transmet le **diff ciblé** — la liste minimale des changements.
4. L'IA réceptrice applique le delta et vérifie l'**empreinte globale**.

Le skill `zoran_magasin_contenu_adressable` fournit le contenu réel des éléments
modifiés, dédupliqué et vérifié par empreinte. La paire boussole + coffre est
l'implémentation déjà disponible de ce protocole.

## 4. Invariants

**Invariant DT-1 — delta minimal** : un delta ne contient que des éléments
réellement changés. Inclure un élément inchangé est un NO-GO.

**Invariant DT-2 — vérifiabilité** : tout delta porte l'empreinte globale de
l'état résultant. L'IA réceptrice **doit** la vérifier — sinon la dérive
silencieuse réapparaît.

**Invariant DT-3 — delta ≪ contexte** : le coût d'un delta doit rester très
inférieur au coût d'une retransmission complète (cf. `TOKEN_BUDGET_MODEL.md`
TB-3). Si ce n'est pas le cas, c'est qu'on transmet du contexte déguisé.

**Invariant DT-4 — pas de delta sur delta non vérifié** : on n'empile pas un
delta sur un état dont l'empreinte n'a pas été confirmée. Sinon les erreurs
composent.

## 5. Cas observé dans la session de conception

Plusieurs fois, du travail a été annoncé « livré » sans transmission réelle (un
fichier de mission jamais écrit sur disque, un bundle jamais transmis, une
fondation V2 jamais poussée). Ce protocole l'empêche : « livré » signifie
« delta émis **et** empreinte globale vérifiée par le récepteur ». Un livrable
non vérifié n'existe pas.

## 6. Traçabilité

Journalise : `mission_id`, IA émettrice/réceptrice, taille du delta, taille du
contexte évité, empreinte globale avant/après, confirmation de vérification.

---

*Livrable 5/8 — `ZORAN_META_ORCHESTRATOR_20260521`. Spec, aucun code.*
