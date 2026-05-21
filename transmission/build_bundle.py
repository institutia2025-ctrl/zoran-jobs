"""
transmission/build_bundle.py — Générateur du bundle de transmission mono-fichier.

Mission : ZORAN_AI_NATIVE_TRANSMISSION_20260521
Signé : Claude, prestataire, 2026-05-21

OBJECTIF (Fred → Xavier) : pouvoir donner UN SEUL fichier à une IA, et que cette
IA — avec ce fichier SEUL — soit capable de tout mettre en œuvre : comprendre le
projet, reconstruire le dépôt, lancer les 85 tests, faire revivre le runtime,
et s'arrêter aux bonnes frontières.

Ce script empaquète TOUT le dépôt zoran-jobs dans un fichier texte unique et
auto-suffisant : `ZORAN_JOBS_TRANSMISSION_BUNDLE.md` (écrit à côté du dépôt).
Ce fichier contient, dans l'ordre :
  1. le bootstrap IA-native (instructions à l'IA) ;
  2. un EXTRACTEUR AUTONOME — un bloc Python copiable/exécutable qui reconstruit
     le dépôt, vérifie tous les hash et lance les 85 tests, SANS dépendance ;
  3. chaque fichier du projet, délimité par des marqueurs vérifiables
     (compte d'octets + sha256).

C'est le mode « ChatGPT-native » : Xavier dépose le fichier, l'IA exécute le
bloc extracteur, le projet revit. L'IA peut aussi reconstruire à la main.

Outil RÉUTILISABLE et DÉTERMINISTE — relançable après toute modification du
dépôt pour régénérer un bundle à jour. Conforme à la philosophie du projet :
falsifiable (chaque fichier est vérifiable par hash), transmissible (le bundle
se suffit à lui-même), jetable (ce script est supprimable sans rien casser).

USAGE :
  python transmission/build_bundle.py
      → construit ZORAN_JOBS_TRANSMISSION_BUNDLE.md

  python transmission/build_bundle.py --extract <bundle.md> <dossier_cible>
      → reconstruit le dépôt depuis un bundle, et vérifie tous les hash
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / "ZORAN_JOBS_TRANSMISSION_BUNDLE.md"

# Exclus : caches Python, artefacts d'outillage, archives, bundles eux-mêmes.
EXCLUDE_DIRS = {"__pycache__", "graphify-out", ".git", ".idea", ".vscode"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip", ".pyd"}
EXCLUDE_NAMES = {OUT.name, "_verify_bundle_tmp.py"}

# Marqueurs de bloc. La collision avec un contenu de fichier est neutralisée
# par la vérification du compte d'octets + sha256 à l'extraction.
F_START = ">>>>> ZORAN-JOBS FILE START"
F_END = "<<<<< ZORAN-JOBS FILE END"
# L'ancre est construite par concaténation : ainsi la chaîne entière n'apparaît
# JAMAIS littéralement dans le code source (ni ici, ni dans l'extracteur
# embarqué). Elle n'existe donc qu'une seule fois dans le bundle — à la
# position structurelle écrite par build(). Cela évite que `find(ancre)` tombe
# sur une mention pédagogique de l'en-tête au lieu du vrai début des fichiers.
FILES_ANCHOR = "## ── FICHIERS " + "DU DÉPÔT ──"


# ── EXTRACTEUR AUTONOME ─────────────────────────────────────────────────────
# Ce bloc est inséré tel quel dans l'en-tête du bundle, dans une clôture
# ```python. Une IA dotée d'un outil Python le copie et l'exécute : il
# reconstruit le dépôt et le valide, sans aucune dépendance ni fichier tiers.
# Volontairement autonome (pas d'import de build_bundle.py) : il doit tourner
# AVANT que quoi que ce soit ne soit extrait.
EMBEDDED_EXTRACTOR = r'''# ============================================================
#  ZORAN'S JOBS — EXTRACTEUR AUTONOME
#  IA : copie ce bloc ENTIER dans ton outil d'execution Python et lance-le.
#  Il reconstruit le depot complet, verifie chaque hash sha256, lance les
#  85 tests, puis te dit quoi faire ensuite. Aucune dependance. Python 3.11+.
# ============================================================
import hashlib, os, subprocess, sys
from pathlib import Path

# Chemin du bundle (le fichier .md recu). Laisse vide pour auto-detection ;
# renseigne-le si besoin, ex. "/mnt/data/ZORAN_JOBS_TRANSMISSION_BUNDLE.md".
BUNDLE_PATH = ""
DEST = "zoran-jobs"          # dossier de reconstruction
RUN_TESTS = True             # lance les 85 tests apres reconstruction

_SENTINEL = "BUNDLE DE TRANSMISSION AUTO-SUFFISANT"
_FS = ">>>>> ZORAN-JOBS FILE START"
_FE = "<<<<< ZORAN-JOBS FILE END"
# Ancre construite par concatenation : la chaine entiere n'apparait jamais
# litteralement ici, donc elle n'existe qu'une fois dans le bundle (au vrai
# debut des fichiers) et find() ne tombe pas sur une mention de l'en-tete.
_ANCHOR = "## ── FICHIERS " + "DU DÉPÔT ──"

def _locate():
    if BUNDLE_PATH and Path(BUNDLE_PATH).is_file():
        return Path(BUNDLE_PATH)
    found = []
    for d in (".", "/mnt/data", os.getcwd(), str(Path.home()),
              str(Path.home() / "Desktop")):
        p = Path(d)
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.md")):
            try:
                if _SENTINEL in f.read_bytes()[:800].decode("utf-8", "ignore"):
                    found.append(f)
            except Exception:
                pass
    return found[0] if found else None

_bundle = _locate()
if not _bundle:
    raise SystemExit("Bundle introuvable : renseigne BUNDLE_PATH en haut du bloc.")
print("Bundle :", _bundle)

_text = _bundle.read_bytes().decode("utf-8")
_dest = Path(DEST)
_pos = _text.find(_ANCHOR)
if _pos == -1:
    _pos = 0
_ok = _bad = 0
while True:
    _s = _text.find(_FS, _pos)
    if _s == -1:
        break
    _le = _text.index("\n", _s)
    _parts = [x.strip() for x in _text[_s:_le].split("::")]
    _rel, _nb = _parts[1], int(_parts[2])
    _declared = _parts[3].split(">>>>>")[0].strip()
    _end = "\n" + _FE + " :: " + _rel + " <<<<<"
    _e = _text.index(_end, _le + 1)
    _data = _text[_le + 1:_e].encode("utf-8")
    _tgt = _dest / _rel
    _tgt.parent.mkdir(parents=True, exist_ok=True)
    _tgt.write_bytes(_data)   # octets bruts : fins de ligne preservees
    if len(_data) == _nb and "sha256:" + hashlib.sha256(_data).hexdigest() == _declared:
        _ok += 1
    else:
        _bad += 1
        print("  HASH KO :", _rel)
    _pos = _e + len(_end)
print("Reconstruction :", _ok, "fichiers OK,", _bad, "KO  ->", _dest.resolve())
if _bad:
    raise SystemExit("Reconstruction incomplete — ne pas continuer.")

if RUN_TESTS:
    _tests = ["tests/test_registry.py", "tests/test_runtime_loop.py",
              "tests/test_cinematique.py", "tests/test_oracle.py",
              "tests/test_immune.py", "tests/stress/massive_validation.py"]
    print("Validation (85 assertions attendues, 0 echec) :")
    for _t in _tests:
        try:
            _r = subprocess.run([sys.executable, _t], cwd=str(_dest),
                                capture_output=True, text=True, timeout=120)
            _out = _r.stdout + _r.stderr
            _line = next((l for l in _out.splitlines()
                          if "PASS" in l and "FAIL" in l), "(pas de ligne resultat)")
        except Exception as _ex:
            _line = "(execution test impossible : %s)" % _ex
        print("  ", _t, "->", _line.strip())

print()
print("FAIT. Etape suivante : ouvre et suis", str(_dest / "transmission" / "AI_BOOTSTRAP.md"))
print("Rappel : tu ne dois PAS ouvrir la Phase 4 (statut NO-GO).")
'''


def collect_files() -> list[Path]:
    """Liste triée (déterministe) de tous les fichiers du dépôt à empaqueter."""
    files: list[Path] = []
    for p in sorted(ROOT.rglob("*"),
                    key=lambda x: str(x.relative_to(ROOT)).replace("\\", "/")):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(ROOT).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        if p.suffix in EXCLUDE_SUFFIXES or p.name in EXCLUDE_NAMES:
            continue
        files.append(p)
    return files


def rel(p: Path) -> str:
    """Chemin relatif POSIX (séparateur `/`) — portable Windows/Linux/macOS."""
    return str(p.relative_to(ROOT)).replace("\\", "/")


def header(n_files: int, total_bytes: int) -> str:
    """En-tête du bundle : bootstrap + extracteur autonome + démarrage."""
    part1 = f"""# ZORAN'S JOBS — BUNDLE DE TRANSMISSION AUTO-SUFFISANT

> **Ce fichier unique EST le projet entier.** Il contient le dépôt complet de
> ZORAN's Jobs ({n_files} fichiers, {total_bytes} octets de source), un
> extracteur autonome, et les instructions pour faire revivre le système.
> Donné à une IA, ce fichier seul suffit.

Mission : `ZORAN_AI_NATIVE_TRANSMISSION_20260521`
Généré par : `transmission/build_bundle.py` (déterministe, réutilisable)

---

## 🤖 POUR L'IA QUI LIT CE FICHIER

Tu viens de recevoir ce fichier, probablement de la part d'une personne qui
n'est pas développeuse et qui te demande de « tout mettre en œuvre ». Voici
exactement quoi faire. **Commence par résumer ce que tu as compris**, puis agis.

### Étape A — Reconstruis le dépôt · MÉTHODE RAPIDE (recommandée)

Si tu disposes d'un outil d'exécution Python (ChatGPT, Claude, etc.) : copie le
bloc **EXTRACTEUR AUTONOME** ci-dessous et exécute-le tel quel. Il reconstruit
les {n_files} fichiers du dépôt, vérifie chaque hash sha256, lance les 85 tests,
et t'indique l'étape suivante. C'est le mode « ChatGPT-native ».

"""
    fence = "```python\n" + EMBEDDED_EXTRACTOR + "```\n"
    part2 = f"""
### Étape A bis — Reconstruis le dépôt · MÉTHODE MANUELLE (sans outil Python)

Si tu n'as pas d'exécution Python, reconstruis à la main. Plus bas, chaque
fichier est encadré par deux marqueurs :

```
{F_START} :: <chemin/relatif> :: <nb_octets> :: sha256:<hash> >>>>>
<contenu exact du fichier, verbatim>
{F_END} :: <chemin/relatif> <<<<<
```

Pour chaque bloc :
1. Crée un dossier de travail, par exemple `zoran-jobs/`.
2. Recrée le fichier au `<chemin/relatif>` indiqué (crée les sous-dossiers).
3. Écris le contenu **exactement** tel qu'il apparaît entre les deux marqueurs
   (encodage UTF-8, ne rien ajouter, ne rien retirer).
4. **Préserve les fins de ligne à l'identique** (LF). N'introduis pas de retour
   chariot Windows (CRLF) : le runtime vérifie le sha256 de chaque `skill.py`,
   et la moindre modification d'octet ferait échouer cette vérification.
5. Vérifie : le sha256 du contenu reconstruit doit égaler le hash annoncé.

### Étape B — Suis le bootstrap IA-native

Une fois le dépôt reconstruit, **ouvre `transmission/AI_BOOTSTRAP.md`** et
suis-le. Ordre de lecture : `AI_BOOTSTRAP.md` → `RUNTIME_INVARIANTS.md` →
`NO_GO_BOUNDARIES.md` → `AI_ONBOARDING_FLOW.md` → `README.md`.

### Étape C — Vérifie (si non déjà fait par l'extracteur)

Avec Python 3.11+, depuis la racine du dépôt reconstruit :

```
python tests/test_registry.py
python tests/test_runtime_loop.py
python tests/test_cinematique.py
python tests/test_oracle.py
python tests/test_immune.py
python tests/stress/massive_validation.py
```

Résultat attendu : **85 assertions, 0 échec**. Aucune dépendance externe pour
le runtime — aucune installation nécessaire.

### Étape D — Ce que tu ne dois PAS faire

> ⛔ **Tu ne dois PAS ouvrir la Phase 4** (« GitHub Skill Discovery »). Statut
> NO-GO (1 critère sur 13). Aucun code de téléchargement, de crawl, ou
> d'exécution de skill externe.

Autres interdits : ne rien greffer dans un projet `zoran/` externe, aucun appel
réseau, ne pas modifier les fichiers gelés, ne maquiller aucun test rouge.
Détail : `transmission/NO_GO_BOUNDARIES.md`.

### Étape E — Rends compte, puis arrête-toi

Donne à la personne un compte-rendu clair, sans jargon si elle n'est pas
technique (ton : `transmission/HUMAN_HANDOFF.md`) : 85 tests OK ou non, ce que
fait le projet, et confirme que tu t'es arrêtée aux frontières. Puis **arrête-toi**.

---

## ▶️ DÉMARRAGE — pour la personne qui transmet ce fichier

Tu n'es pas développeur ? Tu veux juste que ton IA s'occupe de tout ? Ouvre ton
IA (ChatGPT, Claude…), **joins ce fichier**, et colle ce message :

```
Lis entièrement le fichier que je te donne (le bundle ZORAN's Jobs).
Suis la section "POUR L'IA QUI LIT CE FICHIER", sans sauter d'étape.
Si tu as un outil Python : exécute le bloc EXTRACTEUR AUTONOME.
Reconstruis le projet, vérifie les hash, lance les 85 tests.
Commence par me résumer ce que tu as compris AVANT d'agir.
Respecte les interdictions : tu ne dois PAS ouvrir la Phase 4.
Termine par un résumé simple : est-ce que les 85 tests passent,
et à quoi sert ce projet.
```

C'est tout. L'IA fait le reste.

---

## MANIFESTE DU BUNDLE

{n_files} fichiers empaquetés ci-dessous. Caches, artefacts et archives exclus.

---
"""
    return part1 + fence + part2


def build() -> int:
    files = collect_files()
    blocks: list[str] = []
    manifest: list[str] = []
    total = 0
    for p in files:
        # Lecture/écriture en OCTETS BRUTS : aucune traduction de fin de ligne.
        # `read_text`/`write_text` traduiraient \n <-> \r\n sur Windows, ce qui
        # changerait les octets d'un skill.py et casserait sa vérification de
        # hash par le Loader. Le bundle doit être fidèle à l'octet près.
        raw = p.read_bytes()
        content = raw.decode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        nbytes = len(raw)
        total += nbytes
        r = rel(p)
        manifest.append(f"- `{r}` — {nbytes} octets")
        blocks.append(
            f"{F_START} :: {r} :: {nbytes} :: sha256:{digest} >>>>>\n"
            f"{content}\n"
            f"{F_END} :: {r} <<<<<"
        )

    body = header(len(files), total)
    body += "\n".join(manifest)
    body += f"\n\n---\n\n{FILES_ANCHOR}\n\n"
    body += "\n\n".join(blocks)
    body += "\n\n---\n\n*Fin du bundle. `ZORAN_AI_NATIVE_TRANSMISSION_20260521`.*\n"

    OUT.write_bytes(body.encode("utf-8"))
    print(f"Bundle écrit : {OUT}")
    print(f"  {len(files)} fichiers · {total} octets de source · "
          f"{len(body.encode('utf-8'))} octets de bundle")
    return 0


def extract(bundle_path: str, dest: str) -> int:
    """Reconstruit le dépôt depuis un bundle et vérifie tous les hash."""
    # Octets bruts → décodage : aucune traduction de fin de ligne (cf. build()).
    text = Path(bundle_path).read_bytes().decode("utf-8")
    dest_root = Path(dest)
    n_ok, n_bad = 0, 0
    # On démarre APRÈS l'ancre de section : l'en-tête contient un exemple de
    # marqueur (pédagogique) qui ne doit pas être pris pour un vrai bloc.
    anchor = text.find(FILES_ANCHOR)
    pos = anchor if anchor != -1 else 0
    while True:
        s = text.find(F_START, pos)
        if s == -1:
            break
        line_end = text.index("\n", s)
        head = text[s:line_end]
        # format : F_START :: <rel> :: <nbytes> :: sha256:<hash> >>>>>
        parts = [x.strip() for x in head.split("::")]
        r = parts[1]
        nbytes = int(parts[2])
        declared = parts[3].split(">>>>>")[0].strip()
        end_marker = f"\n{F_END} :: {r} <<<<<"
        e = text.index(end_marker, line_end + 1)
        content = text[line_end + 1:e]
        data = content.encode("utf-8")
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        target = dest_root / r
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)  # octets bruts : fins de ligne préservées
        if digest == declared and len(data) == nbytes:
            n_ok += 1
        else:
            n_bad += 1
            print(f"  HASH KO : {r}")
        pos = e + len(end_marker)
    print(f"Extraction vers {dest_root} : {n_ok} fichiers OK · {n_bad} KO")
    return 0 if n_bad == 0 else 1


def main(argv: list[str]) -> int:
    if len(argv) >= 4 and argv[1] == "--extract":
        return extract(argv[2], argv[3])
    if len(argv) > 1:
        print("Usage : build_bundle.py            (construit le bundle)")
        print("        build_bundle.py --extract <bundle.md> <dossier_cible>")
        return 2
    return build()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
