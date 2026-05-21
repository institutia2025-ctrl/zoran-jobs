"""skill Barrière de progression cohérente — discipline de ticket ZORAN.

Mission : ZORAN_JOBS_20260521 · skill méta de gouvernance.
Inspiration : discipline ZORAN — journalisation intégrale, checklist, refus de
dévier, validation obligatoire (back + front + tests massifs) avant de passer
au ticket suivant.

Ce skill est le CERVEAU DÉTERMINISTE de la discipline de progression : il DÉCIDE
si un ticket peut être validé et si l'on peut passer au suivant. Il n'exécute
pas les tests lui-même — un skill du runtime est une fonction pure, sans réseau
ni process (invariant). Il reçoit l'état réel des validations et agit comme une
barrière incorruptible.

Règle dure : on n'avance JAMAIS tant qu'un item de la checklist n'est pas `ok`,
ni tant qu'une validation obligatoire (back, front, tests massifs…) n'est pas
verte. Chaque évaluation produit une entrée de journal.

⚠️ MVP : le skill DÉCIDE et JOURNALISE. L'exécution réelle des tests massifs et
la surveillance multi-agents relèvent du harnais agentique, pas d'un skill pur.
Loi 1 : aucune validation n'est supposée — chaque statut est fourni explicitement.

Contrat io :
    inputs  : {ticket, checklist:[{item,statut}], validations_obligatoires?, journal?}
    outputs : {peut_avancer, items_bloquants, journal, prochaine_action, verdict, reference}
"""

from __future__ import annotations

STATUTS = {"ok", "ko", "pending"}


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    ticket = str(inputs.get("ticket", "")).strip()
    if not ticket:
        raise ValueError("ticket : identifiant non vide requis")
    checklist = inputs.get("checklist")
    if not isinstance(checklist, list) or not checklist:
        raise ValueError("checklist : liste non vide attendue")
    obligatoires = [str(x) for x in (inputs.get("validations_obligatoires") or [])]
    journal = list(inputs.get("journal") or [])

    items: dict[str, str] = {}
    for i, it in enumerate(checklist):
        it = it or {}
        nom = str(it.get("item", "")).strip()
        statut = str(it.get("statut", "")).lower()
        if not nom:
            raise ValueError(f"checklist[{i}].item : nom non vide requis")
        if statut not in STATUTS:
            raise ValueError(f"checklist[{i}].statut : attendu l'un de {sorted(STATUTS)}")
        items[nom] = statut

    # Bloquants : tout item non `ok`, plus toute validation obligatoire absente.
    bloquants = [f"{nom} ({statut})" for nom, statut in items.items() if statut != "ok"]
    for req in obligatoires:
        if req not in items:
            bloquants.append(f"{req} (validation obligatoire absente de la checklist)")

    peut_avancer = not bloquants
    nb_ok = sum(1 for s in items.values() if s == "ok")

    entree = {
        "sequence": len(journal) + 1,
        "ticket": ticket,
        "verdict": "AVANCE" if peut_avancer else "BLOQUE",
        "items_ok": nb_ok,
        "items_total": len(items),
        "bloquants": list(bloquants),
    }
    journal_maj = journal + [entree]

    if peut_avancer:
        action = f"Ticket '{ticket}' validé — passage au ticket suivant autorisé."
    else:
        action = (f"Rester sur '{ticket}' — ne pas dévier. À traiter : "
                  + " ; ".join(bloquants))

    return {
        "peut_avancer": peut_avancer,
        "ticket": ticket,
        "nb_items_ok": nb_ok,
        "nb_items_total": len(items),
        "items_bloquants": bloquants,
        "journal": journal_maj,
        "prochaine_action": action,
        "verdict": ("Progression cohérente autorisée."
                    if peut_avancer else
                    f"Progression BLOQUÉE — {len(bloquants)} point(s) non validé(s)."),
        "reference": "Discipline de progression ZORAN — journalisation + checklist + barrière dure",
    }
