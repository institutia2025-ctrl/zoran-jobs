# ZGNET_RUNTIME_LANGUAGE — SPÉCIFICATION MINIMALISTE

**Mission** : `ZORAN_JOBS_20260521` · **Spec 5/5** · **Date** : 2026-05-21
**Statut** : Phase 0 — **spécification d'intention seulement**
**Cible d'implémentation** : V4+ — **PAS le runtime actuel**
**Couche de dépendance** : **3** — périphérique. Référence EVENT_SCHEMA (couche 0) uniquement. Aucun composant Phase 1 ne dépend de ZGNET.

> ⚠️ ZGNET n'est **PAS implémenté** et ne doit PAS l'être maintenant.
> Ce document fixe son rôle et ses invariants pour qu'on ne dérive pas plus tard.
> Discipline ZORAN : « ZGNET doit être spécifié, pas codé. Mode minimaliste. »

---

## 1. Pourquoi ce document existe (et pas le code)

Le danger : implémenter un langage runtime maintenant = réinventer un OS avant
le MVP. Interdit. Mais ne pas le spécifier du tout = risquer que chaque IA qui
reconstruit le système improvise un dialecte différent.

→ On **borne l'intention** dès maintenant. On **n'implémente pas**.

---

## 2. Le problème que ZGNET résoudra (un jour)

Quand le satellite sera transmissible entre IA différentes (Claude, GPT,
DeepSeek, futur modèle), chaque IA doit interpréter les échanges runtime
**exactement de la même façon**. Le langage naturel et le JSON libre laissent
trop de place à l'ambiguïté → chaque IA reconstruirait un ZORAN différent.

ZGNET = le **langage invariant de transmission cognitive** : strict, borné,
non-ambigu, non extensible librement.

---

## 3. Invariants de ZGNET (à respecter quand il sera conçu)

| Invariant | Raison |
|---|---|
| **Strict** | une instruction = une seule interprétation possible |
| **Borné** | vocabulaire fini, fermé — pas d'extension libre à la volée |
| **Invariant** | la même instruction produit le même effet sur toute IA / tout runtime |
| **Non-ambigu** | aucune inférence implicite ; tout est explicite |
| **Transmissible** | lisible et reconstructible par une IA sans contexte humain |
| **Souverain** | aucune dépendance à un moteur ou un fournisseur particulier |
| **Traçable** | toute expression ZGNET produit un événement (spec 2) |

---

## 4. Ce que ZGNET N'EST PAS

- ❌ un langage de programmation généraliste
- ❌ un format extensible par plugins
- ❌ un protocole réseau
- ❌ quelque chose à coder avant que le MVP (Phases 1-3) soit prouvé

---

## 5. Position dans la trajectoire

```
Phase 1-3  : runtime fonctionne en Python + EVENT_SCHEMA (JSON).  ZGNET absent.
Phase 4    : GitHub discovery — toujours pas de ZGNET.
V4+        : SI le satellite est prouvé ET qu'on vise la transmission
             inter-IA réelle → ZGNET est conçu, à partir de ce document.
```

Tant que le satellite tourne sur un seul type de runtime, l'`EVENT_SCHEMA` (JSON
strict) **suffit**. ZGNET ne devient nécessaire que pour la transmission
inter-intelligences à grande échelle.

---

## 6. Critère de déclenchement

ZGNET ne sera conçu QUE si ces 3 conditions sont réunies :
1. Le MVP (Phases 1-3) est prouvé survivant et falsifiable
2. Un besoin réel de transmission inter-IA est démontré (pas supposé)
3. L'`EVENT_SCHEMA` JSON a montré ses limites concrètes d'ambiguïté

Si une seule condition manque → ZGNET attend. Pas de magie anticipée.

---

*Spec 5/5 — ZGNET (spécification minimaliste, non implémentée).
Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.
Les 5 contrats Phase 0 sont écrits.*
