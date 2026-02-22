# PROMPT DE DÉMARRAGE — À COPIER EN PREMIER MESSAGE À CLAUDE CODE

---

## Instructions pour Claude Code

Tu travailles sur **Infernum Aeterna**, un bot Discord de jeu de rôle (univers Bleach).

Le fichier `CLAUDE.md` à la racine du projet contient toute la documentation technique.
**Lis-le en premier** avant toute action.

Les tâches sont dans `claude_code/prompts/`, numérotées par priorité.
La documentation de référence est dans `claude_code/docs/`.

## Ordre de travail recommandé

1. Lire `CLAUDE.md`
2. Lire `claude_code/docs/architecture.md`
3. Traiter les tâches dans l'ordre : 01 → 02 → 03 → 04 → 05
4. Après chaque tâche : vérifier la syntaxe avec `python -c "import ast; ast.parse(open('cogs/fichier.py').read())"`, et mettre à jour le tableau de statut dans `CLAUDE.md`

## Première tâche à traiter

Commence par `claude_code/prompts/01_peupler_channels_lore.md`.

Avant de coder :
1. Lis `cogs/lore.py` en entier pour voir les données disponibles
2. Lis `cogs/personnage.py` lignes 39-75 (RANGS_POINTS)
3. Lis `cogs/construction.py` lignes 260-335 (fonctions _envoyer_*)
4. Implémente `_peupler_channels_lore()` selon le prompt

## Contraintes globales à respecter toujours

- Ne jamais hardcoder de valeur hex de couleur — utiliser `COULEURS` depuis `config.py`
- `await asyncio.sleep(0.4)` entre chaque post Discord en masse
- Chaque embed doit avoir un `set_footer`
- Les imports inter-cogs passent par `self.bot.cogs.get("NomCog")` sauf `charger_roles()`
- Vérifier la syntaxe après chaque modification : `python -c "import ast; ast.parse(open('cogs/X.py').read())"`

## Structure du projet
```
infernum_bot/
├── CLAUDE.md          ← documentation principale
├── main.py
├── config.py
├── cogs/              ← 8 cogs fonctionnels
├── data/              ← JSON runtime + structure_serveur.py
└── claude_code/
    ├── prompts/       ← tâches 01 à 05
    └── docs/          ← architecture.md, lore_reference.md
```
