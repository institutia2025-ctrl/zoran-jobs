# PHASE 4 — TOXIC LOCAL COHERENCE DETECTION

**Mission** : `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521` · **Doc 2/5**
**Date** : 2026-05-21 · **Statut** : pré-audit, AUCUN code
**Signé** : Claude, prestataire

> Une **cohérence locale toxique** : un skill excellent dans son cadre code,
> destructeur ailleurs. C'est la menace que l'Oracle mono-cadre ne voit pas.
> Ce document définit comment la *détecter*.

---

## 1. Définition

Un skill est en **cohérence locale toxique** quand :

```
S_code  est ÉLEVÉ        (il est propre, stable, efficace, déterministe)
   ET
S_global est BAS         (il dégrade sécurité / user / système / écosystème)
```

Le malware est l'archétype : pour réussir son attaque, il DOIT être bien
écrit — donc `S_code` haut. C'est précisément ce qui le rend dangereux : il
**passe** un audit de qualité de code.

---

## 2. La signature de détection

Le signal n'est pas la valeur de `S_code`, ni celle de `S_global` — c'est
**l'ÉCART entre les deux** :

```
toxicité_locale  =  S_code  −  S_global
```

| `S_code` | `S_global` | écart | Interprétation |
|---|---|---|---|
| bas | bas | ~0 | skill mauvais — rejeté pour incompétence |
| haut | haut | ~0 | skill **sain** — aligné dans tous les cadres |
| bas | haut | < 0 | improbable (un skill mal codé rarement globalement bon) |
| **haut** | **bas** | **grand** | 🚨 **COHÉRENCE LOCALE TOXIQUE** |

→ **Un écart `S_code − S_global` important est le marqueur d'alerte.** Plus un
skill est « bien fait » tout en ayant un `S_global` bas, plus il est suspect :
la qualité technique au service d'un objectif désaligné.

---

## 3. Méthodes de détection (toutes sans exécuter le skill en confiance)

| Méthode | Détecte | Cadre concerné |
|---|---|---|
| **Écart inter-cadres** | `S_code` ≫ `min(autres cadres)` | tous |
| **Permissions vs comportement** | accès observés en sandbox > permissions déclarées | `S_security` |
| **Effets de bord** | le skill modifie l'état/le FS/d'autres skills | `S_runtime`, `S_ecosystem` |
| **Asymétrie déclaration/réalité** | manifest sobre, comportement runtime intrusif | `S_security`, `S_user` |
| **Intention cachée** | code propre mais finalité non déclarée (exfiltration, mining) | `S_user`, `S_system` |

Aucune méthode seule ne suffit. La détection est la **conjonction** : un skill
qui déclenche plusieurs signaux est toxique avec une forte probabilité.

---

## 4. Le piège à éviter absolument

> Ne JAMAIS valider un skill sur son seul `S_code`.

C'est l'erreur que l'Oracle Phase 2 commettrait s'il était utilisé tel quel en
Phase 4. Phase 2 a déjà prouvé qu'il détecte la non-conformité (`greet_ko`) —
mais `greet_ko` était *incompétent*. Le malware, lui, est *compétent*. Le
détecter exige les 7 cadres, pas un seul.

---

## 5. Réaction à une cohérence locale toxique

Un skill détecté toxique :
1. ne passe **jamais** `quarantined → verified` (cf. `PHASE_4_TRUST_MODEL.md`) ;
2. son hash est ajouté à la liste noire (`banned`) si la toxicité est avérée ;
3. l'incident est journalisé (journal signé Phase 3) avec les 7 valeurs de S —
   pour que la décision soit reconstructible et falsifiable.

---

## 6. Limites

- L'écart `S_code − S_global` détecte la toxicité **flagrante**. Une toxicité
  *lente* (skill qui se comporte bien longtemps puis bascule) demande une
  observation prolongée — d'où la promotion lente du Trust Model.
- Un attaquant connaissant cette métrique pourrait **dégrader volontairement**
  son `S_code` pour réduire l'écart. Contre-mesure : les cadres `S_security`/
  `S_user` restent en VETO absolu — un `S_security` bas rejette, quel que soit
  l'écart.

---

*Doc 2/5 — TOXIC_LOCAL_COHERENCE. `ZORAN_JOBS_PHASE4_SAFE_GOVERNANCE_20260521`. Aucun code produit.*
