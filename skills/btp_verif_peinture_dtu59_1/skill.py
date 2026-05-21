"""
skill btp_verif_peinture_dtu59_1 — Vérification de conformité avant peinture.

Mission : ZORAN_JOBS_20260521 · Phase A · lot Claude Code (second œuvre)
Référence : NF DTU 59.1 (travaux de peinture des bâtiments).
Point d'entrée : run(inputs: dict) -> dict.

Vérifie qu'un support est apte à recevoir une peinture selon les conditions de
mise en œuvre du DTU 59.1 : siccité du support, conditions hygrothermiques
ambiantes, préparation. Logique 100 % déterministe, seuils explicites.
"""

from __future__ import annotations

# Seuils DTU 59.1 — conditions courantes d'application (peintures en phase
# aqueuse/solvant, films minces). Indicatifs : un CCTP peut être plus strict.
HUMIDITE_MAX_PCT = {
    "enduit_platre": 5.0, "plaque_platre": 5.0, "beton": 5.0,
    "maconnerie": 5.0, "bois": 18.0, "metal": 0.0,
}
TEMP_MIN_C = 5.0
TEMP_MAX_C = 35.0
HYGRO_AMBIANTE_MAX_PCT = 70.0


def run(inputs: dict) -> dict:
    """Contrat io : voir manifest.json. Retourne un verdict de conformité."""
    inp = inputs or {}
    support = str(inp.get("support", "")).lower()
    humidite = float(inp.get("humidite_pct", 0.0))
    temperature = float(inp.get("temperature_c", 20.0))
    hygro = float(inp.get("hygrometrie_ambiante_pct", 50.0))
    prepare = bool(inp.get("support_prepare", False))

    nc: list[str] = []
    if support not in HUMIDITE_MAX_PCT:
        nc.append(f"support '{support}' inconnu (attendu : {sorted(HUMIDITE_MAX_PCT)})")
        seuil = 5.0
    else:
        seuil = HUMIDITE_MAX_PCT[support]
    if humidite > seuil:
        nc.append(f"humidité support {humidite}% > {seuil}% admis "
                  f"(DTU 59.1 : support non sec)")
    if temperature < TEMP_MIN_C:
        nc.append(f"température {temperature}°C < {TEMP_MIN_C}°C minimum d'application")
    if temperature > TEMP_MAX_C:
        nc.append(f"température {temperature}°C > {TEMP_MAX_C}°C maximum d'application")
    if hygro > HYGRO_AMBIANTE_MAX_PCT:
        nc.append(f"hygrométrie ambiante {hygro}% > {HYGRO_AMBIANTE_MAX_PCT}% "
                  f"(risque de condensation)")
    if not prepare:
        nc.append("support non préparé (égrenage/rebouchage/dépoussiérage requis)")

    conforme = not nc
    return {
        "conforme": conforme,
        "non_conformites": nc,
        "verdict": ("Support apte à recevoir la peinture (DTU 59.1)."
                    if conforme else
                    f"{len(nc)} non-conformité(s) — application non conforme DTU 59.1."),
    }
