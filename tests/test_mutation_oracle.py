"""tests/test_mutation_oracle.py — Test de mutation du skill oracle.

Mission : ZORAN_ORACLE_AGENTIC_BRIDGE_20260522 (suite — durcissement).
Signé : Claude Code, 2026-05-22.

Mutation testing maison, zéro dépendance. On applique une à une des mutations à
`skills_examples/zoran_oracle_adaptation_agents/skill.py` — opérateurs de
comparaison, booléens, arithmétiques, constantes booléennes — et on vérifie que
la batterie de contrôle DÉTECTE chaque mutant (le « tue »).

Un mutant TUÉ = la batterie observe une différence de comportement vs le code
original. Un mutant SURVIVANT = aucune différence observée : soit un mutant
équivalent (alors listé et justifié dans EQUIVALENTS), soit un trou de test
réel — et dans ce cas ce fichier ÉCHOUE.

Pourquoi maison et pas mutmut : le Loader vérifie le sha256 de skill.py. Un
outil qui mute le fichier sur disque ferait échouer le chargement par le hash
(INV-4), tuant tous les mutants trivialement — un faux 100 %. Ici on exécute le
code muté DIRECTEMENT, en contournant le Loader, pour éprouver la logique elle-même.

Exécutable : python tests/test_mutation_oracle.py
"""

from __future__ import annotations

import ast
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKILL = ROOT / "skills_examples" / "zoran_oracle_adaptation_agents" / "skill.py"

# Mutants équivalents connus : une mutation sémantiquement indistinguable du
# code original (aucune entrée ne peut les séparer). Clé = description du mutant.
# Tout SURVIVANT hors de cette liste est un échec.
EQUIVALENTS: set[str] = set()

CMP_FLIP = {ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.LtE: ast.Gt, ast.Gt: ast.LtE,
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.In: ast.NotIn,
            ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}
BIN_FLIP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div,
            ast.Div: ast.Mult}
BOOL_FLIP = {ast.And: ast.Or, ast.Or: ast.And}


def _etapes(*statuts: str) -> list[dict]:
    """Construit une liste d'étapes (charge 1.0) à partir de leurs statuts."""
    return [{"id": f"e{i}", "statut": s, "charge": 1.0}
            for i, s in enumerate(statuts)]


# Batterie de contrôle : exerce les 5 verdicts, l'allocation, le budget, le
# journal, l'estimation de cycles, les bornes et tous les cas d'erreur.
BATTERY: list[dict] = [
    # TERMINE
    {"etapes": _etapes("fait", "fait"),
     "agents_disponibles": {"api": 2, "local": 2}, "budget_restant": 100},
    # CONTINUER — locaux d'abord, puis API
    {"etapes": _etapes("a_faire", "a_faire", "a_faire", "a_faire"),
     "agents_disponibles": {"api": 5, "local": 2}, "budget_restant": 100,
     "cout_api_par_agent": 1.0},
    # CONTINUER — API plafonnée par le budget
    {"etapes": _etapes("a_faire", "a_faire", "a_faire", "a_faire"),
     "agents_disponibles": {"api": 5, "local": 0}, "budget_restant": 3,
     "cout_api_par_agent": 1.0},
    # STOP_INCOHERENCE (prioritaire sur le budget)
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 5, "local": 5}, "budget_restant": 100,
     "coherence_courante": 0.2, "seuil_coherence": 0.3},
    # cohérence exactement au seuil → PAS d'incohérence
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 1, "local": 0}, "budget_restant": 100,
     "coherence_courante": 0.3, "seuil_coherence": 0.3},
    # STOP_BUDGET
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 5, "local": 5}, "budget_restant": 0,
     "coherence_courante": 1.0},
    # STOP_RESSOURCE — aucun agent
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 0, "local": 0}, "budget_restant": 100},
    # STOP_RESSOURCE — API non finançable
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 3, "local": 0}, "budget_restant": 5,
     "cout_api_par_agent": 100.0},
    # en_cours sans a_faire → CONTINUER, 0 agent neuf
    {"etapes": _etapes("fait", "en_cours"),
     "agents_disponibles": {"api": 2, "local": 2}, "budget_restant": 10},
    # progression pondérée par la charge (3/4 = 75 %)
    {"etapes": [{"id": "e1", "statut": "fait", "charge": 3},
                {"id": "e2", "statut": "a_faire", "charge": 1}],
     "agents_disponibles": {"api": 1, "local": 0}, "budget_restant": 10},
    # journal cumulatif fourni + cycle explicite
    {"etapes": _etapes("a_faire"),
     "agents_disponibles": {"api": 1, "local": 0}, "budget_restant": 50,
     "cycle": 3, "journal": [{"sequence": 1}, {"sequence": 2}]},
    # estimation de cycles : charge / débit, charge_par_agent custom
    {"etapes": _etapes("a_faire", "a_faire", "a_faire", "a_faire"),
     "agents_disponibles": {"api": 0, "local": 2}, "budget_restant": 100,
     "charge_par_agent": 2.0},
    # allocation : local exactement égal au besoin
    {"etapes": _etapes("a_faire", "a_faire"),
     "agents_disponibles": {"api": 4, "local": 2}, "budget_restant": 100},
    # cas d'erreur attendus (ValueError)
    {"etapes": [], "agents_disponibles": {"api": 1}},
    {"etapes": [{"id": "e1", "statut": "peut-etre"}],
     "agents_disponibles": {"api": 1}},
    {"etapes": [{"id": "", "statut": "a_faire"}],
     "agents_disponibles": {"api": 1}},
    {"etapes": [{"id": "e1", "statut": "a_faire", "charge": 0}],
     "agents_disponibles": {"api": 1}},
    {"etapes": [{"id": "e1", "statut": "a_faire", "charge": -2}],
     "agents_disponibles": {"api": 1}},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "coherence_courante": 1.5},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "budget_restant": -10},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "cycle": 0},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": -1}},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"local": -1}},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "budget_restant": float("inf")},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "coherence_courante": float("nan")},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "cout_api_par_agent": 0},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "charge_par_agent": -1},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "seuil_coherence": 2.0},
    # type des champs numériques : rejet d'un non-nombre et d'un booléen
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "budget_restant": "100"},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "budget_restant": True},
    # type du nombre d'agents : rejet d'un booléen et d'un flottant
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": True}},
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1.5}},
    # borne stricte de charge_par_agent : 0 doit être refusé
    {"etapes": _etapes("a_faire"), "agents_disponibles": {"api": 1},
     "charge_par_agent": 0},
    # CONTINUER avec un coût API != 1.0 (sépare api*cout de api/cout)
    {"etapes": _etapes("a_faire", "a_faire", "a_faire", "a_faire"),
     "agents_disponibles": {"api": 5, "local": 0}, "budget_restant": 100,
     "cout_api_par_agent": 2.0},
]


def load_run(source: str):
    """Compile et exécute un code source, renvoie sa fonction `run`."""
    namespace: dict = {}
    exec(compile(source, "<oracle-mutant>", "exec"), namespace)  # noqa: S102
    return namespace["run"]


def behaviour(run_fn) -> list:
    """Comportement observable de `run` sur toute la batterie."""
    observed = []
    for payload in BATTERY:
        try:
            observed.append(("ok", run_fn(copy.deepcopy(payload))))
        except ValueError:
            observed.append(("ValueError", None))
        except Exception as exc:  # noqa: BLE001
            observed.append((type(exc).__name__, None))
    return observed


def collect(tree: ast.AST) -> list:
    """Liste ordonnée et déterministe des nœuds mutables d'un arbre."""
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 \
                and type(node.ops[0]) in CMP_FLIP:
            targets.append((node, "cmp"))
        elif isinstance(node, ast.BoolOp):
            targets.append((node, "bool"))
        elif isinstance(node, ast.BinOp) and type(node.op) in BIN_FLIP:
            targets.append((node, "bin"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            targets.append((node, "const"))
    return targets


def mutate(node, kind: str) -> str:
    """Applique la mutation au nœud, renvoie sa description."""
    if kind == "cmp":
        old = type(node.ops[0])
        node.ops[0] = CMP_FLIP[old]()
        return f"cmp {old.__name__}->{CMP_FLIP[old].__name__}"
    if kind == "bool":
        old = type(node.op)
        node.op = BOOL_FLIP[old]()
        return f"bool {old.__name__}->{BOOL_FLIP[old].__name__}"
    if kind == "bin":
        old = type(node.op)
        node.op = BIN_FLIP[old]()
        return f"bin {old.__name__}->{BIN_FLIP[old].__name__}"
    old_value = node.value
    node.value = not node.value
    return f"const {old_value}->{node.value}"


def main() -> int:
    source = SKILL.read_text(encoding="utf-8")
    reference = behaviour(load_run(source))
    total_targets = len(collect(ast.parse(source)))

    killed, survivors = 0, []
    for index in range(total_targets):
        tree = ast.parse(source)
        node, kind = collect(tree)[index]
        label = f"L{node.lineno}C{node.col_offset} {mutate(node, kind)}"
        ast.fix_missing_locations(tree)
        try:
            mutant_run = load_run(ast.unparse(tree))
            tue = behaviour(mutant_run) != reference
        except Exception:  # noqa: BLE001
            tue = True  # un mutant qui ne compile/charge plus est tué
        if tue:
            killed += 1
        else:
            survivors.append(label)

    print("=" * 60)
    print("TEST DE MUTATION — zoran_oracle_adaptation_agents")
    print("=" * 60)
    print(f"mutants générés : {total_targets}")
    print(f"tués            : {killed}")
    print(f"survivants      : {len(survivors)}")

    non_justifies = [s for s in survivors if s not in EQUIVALENTS]
    for s in survivors:
        etat = "ÉQUIVALENT (justifié)" if s in EQUIVALENTS else "TROU DE TEST"
        print(f"  survivant : {s}  → {etat}")

    score = 100.0 * killed / total_targets if total_targets else 0.0
    print(f"score de détection : {score:.1f}%")
    print("=" * 60)
    if non_justifies:
        print(f"=== ÉCHEC : {len(non_justifies)} mutant(s) survivant(s) "
              "non justifié(s) ===")
        return 1
    print("=== RESULTAT : tous les mutants tués ou justifiés équivalents ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
