"""
INFERNUM AETERNA — Aptitudes : Index & Helpers
Agrège les 4 factions et fournit les fonctions d'accès.
"""

from data.aptitudes.constants import (
    REIRYOKU_PAR_RANG, RANGS_P3, COUT_PALIER,
    COULEURS_FACTION, EMOJI_FACTION, EMOJI_PALIER, NOM_PALIER,
)
from data.aptitudes.shinigami import VOIES_SHINIGAMI
from data.aptitudes.togabito import VOIES_TOGABITO
from data.aptitudes.arrancar import VOIES_ARRANCAR
from data.aptitudes.quincy import VOIES_QUINCY


# ══════════════════════════════════════════════════════════════════════════════
#  MIGRATION D'IDS (v1 → v2)
# ══════════════════════════════════════════════════════════════════════════════
# Aptitudes dont l'ID a changé suite à la restructuration v2
# (Resurrección et Vollständig déplacés P2→P3, IDs renommés)

MIGRATION_MAP = {
    # Arrancar — Resurrección restructurée
    "arr_res_p2a": "arr_res_p3a",   # Resurrección était P2, maintenant P3
    "arr_res_p3":  "arr_res_p3b",   # Segunda Etapa → nouvel ID P3b
    # Arrancar — anciens IDs P3 simples
    "arr_cer_p3":  "arr_cer_p3a",
    "arr_hie_p3":  "arr_hie_p3a",
    "arr_son_p3":  "arr_son_p3a",
    # Quincy — Seikei restructurée
    "quin_sei_p2a": "quin_sei_p3a",  # Vollständig était P2, maintenant P3
    "quin_sei_p2b": "quin_sei_p2a",  # Sklaverei garde sa place mais change d'ID
    "quin_sei_p3":  "quin_sei_p3b",  # Schrift → nouvel ID P3b
    # Quincy — anciens IDs P3 simples
    "quin_rei_p3":  "quin_rei_p3a",
    "quin_blu_p3":  "quin_blu_p3a",
    "quin_hir_p3":  "quin_hir_p3a",
    # Quincy — Reishi Sōsa (Gintō renommé)
    "quin_rei_p2b": "quin_rei_p2b",  # Gintō → Gintō Kiso (même ID)
    # Shinigami — anciens IDs P3 simples
    "shin_zan_p3":  "shin_zan_p3a",
    "shin_kid_p3":  "shin_kid_p3a",
    "shin_hoh_p3":  "shin_hoh_p3a",
    "shin_hak_p3":  "shin_hak_p3a",
    # Shinigami — Shunkō extrait de Hakuda vers sa propre Voie
    "shin_hak_p3b": "shin_shun_p1a",  # Shunkō (ancien P3 Hakuda → P1 Voie Shunkō)
    "shin_hak_p3c": "shin_hak_p3b",   # Oni Dekopin (renuméroté)
    # Togabito — anciens IDs P3 simples
    "toga_jig_p3":  "toga_jig_p3a",
    "toga_gok_p3":  "toga_gok_p3a",
    "toga_sai_p3":  "toga_sai_p3a",
    "toga_rin_p3":  "toga_rin_p3a",
}


def migrer_aptitudes(aptitudes_ids: list[str]) -> list[str]:
    """
    Migre une liste d'IDs d'aptitudes de l'ancien format vers le nouveau.
    Applique MIGRATION_MAP et supprime les IDs devenus invalides.
    """
    migrees = []
    for apt_id in aptitudes_ids:
        nouvel_id = MIGRATION_MAP.get(apt_id, apt_id)
        if nouvel_id in APTITUDES_INDEX and nouvel_id not in migrees:
            migrees.append(nouvel_id)
    return migrees


# ══════════════════════════════════════════════════════════════════════════════
#  INDEX GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

VOIES_PAR_FACTION = {
    "shinigami": VOIES_SHINIGAMI,
    "togabito":  VOIES_TOGABITO,
    "arrancar":  VOIES_ARRANCAR,
    "quincy":    VOIES_QUINCY,
}

# Index plat : voie_id → voie dict
VOIES_INDEX = {}
# Index plat : aptitude_id → aptitude dict
APTITUDES_INDEX = {}
# Index : aptitude_id → voie dict (pour retrouver la voie d'une aptitude)
APTITUDE_VOIE = {}

for faction, voies in VOIES_PAR_FACTION.items():
    for voie in voies:
        VOIES_INDEX[voie["id"]] = voie
        for apt in voie["aptitudes"]:
            APTITUDES_INDEX[apt["id"]] = apt
            APTITUDE_VOIE[apt["id"]] = voie


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_voie(voie_id: str) -> dict | None:
    """Retourne une Voie par son ID."""
    return VOIES_INDEX.get(voie_id)


def get_aptitude(apt_id: str) -> dict | None:
    """Retourne une aptitude par son ID."""
    return APTITUDES_INDEX.get(apt_id)


def get_voie_pour_aptitude(apt_id: str) -> dict | None:
    """Retourne la Voie contenant une aptitude donnée."""
    return APTITUDE_VOIE.get(apt_id)


def voies_pour_faction(faction: str) -> list[dict]:
    """Retourne la liste des Voies d'une faction."""
    return VOIES_PAR_FACTION.get(faction, [])


def budget_reiryoku(rang_cle: str, bonus: int = 0) -> int:
    """Calcule le budget Reiryoku total pour un rang donné."""
    base = REIRYOKU_PAR_RANG.get(rang_cle, 0)
    return base + bonus


def reiryoku_depense(aptitudes_debloquees: list[str]) -> int:
    """Calcule le Reiryoku total dépensé."""
    total = 0
    for apt_id in aptitudes_debloquees:
        apt = APTITUDES_INDEX.get(apt_id)
        if apt:
            total += apt["cout"]
    return total


def aptitudes_par_voie(aptitudes_debloquees: list[str], voie_id: str) -> list[dict]:
    """Retourne les aptitudes débloquées dans une Voie donnée."""
    voie = VOIES_INDEX.get(voie_id)
    if not voie:
        return []
    return [apt for apt in voie["aptitudes"] if apt["id"] in aptitudes_debloquees]


def peut_debloquer(apt_id: str, aptitudes_debloquees: list[str], rang_cle: str, faction: str) -> tuple[bool, str]:
    """
    Vérifie si une aptitude peut être débloquée.
    Retourne (True, "") ou (False, "raison").
    """
    apt = APTITUDES_INDEX.get(apt_id)
    if not apt:
        return False, "Aptitude inconnue."

    # Déjà débloquée
    if apt_id in aptitudes_debloquees:
        return False, "Cette aptitude est déjà débloquée."

    # Vérifier que l'aptitude appartient à la faction du joueur
    voie = APTITUDE_VOIE.get(apt_id)
    if not voie or voie["faction"] != faction:
        return False, "Cette aptitude n'appartient pas à votre faction."

    # Vérifier le budget
    cout = apt["cout"]
    depense = reiryoku_depense(aptitudes_debloquees)
    budget = budget_reiryoku(rang_cle)
    if depense + cout > budget:
        return False, f"Budget insuffisant ({depense + cout} > {budget} 霊力)."

    # Vérifier les prérequis (supporte les prereqs cross-voie)
    for prereq_id in apt.get("prereqs", []):
        if prereq_id not in aptitudes_debloquees:
            prereq = APTITUDES_INDEX.get(prereq_id)
            nom_prereq = prereq["nom"] if prereq else prereq_id
            return False, f"Prérequis manquant : {nom_prereq}."

    # Vérifier P2 : au moins 1 P1 dans la même Voie
    if apt["palier"] == 2:
        voie = APTITUDE_VOIE[apt_id]
        p1_dans_voie = [
            a for a in voie["aptitudes"]
            if a["palier"] == 1 and a["id"] in aptitudes_debloquees
        ]
        if len(p1_dans_voie) < 1:
            return False, "Au moins 1 aptitude P1 dans cette Voie est requise."

    # Vérifier P3 : restriction de rang
    if apt["palier"] == 3:
        rangs_autorises = RANGS_P3.get(faction, set())
        if rang_cle not in rangs_autorises:
            return False, "Votre rang ne permet pas encore d'accéder au Palier 3."
        # P3 requiert 2 P2 dans la voie (déjà couvert par prereqs, mais double vérification)
        voie = APTITUDE_VOIE[apt_id]
        p2_dans_voie = [
            a for a in voie["aptitudes"]
            if a["palier"] == 2 and a["id"] in aptitudes_debloquees
        ]
        if len(p2_dans_voie) < 2:
            return False, "Au moins 2 aptitudes P2 dans cette Voie sont requises."

    # Vérifier rang minimum spécifique de l'aptitude
    if apt.get("rang_min"):
        rang_budget = REIRYOKU_PAR_RANG.get(rang_cle, 0)
        rang_min_budget = REIRYOKU_PAR_RANG.get(apt["rang_min"], 999)
        if rang_budget < rang_min_budget:
            return False, f"Rang minimum requis : {apt['rang_min']}."

    return True, ""


def peut_retirer(apt_id: str, aptitudes_debloquees: list[str]) -> tuple[bool, str]:
    """
    Vérifie si une aptitude peut être retirée sans casser les dépendances.
    Retourne (True, "") ou (False, "raison").
    """
    if apt_id not in aptitudes_debloquees:
        return False, "Cette aptitude n'est pas débloquée."

    # Vérifier qu'aucune aptitude débloquée ne dépend de celle-ci
    for other_id in aptitudes_debloquees:
        if other_id == apt_id:
            continue
        other = APTITUDES_INDEX.get(other_id)
        if other and apt_id in other.get("prereqs", []):
            return False, f"Impossible : **{other['nom']}** dépend de cette aptitude."

    return True, ""


def est_sur_budget(aptitudes_debloquees: list[str], rang_cle: str, bonus: int = 0) -> bool:
    """Vérifie si le joueur est en sur-budget (plus d'aptitudes que le budget ne permet)."""
    depense = reiryoku_depense(aptitudes_debloquees)
    budget = budget_reiryoku(rang_cle, bonus)
    return depense > budget


# ══════════════════════════════════════════════════════════════════════════════
#  PUISSANCE SPIRITUELLE
# ══════════════════════════════════════════════════════════════════════════════

def puissance_spirituelle(points: int) -> int:
    """Calcule la Puissance Spirituelle (PS) à partir des points de progression.
    Formule quadratique : PS = points² ÷ 1000 (minimum 1).
    L'échelle quadratique creuse exponentiellement l'écart entre rangs élevés."""
    return max(1, points * points // 1000)


def palier_combat(ps_a: int, ps_b: int) -> dict:
    """Détermine le palier de combat entre deux combattants (A attaque B).
    Retourne le palier dict depuis PALIERS_COMBAT."""
    from config import PALIERS_COMBAT
    ecart_abs = abs(ps_a - ps_b)
    for palier in PALIERS_COMBAT:
        if palier["ecart_min"] <= ecart_abs <= palier["ecart_max"]:
            return palier
    return PALIERS_COMBAT[-1]
