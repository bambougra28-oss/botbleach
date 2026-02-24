"""
INFERNUM AETERNA — Tests d'intégration
Vérifie la cohérence du projet sans connexion Discord.
"""

import ast
import os
import sys
import unittest.mock as m

# ── Répertoire de travail = racine du projet ─────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)


# ══════════════════════════════════════════════════════════════════════════════
#  1. Syntaxe de tous les fichiers Python
# ══════════════════════════════════════════════════════════════════════════════

def test_syntax():
    errors = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fp:
                src = fp.read()
            try:
                ast.parse(src)
            except SyntaxError as e:
                errors.append(f"{path} L{e.lineno}: {e.msg}")
    assert not errors, "\n".join(errors)


# ══════════════════════════════════════════════════════════════════════════════
#  2. Imports critiques (mock discord)
# ══════════════════════════════════════════════════════════════════════════════

def _mock_discord():
    """Mock discord et ses sous-modules pour pouvoir importer les cogs."""
    mods = [
        "discord", "discord.ext", "discord.ext.commands", "discord.app_commands",
        "discord.ext.tasks", "discord.ui", "anthropic",
    ]
    for mod in mods:
        sys.modules.setdefault(mod, m.MagicMock())


def test_imports_critiques():
    from data.structure_serveur import ROLES, CATEGORIES
    assert len(ROLES) >= 30, f"Trop peu de rôles : {len(ROLES)}"
    assert len(CATEGORIES) >= 10, f"Trop peu de catégories : {len(CATEGORIES)}"


# ══════════════════════════════════════════════════════════════════════════════
#  3. Structure des données
# ══════════════════════════════════════════════════════════════════════════════

def test_structure_roles():
    from data.structure_serveur import ROLES
    cles_requises = {"cle", "nom", "couleur", "hoist", "mentionable", "position"}
    for role in ROLES:
        manquantes = cles_requises - set(role.keys())
        assert not manquantes, f"Rôle {role.get('nom', '?')} manque : {manquantes}"


def test_structure_categories():
    from data.structure_serveur import CATEGORIES
    for cat in CATEGORIES:
        assert "nom" in cat, "Catégorie sans nom"
        assert "channels" in cat, f"Catégorie {cat['nom']} sans channels"
        for ch in cat["channels"]:
            assert "nom" in ch, f"Channel sans nom dans {cat['nom']}"
            assert "type" in ch, f"Channel {ch.get('nom', '?')} sans type"


def test_rangs_points():
    _mock_discord()
    g = {}
    with open("cogs/personnage.py", encoding="utf-8") as f:
        exec(f.read(), g)
    rp = g["RANGS_POINTS"]
    assert set(rp.keys()) == {"shinigami", "togabito", "arrancar", "quincy"}
    for faction, rangs in rp.items():
        assert len(rangs) >= 4, f"{faction} a seulement {len(rangs)} rangs"
        # Vérifier ordre croissant des points
        points = [r[1] for r in rangs]
        assert points == sorted(points), f"{faction} : rangs non ordonnés par points"


def test_glossaire_complet():
    _mock_discord()
    g = {}
    with open("cogs/lore.py", encoding="utf-8") as f:
        exec(f.read(), g)
    glossaire = g["GLOSSAIRE"]
    assert len(glossaire) >= 25, f"Glossaire trop court : {len(glossaire)} entrées"
    for cle, val in glossaire.items():
        assert isinstance(val, tuple) and len(val) == 2, f"{cle} : format incorrect"
        assert val[0], f"{cle} : kanji vide"
        assert val[1], f"{cle} : définition vide"


def test_lore_data_structure():
    _mock_discord()
    g = {}
    with open("cogs/lore.py", encoding="utf-8") as f:
        exec(f.read(), g)
    lore_data = g["LORE_DATA"]
    cles_requises = {"origine", "fissure", "reio", "division_zero", "konso_reisai", "systeme",
                      "gotei", "strates_lore", "tensions", "creation"}
    assert cles_requises <= set(lore_data.keys()), f"LORE_DATA manque : {cles_requises - set(lore_data.keys())}"
    for cle, data in lore_data.items():
        assert "titre" in data, f"LORE_DATA[{cle}] sans titre"
        assert "description" in data, f"LORE_DATA[{cle}] sans description"
        assert "couleur" in data, f"LORE_DATA[{cle}] sans couleur"
        # Vérifier que la description ne dépasse pas 4096 chars
        assert len(data["description"]) <= 4096, f"LORE_DATA[{cle}] description trop longue"
        for nom, val in data.get("fields", []):
            assert len(val) <= 1024, f"LORE_DATA[{cle}] field '{nom}' > 1024 chars"


# ══════════════════════════════════════════════════════════════════════════════
#  4. Cohérence inter-fichiers
# ══════════════════════════════════════════════════════════════════════════════

def test_cles_roles_coherentes():
    """Les clés dans ROLES doivent correspondre aux clés utilisées dans CATEGORIES."""
    from data.structure_serveur import ROLES, CATEGORIES

    cles_roles = {r["cle"] for r in ROLES}

    # Collecter toutes les clés de rôles référencées dans les channels
    cles_utilisees = set()
    for cat in CATEGORIES:
        # visible_a au niveau catégorie
        va_cat = cat.get("visible_a")
        if va_cat:
            cles_utilisees.add(va_cat)
        for ch in cat.get("channels", []):
            # faction_write (string), rank_write (list), visible_a (string)
            for key in ["faction_write", "visible_a"]:
                val = ch.get(key)
                if isinstance(val, str):
                    cles_utilisees.add(val)
            rw = ch.get("rank_write")
            if isinstance(rw, list):
                cles_utilisees.update(rw)

    inconnues = cles_utilisees - cles_roles
    assert not inconnues, f"Clés inconnues dans CATEGORIES : {inconnues}"


def test_couleurs_config():
    """Toutes les couleurs requises existent dans config.py."""
    _mock_discord()
    # Forcer le mock de dotenv pour config.py
    sys.modules.setdefault("dotenv", m.MagicMock())

    g_config = {}
    with open("config.py", encoding="utf-8") as f:
        exec(f.read(), g_config)
    couleurs = g_config.get("COULEURS", {})

    # Couleurs effectivement utilisées dans le code
    cles_requises = [
        "or_ancien", "or_pale", "rouge_chaine", "pourpre_infernal",
        "blanc_seireitei", "gris_acier", "gris_sable", "bleu_abyssal",
        "noir_abyssal",
    ]
    for cle in cles_requises:
        assert cle in couleurs, f"Couleur manquante dans config.COULEURS : {cle}"


# ══════════════════════════════════════════════════════════════════════════════
#  5. Fichiers requis
# ══════════════════════════════════════════════════════════════════════════════

def test_fichiers_requis():
    fichiers = [
        "main.py", "config.py", "requirements.txt",
        "cogs/construction.py", "cogs/narrateur.py", "cogs/combat.py",
        "cogs/personnage.py", "cogs/zones.py", "cogs/ambiance.py",
        "cogs/evenements.py", "cogs/lore.py", "cogs/moderation.py",
        "data/structure_serveur.py",
        "utils/__init__.py", "utils/json_store.py",
    ]
    manquants = [f for f in fichiers if not os.path.exists(f)]
    assert not manquants, f"Fichiers manquants : {manquants}"


# ══════════════════════════════════════════════════════════════════════════════
#  6. JsonStore
# ══════════════════════════════════════════════════════════════════════════════

def test_json_store_class():
    """Vérifie que JsonStore existe et a les méthodes attendues."""
    from utils.json_store import JsonStore
    assert hasattr(JsonStore, "save")
    assert hasattr(JsonStore, "load")
    assert hasattr(JsonStore, "data")


# ══════════════════════════════════════════════════════════════════════════════
#  7. Fonctions d'infrastructure channels
# ══════════════════════════════════════════════════════════════════════════════

def test_construction_exports():
    """Vérifie que construction.py exporte les fonctions utilitaires et views attendues."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.construction")
    for fn_name in ["charger_roles", "charger_channels", "sauvegarder_channels", "trouver_channel"]:
        assert hasattr(mod, fn_name), f"cogs.construction manque l'export : {fn_name}"
    for cls_name in ["BoutonPacte", "BoutonCombat", "BoutonsAbonnements"]:
        assert hasattr(mod, cls_name), f"cogs.construction manque la view : {cls_name}"


# ══════════════════════════════════════════════════════════════════════════════
#  8. Factions valides cohérentes
# ══════════════════════════════════════════════════════════════════════════════

def test_role_voyageur_existe():
    """Le rôle voyageur doit exister pour le gating du Pacte des Âmes."""
    from data.structure_serveur import ROLES
    cles = {r["cle"] for r in ROLES}
    assert "voyageur" in cles, "Rôle 'voyageur' absent de ROLES"
    # Vérifier qu'il est positionné entre observateur et personnage_valide
    pos = {r["cle"]: r["position"] for r in ROLES}
    assert pos["voyageur"] > pos["observateur"], "voyageur doit être au-dessus d'observateur"
    assert pos["voyageur"] <= pos["personnage_valide"], "voyageur doit être en-dessous ou égal à personnage_valide"


def test_factions_coherentes():
    """Les factions dans RANGS_POINTS doivent correspondre à celles dans structure_serveur ROLES."""
    _mock_discord()
    g = {}
    with open("cogs/personnage.py", encoding="utf-8") as f:
        exec(f.read(), g)
    factions_rangs = set(g["RANGS_POINTS"].keys())
    assert factions_rangs == {"shinigami", "togabito", "arrancar", "quincy"}, (
        f"Factions dans RANGS_POINTS incohérentes : {factions_rangs}"
    )
    # Vérifier que chaque faction a un rôle correspondant dans structure_serveur
    from data.structure_serveur import ROLES
    cles_roles = {r["cle"] for r in ROLES}
    for faction in factions_rangs:
        assert faction in cles_roles, f"Faction {faction} absente des ROLES"


# ══════════════════════════════════════════════════════════════════════════════
#  9. Modération
# ══════════════════════════════════════════════════════════════════════════════

def test_moderation_fichier_existe():
    """Vérifie que cogs/moderation.py existe."""
    assert os.path.exists("cogs/moderation.py"), "cogs/moderation.py manquant"


def test_moderation_exports():
    """Vérifie que le cog Moderation existe et exporte setup()."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.moderation")
    assert hasattr(mod, "Moderation"), "Classe Moderation absente"
    assert hasattr(mod, "setup"), "Fonction setup() absente"


def test_moderation_config_keys():
    """Vérifie que config.py contient les clés de modération."""
    _mock_discord()
    sys.modules.setdefault("dotenv", m.MagicMock())
    g_config = {}
    with open("config.py", encoding="utf-8") as f:
        exec(f.read(), g_config)
    assert "MODERATION_MODEL" in g_config, "MODERATION_MODEL absent de config.py"
    assert "MODERATION_SYSTEM" in g_config, "MODERATION_SYSTEM absent de config.py"
    assert "OWNER_ID" in g_config, "OWNER_ID absent de config.py"
    assert "rouge_moderation" in g_config.get("COULEURS", {}), "rouge_moderation absent de COULEURS"


# ══════════════════════════════════════════════════════════════════════════════
#  10. Nouveaux cogs — fichiers et imports
# ══════════════════════════════════════════════════════════════════════════════

def test_nouveaux_cogs_fichiers():
    """Vérifie que les 6 nouveaux cogs existent."""
    cogs = [
        "cogs/scenes.py", "cogs/missions.py",
        "cogs/pnj.py", "cogs/territoire.py", "cogs/journal.py",
    ]
    manquants = [f for f in cogs if not os.path.exists(f)]
    assert not manquants, f"Nouveaux cogs manquants : {manquants}"


def test_nouveaux_cogs_imports():
    """Vérifie que les 6 nouveaux cogs s'importent sans erreur."""
    _mock_discord()
    import importlib
    cogs = ["scenes", "missions", "pnj", "territoire", "journal"]
    for cog in cogs:
        mod = importlib.import_module(f"cogs.{cog}")
        assert hasattr(mod, "setup"), f"cogs.{cog} manque la fonction setup()"


def test_scenes_exports():
    """Vérifie que scenes.py exporte BoutonScene (view persistante) et Scenes."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.scenes")
    assert hasattr(mod, "BoutonScene"), "BoutonScene absent de scenes.py"
    assert hasattr(mod, "Scenes"), "Classe Scenes absente de scenes.py"
    assert hasattr(mod, "ZONES_RP"), "ZONES_RP absent de scenes.py"


def test_missions_structure():
    """Vérifie la structure de missions.py."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.missions")
    assert hasattr(mod, "Missions"), "Classe Missions absente"
    assert hasattr(mod, "COULEURS_DIFFICULTE"), "COULEURS_DIFFICULTE absent"
    # Vérifier les 4 niveaux de difficulté
    assert set(mod.COULEURS_DIFFICULTE.keys()) == {"facile", "normale", "difficile", "legendaire"}



def test_pnj_catalogue():
    """Vérifie le catalogue des PNJ."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.pnj")
    assert hasattr(mod, "PNJ"), "Classe PNJ absente"
    assert hasattr(mod, "PNJ_CATALOGUE"), "PNJ_CATALOGUE absent"
    assert len(mod.PNJ_CATALOGUE) >= 7, f"Catalogue PNJ trop petit : {len(mod.PNJ_CATALOGUE)}"
    for cle, data in mod.PNJ_CATALOGUE.items():
        for champ in ("nom", "description", "personnalite", "emoji", "couleur"):
            assert champ in data, f"PNJ '{cle}' manque le champ '{champ}'"


def test_territoire_zones():
    """Vérifie les zones contestées du territoire."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.territoire")
    assert hasattr(mod, "Territoire"), "Classe Territoire absente"
    assert hasattr(mod, "ZONES_CONTESTEES"), "ZONES_CONTESTEES absent"
    assert len(mod.ZONES_CONTESTEES) >= 5, f"Trop peu de zones : {len(mod.ZONES_CONTESTEES)}"
    assert set(mod.FACTIONS) == {"shinigami", "togabito", "arrancar", "quincy"}


def test_journal_types_evenement():
    """Vérifie les types d'événements du journal."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.journal")
    assert hasattr(mod, "Journal"), "Classe Journal absente"
    assert hasattr(mod, "TYPES_EVENEMENT"), "TYPES_EVENEMENT absent"
    types_attendus = {"validation", "rang", "combat", "mission", "mort", "custom"}
    assert types_attendus <= set(mod.TYPES_EVENEMENT.keys()), (
        f"Types manquants : {types_attendus - set(mod.TYPES_EVENEMENT.keys())}"
    )


def test_config_pnj_system():
    """Vérifie que PNJ_SYSTEM existe dans config.py."""
    _mock_discord()
    sys.modules.setdefault("dotenv", m.MagicMock())
    g_config = {}
    with open("config.py", encoding="utf-8") as f:
        exec(f.read(), g_config)
    assert "PNJ_SYSTEM" in g_config, "PNJ_SYSTEM absent de config.py"
    assert len(g_config["PNJ_SYSTEM"]) > 100, "PNJ_SYSTEM trop court"


def test_config_couleurs_nouvelles():
    """Vérifie les nouvelles couleurs ajoutées pour les nouveaux systèmes."""
    _mock_discord()
    sys.modules.setdefault("dotenv", m.MagicMock())
    g_config = {}
    with open("config.py", encoding="utf-8") as f:
        exec(f.read(), g_config)
    couleurs = g_config.get("COULEURS", {})
    for cle in ("orange_mission",):
        assert cle in couleurs, f"Couleur '{cle}' manquante dans COULEURS"


def test_main_charge_nouveaux_cogs():
    """Vérifie que main.py référence les 6 nouveaux cogs."""
    with open("main.py", encoding="utf-8") as f:
        contenu = f.read()
    nouveaux = ["cogs.scenes", "cogs.missions",
                "cogs.pnj", "cogs.territoire", "cogs.journal"]
    for cog in nouveaux:
        assert cog in contenu, f"main.py ne charge pas {cog}"


def test_structure_forums_rp():
    """Vérifie que les zones RP sont bien en format forum."""
    from data.structure_serveur import CATEGORIES
    forums_trouves = 0
    for cat in CATEGORIES:
        for ch in cat.get("channels", []):
            if ch.get("type") == "forum":
                forums_trouves += 1
    assert forums_trouves >= 10, f"Trop peu de forums RP : {forums_trouves} (attendu >= 10)"


def test_structure_journaux_categorie():
    """Vérifie que la catégorie JOURNAUX DES ÂMES existe."""
    from data.structure_serveur import CATEGORIES
    noms_cats = [c["nom"] for c in CATEGORIES]
    journal_cat = [n for n in noms_cats if "JOURNAUX" in n.upper()]
    assert journal_cat, f"Catégorie JOURNAUX absente. Catégories : {noms_cats}"


# ══════════════════════════════════════════════════════════════════════════════
#  11. Système d'Aptitudes (Reiryoku)
# ══════════════════════════════════════════════════════════════════════════════

def test_aptitudes_constants():
    """Vérifie les constantes du système Reiryoku."""
    from data.aptitudes.constants import REIRYOKU_PAR_RANG, RANGS_P3, COUT_PALIER
    # Budget Reiryoku existe pour toutes les factions
    assert len(REIRYOKU_PAR_RANG) >= 25, f"Trop peu de rangs dans REIRYOKU_PAR_RANG : {len(REIRYOKU_PAR_RANG)}"
    # Budget max = 26 (rangs apex : Sōtaichō, Gokuō, Rey, Seitei)
    assert max(REIRYOKU_PAR_RANG.values()) == 26
    # Budget min = 3
    assert min(REIRYOKU_PAR_RANG.values()) == 3
    # P3 restrictions pour les 4 factions
    assert set(RANGS_P3.keys()) == {"shinigami", "togabito", "arrancar", "quincy"}
    # Coûts par palier
    assert COUT_PALIER == {1: 1, 2: 2, 3: 3}


def test_aptitudes_data_completeness():
    """Vérifie la complétude des données d'aptitudes (139 aptitudes, 17 Voies)."""
    from data.aptitudes import VOIES_PAR_FACTION, APTITUDES_INDEX, VOIES_INDEX
    # 4 factions
    assert set(VOIES_PAR_FACTION.keys()) == {"shinigami", "togabito", "arrancar", "quincy"}
    # 4 Voies par faction sauf shinigami (5 avec Shunkō) = 17 Voies
    voies_attendues = {"shinigami": 5, "togabito": 4, "arrancar": 4, "quincy": 4}
    for faction, voies in VOIES_PAR_FACTION.items():
        attendu = voies_attendues[faction]
        assert len(voies) == attendu, f"{faction} a {len(voies)} Voies (attendu {attendu})"
    assert len(VOIES_INDEX) == 17, f"{len(VOIES_INDEX)} Voies (attendu 17)"
    # 139 aptitudes (ancien 133 - 1 Shunkō Hakuda + 7 Voie Shunkō)
    assert len(APTITUDES_INDEX) == 139, f"{len(APTITUDES_INDEX)} aptitudes (attendu 139)"


def test_aptitudes_structure():
    """Vérifie la structure de chaque aptitude."""
    from data.aptitudes import APTITUDES_INDEX
    champs_requis = {"id", "nom", "kanji", "palier", "cout", "prereqs", "rang_min", "description"}
    for apt_id, apt in APTITUDES_INDEX.items():
        manquants = champs_requis - set(apt.keys())
        assert not manquants, f"Aptitude {apt_id} manque : {manquants}"
        assert apt["palier"] in (1, 2, 3), f"{apt_id} : palier invalide {apt['palier']}"
        assert apt["cout"] == apt["palier"], f"{apt_id} : coût {apt['cout']} != palier {apt['palier']}"
        assert len(apt["description"]) >= 50, f"{apt_id} : description trop courte"


def test_aptitudes_voie_structure():
    """Vérifie la structure de chaque Voie."""
    from data.aptitudes import VOIES_INDEX
    champs_requis = {"id", "nom", "kanji", "sous_titre", "faction", "couleur", "description", "aptitudes"}
    for voie_id, voie in VOIES_INDEX.items():
        manquants = champs_requis - set(voie.keys())
        assert not manquants, f"Voie {voie_id} manque : {manquants}"
        # 7-9 aptitudes par Voie : 3 P1 + 2-4 P2 + 2-3 P3
        apts = voie["aptitudes"]
        assert 7 <= len(apts) <= 10, f"Voie {voie_id} a {len(apts)} aptitudes (attendu 7-10)"
        paliers = [a["palier"] for a in apts]
        assert paliers.count(1) == 3, f"Voie {voie_id} : {paliers.count(1)} P1 (attendu 3)"
        assert 2 <= paliers.count(2) <= 4, f"Voie {voie_id} : {paliers.count(2)} P2 (attendu 2-4)"
        assert 2 <= paliers.count(3) <= 3, f"Voie {voie_id} : {paliers.count(3)} P3 (attendu 2-3)"


def test_aptitudes_prereqs_valides():
    """Vérifie que tous les prérequis référencent des aptitudes existantes et sont de la même faction."""
    from data.aptitudes import APTITUDES_INDEX, APTITUDE_VOIE
    # Aptitudes cross-voie autorisées (Voie Shunkō : prereqs dans Hakuda et Kidō)
    CROSS_VOIE_AUTORISEES = {"shin_shun_p1a", "shin_shun_p1b", "shin_shun_p1c"}
    for apt_id, apt in APTITUDES_INDEX.items():
        for prereq_id in apt.get("prereqs", []):
            assert prereq_id in APTITUDES_INDEX, (
                f"{apt_id} a un prérequis inconnu : {prereq_id}"
            )
            # Le prérequis doit être de la même faction
            voie_apt = APTITUDE_VOIE[apt_id]
            voie_prereq = APTITUDE_VOIE[prereq_id]
            assert voie_apt["faction"] == voie_prereq["faction"], (
                f"{apt_id} prereq {prereq_id} est dans une faction différente"
            )
            # Le prérequis doit être dans la même Voie (sauf cross-voie autorisées)
            if apt_id not in CROSS_VOIE_AUTORISEES:
                assert voie_apt["id"] == voie_prereq["id"], (
                    f"{apt_id} prereq {prereq_id} est dans une Voie différente"
                )


def test_aptitudes_ids_uniques():
    """Vérifie que tous les IDs d'aptitudes et de Voies sont uniques."""
    from data.aptitudes import APTITUDES_INDEX, VOIES_INDEX
    # Pas de doublons (les dicts garantissent déjà ça, mais vérifions les données sources)
    from data.aptitudes.shinigami import VOIES_SHINIGAMI
    from data.aptitudes.togabito import VOIES_TOGABITO
    from data.aptitudes.arrancar import VOIES_ARRANCAR
    from data.aptitudes.quincy import VOIES_QUINCY
    all_ids = []
    for voies in [VOIES_SHINIGAMI, VOIES_TOGABITO, VOIES_ARRANCAR, VOIES_QUINCY]:
        for voie in voies:
            for apt in voie["aptitudes"]:
                all_ids.append(apt["id"])
    assert len(all_ids) == len(set(all_ids)), f"IDs d'aptitudes en doublon : {len(all_ids)} vs {len(set(all_ids))}"


def test_aptitudes_peut_debloquer():
    """Teste la logique de déblocage."""
    from data.aptitudes import peut_debloquer, peut_retirer
    # P1 débloquable sans prérequis (Jinzen pour Shinigami)
    ok, raison = peut_debloquer("shin_zan_p1a", [], "yonseki", "shinigami")
    assert ok, f"P1 devrait être débloquable : {raison}"
    # P2 non débloquable sans P1
    ok, raison = peut_debloquer("shin_zan_p2a", [], "yonseki", "shinigami")
    assert not ok, "P2 ne devrait pas être débloquable sans P1"
    # P2 débloquable avec P1
    ok, raison = peut_debloquer("shin_zan_p2a", ["shin_zan_p1a"], "yonseki", "shinigami")
    assert ok, f"P2 devrait être débloquable avec P1 : {raison}"
    # P3 non débloquable pour rang trop bas (IDs mis à jour v2)
    ok, raison = peut_debloquer("shin_zan_p3a", ["shin_zan_p1a", "shin_zan_p1b", "shin_zan_p2a", "shin_zan_p2b"], "yonseki", "shinigami")
    assert not ok, "P3 ne devrait pas être débloquable pour un yonseki"
    # P3 débloquable pour fukutaicho
    ok, raison = peut_debloquer("shin_zan_p3a", ["shin_zan_p1a", "shin_zan_p1b", "shin_zan_p2a", "shin_zan_p2b"], "fukutaicho", "shinigami")
    assert ok, f"P3 devrait être débloquable pour un fukutaicho : {raison}"
    # Mauvaise faction
    ok, raison = peut_debloquer("shin_zan_p1a", [], "zainin", "togabito")
    assert not ok, "Ne devrait pas pouvoir débloquer une aptitude d'une autre faction"


def test_aptitudes_peut_retirer():
    """Teste la logique de retrait."""
    from data.aptitudes import peut_retirer
    # Retrait simple
    ok, raison = peut_retirer("shin_zan_p1a", ["shin_zan_p1a"])
    assert ok, f"Devrait pouvoir retirer : {raison}"
    # Retrait bloqué par dépendance
    ok, raison = peut_retirer("shin_zan_p1a", ["shin_zan_p1a", "shin_zan_p2a"])
    assert not ok, "Ne devrait pas pouvoir retirer P1 si P2 en dépend"


def test_aptitudes_budget_calcul():
    """Teste les calculs de budget."""
    from data.aptitudes import budget_reiryoku, reiryoku_depense, est_sur_budget
    # Budget d'un capitaine
    assert budget_reiryoku("taicho") == 22
    # Budget avec bonus
    assert budget_reiryoku("taicho", 2) == 24
    # Dépense
    assert reiryoku_depense(["shin_zan_p1a", "shin_zan_p1b", "shin_zan_p2a"]) == 4  # 1+1+2
    # Sur-budget
    assert not est_sur_budget(["shin_zan_p1a"], "taicho")
    # Inconnu = 0 budget
    assert budget_reiryoku("rang_inexistant") == 0


def test_aptitudes_p3_rang_min():
    """Vérifie que toutes les aptitudes P3 ont un rang_min."""
    from data.aptitudes import APTITUDES_INDEX
    for apt_id, apt in APTITUDES_INDEX.items():
        if apt["palier"] == 3:
            assert apt.get("rang_min"), f"P3 {apt_id} n'a pas de rang_min"


def test_aptitudes_cog_fichier():
    """Vérifie que le cog aptitudes existe."""
    assert os.path.exists("cogs/aptitudes.py"), "cogs/aptitudes.py manquant"


def test_aptitudes_cog_import():
    """Vérifie que le cog aptitudes s'importe."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.aptitudes")
    assert hasattr(mod, "Aptitudes"), "Classe Aptitudes absente"
    assert hasattr(mod, "setup"), "Fonction setup() absente"


def test_main_charge_aptitudes():
    """Vérifie que main.py charge le cog aptitudes."""
    with open("main.py", encoding="utf-8") as f:
        contenu = f.read()
    assert "cogs.aptitudes" in contenu, "main.py ne charge pas cogs.aptitudes"


# ══════════════════════════════════════════════════════════════════════════════
#  12. Puissance Spirituelle & Paliers de Combat
# ══════════════════════════════════════════════════════════════════════════════

def test_puissance_spirituelle_calcul():
    """Vérifie PS = points² // 1000, minimum 1."""
    from data.aptitudes import puissance_spirituelle
    assert puissance_spirituelle(500) == 250          # 500² / 1000 = 250
    assert puissance_spirituelle(10000) == 100_000    # 10000² / 1000 = 100 000
    assert puissance_spirituelle(0) == 1              # min 1
    assert puissance_spirituelle(50) == 2             # 50² / 1000 = 2
    assert puissance_spirituelle(1200) == 1440        # 1200² / 1000 = 1 440
    assert puissance_spirituelle(31) == 1             # 31² / 1000 = 0 → min 1
    assert puissance_spirituelle(8500) == 72_250      # 8500² / 1000 = 72 250


def test_palier_combat_equilibre():
    """Écart 0-2000 = Équilibre."""
    from data.aptitudes import palier_combat
    palier = palier_combat(72_250, 72_250)  # Deux Taichō, écart 0
    assert palier["nom"] == "Équilibre"
    assert palier["kanji"] == "均衡"
    assert palier["effet_p1"] == "normal"
    # Écart 1500 — toujours Équilibre
    palier2 = palier_combat(6_250, 4_750)
    assert palier2["nom"] == "Équilibre"


def test_palier_combat_abime():
    """Écart 55001+ = Abîme."""
    from data.aptitudes import palier_combat
    palier = palier_combat(100_000, 250)  # Sōtaichō vs Gakusei, écart 99 750
    assert palier["nom"] == "Abîme"
    assert palier["effet_p3"] == "inefficace"
    # Écart ~30 000 = Écrasement (pas Abîme)
    palier2 = palier_combat(72_250, 42_250)
    assert palier2["nom"] == "Écrasement"


def test_paliers_combat_config():
    """Vérifie que PALIERS_COMBAT est une liste de 5 dicts correctement structurés."""
    _mock_discord()
    sys.modules.setdefault("dotenv", m.MagicMock())
    g_config = {}
    with open("config.py", encoding="utf-8") as f:
        exec(f.read(), g_config)
    paliers = g_config["PALIERS_COMBAT"]
    assert isinstance(paliers, list)
    assert len(paliers) == 5
    champs = {"ecart_min", "ecart_max", "nom", "kanji", "effet_p1", "effet_p2", "effet_p3"}
    for p in paliers:
        assert champs <= set(p.keys()), f"Palier {p.get('nom', '?')} manque des champs"


def test_kido_joi_p3_existe():
    """Vérifie que shin_kid_p3c (Kidō Jōi) existe dans l'index."""
    from data.aptitudes import APTITUDES_INDEX
    assert "shin_kid_p3c" in APTITUDES_INDEX, "shin_kid_p3c absent de l'index"
    apt = APTITUDES_INDEX["shin_kid_p3c"]
    assert apt["palier"] == 3
    assert apt["nom"] == "Kidō Jōi"
    assert "shin_kid_p2c" in apt["prereqs"]
    assert "shin_kid_p2d" in apt["prereqs"]


def test_pnj_catalogue_ps():
    """Vérifie que chaque PNJ a un champ ps entier > 0."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.pnj")
    for cle, data in mod.PNJ_CATALOGUE.items():
        assert "ps" in data, f"PNJ '{cle}' n'a pas de champ 'ps'"
        assert isinstance(data["ps"], int), f"PNJ '{cle}' ps n'est pas un int"
        assert data["ps"] > 0, f"PNJ '{cle}' ps doit être > 0"


def test_aptitudes_zero_personnage_canon():
    """Vérifie qu'aucun personnage canon Bleach n'apparaît dans les descriptions."""
    from data.aptitudes import APTITUDES_INDEX, VOIES_INDEX
    # Noms de personnages canon à vérifier
    personnages_canon = [
        "yamamoto", "aizen", "ichigo", "byakuya", "yoruichi", "urahara",
        "kenpachi zaraki", "unohana", "shunsui", "ukitake", "toshiro",
        "grimmjow", "ulquiorra", "nelliel", "starrk", "barragan",
        "uryu", "ryuken", "jugram", "yhwach", "haschwalth",
    ]
    for apt_id, apt in APTITUDES_INDEX.items():
        desc_lower = apt["description"].lower()
        for nom in personnages_canon:
            assert nom not in desc_lower, (
                f"Personnage canon '{nom}' trouvé dans {apt_id}"
            )
    for voie_id, voie in VOIES_INDEX.items():
        desc_lower = voie["description"].lower()
        for nom in personnages_canon:
            assert nom not in desc_lower, (
                f"Personnage canon '{nom}' trouvé dans Voie {voie_id}"
            )
