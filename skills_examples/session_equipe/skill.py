"""skill session_equipe — equipe de sessions IA nommee, menu de reprise, mobilisation.

Mission : MENU_CTA_REPRISE_SESSION_V1 (projet zoran, 2026-07-03, session Jules/PROTOTYPEUR 6).
Decisions Fred gravees ici :
  - 02/07 21:22 : la reprise de session manuelle est FASTIDIEUSE -> menu CTA au boot,
    etat REEL MESURE (jamais declaratif), critere de succes = "plus de prompt a copier-coller".
  - 03/07 09:04 : prenoms evocateurs facon Grande Evasion (Jules Verne=Prototypeur,
    Marie Curie=Certificateur, Karl Popper=Falsificateur, Gustave Eiffel=Codex,
    Zoran/Barjavel=Gouvernance, Milou=Watchdog, Leon=Cleaner, Neo=Oracle).
  - 03/07 09:15 : equipe doublable par projet -> identite = {prenom, projet, numero},
    compteurs continus PAR (role, projet).

INVARIANT : toute mobilisation (par un humain OU une session IA) reste EN ATTENTE
du GO humain — une IA ne leve jamais une armee seule.

Anti-mensonge (les 3 pieges Fred) :
  1. Derniere activite = date LUE (onglets/battements/MAILBOX), jamais inventee ;
     sans capteur -> "etat INCONNU", pas "silencieuse". STAGNANT au-dela de 24 h.
  2. Chantiers marques RESOLU exclus du menu (un CTA clos est un mensonge).
  3. Prochaine action = marqueur explicite, sinon renvoi honnete a l'onglet.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import session_menu  # noqa: E402


def run(inputs: dict) -> dict:
    """Point d'entree zoran-jobs. action: menu|sessions|bootstrap|claim|mobilise|go."""
    action = (inputs or {}).get("action", "sessions")
    arg = (inputs or {}).get("argument", "")
    projet = (inputs or {}).get("projet") or session_menu.DEFAULT_PROJET
    state = None
    if action in ("menu", "sessions", "bootstrap"):
        state = session_menu.collect()
    if action == "menu":
        return {"ok": True, "texte": session_menu.render_menu(state)}
    if action == "sessions":
        return {"ok": True, "texte": session_menu.render_sessions(state)}
    if action == "bootstrap":
        if not arg.isdigit():
            return {"ok": False, "texte": "bootstrap exige un numero de chantier"}
        return {"ok": True, "texte": session_menu.render_bootstrap(state, int(arg))}
    if action == "claim":
        return {"ok": True, "texte": session_menu.claim(arg.upper(), projet)}
    if action == "mobilise":
        mission = (inputs or {}).get("mission", "")
        if not (arg and mission):
            return {"ok": False, "texte": "mobilise exige argument=<Prenom> et mission=<texte>"}
        return {"ok": True, "texte": session_menu.mobilise(arg, mission, projet=projet)}
    if action == "go":
        # GO = decision HUMAINE : l'appelant certifie que l'humain a valide.
        return {"ok": True, "texte": session_menu.go(arg)}
    return {"ok": False, "texte": "action inconnue : %s" % action}
