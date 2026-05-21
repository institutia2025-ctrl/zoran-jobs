# ZORAN_EVENT_SCHEMA

**Mission** : `ZORAN_JOBS_20260521` · **Spec 2/5** · **Date** : 2026-05-21
**Statut** : Phase 0 — contrat invariant · **Priorité** : 2 (traçabilité / rollback / survie)
**Couche de dépendance** : **0** — fondation. Ne référence AUCUNE autre spec.

> Discipline : chaque événement est **strictement reconstructible**.
> Si un événement ne peut pas être rejoué à l'identique, il est invalide.

---

## 1. Rôle

Tout ce qui se passe dans le runtime émet un **événement**. Le flux d'événements
est la **mémoire de vérité** du système : il permet de tracer, auditer, rejouer,
et rollback. L'état runtime se reconstruit en rejouant les événements — ce
mécanisme de repli appartient au consommateur du flux, hors de ce contrat.

**Append-only** : un événement n'est jamais modifié ni supprimé. Correction =
nouvel événement.

---

## 2. Format minimal (invariant)

```json
{
  "event_id": "evt_<timestamp>_<uuid8>",   // unique, immuable
  "timestamp": "ISO-8601",                 // UTC
  "type": "skill_selected",                // voir §3
  "source": "router",                      // composant émetteur
  "target": "printer_connect",             // skill_id ou composant cible
  "provider": "local",                     // provider d'exécution
  "trace_id": "trace_<uuid8>",             // corrèle tous les events d'une requête
  "rollback_id": "rb_<uuid8>",             // null si non rollbackable
  "payload": {},                           // données typées selon `type`
  "signature": "sha256:..."                // hash(event sans signature)
}
```

**Invariants :**
- `event_id` unique et immuable
- `trace_id` partagé par tous les événements d'une même requête utilisateur
- `rollback_id` présent ⇒ l'événement peut être annulé ; `null` ⇒ irréversible
- `signature` = hash de l'événement (champ `signature` exclu) — détecte toute altération

---

## 3. Types d'événements MVP (Phase 1)

| `type` | Émis par | `payload` contient |
|---|---|---|
| `request_received` | runtime | prompt, contexte, device, permissions |
| `coherence_measured` | coherence engine | S, β, ΔΦ, T, σ, dS/dt |
| `skill_candidates_ranked` | router | liste [skill_id, skill_score] |
| `skill_selected` | router | skill_id, skill_score, raison |
| `skill_loaded` | loader | skill_id, hash vérifié (bool) |
| `skill_executed` | runtime | skill_id, inputs, outputs, durée_ms |
| `skill_failed` | runtime | skill_id, erreur, phase |
| `coherence_delta` | coherence engine | S_avant, S_après, ΔS_mesuré |
| `skill_rejected` | loader/registry | skill_id, motif (non signé, hash KO, tests KO) |
| `rollback_executed` | runtime | rollback_id ciblé, résultat |

> Types Phase 2+ (HORS MVP) : `skill_quarantined`, `skill_promoted`,
> `skill_demoted`, `oracle_compared`, `github_discovered`… ajoutés plus tard.
> On ne spécifie QUE ce dont le MVP a besoin.

---

## 4. Reconstructibilité

Un observateur externe (autre IA) doit pouvoir, à partir du seul flux d'événements :
1. **Rejouer** la séquence d'une requête (`trace_id`)
2. **Reconstruire** l'état runtime à l'instant T par repli (fold) du flux
3. **Annuler** une action (`rollback_id`)
4. **Détecter** toute altération (`signature`)

Test de validité d'un événement : *« puis-je le rejouer et obtenir le même
résultat ? »* Si non → l'événement contient de la magie implicite → invalide.

---

## 5. Stockage

- Fichier `runtime/events.jsonl` — append-only, une ligne JSON par événement
- Jamais de réécriture ; rotation par archivage daté si volumétrie excessive
- Chaque ligne est auto-suffisante (pas de référence à un état externe non tracé)

---

## 6. Lien avec le Moteur de Cohérence

Les événements `coherence_measured` et `coherence_delta` construisent le
**`S_history`** — la série temporelle de S. C'est cette série que la
**cinématique** (`dS/dt`) et la **projection** (futur probable) exploitent.
Sans flux d'événements fiable, pas de cinématique. L'Event Schema est donc le
socle des couches cohérence 2 et 3.

---

*Spec 2/5 — EVENT_SCHEMA. Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.
Prochain : STATE_MODEL.*
