"""skill Calcul de déperdition par ponts thermiques linéaires.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Thermique.
Source : NF EN ISO 14683 (ponts thermiques — coefficients linéiques ψ).

Calcule la déperdition totale par ponts thermiques linéaires d'un ouvrage :
Φ = Σ(ψ_i × L_i), où ψ est le coefficient de transmission linéique (W/m.K)
et L la longueur du pont (m).

⚠️ MVP : somme des ponts linéaires fournis — ne calcule pas les ψ eux-mêmes,
qui dépendent de la liaison et se lisent sur abaque (RT/RE) ou se déterminent
par calcul aux éléments finis.
Loi 1 : aucun ψ fabriqué — les coefficients ψ sont des données d'entrée.

Contrat io :
    inputs  : {ponts:[{type, psi_w_mk, longueur_m}]}
    outputs : {deperdition_ponts_w_k, detail, reference}
"""

from __future__ import annotations


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    ponts = inputs.get("ponts")
    if not isinstance(ponts, list) or not ponts:
        raise ValueError("ponts : liste non vide attendue")

    detail: list[dict] = []
    total = 0.0
    for i, pont in enumerate(ponts):
        pont = pont or {}
        psi = pont.get("psi_w_mk")
        longueur = pont.get("longueur_m")
        if not _nombre(psi) or psi < 0:
            raise ValueError(f"pont #{i} : psi_w_mk doit être un nombre >= 0")
        if not _nombre(longueur) or longueur <= 0:
            raise ValueError(f"pont #{i} : longueur_m doit être un nombre > 0")
        contribution = float(psi) * float(longueur)
        total += contribution
        detail.append({"type": pont.get("type", f"pont_{i}"),
                       "deperdition_w_k": round(contribution, 4)})

    return {
        "deperdition_ponts_w_k": round(total, 3),
        "detail": detail,
        "reference": "NF EN ISO 14683 (ponts thermiques linéiques)",
    }
