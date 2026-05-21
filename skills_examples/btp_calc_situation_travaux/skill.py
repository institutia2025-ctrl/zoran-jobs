"""skill Calcul d'une situation de travaux (décompte mensuel).

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Économie.
Source : usage des marchés de travaux — situation mensuelle, retenue de
garantie (CCAG Travaux et pratique courante).

Calcule un décompte mensuel d'avancement :
- travaux réalisés = montant du marché × avancement,
- retenue de garantie prélevée sur les travaux réalisés,
- montant cumulé dû = travaux réalisés − retenue,
- acompte de la période = montant cumulé dû − déjà payé.

⚠️ MVP : décompte HT, avancement global. Ne traite pas la révision de prix
(voir btp_calc_revision_prix), ni la TVA, ni les pénalités, ni le compte
prorata, ni la libération de la retenue de garantie.
Loi 1 : taux de retenue et avancement sont fournis ; aucune valeur supposée.

Contrat io :
    inputs  : {montant_marche_ht, avancement_pct, retenue_garantie_pct?, deja_paye_ht?}
    outputs : {travaux_realises_ht, retenue_garantie_ht, montant_cumul_du_ht,
               acompte_periode_ht, reference}
"""

from __future__ import annotations

RETENUE_GARANTIE_DEFAUT_PCT = 5.0  # taux usuel de retenue de garantie


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    montant = inputs.get("montant_marche_ht")
    avancement = inputs.get("avancement_pct")
    retenue_pct = inputs.get("retenue_garantie_pct", RETENUE_GARANTIE_DEFAUT_PCT)
    deja_paye = inputs.get("deja_paye_ht", 0.0)

    if not _nombre(montant) or montant <= 0:
        raise ValueError("montant_marche_ht : nombre > 0 requis")
    if not _nombre(avancement) or not (0.0 <= avancement <= 100.0):
        raise ValueError("avancement_pct : nombre dans [0..100] requis")
    if not _nombre(retenue_pct) or not (0.0 <= retenue_pct <= 100.0):
        raise ValueError("retenue_garantie_pct : nombre dans [0..100] requis")
    if not _nombre(deja_paye) or deja_paye < 0:
        raise ValueError("deja_paye_ht : nombre >= 0 requis")

    travaux = float(montant) * float(avancement) / 100.0
    retenue = travaux * float(retenue_pct) / 100.0
    cumul_du = travaux - retenue
    acompte = cumul_du - float(deja_paye)
    return {
        "travaux_realises_ht": round(travaux, 2),
        "retenue_garantie_ht": round(retenue, 2),
        "montant_cumul_du_ht": round(cumul_du, 2),
        "acompte_periode_ht": round(acompte, 2),
        "reference": "Situation de travaux — décompte mensuel + retenue de garantie (CCAG Travaux)",
    }
