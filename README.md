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

Quatre factions, chacune avec sa propre hiérarchie de rangs. Le staff attribue des points de progression en récompense du RP actif (scènes, combats, arcs narratifs, missions, journal personnel). Quand les points franchissent un seuil de rang, la montée est automatique : le bot attribue les nouveaux rôles Discord et publie une narration épique dans le Journal de l'Enfer.

Chaque rang débloque un budget de Reiryoku (霊力) à investir dans les aptitudes, et une Puissance Spirituelle (PS) calculée par la formule PS = Points² ÷ 1 000.

### Shinigami

| Rang | Points | 霊力 | PS |
|---|---|---|---|
| Gakusei (Étudiant) | 500 | 3 | 250 |
| Shinigami | 1 200 | 6 | 1 440 |
| Yonseki (4e Siège) | 2 500 | 10 | 6 250 |
| Sanseki (3e Siège) | 4 000 | 14 | 16 000 |
| Fukutaichō | 6 500 | 18 | 42 250 |
| Taichō | 8 500 | 22 | 72 250 |
| Sōtaichō | 10 000 | 26 | 100 000 |

### Togabito

| Rang | Points | 霊力 | PS |
|---|---|---|---|
| Zainin | 500 | 3 | 250 |
| Togabito | 2 000 | 8 | 4 000 |
| Tan-Togabito | 4 500 | 14 | 20 250 |
| Kō-Togabito | 7 500 | 20 | 56 250 |
| Gokuō | 10 000 | 26 | 100 000 |

### Arrancar

| Rang | Points | 霊力 | PS |
|---|---|---|---|
| Horō (Hollow) | 500 | 3 | 250 |
| Gillian | 1 000 | 5 | 1 000 |
| Adjuchas | 2 000 | 8 | 4 000 |
| Vasto Lorde | 3 500 | 11 | 12 250 |
| Números | 5 000 | 14 | 25 000 |
| Fracción | 6 500 | 17 | 42 250 |
| Privaron Espada | 8 000 | 20 | 64 000 |
| Espada | 9 000 | 23 | 81 000 |
| Rey | 10 000 | 26 | 100 000 |

Les rangs Horō à Vasto Lorde sont des Hollow qui n'ont pas encore brisé leur masque. Ils n'ont pas accès à la Voie Resurrección, réservée aux véritables Arrancar (à partir de Números).

### Quincy

| Rang | Points | 霊力 | PS |
|---|---|---|---|
| Minarai (Apprenti) | 500 | 3 | 250 |
| Quincy | 1 500 | 7 | 2 250 |
| Jagdarmee | 3 000 | 12 | 9 000 |
| Sternritter | 6 000 | 18 | 36 000 |
| Schutzstaffel | 8 500 | 22 | 72 250 |
| Seitei | 10 000 | 26 | 100 000 |

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
