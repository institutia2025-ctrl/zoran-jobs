# ZORAN_SKILL_CONTRACT_V2 — Contrat de skill enrichi

**Mission** : `ZORAN_JOBS_20260521`
**Statut** : SPEC GELÉE — extension rétro-compatible du contrat V1.
**Auteur** : Frédéric TABARY · Claude · 2026-05-21
**Précédent** : `specs/ZORAN_SKILL_CONTRACT.md` (V1, reste valide)

> V2 ne **remplace pas** V1. Tout skill `schema_version: "1.0"` continue de fonctionner sans modification.
> V2 ajoute **4 champs optionnels** que les skills industrialisés (BTP, structure, nucléaire) renseignent pour permettre :
> - cohérence multi-cadres (au-delà du scalaire unique de V1),
> - projection « futur probable » (Loi 2 Zoran),
> - veto sécurité (le runtime bloque un skill non sûr **avant** scoring),
> - limites explicites (Loi 10 anti-hallucination, refus partiel autorisé).

---

## 1. Quand utiliser V2

Un skill **doit** passer en V2 si **au moins une** des conditions suivantes est vraie :

- Son routage doit tenir compte d'autres dimensions que la cohérence interne (coût, carbone, sécurité, maintenance, exploitabilité).
- Sa recommandation a des **conséquences à horizon > 1 an** (pathologie probable, dégradation prévisible).
- Il opère dans un domaine où une erreur peut engager la **sécurité** (structure, ouvrages spéciaux, nucléaire, MEP critique).
- Il a des **limites métier** non triviales que le routeur doit respecter (« ne sait pas faire X, Y »).

Un skill V1 simple (ex. `palette_harmonique`, `echo`) n'a aucune raison de migrer.

## 2. Champs V2 (tous optionnels, en plus du contrat V1)

### 2.1 `coherence_multi_frame`

Permet de déclarer une cohérence par **cadre** (≠ un scalaire global). Chaque cadre suit INV-1 strict (`S = β × ΔΦ / (1 + T + σ)`).

```json
"coherence_multi_frame": {
  "structure":    { "expected_delta_phi": 0.80, "expected_T_added": 0.05, "expected_sigma_added": 0.05, "weight": 0.30 },
  "cout":         { "expected_delta_phi": 0.40, "expected_T_added": 0.10, "expected_sigma_added": 0.00, "weight": 0.15 },
  "carbone":      { "expected_delta_phi": 0.30, "expected_T_added": 0.00, "expected_sigma_added": 0.10, "weight": 0.10 },
  "maintenance":  { "expected_delta_phi": 0.50, "expected_T_added": 0.00, "expected_sigma_added": 0.05, "weight": 0.15 },
  "exploitation": { "expected_delta_phi": 0.40, "expected_T_added": 0.00, "expected_sigma_added": 0.05, "weight": 0.10 },
  "securite":     { "expected_delta_phi": 0.90, "expected_T_added": 0.05, "expected_sigma_added": 0.05, "weight": 0.20 }
}
```

**Cadres BTP recommandés** : `structure`, `cout`, `carbone`, `maintenance`, `exploitation`, `securite`.

**Règles** :
- Chaque champ `expected_*` ∈ [0..1] (comme V1).
- `weight` ∈ [0..1] ; somme des poids = 1.0 ± 0.01 (validation stricte).
- Si `coherence_multi_frame` est présent, le champ V1 `coherence` reste **toléré** (compatibilité) mais le moteur utilise multi-frame en priorité.
- Le runtime calcule `S_global = Σ (weight_i × S_i)`.

### 2.2 `futur_probable`

Projette les conséquences à horizon temporel — incarne la **Loi 2 (Futur Cohérent)** de Zoran.

```json
"futur_probable": [
  {
    "horizon_an": 10,
    "evenement": "Carbonatation atteint l'enrobage des armatures (zone XC3)",
    "probabilite": 0.45,
    "gravite": "moyenne",
    "reference": "NF EN 14630 + abaques k de carbonatation"
  },
  {
    "horizon_an": 30,
    "evenement": "Corrosion généralisée si pas de réparation",
    "probabilite": 0.75,
    "gravite": "elevee",
    "reference": "NF EN 1504 §3.2"
  }
]
```

**Champs** :
- `horizon_an` (int) : horizon temporel en années (typiquement 10, 30, 50).
- `evenement` (str) : description courte de la pathologie ou conséquence.
- `probabilite` ∈ [0..1] : estimation, **doit citer sa source** dans `reference`.
- `gravite` ∈ {"faible", "moyenne", "elevee", "critique"}.
- `reference` (str) : norme ou document public vérifiable. **Loi 1 stricte : aucune valeur fabriquée**.

### 2.3 `veto_capable`

Déclare que ce skill **peut être bloqué** par le veto sécurité du routeur. Default = `false` (rétro-compat).

```json
"veto_capable": true
```

**Sémantique** : si `veto_capable: true` et que `coherence_multi_frame.securite` a un `S_securite < seuil_runtime` (par défaut 0.15), le skill est **exclu du classement avant scoring**. C'est un filtre dur, pas une pénalité.

Seuil par défaut : configurable au niveau runtime, pas du skill — typiquement 0.15 (les skills critiques nucléaires/structuraux exigent S_securite > 0.5).

### 2.4 `limites_explicites`

Liste les choses que le skill **ne sait pas** faire. Permet au router et à l'IA appelante de ne pas mal interpréter le résultat.

```json
"limites_explicites": [
  "Ne traite que les fissures non structurelles (classification AQC a/b/c). Pour fissures d, escalade requise.",
  "Hypothèse maçonnerie traditionnelle pierre/parpaing — ne couvre pas BTC ni paille porteuse.",
  "Ne remplace pas un diagnostic in situ : sortie = orientation, pas verdict."
]
```

**Règles** :
- Chaque limite doit être actionnable (l'IA appelante peut décider d'escalader ou pas).
- Aucune limite générique du type « ne pas utiliser en production ». Concret, métier, falsifiable.

## 3. Implémentation runtime — impacts

### 3.1 `registry/manifest.py`

Nouvelle fonction `_validate_v2_extensions(data, errors)` appelée si `coherence_multi_frame` OU `futur_probable` OU `veto_capable` OU `limites_explicites` présent. Valide :
- bornes [0..1], somme des poids = 1.0,
- énumérations fermées (gravite),
- types stricts.

### 3.2 `runtime/coherence/engine.py`

Nouvelle fonction :

```python
def compute_S_multi_frame(state: CoherenceState, multi_frame: dict) -> dict[str, float]:
    """Calcule S par cadre. Chaque cadre suit INV-1 (1 + T + sigma)."""
    return {
        frame: compute_S(
            state.beta,
            state.delta_phi + cfg["expected_delta_phi"],
            state.T + cfg["expected_T_added"],
            state.sigma + cfg["expected_sigma_added"],
        )
        for frame, cfg in multi_frame.items()
        if frame != "weight"  # garde
    }

def s_global(s_per_frame: dict, weights: dict) -> float:
    """S_global = Σ w_i × S_i. Somme des poids = 1.0."""
    return sum(weights[f] * s_per_frame[f] for f in s_per_frame)
```

INV-1 est **préservé partout** : chaque cadre a son propre `(1 + T_frame + σ_frame)`.

### 3.3 `router/router.py`

Pré-filtre **avant** scoring :

```python
def _veto_securite(manifest: Manifest, state: CoherenceState, seuil: float = 0.15) -> bool:
    """True si le skill est BLOQUE par veto. False sinon."""
    if not getattr(manifest, "veto_capable", False):
        return False
    mf = getattr(manifest, "coherence_multi_frame", None)
    if mf is None or "securite" not in mf:
        return False
    s_sec = compute_S(state.beta,
                      state.delta_phi + mf["securite"]["expected_delta_phi"],
                      state.T + mf["securite"]["expected_T_added"],
                      state.sigma + mf["securite"]["expected_sigma_added"])
    return s_sec < seuil
```

Skills filtrés ne paraissent pas dans le résultat de `route()`.

### 3.4 Trace runtime

`run_once()` ajoute deux champs à la trace si V2 :

```json
{
  ...,
  "s_per_frame": { "structure": 1.23, "securite": 0.95, ... },
  "futur_probable_alerte": [
    {"horizon_an": 30, "evenement": "...", "probabilite": 0.75}
  ]
}
```

## 4. Invariants V2 (s'ajoutent aux invariants V1)

- **INV-10 — Rétrocompatibilité absolue** : un skill V1 doit continuer de marcher sans modification. Toute évolution V2 est purement additive.
- **INV-11 — INV-1 préservé par cadre** : chaque cadre suit `(1 + T + σ)`. Pas de produit T×σ caché dans la pondération.
- **INV-12 — Veto déterministe** : `_veto_securite(manifest, state)` appelé deux fois sur (manifest, state) identiques renvoie le même résultat.
- **INV-13 — Loi 10 traçable** : les `limites_explicites` du skill apparaissent dans la trace si le skill est sélectionné, pour que l'IA appelante les voie.

## 5. Exemple complet — `verif_seisme_classe1_asn` migré V2

```json
{
  "schema_version": "2.0",
  "identity": { ... },
  "routing": { ... },

  "coherence": { ... },

  "coherence_multi_frame": {
    "structure":    { "expected_delta_phi": 0.85, "expected_T_added": 0.05, "expected_sigma_added": 0.10, "weight": 0.30 },
    "securite":     { "expected_delta_phi": 0.90, "expected_T_added": 0.05, "expected_sigma_added": 0.05, "weight": 0.40 },
    "cout":         { "expected_delta_phi": 0.30, "expected_T_added": 0.10, "expected_sigma_added": 0.00, "weight": 0.10 },
    "maintenance":  { "expected_delta_phi": 0.40, "expected_T_added": 0.00, "expected_sigma_added": 0.05, "weight": 0.10 },
    "exploitation": { "expected_delta_phi": 0.50, "expected_T_added": 0.00, "expected_sigma_added": 0.05, "weight": 0.10 }
  },

  "futur_probable": [
    {
      "horizon_an": 50,
      "evenement": "Re-evaluation aleas sismiques (mise a jour donnees IRSN)",
      "probabilite": 0.80,
      "gravite": "elevee",
      "reference": "RFS 2001-01 §3 + reactualisations periodiques ASN"
    }
  ],

  "veto_capable": true,

  "limites_explicites": [
    "MVP demonstratif : marge SMS / PGA seulement. Ne remplace pas une note de calcul EIPS complete (IRSN + AREVA/EDF + audit ASN).",
    "Ne couvre pas les effets secondaires : liquefaction, glissement, tsunami.",
    "Spectre de reponse non integre : seuls PGA scalaires verifies."
  ]
}
```

## 6. Migration & adoption

- Les **5 skills BTP Phase A** sont migrés vers V2 dans la même session que la mise en place du contrat (preuve d'usage).
- Les **5 skills d'exemple V1** (echo, greet, etc.) restent V1 inchangés — preuve de rétrocompatibilité.
- Les **skills BTP Phase B+ (pathologies, fluides, géotechnique, infra, nucléaire)** sont créés directement V2.

## 7. Test (validation)

Voir `tests/test_contract_v2.py` : ~20 assertions couvrant manifest, engine multi-frame, veto router, rétrocompatibilité V1, trace enrichie.

---

*Spec V2 — gelée 2026-05-21. Toute évolution future = V2.1 ou V3 avec migration documentée.*
