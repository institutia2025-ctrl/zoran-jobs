"""skill planning_gantt_simple — conducteur de travaux.

Mission : ZORAN_JOBS_20260521 · Phase A BTP.
Algorithme : Critical Path Method (CPM) — méthode classique du chemin critique.
Référence : domaine public (Kelley & Walker, 1959 ; ISO 21500).

Calcule pour chaque tâche : ES (early start), EF (early finish), LS (late start),
LF (late finish), float (marge). Identifie les tâches critiques (float = 0).

Contrat io :
    inputs  : {
        "tasks": [
            {"id": str, "duree_j": int, "depends_on": list[str]},
            ...
        ]
    }
    outputs : {
        "schedule": [
            {"id": str, "ES": int, "EF": int, "LS": int, "LF": int,
             "float": int, "critique": bool}
        ],
        "duree_totale_j": int,
        "chemin_critique": list[str]
    }
"""

from __future__ import annotations


def run(inputs: dict) -> dict:
    inputs = inputs or {}
    tasks = inputs.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks (liste non vide) requis")

    by_id = {}
    for t in tasks:
        if not isinstance(t, dict) or "id" not in t or "duree_j" not in t:
            raise ValueError("chaque tache doit avoir id et duree_j")
        if not isinstance(t["duree_j"], int) or t["duree_j"] < 0:
            raise ValueError(f"duree_j de {t['id']} doit etre un entier >= 0")
        by_id[t["id"]] = {"id": t["id"], "duree": t["duree_j"],
                          "deps": list(t.get("depends_on", []))}

    # Forward pass : ES/EF
    sched = {}
    remaining = set(by_id)
    while remaining:
        progress = False
        for tid in list(remaining):
            t = by_id[tid]
            if all(d in sched for d in t["deps"]):
                es = max((sched[d]["EF"] for d in t["deps"]), default=0)
                sched[tid] = {"ES": es, "EF": es + t["duree"]}
                remaining.discard(tid)
                progress = True
        if not progress:
            raise ValueError("dependances cycliques ou manquantes")

    duree_totale = max(s["EF"] for s in sched.values())

    # Backward pass : LF/LS, float
    # Successeurs
    succ = {tid: [] for tid in by_id}
    for tid, t in by_id.items():
        for d in t["deps"]:
            succ[d].append(tid)

    for tid in by_id:
        sched[tid]["LF"] = duree_totale
    # ordre topologique inverse
    order = sorted(by_id, key=lambda x: -sched[x]["EF"])
    for tid in order:
        if succ[tid]:
            sched[tid]["LF"] = min(sched[s]["LS"] if "LS" in sched[s] else duree_totale
                                    for s in succ[tid])
        sched[tid]["LS"] = sched[tid]["LF"] - by_id[tid]["duree"]
        sched[tid]["float"] = sched[tid]["LS"] - sched[tid]["ES"]
        sched[tid]["critique"] = sched[tid]["float"] == 0

    schedule = [{"id": tid, **sched[tid]} for tid in by_id]
    chemin = sorted([tid for tid in by_id if sched[tid]["critique"]],
                    key=lambda x: sched[x]["ES"])
    return {"schedule": schedule, "duree_totale_j": duree_totale, "chemin_critique": chemin}
