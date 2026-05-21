"""skill Vérification de la stabilité d'un talus simple.

Mission : ZORAN_JOBS_20260521 · Phase B BTP bloc Géotechnique.
Source : mécanique des sols — modèle de la pente infinie ; cadre NF EN 1997-1.

Vérifie la stabilité d'un talus pulvérulent sec par le modèle de la pente
infinie (sol sans cohésion, sans nappe) :
    FS = tan(φ) / tan(β)
avec φ = angle de frottement interne, β = angle du talus. Le talus est jugé
stable si FS ≥ facteur de sécurité requis.

⚠️ MVP : sol pulvérulent (cohésion nulle), sec (hors nappe), pente infinie.
Ne traite ni les sols cohérents, ni les nappes, ni les ruptures circulaires,
ni les surcharges en crête, ni les effets sismiques. Un talus réel relève
d'une étude géotechnique (G2).
Loi 1 : φ provient de l'étude géotechnique — il est fourni, jamais inventé.

Contrat io :
    inputs  : {angle_talus_deg, angle_frottement_deg, facteur_securite_requis?}
    outputs : {facteur_securite_calcule, facteur_securite_requis, conforme, reference}
"""

from __future__ import annotations

import math

FACTEUR_SECURITE_DEFAUT = 1.5  # facteur de sécurité usuel pour un talus


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def run(inputs: dict) -> dict:
    """Voir contrat io. Lève ValueError sur entrée invalide (falsifiabilité)."""
    inputs = inputs or {}
    angle_talus = inputs.get("angle_talus_deg")
    phi = inputs.get("angle_frottement_deg")
    fs_requis = inputs.get("facteur_securite_requis", FACTEUR_SECURITE_DEFAUT)
    if not _nombre(angle_talus) or not (0.0 < angle_talus < 90.0):
        raise ValueError("angle_talus_deg : nombre dans ]0..90[ requis")
    if not _nombre(phi) or not (0.0 < phi < 90.0):
        raise ValueError("angle_frottement_deg : nombre dans ]0..90[ requis")
    if not _nombre(fs_requis) or fs_requis <= 0:
        raise ValueError("facteur_securite_requis : nombre > 0 requis")

    fs_calcule = math.tan(math.radians(float(phi))) / math.tan(math.radians(float(angle_talus)))
    conforme = fs_calcule >= float(fs_requis)
    return {
        "facteur_securite_calcule": round(fs_calcule, 3),
        "facteur_securite_requis": float(fs_requis),
        "conforme": conforme,
        "verdict": ("Talus stable (modèle de pente infinie)." if conforme
                    else "Talus INSTABLE — facteur de sécurité insuffisant ; étude G2 requise."),
        "reference": "Mécanique des sols — modèle de la pente infinie ; cadre NF EN 1997-1",
    }
