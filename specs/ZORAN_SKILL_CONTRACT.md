# ZORAN_SKILL_CONTRACT

**Mission** : `ZORAN_JOBS_20260521` · **Spec 1/5** · **Date** : 2026-05-21
**Statut** : Phase 0 — contrat invariant · **Priorité** : 1 (le plus critique)
**Couche de dépendance** : **1** — format autonome. Ne référence aucune autre spec.

> Règle de discipline : tout ce qui suit est **nécessaire au MVP survivant**.
> Pas de magie implicite. Chaque champ est explicite, borné, traçable.

---

## 1. Définition

Un **skill** = une micro-capacité runtime isolée. Ce n'est PAS un skill Claude Code.
Un skill ZORAN's Jobs est un **dossier** contenant :

```
skills/<skill_id>/
├── manifest.json     ← le contrat déclaratif (ce document le définit)
├── skill.py          ← le code (point d'entrée : run(inputs) -> outputs)
└── tests/            ← tests du skill (obligatoire pour promotion)
```

Le runtime ne connaît un skill QUE par son `manifest.json`. Le code n'est lu
qu'au moment du chargement par le Loader. **Le manifest est le contrat.**

---

## 2. Schéma du manifest (`manifest.json`)

```json
{
  "schema_version": "1.0",

  "identity": {
    "skill_id": "printer_connect",         // [a-z0-9_], unique, immuable
    "name": "Connexion imprimante",
    "version": "1.0.0",                    // semver
    "hash": "sha256:...",                  // hash du code skill.py
    "signature": "...",                    // signature de l'auteur
    "author": "",
    "created_at": "ISO-8601"
  },

  "io": {
    "inputs":  { "type": "object", "properties": { } },   // JSON Schema
    "outputs": { "type": "object", "properties": { } }    // JSON Schema
  },

  "routing": {
    "domain": "devices",                   // domaine unique
    "triggers": ["imprimante", "printer", "connecter une imprimante"],
    "description": "Détecte et connecte une imprimante réseau ou USB."
  },

  "coherence": {                           // ★ liaison au Moteur de Cohérence
    "expected_delta_phi": 0.7,             // gain d'info attendu (0..1)
    "expected_T_added": 0.1,               // contradictions injectées (0..1)
    "expected_sigma_added": 0.1,           // bruit injecté (0..1)
    "corrective": false                    // true = skill correcteur de dérive
  },

  "cost": {
    "runtime_cost": 2,                     // coût relatif 1..10
    "latency_class": "fast",               // fast | medium | slow
    "external_calls": false                // appels réseau/système externes ?
  },

  "permissions": ["device.printer", "network.local"],   // permissions requises
  "sandbox_level": "isolated",             // none | isolated | strict

  "dependencies": {
    "skills": [],                          // skill_ids requis
    "python": ["pyusb>=1.2"]               // paquets Python
  },

  "rollback": {
    "rollbackable": true,
    "rollback_strategy": "undo_function"   // undo_function | snapshot | none
  },

  "providers_compatible": ["local", "zoran"],   // providers d'exécution
  "lifecycle_state": "active"              // MVP: candidate|active|rejected · Phase 2+: quarantine|deprecated|revoked
}
```

---

## 3. Champs — règles invariantes

| Champ | Règle |
|---|---|
| `skill_id` | immuable. Renommer = nouveau skill. |
| `version` | semver strict. Toute modif de `skill.py` ⇒ bump + nouveau `hash`. |
| `hash` | `sha256` du `skill.py`. Le Loader REFUSE de charger si hash ≠ fichier. |
| `signature` | obligatoire. Skill non signé ⇒ `rejected` (refusé au registre — pas de quarantaine en MVP). |
| `io.inputs/outputs` | JSON Schema. Le runtime valide I/O à chaque appel. |
| `coherence.*` | valeurs **déclarées** par l'auteur ; l'Oracle (Phase 2) les **mesure** réellement et corrige. Déclaration ≠ vérité — la mesure tranche. |
| `sandbox_level` | `strict` obligatoire si `external_calls=true` ou `permissions` sensibles. |
| `lifecycle_state` | énumération de valeurs fermée. Les *transitions* sont pilotées par l'orchestrateur — hors de ce contrat. Jamais modifié à la main. |

---

## 4. Liaison au Moteur de Cohérence

Le bloc `coherence` permet au Router de calculer, AVANT chargement, le S attendu :

```
S_attendu(skill) = (β × ΔΦ_expected) / (1 + T_expected + σ_expected)
```

- C'est une **estimation a priori** (déclarée).
- Après exécution, le runtime **mesure** le ΔS réel et l'écrit dans l'historique.
- L'écart `S_attendu − S_mesuré` alimente le ranking de survie du skill.
- Un skill qui promet `ΔΦ=0.9` mais mesure `0.2` est dégradé. **La mesure falsifie la promesse.**

`corrective: true` → le skill est candidat prioritaire quand la cinématique
détecte `dS/dt < 0` (cohérence qui s'effondre).

---

## 5. Cycle de vie d'un skill

```
# MVP (Phase 1) — 3 états seulement, transitions terminales
candidate ──(tests OK + signé)──> active
candidate ──(non signé OU tests KO)──> rejected

# Phase 2+ (HORS MVP) — quarantine, re-tests, promotion/démotion,
#   revoked, deprecated. NON implémenté Phase 1.
```

Toute transition est tracée (un événement) et rollbackable. Le mécanisme de
traçage et l'orchestration des transitions sont hors de ce contrat.

---

## 6. Ce qui est HORS contrat (différé, non-MVP)

- Skills auto-modifiants — interdit Phase 1
- Skills sans tests — ne peuvent pas atteindre `active`
- Dépendances circulaires entre skills — refusées au registry
- Skills GitHub — Phase 4, passent obligatoirement par quarantine

---

*Spec 1/5 — SKILL_CONTRACT. Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.
Prochain : EVENT_SCHEMA.*
