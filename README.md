# Infernum Aeterna

Bot Discord pour un serveur de jeu de rôle francophone dans l'univers Bleach. Timeline alternative, arc de l'Enfer. Quatre factions jouables, progression par points, système d'aptitudes complet, narration IA intégrée.

Python 3.11+ · discord.py 2.x · Anthropic SDK (Claude)

## Ce que fait le bot

Infernum Aeterna gère un serveur RP de bout en bout. À l'installation, il construit la totalité de la structure Discord : rôles, catégories, channels, permissions par faction, messages d'accueil, boutons persistants. En fonctionnement, il accompagne chaque étape du jeu.

**Accueil des joueurs.** Un nouveau membre reçoit le rôle Observateur, un message narratif immersif, puis un parcours d'intégration en plusieurs étapes. Serment, choix de faction, soumission de fiche, validation staff. Le tout sans intervention manuelle.

**Personnages.** Soumission par modal Discord, validation staff, attribution automatique des rôles de faction et de rang. Le dashboard `/personnage` affiche la progression, les statistiques de combat, la Puissance Spirituelle et le rang actuel.

**Combat.** Création de fils dédiés avec `/combat`, suivi tour par tour, calcul automatique du palier de puissance entre les deux combattants. Archivage automatique des combats inactifs après sept jours. Statistiques victoires/défaites mises à jour à la clôture.

**Aptitudes.** Chaque faction possède quatre Voies d'aptitudes (environ 20 techniques par faction), réparties en trois paliers : Éveil, Maîtrise et Transcendance. Le budget de Reiryoku croît avec le rang et se dépense librement dans les Voies.

**Puissance Spirituelle.** Un indicateur chiffré calculé à partir des points de progression (PS = Points² ÷ 1 000). L'échelle quadratique crée des écarts de puissance cohérents : un étudiant possède 250 PS, un Capitaine atteint 72 250 PS, un Commandant culmine à 100 000 PS. En combat, l'écart de PS détermine un palier narratif (Équilibre, Ascendant, Domination, Écrasement, Abîme) qui guide l'efficacité des aptitudes.

**Narration IA.** Le bot génère des narrations épiques via Claude pour les montées en rang, les validations de fiche, les clôtures d'arc et les moments clés du RP. Des messages d'ambiance IA sont publiés automatiquement dans les zones actives.

**PNJ interactifs.** Huit personnages non-joueurs invocables par les joueurs, chacun avec sa personnalité et sa puissance spirituelle. Les échanges se font en thread dédié, via Claude, avec un quota journalier.

**Missions, territoires, journaux.** Système complet de missions créées par le staff, guerre d'influence entre factions sur six zones contestées, journaux personnels en forum Discord avec événements automatiques.

**Modération autonome.** Détection de spam, raids, et contenu problématique en trois tiers : heuristique instantanée, analyse IA par lots, commandes staff. Escalade automatique des récidivistes.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Remplir DISCORD_TOKEN, ANTHROPIC_API_KEY, GUILD_ID
python main.py
```

Au premier lancement, exécuter `/setup` dans n'importe quel channel. Le bot construit tout le serveur en quelques minutes : 37 rôles, 11 catégories, plus de 65 channels avec permissions granulaires.

## Architecture

```
├── main.py                    Point d'entrée, chargement des 15 cogs
├── config.py                  Couleurs, prompts IA, paliers de combat
├── cogs/
│   ├── construction.py        /setup, /refresh-lore, boutons persistants
│   ├── narrateur.py           /narrer, /flash, narrations automatiques
│   ├── combat.py              /combat, /tour, /clore-combat, archivage
│   ├── personnage.py          /personnage, /fiche-*, /classement
│   ├── zones.py               Zones RP dynamiques
│   ├── ambiance.py            Messages d'ambiance IA (boucle 10min)
│   ├── evenements.py          Arcs narratifs, Fissure, événements planifiés
│   ├── lore.py                /lore, /glossaire, /fiche-faction, /strates
│   ├── moderation.py          Modération 3 tiers (heuristique + IA + staff)
│   ├── scenes.py              Scènes RP en forums, archivage automatique
│   ├── missions.py            Missions staff, acceptation, rapports
│   ├── pnj.py                 PNJ interactifs IA (8 PNJ, sessions thread)
│   ├── territoire.py          Guerre de factions, influence, saisons
│   └── journal.py             Journaux personnels, événements auto
├── data/
│   ├── structure_serveur.py   Définition des rôles et channels
│   ├── aptitudes/             Système d'aptitudes (4 factions × 4 voies)
│   └── *.json                 Persistence runtime (personnages, combats, etc.)
├── utils/
│   └── json_store.py          Persistence JSON thread-safe (asyncio.Lock)
├── web/
│   ├── index.html             Page lore statique (GitHub Pages)
│   └── aptitudes.html         Système d'aptitudes interactif
└── tests/
    └── test_integration.py    49 tests (structure, imports, données, logique)
```

## Commandes

Le bot expose une cinquantaine de commandes slash, réparties par domaine.

**Construction** : `/setup`, `/purge-serveur`, `/scan-channels`, `/sync-roles`, `/refresh-lore`, `/sync-permissions`

**Narration** : `/narrer`, `/flash`

**Combat** : `/combat`, `/tour`, `/clore-combat`, `/combats-actifs`

**Personnages** : `/personnage`, `/fiche-soumettre`, `/fiche-valider`, `/points-ajouter`, `/rang-attribuer`, `/classement`, `/historique`, `/chercher-perso`, `/relation-declarer`, `/relations`

**Scènes et zones** : `/scene-creer`, `/scene-rejoindre`, `/scene-clore`, `/scenes-actives`, `/zone-creer`, `/zone-archiver`, `/zones-actives`

**Missions** : `/mission-creer`, `/mission-accepter`, `/mission-rapport`, `/mission-valider`, `/missions-actives`

**PNJ** : `/pnj-invoquer`, `/pnj-parler`, `/pnj-congedier`, `/pnj-liste`

**Événements** : `/arc-ouvrir`, `/arc-clore`, `/arc-actuel`, `/arc-evenement`, `/fissure-etat`, `/portail-ouvrir`, `/portail-fermer`, `/etat-serveur`, `/evenement-planifier`, `/evenements-liste`

**Territoires** : `/territoire`, `/influence`, `/territoire-reset`, `/territoire-historique`

**Journal** : `/journal`, `/journal-ecrire`, `/journal-lire`, `/journal-stats`

**Lore** : `/lore`, `/glossaire`, `/fiche-faction`, `/strates`

**Ambiance** : `/ambiance-activer`, `/ambiance-desactiver`, `/ambiance-forcer`, `/ambiance-statut`

**Modération** : `/mod-warn`, `/mod-timeout`, `/mod-historique`, `/mod-config`, `/mod-rapport`

## Système de progression

Quatre factions, chacune avec sa propre hiérarchie de rangs et ses propres seuils de points.

| Faction | Rangs | Points |
|---|---|---|
| Shinigami | 7 (Gakusei à Sōtaichō) | 500 à 10 000 |
| Togabito | 5 (Zainin à Gokuō) | 500 à 10 000 |
| Arrancar | 9 (Horō à Rey) | 500 à 10 000 |
| Quincy | 6 (Minarai à Seitei) | 500 à 10 000 |

La montée en rang est détectée automatiquement quand les points franchissent un seuil. Le staff est notifié, le joueur reçoit ses nouveaux rôles, et une narration épique est publiée dans le journal de l'Enfer.

## Pages web

Deux pages HTML statiques déployables sur GitHub Pages, sans dépendance externe (à l'exception de Google Fonts).

**Chroniques des Quatre Races** (`web/index.html`) : le lore intégral du serveur en sept onglets. Prologue, Shinigami, Togabito, Arrancar, Quincy, Division Zéro, Création de personnage.

**Système d'Aptitudes** (`web/aptitudes.html`) : présentation interactive des quatre factions, de leurs Voies et de toutes les aptitudes. Arbres visuels, descriptions narratives, section Système avec les paliers de combat et la Puissance Spirituelle.

## Déploiement

### Avec screen
```bash
screen -S infernum
python main.py
# Ctrl+A puis D pour détacher
```

### Avec systemd
```ini
# /etc/systemd/system/infernum.service
[Unit]
Description=Infernum Aeterna Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/infernum_bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/infernum_bot/.env

[Install]
WantedBy=multi-user.target
```

## Notes techniques

Les boutons d'interaction (serment, combat, scènes, abonnements) utilisent des `custom_id` statiques et survivent aux redémarrages du bot. Les données sont stockées en JSON dans `data/`, protégées par un verrou asyncio pour la concurrence. Le bot utilise Claude Sonnet pour la narration et Claude Haiku pour la modération IA.
