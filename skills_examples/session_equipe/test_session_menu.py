# CLAUDE SIGNATURE BLOCK
# MISSION_ID: ZORAN-DUAL-VALIDATION-GUARD-2026-04-29-A
# MISSION: MENU_CTA_REPRISE_SESSION_V1
# DATE: 2026-07-03
# PREVIOUS_AUTHOR: CLAUDE
# CHANGE_REASON: verrouille les 3 pieges du menu CTA (Fred 02/07) : anti-mensonge etat,
#   chantiers clos exclus, prochaine action jamais devinee. Fichier separe de
#   test_stabilization.py (sous claim Codex au moment de la creation).
# IMPACT: TESTS_ONLY
"""Tests du menu CTA de reprise (scripts/session_menu.py)."""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import session_menu  # noqa: E402


def _onglet(tmp_path, text):
    p = tmp_path / "TEST.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_chantier_resolu_est_exclu_du_menu(tmp_path):
    p = _onglet(tmp_path, "\n".join([
        "## 🔴 EN COURS",
        "- **Fix machin — ✅ RÉSOLU 02/07 19:15** : tout va bien.",
        "- **Chantier vivant (GO Fred 02/07 18:52)** : en construction.",
        "- ~~ancienne entree barree~~ abandonnee.",
    ]))
    items = session_menu._parse_onglet(p)
    vivants = [it for it in items if not it["closed"]]
    assert len(vivants) == 1
    assert "Chantier vivant" in vivants[0]["title"]


def test_etape_faite_ne_ferme_pas_le_chantier(tmp_path):
    # "E0 FAIT" decrit une etape d'un chantier VIVANT : il doit rester au menu
    p = _onglet(tmp_path, "\n".join([
        "## 🔴 EN COURS",
        "- **Reconstruction — E0 FAIT** : NEXT : tenue 24 h puis E2.",
    ]))
    items = session_menu._parse_onglet(p)
    assert not items[0]["closed"]
    assert "tenue 24" in items[0]["next"]


def test_derniere_activite_est_lue_jamais_inventee(tmp_path):
    p = _onglet(tmp_path, "\n".join([
        "## 🔴 EN COURS",
        "- **Avec dates** : demarre 02/07 18:52, patch 03/07 08:23.",
        "- **Sans date** : rien de datable ici.",
    ]))
    items = session_menu._parse_onglet(p)
    now = datetime.datetime.now()
    assert items[0]["last_seen"] == datetime.datetime(now.year, 7, 3, 8, 23)
    assert items[1]["last_seen"] is None
    assert "aucune date lisible" in session_menu._age_label(None)


def test_prochaine_action_marqueur_explicite_sinon_renvoi_onglet(tmp_path):
    p = _onglet(tmp_path, "\n".join([
        "## 🔴 EN COURS",
        "- **Explicite** : prochaine action = lancer le lot 4.",
        "- **Piegeux** : le cœur mort rc=1 → relance backoff (fleche NARRATIVE, pas une action).",
    ]))
    items = session_menu._parse_onglet(p)
    assert items[0]["next"].startswith("lancer le lot 4")
    assert items[1]["next"] == "voir l'onglet TEST"  # jamais deviner


def test_stagnant_au_dela_de_24h():
    vieux = datetime.datetime.now() - datetime.timedelta(hours=30)
    assert "STAGNANT" in session_menu._age_label(vieux)
    recent = datetime.datetime.now() - datetime.timedelta(hours=2)
    assert "STAGNANT" not in session_menu._age_label(recent)


def test_tri_en_cours_avant_stand_by_puis_plus_recent(tmp_path, monkeypatch):
    p = tmp_path / "T.md"
    p.write_text("\n".join([
        "## 🟡 STAND-BY",
        "- **standby recent** : vu 03/07 08:00.",
        "## 🔴 EN COURS",
        "- **encours vieux** : vu 01/07 10:00.",
        "- **encours recent** : vu 03/07 07:00.",
    ]), encoding="utf-8")
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [])
    state = session_menu.collect()
    titles = [it["title"] for it in state["items"]]
    assert titles == ["encours recent", "encours vieux", "standby recent"]


def test_registre_sessions_prochain_numero_et_claim(tmp_path, monkeypatch):
    reg = tmp_path / "_session_registry.jsonl"
    reg.write_text('{"role": "PROTOTYPEUR", "num": 6, "ts": "2026-07-03T08:07:00"}\n',
                   encoding="utf-8")
    monkeypatch.setattr(session_menu, "REGISTRY", reg)
    monkeypatch.setattr(session_menu, "LIVE_DIR", tmp_path / "_session_live")
    assert session_menu._registry()[("PROTOTYPEUR", "zoran")]["num"] == 6
    out = session_menu.claim("PROTOTYPEUR")
    assert "PROTOTYPEUR 7" in out
    assert session_menu._registry()[("PROTOTYPEUR", "zoran")]["num"] == 7


def test_equipe_doublee_sur_plusieurs_projets(tmp_path, monkeypatch):
    # Fred 03/07 : meme role arme sur DEUX projets = compteurs INDEPENDANTS
    monkeypatch.setattr(session_menu, "REGISTRY", tmp_path / "_session_registry.jsonl")
    monkeypatch.setattr(session_menu, "LIVE_DIR", tmp_path / "_session_live")
    session_menu.claim("PROTOTYPEUR", "zoran")
    session_menu.claim("PROTOTYPEUR", "zoran")
    session_menu.claim("PROTOTYPEUR", "modurable")
    reg = session_menu._registry()
    assert reg[("PROTOTYPEUR", "zoran")]["num"] == 2
    assert reg[("PROTOTYPEUR", "modurable")]["num"] == 1
    # le menu affiche les deux affectations, taggees par projet
    roster = tmp_path / "_team_roster.json"
    roster.write_text(json.dumps({"equipe": [
        {"nom": "Jules", "inspiration": "Jules Verne", "role": "PROTOTYPEUR",
         "mission": "prototyper"}]}), encoding="utf-8")
    monkeypatch.setattr(session_menu, "ROSTER", roster)
    monkeypatch.setattr(session_menu, "MOBS", tmp_path / "mobs.jsonl")
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_sessions_live", lambda: {})
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [])
    out = session_menu.render_sessions(session_menu.collect())
    assert "Jules 3" in out                 # zoran : prochaine = 3
    assert "Jules 2" in out and "modurable" in out  # modurable : prochaine = 2


def test_sessions_sans_capteur_dit_inconnu_pas_silencieuse(tmp_path, monkeypatch):
    # anti-mensonge : sans capteur MAILBOX, l'etat est INCONNU (pas "silencieuse")
    reg = tmp_path / "_session_registry.jsonl"
    reg.write_text('{"role": "PROTOTYPEUR", "num": 6, "ts": "2026-07-03T08:07:00"}\n',
                   encoding="utf-8")
    monkeypatch.setattr(session_menu, "REGISTRY", reg)
    monkeypatch.setattr(session_menu, "LIVE_DIR", tmp_path / "_session_live_vide")
    monkeypatch.setattr(session_menu, "ROSTER", tmp_path / "roster_absent.json")
    monkeypatch.setattr(session_menu, "MOBS", tmp_path / "mobs_absent.jsonl")
    monkeypatch.setattr(session_menu, "_sessions_live", lambda: {})
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [])
    out = session_menu.render_sessions(session_menu.collect())
    assert "Prototypeur 7" in out          # compteur continu : la prochaine
    assert "INCONNU" in out                # honnete
    assert "silencieuse" not in out


def test_battement_role_rend_la_session_visible(tmp_path, monkeypatch):
    # constat Fred 03/07 08:55 : Prototypeur 6 tournait mais "aucun capteur".
    # Le battement data/_session_live/<ROLE>.json doit rendre la session VISIBLE.
    import datetime as dt
    reg = tmp_path / "_session_registry.jsonl"
    reg.write_text('{"role": "PROTOTYPEUR", "num": 6, "ts": "2026-07-03T08:07:00"}\n',
                   encoding="utf-8")
    live = tmp_path / "_session_live"
    live.mkdir()
    (live / "PROTOTYPEUR.json").write_text(
        '{"role": "PROTOTYPEUR", "ts": "%s"}'
        % dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), encoding="utf-8")
    monkeypatch.setattr(session_menu, "REGISTRY", reg)
    monkeypatch.setattr(session_menu, "LIVE_DIR", live)
    monkeypatch.setattr(session_menu, "_sessions_live", lambda: {})
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [])
    out = session_menu.render_sessions(session_menu.collect())
    assert "la 6 TOURNE" in out
    assert "INCONNU" not in out


def test_claim_arme_le_battement(tmp_path, monkeypatch):
    monkeypatch.setattr(session_menu, "REGISTRY", tmp_path / "_session_registry.jsonl")
    monkeypatch.setattr(session_menu, "LIVE_DIR", tmp_path / "_session_live")
    session_menu.claim("CERTIFICATEUR")
    assert (tmp_path / "_session_live" / "_current_role.txt").read_text(
        encoding="utf-8") == "CERTIFICATEUR@zoran"
    assert (tmp_path / "_session_live" / "CERTIFICATEUR@zoran.json").is_file()


def _equipe_test(tmp_path, monkeypatch):
    roster = tmp_path / "_team_roster.json"
    roster.write_text(json.dumps({"equipe": [
        {"nom": "Marie", "inspiration": "Marie Curie", "role": "CERTIFICATEUR",
         "mission": "certifier"}]}), encoding="utf-8")
    monkeypatch.setattr(session_menu, "ROSTER", roster)
    monkeypatch.setattr(session_menu, "MOBS", tmp_path / "_team_mobilisations.jsonl")
    monkeypatch.setattr(session_menu, "REGISTRY", tmp_path / "_session_registry.jsonl")
    monkeypatch.setattr(session_menu, "LIVE_DIR", tmp_path / "_session_live")
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_sessions_live", lambda: {})
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [])


def test_mobilisation_exige_le_go_humain(tmp_path, monkeypatch):
    _equipe_test(tmp_path, monkeypatch)
    out = session_menu.mobilise("Marie", "certifier le lot X", demandeur="Jules")
    assert "EN ATTENTE DU GO DE FRED" in out
    # la demande apparait au menu, RIEN n'est lance (pas de claim)
    menu = session_menu.render_sessions(session_menu.collect())
    assert "GO requis" in menu
    assert session_menu._registry().get(("CERTIFICATEUR", "zoran")) is None
    # GO Fred -> claim du role ; un 2e GO est refuse
    ok = session_menu.go("M001")
    assert "GO Fred" in ok
    assert session_menu._registry()[("CERTIFICATEUR", "zoran")]["num"] == 1
    assert "deja traitee" in session_menu.go("M001")


def test_mobilisation_inconnu_au_roster(tmp_path, monkeypatch):
    _equipe_test(tmp_path, monkeypatch)
    assert "inconnu au roster" in session_menu.mobilise("Rambo", "tout casser")


def test_menu_equipe_affiche_prenoms(tmp_path, monkeypatch):
    _equipe_test(tmp_path, monkeypatch)
    out = session_menu.render_sessions(session_menu.collect())
    assert "Marie 1" in out
    assert "Marie Curie" in out
    assert "jamais lancee" in out


def test_bootstrap_cite_ses_sources(tmp_path, monkeypatch):
    p = tmp_path / "T.md"
    p.write_text("## 🔴 EN COURS\n- **Chantier X** : prochaine action = faire Y.",
                 encoding="utf-8")
    monkeypatch.setattr(session_menu, "ONGLETS", tmp_path)
    monkeypatch.setattr(session_menu, "_ports_live", lambda: [("frontend 5175", True)])
    state = session_menu.collect()
    boot = session_menu.render_bootstrap(state, 1)
    assert "Sources exhumees" in boot
    assert "Chantier X" in boot
    assert "faire Y" in boot
    assert session_menu.render_bootstrap(state, 99).startswith("chantier 99 inexistant")
