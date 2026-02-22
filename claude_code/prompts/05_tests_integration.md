# TÂCHE 05 — Tests d'intégration

**Priorité : BASSE**  
**Nouveau fichier à créer : `tests/test_integration.py`**  
**Fichiers à lire : tous les cogs**

---

## Objectif

Créer une suite de tests qui vérifient la cohérence du projet sans nécessiter
une connexion Discord réelle. Tests syntaxiques, structurels et logiques.

---

## Tests à implémenter

### 1. Syntaxe de tous les fichiers Python

```python
import ast, os

def test_syntax():
    errors = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            with open(path) as fp:
                src = fp.read()
            try:
                ast.parse(src)
            except SyntaxError as e:
                errors.append(f"{path} L{e.lineno}: {e.msg}")
    assert not errors, "\n".join(errors)
```

### 2. Imports critiques

```python
def test_imports_critiques():
    # Simuler discord sans connexion
    import unittest.mock as m, sys
    for mod in ["discord", "discord.ext", "discord.ext.commands", "discord.app_commands",
                "discord.ext.tasks", "anthropic"]:
        sys.modules[mod] = m.MagicMock()
    
    # Ces imports doivent fonctionner
    from data.structure_serveur import ROLES, CATEGORIES
    assert len(ROLES) >= 30, f"Trop peu de rôles : {len(ROLES)}"
    assert len(CATEGORIES) >= 10, f"Trop peu de catégories : {len(CATEGORIES)}"
```

### 3. Structure des données

```python
def test_structure_roles():
    from data.structure_serveur import ROLES
    cles_requises = {"cle", "nom", "couleur", "hoist", "mentionable", "position"}
    for role in ROLES:
        manquantes = cles_requises - set(role.keys())
        assert not manquantes, f"Rôle {role.get('nom', '?')} manque : {manquantes}"

def test_structure_categories():
    from data.structure_serveur import CATEGORIES
    for cat in CATEGORIES:
        assert "nom" in cat, f"Catégorie sans nom"
        assert "channels" in cat, f"Catégorie {cat['nom']} sans channels"
        for ch in cat["channels"]:
            assert "nom" in ch, f"Channel sans nom dans {cat['nom']}"
            assert "type" in ch, f"Channel {ch.get('nom','?')} sans type"

def test_rangs_points():
    # RANGS_POINTS doit avoir 4 factions avec au moins 4 rangs chacune
    import sys, unittest.mock as m
    for mod in ["discord","discord.ext","discord.ext.commands","discord.app_commands"]:
        sys.modules.setdefault(mod, m.MagicMock())
    g = {}
    exec(open("cogs/personnage.py").read(), g)
    rp = g["RANGS_POINTS"]
    assert set(rp.keys()) == {"shinigami","togabito","arrancar","quincy"}
    for faction, rangs in rp.items():
        assert len(rangs) >= 4, f"{faction} a seulement {len(rangs)} rangs"
        # Vérifier ordre croissant des points
        points = [r[1] for r in rangs]
        assert points == sorted(points), f"{faction} : rangs non ordonnés par points"

def test_glossaire_complet():
    import sys, unittest.mock as m
    for mod in ["discord","discord.ext","discord.ext.commands","discord.app_commands"]:
        sys.modules.setdefault(mod, m.MagicMock())
    g = {}
    exec(open("cogs/lore.py").read(), g)
    glossaire = g["GLOSSAIRE"]
    assert len(glossaire) >= 15, f"Glossaire trop court : {len(glossaire)} entrées"
    for cle, val in glossaire.items():
        assert isinstance(val, tuple) and len(val) == 2, f"{cle} : format incorrect"
        assert val[0], f"{cle} : kanji vide"
        assert val[1], f"{cle} : définition vide"
```

### 4. Cohérence inter-fichiers

```python
def test_cles_roles_coherentes():
    """Les clés dans ROLES doivent correspondre aux clés utilisées dans CATEGORIES."""
    from data.structure_serveur import ROLES, CATEGORIES
    import json
    
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
    """Toutes les couleurs utilisées dans lore.py doivent exister dans config.py."""
    import sys, unittest.mock as m
    for mod in ["discord","discord.ext","discord.ext.commands","discord.app_commands",
                "anthropic","dotenv"]:
        sys.modules.setdefault(mod, m.MagicMock())
    
    g_config = {}
    exec(open("config.py").read(), g_config)
    couleurs = g_config.get("COULEURS", {})
    
    # Vérifier couleurs minimales requises
    cles_requises = [
        "or_ancien", "or_pale", "rouge_chaine", "pourpre_infernal",
        "blanc_seireitei", "gris_acier", "gris_sable", "bleu_abyssal",
        "vert_sombre", "noir_absolu"
    ]
    for cle in cles_requises:
        assert cle in couleurs, f"Couleur manquante dans config.COULEURS : {cle}"
```

### 5. Fichiers requis

```python
def test_fichiers_requis():
    fichiers = [
        "main.py", "config.py", "requirements.txt", ".env.example",
        "cogs/construction.py", "cogs/narrateur.py", "cogs/combat.py",
        "cogs/personnage.py", "cogs/zones.py", "cogs/ambiance.py",
        "cogs/evenements.py", "cogs/lore.py",
        "data/structure_serveur.py",
    ]
    manquants = [f for f in fichiers if not os.path.exists(f)]
    assert not manquants, f"Fichiers manquants : {manquants}"
```

---

## Lancer les tests

```bash
cd infernum_bot
pip install pytest
pytest tests/test_integration.py -v
```

Résultat attendu : tous les tests `PASSED`.

---

## Validation

- [ ] `pytest tests/test_integration.py` → 0 erreur
- [ ] Tests exécutables sans connexion Discord
- [ ] Ajout d'un test quand un bug est corrigé (non-régression)
