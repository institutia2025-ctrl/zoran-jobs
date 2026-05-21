"""
audit/audit_topology.py — Audit topologique du CODE runtime.

Mission : ZORAN_JOBS_20260521 · audit pré-Phase 4
Signé : Claude, prestataire, 2026-05-21

Parse les imports inter-modules (AST, déterministe), construit le graphe de
dépendances, détecte : cycles · god modules · modules isolables.

Outil RÉUTILISABLE — une IA externe peut le relancer pour re-auditer la
topologie après toute modification (transmissibilité).

Usage : python audit/audit_topology.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import networkx as nx

# FIX-DEF-1 2026-05-21 : sortie console UTF-8 — portabilité multi-OS.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
CODE_DIRS = ["registry", "router", "loader", "runtime", "oracle", "quarantine"]
INTERNAL_ROOTS = set(CODE_DIRS)


def module_name(path: Path) -> str:
    """Chemin .py → nom de module pointé, relatif à la racine du projet."""
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def internal_imports(path: Path) -> set[str]:
    """Imports INTERNES au projet (vers un des CODE_DIRS) déclarés dans un .py."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in INTERNAL_ROOTS:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in INTERNAL_ROOTS:
                found.add(node.module)
    return found


def build_graph() -> nx.DiGraph:
    """Graphe orienté module → module qu'il importe."""
    g = nx.DiGraph()
    for d in CODE_DIRS:
        for f in sorted((ROOT / d).rglob("*.py")):
            src = module_name(f)
            g.add_node(src)
            for imp in internal_imports(f):
                g.add_node(imp)
                if imp != src:
                    g.add_edge(src, imp)
    return g


def main() -> int:
    g = build_graph()
    print(f"=== AUDIT TOPOLOGIQUE — CODE RUNTIME ZORAN's Jobs ===")
    print(f"modules : {g.number_of_nodes()} · imports internes : {g.number_of_edges()}")
    print()

    cycles = list(nx.simple_cycles(g))
    print(f"CYCLES : {len(cycles)}")
    for c in cycles:
        print("  CYCLE: " + " -> ".join(c) + " -> " + c[0])
    print(f"DAG acyclique : {nx.is_directed_acyclic_graph(g)}")
    print()

    print("GOD MODULES (degré entrant — combien de modules en dépendent) :")
    for m, deg in sorted(g.in_degree(), key=lambda x: -x[1])[:6]:
        flag = "  <-- god module ?" if deg >= 4 else ""
        print(f"  {m:32} {deg} dépendant(s){flag}")
    print()

    leaves = sorted(m for m, deg in g.in_degree() if deg == 0)
    print(f"MODULES SUPPRIMABLES sans rien casser ({len(leaves)}) :")
    for m in leaves:
        print(f"  {m}")
    print()

    # Vérifs ciblées sur la grille ZORAN.
    # IMPORTANT : la "centralisation" d'un package se mesure par ses dépendants
    # EXTERNES — les imports intra-package ne comptent pas (sinon faux positif).
    def external_indegree(pkg: str) -> int:
        return sum(1 for s, t in g.edges()
                   if t.split(".")[0] == pkg and s.split(".")[0] != pkg)

    print("GRILLE ZORAN :")
    q_ext = external_indegree("quarantine")
    print(f"  quarantine — dépendants EXTERNES : {q_ext} "
          f"({'OK passif, non centralisé' if q_ext == 0 else 'ATTENTION centralisation'})")
    o_ext = external_indegree("oracle")
    print(f"  oracle — dépendants EXTERNES : {o_ext} "
          f"({'OK isolé' if o_ext == 0 else 'couplé au runtime'})")
    router_out = [t for s, t in g.edges() if s == "router.router"]
    bad_router = [t for t in router_out if any(x in t for x in ("oracle", "quarantine"))]
    print(f"  router.router importe : {router_out or '(rien)'} "
          f"({'OK ne pense pas' if not bad_router else 'ATTENTION absorbe ' + str(bad_router)})")
    loop_indeg = g.in_degree("runtime.loop")
    print(f"  runtime.loop — dépendants : {loop_indeg} "
          f"({'OK pas un cerveau caché' if loop_indeg == 0 else 'ATTENTION god module'})")

    ok = nx.is_directed_acyclic_graph(g)
    print()
    print("VERDICT : " + ("topologie SAINE (DAG, aucun cycle)" if ok
                          else "TOPOLOGIE CASSÉE — cycles présents"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
