# CLAUDE SIGNATURE BLOCK
# MISSION_ID: ZORAN-DUAL-VALIDATION-GUARD-2026-04-29-A
# MISSION: MENU_CTA_REPRISE_SESSION_V1
# TRACE_ID: TRC-SESSION-HEARTBEAT-20260703
# DATE: 2026-07-03
# PREVIOUS_AUTHOR: NONE
# CHANGE_REASON: constat Fred 03/07 08:55 - le menu disait "etat INCONNU (aucun capteur)"
#   pour Prototypeur alors que la session 6 tournait : les roles sans boite MAILBOX
#   n'avaient AUCUN instrument de vie. Capteur = battement par role, ecrit a chaque
#   tour via le hook UserPromptSubmit (zero geste).
# IMPACT: TOOL_ONLY; ecrit data/_session_live/<ROLE>.json ; lu par session_menu.py
"""Battement de coeur du role de session courant (capteur du menu de reprise).

Le role courant est pose par `session_menu.py --claim <ROLE>` dans
data/_session_live/_current_role.txt ; chaque tour de session (hook
UserPromptSubmit) rafraichit data/_session_live/<ROLE>.json.

Limite V1 assumee : si DEUX sessions Claude tournent en parallele avec des roles
differents, le dernier claim gagne (les battements sont attribues a un seul role).
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "data" / "_session_live"
CURRENT = LIVE / "_current_role.txt"


def beat() -> None:
    LIVE.mkdir(parents=True, exist_ok=True)
    try:
        # utf-8-sig : PowerShell ecrit souvent un BOM, qui polluerait le nom de fichier
        role = CURRENT.read_text(encoding="utf-8-sig").strip()
    except OSError:
        return  # aucun role reclame : rien a battre, on n'invente pas
    if not role:
        return
    (LIVE / ("%s.json" % role)).write_text(
        json.dumps({"role": role,
                    "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}),
        encoding="utf-8")


if __name__ == "__main__":
    beat()
