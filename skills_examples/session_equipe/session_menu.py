# CLAUDE SIGNATURE BLOCK
# MISSION_ID: ZORAN-DUAL-VALIDATION-GUARD-2026-04-29-A
# MISSION: MENU_CTA_REPRISE_SESSION_V1
# TRACE_ID: TRC-SESSION-MENU-20260703
# DATE: 2026-07-03
# PREVIOUS_AUTHOR: CLAUDE
# CHANGE_REASON: decision Fred 02/07 21:22 (premiere action du 03/07) : la reprise de
#   session est FASTIDIEUSE - dette cognitive payee a chaque boot. V1 = menu CTA numerote
#   {titre, etat REEL mesure, prochaine action, priorite}, goulot bloquant en tete.
#   Piege n1 anti-mensonge : afficher la DERNIERE ACTIVITE MESUREE (dates lues dans les
#   onglets + heartbeats + ports sondes), jamais un "en cours" declaratif.
# IMPACT: TOOL_ONLY; READONLY sur onglets/dcc/heartbeats; ecrit data/session_menu_latest.md
"""session_menu — le menu CTA de reprise de session (verre d'eau applique au boot).

Usage :
    python scripts/session_menu.py            # affiche le menu (etat REEL mesure)
    python scripts/session_menu.py 3          # bootstrap du chantier 3 (contexte a livrer)
    python scripts/session_menu.py --sessions # "Hello Fred" : sessions fraiches lancables
                                              #   (compteurs continus + qui tourne, MESURE)

Sources du "present" (100 % deterministe, zero token, zero reseau externe) :
    project_memory/missions_glissantes/*.md   sections EN COURS / STAND-BY
    observatory/out/dcc_state.json            goulot, MVP, intervention_requise
    clipbridge_v2/data/_supervisor_heartbeat.json
    ports locaux (connect 0.3 s)              5175 8003 8787 8788 8901 8902

Critere de succes (Fred 02/07 21:30) : PLUS DE PROMPT A COPIER-COLLER a la reprise.
V1 = menu + bootstrap par chantier. V2 (meme fichier) = exhumation des fiches liees [[...]].
"""
from __future__ import annotations

import datetime
import json
import re
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "_session_registry.jsonl"
LIVE_DIR = ROOT / "data" / "_session_live"  # battements par role (session_heartbeat.py)
ROSTER = ROOT / "data" / "_team_roster.json"  # l'equipe (prenoms choisis par Fred 03/07)
MOBS = ROOT / "data" / "_team_mobilisations.jsonl"  # demandes de mobilisation + GO Fred
COMMAND_API = "http://127.0.0.1:8902/api/sessions"
ONGLETS = ROOT / "project_memory" / "missions_glissantes"
DCC = ROOT / "observatory" / "out" / "dcc_state.json"
HEARTBEAT_V2 = ROOT / "clipbridge_v2" / "data" / "_supervisor_heartbeat.json"
OUT_MD = ROOT / "data" / "session_menu_latest.md"
PORTS = [("frontend 5175", 5175), ("backend 8003", 8003), ("clip V1 8787", 8787),
         ("clip V2 8788", 8788), ("cockpit 8901", 8901), ("command 8902", 8902)]
STAGNANT_H = 24  # au-dela : "stagnant", pas "actif" (vivant != progresse)

# dates lisibles dans les onglets : "03/07 08:23", "02/07/2026 19:06", "2026-07-03T08:04"
_D_ISO = re.compile(r"(20\d{2})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})")
_D_FR = re.compile(r"(\d{1,2})/(\d{1,2})(?:/(20\d{2}))?(?:\s+(?:~?\s*)?(\d{1,2})[:h](\d{2}))?")


def _now() -> datetime.datetime:
    return datetime.datetime.now()


def _dates_in(text: str) -> list[datetime.datetime]:
    """Toutes les dates plausibles LUES dans le texte (jamais inventees)."""
    now = _now()
    found = []
    for m in _D_ISO.finditer(text):
        try:
            found.append(datetime.datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5])))
        except ValueError:
            pass
    for m in _D_FR.finditer(text):
        try:
            d = datetime.datetime(int(m[3]) if m[3] else now.year, int(m[2]), int(m[1]),
                                  int(m[4] or 0), int(m[5] or 0))
        except ValueError:
            continue
        if d <= now + datetime.timedelta(days=1):  # les dates futures = deadlines, pas activite
            found.append(d)
    return found


def _age_label(dt: datetime.datetime | None) -> str:
    if dt is None:
        return "aucune date lisible"
    h = (_now() - dt).total_seconds() / 3600.0
    when = dt.strftime("%d/%m %H:%M") if (dt.hour or dt.minute) else dt.strftime("%d/%m")
    if h < 1:
        return "%s (il y a %d min)" % (when, int(h * 60))
    if h < STAGNANT_H:
        return "%s (il y a %.0f h)" % (when, h)
    return "%s (il y a %.0f j) STAGNANT" % (when, h / 24)


def _parse_onglet(path: Path) -> list[dict]:
    """Items des sections EN COURS / STAND-BY d'un onglet (bullets de 1er niveau)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    items, prio = [], None
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            up = line.upper()
            prio = ("🔴" if "EN COURS" in up else "🟡" if "STAND-BY" in up else None)
            current = None
            continue
        if prio is None:
            continue
        if line.startswith("- "):
            title_m = re.search(r"\*\*(.+?)\*\*", line)
            title = (title_m[1] if title_m else line[2:80]).strip(" *~")
            # un chantier CLOS n'est pas un CTA : le lister a reprendre = mentir.
            # (mais "E0 FAIT" decrit une ETAPE d'un chantier vivant -> pas un critere)
            closed = bool(re.search(r"r[ée]solu|✅", title, re.I)) or line.startswith("- ~~")
            current = {"onglet": path.stem, "prio": prio, "title": title,
                       "closed": closed, "body": line}
            items.append(current)
        elif current is not None and line.strip():
            current["body"] += "\n" + line
    for it in items:
        dates = _dates_in(it["body"])
        it["last_seen"] = max(dates) if dates else None
        # prochaine action : UNIQUEMENT un marqueur explicite — un extrait deviné qui
        # tombe a cote est pire qu'un renvoi honnete a l'onglet
        m = re.search(r"(?:prochaine action|NEXT|Restes?(?:\s+lot\s*\d+)?|à faire|a faire)\s*[:=]\s*([^\n.;]{5,120})",
                      it["body"], re.I)
        it["next"] = (m[1].strip() if m else "voir l'onglet %s" % it["onglet"])
    return items


def _ports_live() -> list[tuple[str, bool]]:
    out = []
    for name, port in PORTS:
        s = socket.socket()
        s.settimeout(0.3)
        try:
            s.connect(("127.0.0.1", port))
            out.append((name, True))
        except OSError:
            out.append((name, False))
        finally:
            s.close()
    return out


def _json_or(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def collect() -> dict:
    """Etat REEL : onglets parses + dcc + heartbeat + ports. Aucune valeur inventee."""
    items = []
    for p in sorted(ONGLETS.glob("*.md")):
        if p.name.upper().startswith("README"):
            continue
        items.extend(_parse_onglet(p))
    closed_n = sum(1 for it in items if it["closed"])
    items = [it for it in items if not it["closed"]]
    # tri honnete : EN COURS avant STAND-BY, puis activite la plus recente d'abord
    items.sort(key=lambda it: (it["prio"] != "🔴",
                               -(it["last_seen"].timestamp() if it["last_seen"] else 0)))
    dcc = _json_or(DCC, {})
    hb = _json_or(HEARTBEAT_V2, {})
    hb_age = None
    if hb.get("ts"):
        hb_age = (_now().timestamp() - float(hb["ts"])) / 60.0
    return {"items": items, "closed_n": closed_n, "dcc": dcc,
            "hb_age_min": hb_age, "ports": _ports_live()}


def render_menu(state: dict) -> str:
    now = _now().strftime("%d/%m/%Y %H:%M")
    L = ["# 🧭 MENU DE REPRISE — %s (etat MESURE, pas declare)" % now, ""]
    dcc = state["dcc"]
    if dcc.get("intervention_requise"):
        L.append("🚨 GOULOT BLOQUANT (dcc %s) : %s — action : %s"
                 % (dcc.get("ts", "?"), dcc.get("verrou", "?"), dcc.get("prochaine_action", "?")))
        L.append("")
    leds = " · ".join("%s %s" % ("🟢" if ok else "🔴", n) for n, ok in state["ports"])
    hb = state["hb_age_min"]
    leds += " · %s superviseur V2 (beat %s)" % (
        ("🟢" if hb is not None and hb < 10 else "🔴"),
        ("il y a %.0f min" % hb) if hb is not None else "illisible")
    L += ["**Machines** : " + leds, ""]
    if dcc.get("mvp") is not None:
        L.append("**MVP** %.1f %% · vitesse %s%%/j · ETA %s" % (
            dcc["mvp"] * 100,
            ("%.1f" % (dcc["vel_day"] * 100)) if dcc.get("vel_day") is not None else "⚪",
            dcc.get("eta") or "⚪"))
        L.append("")
    for i, it in enumerate(state["items"], 1):
        L.append("**%d. %s %s** _(onglet %s)_" % (i, it["prio"], it["title"][:90], it["onglet"]))
        L.append("   derniere activite lue : %s" % _age_label(it["last_seen"]))
        L.append("   prochaine action : %s" % it["next"])
        L.append("")
    if state.get("closed_n"):
        L.append("_(%d chantier(s) marques RESOLU/FAIT dans les onglets — ignores, un CTA clos est un mensonge)_" % state["closed_n"])
        L.append("")
    L.append("_Reprendre : `python scripts/session_menu.py <numero>` -> bootstrap sans copier-coller._")
    return "\n".join(L)


def render_bootstrap(state: dict, n: int) -> str:
    """Contexte de reprise du chantier n : PERTINENT (son onglet + etat runtime) et
    SUFFISANT (pas tout MEMORY.md). Chaque source citee = auditable."""
    items = state["items"]
    if not (1 <= n <= len(items)):
        return "chantier %d inexistant (menu : 1..%d)" % (n, len(items))
    it = items[n - 1]
    dcc = state["dcc"]
    leds = " · ".join("%s %s" % ("🟢" if ok else "🔴", nm) for nm, ok in state["ports"])
    return "\n".join([
        "# 🔄 BOOTSTRAP CHANTIER — %s" % it["title"],
        "",
        "**Sources exhumees (auditable)** : onglet %s.md · dcc_state.json (%s) · ports live."
        % (it["onglet"], dcc.get("ts", "?")),
        "",
        "## Etat runtime MESURE maintenant",
        "- machines : %s" % leds,
        "- MVP %s · goulot dcc : %s · intervention requise : %s"
        % (("%.1f %%" % (dcc["mvp"] * 100)) if dcc.get("mvp") is not None else "⚪",
           dcc.get("verrou") or "aucun", dcc.get("intervention_requise")),
        "- derniere activite lue sur ce chantier : %s" % _age_label(it["last_seen"]),
        "",
        "## L'onglet, section complete du chantier",
        it["body"],
        "",
        "## Prochaine action (lue, pas inventee)",
        it["next"],
    ])


DEFAULT_PROJET = "zoran"


def _registry() -> dict[tuple[str, str], dict]:
    """Dernier numero connu par (role, projet) — l'equipe est UNE, les affectations
    sont PAR PROJET (Fred 03/07 : "nom + n°, projet, role")."""
    last: dict[tuple[str, str], dict] = {}
    if REGISTRY.is_file():
        for line in REGISTRY.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            r = e.get("role")
            p = e.get("projet", DEFAULT_PROJET)
            if r and ((r, p) not in last
                      or int(e.get("num", 0)) >= int(last[(r, p)].get("num", 0))):
                last[(r, p)] = {**e, "projet": p}
    return last


def _sessions_live() -> dict[str, float | None]:
    """Dernier signe de vie par boite MAILBOX (minutes), via le commandement 8902.
    Mesure, pas declaration : si 8902 est mort -> {} (on le dit, on n'invente pas)."""
    import urllib.request
    try:
        with urllib.request.urlopen(COMMAND_API, timeout=3) as r:
            rows = json.loads(r.read().decode("utf-8"))
        return {row["session"]: row.get("last_min") for row in rows}
    except Exception:
        return {}


def _roster() -> list[dict]:
    try:
        return json.loads(ROSTER.read_text(encoding="utf-8-sig")).get("equipe", [])
    except Exception:
        return []


def _mobilisations() -> list[dict]:
    """Etat courant des mobilisations (le dernier evenement par id gagne)."""
    by_id: dict[str, dict] = {}
    if MOBS.is_file():
        for line in MOBS.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
                by_id[e["id"]] = {**by_id.get(e["id"], {}), **e}
            except Exception:
                pass
    return list(by_id.values())


def _etat_role(role: str, entry: dict, live: dict, projet: str = DEFAULT_PROJET) -> str:
    """Etat MESURE d'un (role, projet) : battement > MAILBOX > INCONNU (jamais devine)."""
    seen = None
    if projet == DEFAULT_PROJET:  # le 8902 ne connait que les boites du projet zoran
        for name, last_min in live.items():
            if name.lower() in role.lower() or role.lower().startswith(name.lower()):
                seen = last_min
    beat_file = LIVE_DIR / ("%s@%s.json" % (role, projet))
    if not beat_file.is_file() and projet == DEFAULT_PROJET:
        beat_file = LIVE_DIR / ("%s.json" % role)  # format d'avant la dimension projet
    if beat_file.is_file():
        try:
            beat_ts = datetime.datetime.strptime(
                json.loads(beat_file.read_text(encoding="utf-8"))["ts"],
                "%Y-%m-%dT%H:%M:%S")
            beat_min = (_now() - beat_ts).total_seconds() / 60.0
            if seen is None or beat_min < seen:
                seen = beat_min
        except Exception:
            pass
    num = int(entry.get("num", 0))
    if seen is None:
        if num == 0:
            return "⚪ jamais lancee"
        return "⚪ la %d : etat INCONNU (aucun capteur pour ce role)" % num
    if num == 0:  # signal MAILBOX mais compteur jamais initie (ex: Codex, app externe)
        return ("%s signe MAILBOX il y a %d min · compteur a initier"
                % ("🟢" if seen <= 15 else "⚫", seen))
    if seen <= 15:
        return "🟢 la %d TOURNE (signe il y a %d min)" % (num, seen)
    return "⚫ la %d silencieuse (signe il y a %d min)" % (num, seen)


def _signaux(state: dict) -> dict[str, str]:
    """Detecteur d'utilite PAR ROLE, branche sur les MESURES existantes.
    Regle absolue : un chiffre affiche = un chiffre LU quelque part (source citee) ;
    jamais de % invente — sinon 'gain ⚪ NON_MESURE (mesure avant/apres a la mission)'."""
    s: dict[str, str] = {}
    dcc = state.get("dcc") or {}
    nm = "gain ⚪ NON_MESURE (mesure avant/apres a la mission)"
    # JULES — chantiers stagnants (>24 h sans date lue) dans les onglets
    stag = [it for it in state.get("items", [])
            if it.get("last_seen") and (_now() - it["last_seen"]).total_seconds() > STAGNANT_H * 3600]
    if stag:
        s["PROTOTYPEUR"] = ("%d chantier(s) STAGNANT >24 h (onglets) — relancer/tuer ; %s"
                            % (len(stag), nm))
    # MARIE — backlog de preuves a certifier
    try:
        st = json.loads((ROOT / "frontend" / "UI_OBJECT_COMPLETENESS_STATUS_5176.json")
                        .read_text(encoding="utf-8"))
        missing = (st.get("counts") or {}).get("action_proof_missing")
        if missing:
            s["CERTIFICATEUR"] = ("%s preuves d'action manquantes (guard completude) — "
                                  "gain max mesurable : %s objets debloques" % (missing, missing))
    except Exception:
        pass
    # KARL — verdicts jamais contre-attaques (absence MESUREE de ledger falsification)
    try:
        led = (ROOT / "claude_outbox" / "CERTIFICATION_CONTINUOUS_LEDGER.jsonl")
        last = json.loads(led.read_text(encoding="utf-8").splitlines()[-1])
        falsif = ROOT / "claude_outbox" / "FALSIFICATION_LEDGER.jsonl"
        if last.get("confirmed") and not falsif.is_file():
            s["FALSIFICATEUR"] = ("%d verdicts CONFIRMED sans AUCUNE passe adverse enregistree "
                                  "(aucun ledger falsification) ; %s" % (last["confirmed"], nm))
    except Exception:
        pass
    # GUSTAVE — le goulot dcc pointe Codex
    if "codex" in str(dcc.get("verrou_resp", "")).lower():
        s["CODEX"] = ("le goulot dcc l'attend : %s (responsable %s) ; %s"
                      % (dcc.get("verrou", "?"), dcc.get("verrou_resp", "?"), nm))
    # ZORAN — conflit non arbitre / intervention requise
    if "CONFLIT" in str(dcc.get("verrou_resp", "")) or dcc.get("intervention_requise"):
        s["GOUVERNANCE"] = ("arbitrage attendu : %s (dcc intervention_requise=%s) ; %s"
                            % (dcc.get("prochaine_action", "?"),
                               dcc.get("intervention_requise"), nm))
    # MILOU — verdicts non-OK du watchdog dans les dernieres 24 h
    try:
        wd = (ROOT / "clipbridge_v2" / "data" / "_passive_watchdog_report.jsonl")
        cutoff = _now() - datetime.timedelta(hours=24)
        bad = 0
        # verdicts DURS seulement : VIVANT_MAIS_STAGNANT = normal journalise en E1
        # (decision Fred 02/07, zero trafic attendu) — le compter serait crier au loup
        for line in wd.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
                if e.get("verdict") not in (None, "OK", "VIVANT_MAIS_STAGNANT") and \
                        datetime.datetime.fromisoformat(e["iso"]) >= cutoff:
                    bad += 1
            except Exception:
                pass
        if bad:
            s["WATCHDOG"] = ("%d verdict(s) DUR(s) en 24 h (watchdog passif : mort/port) — "
                             "surveiller la surveillance ; %s" % (bad, nm))
    except Exception:
        pass
    # LEON — dette au compteur reel du snapshot
    try:
        snap = json.loads((ROOT / "observatory" / "out" / "snapshot.json")
                          .read_text(encoding="utf-8"))
        debt = ((snap.get("product_health") or {}).get("debt") or {}).get("total")
        if debt:
            s["CLEANER"] = ("%s dettes au compteur reel (snapshot) — "
                            "gain max mesurable : -%s dettes" % (
                                f"{int(debt):,}".replace(",", " "),
                                f"{int(debt):,}".replace(",", " ")))
    except Exception:
        pass
    # NEO — boites MAILBOX silencieuses depuis longtemps
    silent = [n for n, m in _sessions_live().items() if m is not None and m > 600]
    if silent:
        s["ORACLE"] = ("%d boite(s) silencieuse(s) >10 h (%s) — relayer/reveiller ; %s"
                       % (len(silent), ", ".join(sorted(silent)), nm))
    return s


def render_sessions(state: dict) -> str:
    """Le "Hello Fred" du boot : l'EQUIPE (prenoms choisis par Fred, facon Grande
    Evasion), etat mesure, compteurs continus, mobilisations en attente de GO."""
    reg = _registry()
    live = _sessions_live()
    roster = _roster()
    now = _now().strftime("%d/%m/%Y %H:%M")
    L = ["# 👋 Hello Fred — l'equipe est la, on lance qui ? (%s)" % now, ""]
    dcc = state["dcc"]
    if dcc.get("intervention_requise"):
        L.append("🚨 avant tout : goulot dcc = %s (action : %s)"
                 % (dcc.get("verrou", "?"), dcc.get("prochaine_action", "?")))
        L.append("")
    attente = [m for m in _mobilisations() if m.get("status") == "EN_ATTENTE_GO_FRED"]
    for m in attente:
        L.append("✋ **GO requis** [%s] : mobiliser %s pour « %s » (demande par %s) — `--go %s`"
                 % (m["id"], m.get("nom", "?"), m.get("mission_texte", "?"),
                    m.get("demandeur", "?"), m["id"]))
    if attente:
        L.append("")
    signaux = _signaux(state)
    n = 0
    if roster:
        for membre in roster:
            role = membre["role"]
            # une ligne PAR PROJET ou ce role est affecte (defaut : zoran)
            projets = sorted({p for (r, p) in reg if r == role} | {DEFAULT_PROJET})
            for projet in projets:
                n += 1
                entry = reg.get((role, projet), {"num": 0})
                nxt = int(entry.get("num", 0)) + 1
                tag = "" if projet == DEFAULT_PROJET else " · **%s**" % projet
                L.append("**%d. %s %d**%s _(%s — %s)_ — %s"
                         % (n, membre["nom"], nxt, tag, membre["role"].title(),
                            membre["inspiration"],
                            _etat_role(role, entry, live, projet)))
                L.append("   _(a quoi sert %s : %s)_" % (membre["nom"], membre["mission"]))
                if projet == DEFAULT_PROJET and role in signaux:
                    L.append("   💡 utile MAINTENANT : %s" % signaux[role])
    else:  # pas de roster : retomber sur le registre brut (jamais ecran vide)
        for (role, projet), entry in sorted(reg.items()):
            n += 1
            L.append("**%d. %s %d** — %s" % (n, role.title(),
                     int(entry.get("num", 0)) + 1,
                     _etat_role(role, entry, live, projet)))
    n += 1
    L.append("**%d. Un nouveau projet** — role + compteur crees a la volee" % n)
    L += ["",
          "**Chargement au choix** (defaut = c, verre d'eau) :",
          "  a) carnet d'experiences (memoire complete)",
          "  b) skill(s) cible(s) du role uniquement",
          "  c) onglet missions glissantes + menu chantiers (`session_menu.py`)",
          "  d) session vierge de tout",
          "",
          "_Lancer : `--claim <ROLE>` · Mobiliser un renfort : `--mobilise <Prenom> \"mission\"`_",
          "_(TOUTE mobilisation attend le GO de Fred : `--go <id>` — jamais d'armee sans humain)._"]
    if not live:
        L.append("")
        L.append("⚠️ commandement 8902 injoignable : 'qui tourne' NON MESURABLE a l'instant.")
    return "\n".join(L)


def mobilise(nom: str, mission_texte: str, demandeur: str = "session",
             projet: str = DEFAULT_PROJET) -> str:
    """Depose une demande de mobilisation d'un membre de l'equipe sur UN projet.
    NE LANCE RIEN : la demande attend le GO humain de Fred (--go <id>)."""
    membre = next((m for m in _roster() if m["nom"].lower() == nom.lower()), None)
    if membre is None:
        return "inconnu au roster : %s (equipe : %s)" % (
            nom, ", ".join(m["nom"] for m in _roster()) or "vide")
    mob_id = "M%03d" % (len(_mobilisations()) + 1)
    entry = {"id": mob_id, "nom": membre["nom"], "role": membre["role"],
             "projet": projet, "mission_texte": mission_texte,
             "demandeur": demandeur,
             "ts": _now().strftime("%Y-%m-%dT%H:%M:%S"),
             "status": "EN_ATTENTE_GO_FRED"}
    with open(MOBS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return ("✋ [%s] %s (%s · %s) demande pour « %s » — EN ATTENTE DU GO DE FRED "
            "(`python scripts/session_menu.py --go %s`)"
            % (mob_id, membre["nom"], membre["role"].title(), projet,
               mission_texte, mob_id))


def go(mob_id: str) -> str:
    """GO humain de Fred sur une mobilisation -> claim du role + bootstrap pret."""
    mob = next((m for m in _mobilisations() if m["id"] == mob_id), None)
    if mob is None:
        return "mobilisation inconnue : %s" % mob_id
    if mob.get("status") != "EN_ATTENTE_GO_FRED":
        return "[%s] deja traitee (status=%s)" % (mob_id, mob.get("status"))
    with open(MOBS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"id": mob_id, "status": "GO_FRED",
                             "ts": _now().strftime("%Y-%m-%dT%H:%M:%S")},
                            ensure_ascii=False) + "\n")
    projet = mob.get("projet", DEFAULT_PROJET)
    claimed = claim(mob["role"], projet)
    num = _registry().get((mob["role"], projet), {}).get("num", "?")
    return ("✅ GO Fred sur [%s] — %s\nMission de %s : %s\n"
            "Ouvre la session : son en-tete = %s %s · %s, son contexte = "
            "`python scripts/session_menu.py` (menu chantiers) + la mission ci-dessus."
            % (mob_id, claimed, mob["nom"], mob["mission_texte"],
               mob["nom"], num, projet))


def claim(role: str, projet: str = DEFAULT_PROJET) -> str:
    """Incremente le compteur d'un (role, projet) (le lancement DECLARE devient TRACE)
    et pose l'affectation courante -> le hook UserPromptSubmit battra pour elle."""
    reg = _registry()
    cur = int(reg.get((role, projet), {}).get("num", 0))
    entry = {"role": role, "projet": projet, "num": cur + 1,
             "ts": _now().strftime("%Y-%m-%dT%H:%M:%S"),
             "source": "claim session_menu"}
    with open(REGISTRY, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    (LIVE_DIR / "_current_role.txt").write_text("%s@%s" % (role, projet),
                                                encoding="utf-8")
    (LIVE_DIR / ("%s@%s.json" % (role, projet))).write_text(
        json.dumps({"role": role, "projet": projet, "num": cur + 1,
                    "ts": entry["ts"]}), encoding="utf-8")
    return "%s %d · %s enregistree (registre %s, battement arme)" % (
        role, cur + 1, projet, REGISTRY.name)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # option globale --projet <p> (defaut zoran) : extraite avant dispatch
    projet = DEFAULT_PROJET
    if "--projet" in argv:
        i = argv.index("--projet")
        if i + 1 < len(argv):
            projet = argv[i + 1].strip().lower()
            argv = argv[:i] + argv[i + 2:]
    if len(argv) > 2 and argv[1] == "--claim":
        print(claim(" ".join(argv[2:]).upper(), projet))
        return 0
    if len(argv) > 3 and argv[1] == "--mobilise":
        print(mobilise(argv[2], " ".join(argv[3:]), projet=projet))
        return 0
    if len(argv) > 2 and argv[1] == "--go":
        print(go(argv[2]))
        return 0
    state = collect()
    if len(argv) > 1 and argv[1] == "--sessions":
        print(render_sessions(state))
        return 0
    if len(argv) > 1 and argv[1].isdigit():
        print(render_bootstrap(state, int(argv[1])))
        return 0
    menu = render_menu(state)
    print(menu)
    try:
        OUT_MD.write_text(menu + "\n", encoding="utf-8")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
