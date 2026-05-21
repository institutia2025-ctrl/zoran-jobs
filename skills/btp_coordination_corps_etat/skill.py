"""
skill btp_coordination_corps_etat — Coordination des corps d'état.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (conduite)
Méthode : graphe d'antécédence — tri topologique (Kahn) + chemin critique.
Point d'entrée : run(inputs: dict) -> dict.

À partir d'une liste de tâches (id, durée, prédécesseurs), calcule un ordre
d'exécution réalisable, détecte les cycles de dépendances, et identifie le
chemin critique (durée totale du chantier).
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json."""
    inp = inputs or {}
    taches = inp.get("taches") or []

    by_id: dict[str, dict] = {}
    for t in taches:
        t = t or {}
        tid = str(t.get("id", "")).strip()
        if tid:
            by_id[tid] = {
                "id": tid,
                "nom": str(t.get("nom", tid)),
                "duree": float(t.get("duree", 0.0)),
                "predecesseurs": [str(p) for p in (t.get("predecesseurs") or [])],
            }

    # Tri topologique (algorithme de Kahn). Un reliquat => cycle.
    indeg = {tid: 0 for tid in by_id}
    for t in by_id.values():
        for p in t["predecesseurs"]:
            if p in by_id:
                indeg[t["id"]] += 1
    file = sorted(tid for tid, d in indeg.items() if d == 0)
    ordre: list[str] = []
    restant = dict(indeg)
    while file:
        cur = file.pop(0)
        ordre.append(cur)
        for t in sorted(by_id.values(), key=lambda x: x["id"]):
            if cur in t["predecesseurs"]:
                restant[t["id"]] -= 1
                if restant[t["id"]] == 0:
                    file.append(t["id"])
        file.sort()
    cycle = len(ordre) != len(by_id)

    # Chemin critique : date de fin au plus tôt, puis remontée.
    chemin_critique: list[str] = []
    duree_totale = 0.0
    if not cycle and by_id:
        fin: dict[str, float] = {}
        for tid in ordre:
            t = by_id[tid]
            debut = max((fin[p] for p in t["predecesseurs"] if p in fin), default=0.0)
            fin[tid] = debut + t["duree"]
        duree_totale = max(fin.values())
        cur = max(fin, key=lambda k: fin[k])
        while cur:
            chemin_critique.append(cur)
            preds = [p for p in by_id[cur]["predecesseurs"] if p in fin]
            cur = max(preds, key=lambda k: fin[k]) if preds else None
        chemin_critique.reverse()

    return {
        "ordre_execution": ordre,
        "cycle_detecte": cycle,
        "chemin_critique": chemin_critique,
        "duree_totale": round(duree_totale, 2),
        "nb_taches": len(by_id),
        "verdict": ("Cycle de dépendances détecté — planning irréalisable."
                    if cycle else
                    f"Planning cohérent — durée totale {round(duree_totale, 2)}."),
    }
