# ZORAN_STATE_MODEL

**Mission** : `ZORAN_JOBS_20260521` · **Spec 3/5** · **Date** : 2026-05-21
**Statut** : Phase 0 — contrat invariant · **Priorité** : 3 (cohérence / snapshots / reconstruction)
**Couche de dépendance** : **1** — dépend UNIQUEMENT d'EVENT_SCHEMA (couche 0).

> Discipline : l'état est **explicite et borné**. Rien d'implicite.
> L'état entier se reconstruit en rejouant le flux d'événements (spec 2).

---

## 1. Principe

L'état runtime = **fold (repli) du flux d'événements**.

```
état(T) = reduce(appliquer_événement, events[0..T], état_initial)
```

Conséquence : l'état n'est jamais la source de vérité — les **événements** le sont.
L'état est un *cache reconstructible*. On peut le jeter et le recalculer.

---

## 2. Composition de l'état runtime

```json
{
  "runtime": {
    "status": "idle",                  // idle | routing | loading | executing | degraded
    "current_trace_id": null,
    "started_at": "ISO-8601"
  },

  "registry": {
    "skills": {                        // index des skills connus (par skill_id)
      "<skill_id>": {
        "version": "1.0.0",
        "lifecycle_state": "active",
        "hash": "sha256:..."
      }
    }
  },

  "loaded": ["<skill_id>", "..."],     // skills actuellement en mémoire

  "coherence": {                       // ★ état du Moteur de Cohérence
    "S_current": 7.4,
    "components": { "beta": 9.0, "delta_phi": 8.2, "T": 0.6, "sigma": 0.4 },
    "S_history": [                     // série temporelle — base cinématique
      { "t": "ISO-8601", "S": 6.1 },
      { "t": "ISO-8601", "S": 7.4 }
    ],
    "dS_dt": 0.43,                     // cinématique : dérivée récente de S
    "projection": {                    // futur probable (couche 3)
      "reliable": true,                // false si passé incohérent (S erratique)
      "S_projected": 7.9,
      "horizon_steps": 1
    }
  },

  "last_snapshot_id": "snap_..."
  // NB : pas de champ `quarantine` en MVP — Phase 2+ uniquement
}
```

---

## 3. Transitions d'état

Toute transition est déclenchée par un événement (spec 2) et est tracée :

```
idle ──request_received──> routing
routing ──skill_selected──> loading
loading ──skill_loaded──> executing
executing ──coherence_delta──> idle
executing ──skill_failed──> degraded
degraded ──rollback_executed──> idle
```

`degraded` = mode dégradation graceful : le runtime reste vivant, refuse de
nouvelles exécutions risquées, attend rollback ou intervention. Jamais de crash
silencieux.

---

## 4. Mémoire minimale (ce qui DOIT survivre à un redémarrage)

| Donnée | Persistée ? | Où |
|---|---|---|
| Flux d'événements | ✅ toujours | `runtime/events.jsonl` |
| Fichiers skills sur disque | ✅ | `skills/*/` |
| `S_history` | ✅ (dérivé des événements) | reconstruit au boot |
| État runtime complet | ❌ | reconstruit par fold au boot |
| Skills chargés en mémoire | ❌ | rechargés à la demande |

**Au démarrage** : le runtime rejoue `events.jsonl` → reconstruit l'état complet,
y compris `S_history`. Aucune perte de cohérence après reboot.

---

## 5. Snapshots & restauration

- Un **snapshot** = capture datée de l'état runtime complet + offset dans `events.jsonl`
- Créé : avant toute opération risquée (chargement skill `sandbox_level=strict`, promotion, Phase 4)
- Restauration : charger le snapshot + rejouer les événements depuis l'offset
- `snapshot_id` tracé ; restauration émet un événement `rollback_executed`

---

## 6. Couches cohérence — où elles vivent dans l'état

| Couche | Champ d'état | Calcul |
|---|---|---|
| **Phénoménale** | `coherence.S_current` + `components` | `S = (β×ΔΦ)/(1+T+σ)` sur l'état courant |
| **Cinématique** | `coherence.dS_dt` | pente de régression sur les N derniers points de `S_history` |
| **Futur probable** | `coherence.projection` | extrapolation de `S_history` ; `reliable=false` si variance(S_history) trop haute |

Règle anti-flou (exigée par ZORAN) : ces 3 champs sont des **nombres calculés et
tracés**, jamais des abstractions. Chaque mise à jour émet un événement
`coherence_measured`. Falsifiable : on peut rejouer et recalculer.

---

## 7. Hors-scope MVP

- État distribué multi-runtime — différé
- Snapshots incrémentaux — MVP = snapshots complets
- Projection multi-horizon — MVP = `horizon_steps: 1`

---

*Spec 3/5 — STATE_MODEL. Signé Claude, prestataire, 2026-05-21 · `ZORAN_JOBS_20260521`.
Prochain : RUNTIME_PROTOCOL.*
