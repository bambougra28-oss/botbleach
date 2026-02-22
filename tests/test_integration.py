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

    # Collecter toutes les clés référencées dans les channels
    cles_utilisees = set()
    for cat in CATEGORIES:
        for ch in cat.get("channels", []):
            for key in ["factions", "role_ecrivant"]:
                val = ch.get(key)
                if isinstance(val, list):
                    cles_utilisees.update(val)
                elif isinstance(val, str):
                    cles_utilisees.add(val)

    inconnues = cles_utilisees - cles_roles - {"personnage_valide", "tous"}
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
    """Vérifie que construction.py exporte les fonctions utilitaires attendues."""
    _mock_discord()
    import importlib
    mod = importlib.import_module("cogs.construction")
    for fn_name in ["charger_roles", "charger_channels", "sauvegarder_channels", "trouver_channel"]:
        assert hasattr(mod, fn_name), f"cogs.construction manque l'export : {fn_name}"


# ══════════════════════════════════════════════════════════════════════════════
#  8. Factions valides cohérentes
# ══════════════════════════════════════════════════════════════════════════════

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
