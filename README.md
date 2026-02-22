# ⛩️ Infernum Aeterna — Bot Discord

Bot administrateur pour le serveur de jeu de rôle **Infernum Aeterna**  
Univers Bleach · Arc de l'Enfer · Timeline indépendante du canon TYBW

---

## Prérequis

- Python 3.11+
- Un serveur Discord avec les permissions Administrateur
- Une clé API Anthropic (Claude)

---

## Installation

```bash
# 1. Cloner ou copier le dossier infernum_bot/
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos tokens

# 4. Lancer le bot
python main.py
```

### Contenu de `.env`
```
DISCORD_TOKEN=ton_token_discord
ANTHROPIC_API_KEY=ta_cle_anthropic
GUILD_ID=id_numerique_du_serveur
```

---

## Premier démarrage

Une fois le bot connecté, exécuter dans n'importe quel channel Discord :

```
/setup
```

Le bot va créer en 2-3 minutes :
- 37 rôles avec couleurs et positions
- 11 catégories
- 65+ channels avec permissions granulaires par faction
- Messages épinglés initiaux (boutons faction, règles, etc.)

---

## Architecture

```
infernum_bot/
├── main.py                   — Point d'entrée, chargement des 8 cogs
├── config.py                 — Tokens, palette couleurs, prompt Narrateur
├── requirements.txt
├── .env.example
├── README.md
├── cogs/
│   ├── construction.py       — /setup, boutons persistants
│   ├── narrateur.py          — /narrer, /flash, déclencheurs auto
│   ├── combat.py             — /combat, /tour, /clore-combat, archivage auto
│   ├── personnage.py         — /personnage, /fiche-*, /classement, /historique
│   ├── zones.py              — /zone-creer, /zone-archiver
│   ├── ambiance.py           — Messages d'ambiance IA automatiques
│   ├── evenements.py         — Arcs narratifs, Fissure, portails
│   └── lore.py               — /lore, /glossaire, /fiche-faction, /strates
└── data/
    ├── structure_serveur.py  — Définition des 37 rôles et 65+ channels
    ├── roles_ids.json         — Généré par /setup
    ├── personnages.json       — Généré automatiquement
    ├── combats_actifs.json    — Généré automatiquement
    ├── evenements.json        — Généré automatiquement
    ├── ambiance.json          — Généré automatiquement
    └── zones_dynamiques.json  — Généré automatiquement
```

---

## Commandes (35 commandes slash)

### 🏗️ Construction
| Commande | Accès | Description |
|---|---|---|
| `/setup` | Admin | Construit le serveur complet (rôles, catégories, channels) |
| `/purge-serveur` | Admin | Supprime tous les channels et rôles gérés |

### 📜 Narration
| Commande | Accès | Description |
|---|---|---|
| `/narrer` | Staff | Génère une narration épique via Claude (8 types × 3 longueurs) |
| `/flash` | Staff | Publie une alerte narrative courte dans flash-événements |

### ⚔️ Combat
| Commande | Accès | Description |
|---|---|---|
| `/combat` | Tous | Crée un fil de combat avec un adversaire |
| `/tour` | Participants | Signale la fin d'un tour et enregistre l'action |
| `/clore-combat` | Participants / Staff | Clôture le combat, propose une narration épique |
| `/combats-actifs` | Staff | Liste tous les combats en cours |

> Les fils de combat inactifs depuis **7 jours** sont archivés automatiquement.

### 👤 Personnages
| Commande | Accès | Description |
|---|---|---|
| `/personnage` | Tous | Dashboard complet d'un personnage (barre progression, stats) |
| `/fiche-soumettre` | Tous | Soumet une fiche via modal Discord |
| `/fiche-valider` | Staff | Valide une fiche, attribue les rôles, notifie en DM |
| `/points-ajouter` | Staff | Ajoute ou retire des points, vérifie la montée en rang |
| `/rang-attribuer` | Staff | Attribue un rang, met à jour les rôles, déclenche la narration |
| `/classement` | Tous | Leaderboard top 10 global ou par faction |
| `/historique` | Tous | Fiche narrative complète (rangs, combats, progression) |
| `/chercher-perso` | Tous | Recherche un personnage par nom ou faction |

### 📍 Zones Dynamiques
| Commande | Accès | Description |
|---|---|---|
| `/zone-creer` | Staff | Crée un salon RP temporaire dans une catégorie existante |
| `/zone-archiver` | Staff | Archive (ferme) un salon dynamique avec message de clôture |
| `/zones-actives` | Staff | Liste toutes les zones dynamiques ouvertes |

### 🌫️ Ambiance
| Commande | Accès | Description |
|---|---|---|
| `/ambiance-activer` | Staff | Active les messages d'ambiance IA dans un channel |
| `/ambiance-desactiver` | Staff | Désactive les messages d'ambiance |
| `/ambiance-forcer` | Staff | Déclenche immédiatement un message d'ambiance |
| `/ambiance-statut` | Staff | Liste les channels avec ambiance active |

### 📖 Événements & Arcs
| Commande | Accès | Description |
|---|---|---|
| `/arc-ouvrir` | Admin | Démarre un nouvel arc narratif (déclenche narration auto) |
| `/arc-clore` | Admin | Clôture l'arc avec résumé IA publié dans les archives |
| `/arc-actuel` | Tous | Affiche l'arc en cours et l'état de la Fissure |
| `/arc-evenement` | Staff | Ajoute un événement notable à l'arc en cours |
| `/fissure-etat` | Admin | Met à jour l'état public de la Fissure (5 niveaux) |
| `/portail-ouvrir` | Staff | Rend un channel événementiel visible + ping rôle |
| `/portail-fermer` | Staff | Archive un channel événementiel |
| `/etat-serveur` | Tous | Tableau de bord global (Fissure, arc, membres, factions) |

### 📚 Lore
| Commande | Accès | Description |
|---|---|---|
| `/lore` | Tous | Résumé d'un concept clé (Fissure, Reiō, Konsō Reisai…) |
| `/glossaire` | Tous | Définition d'un terme japonais du lore |
| `/fiche-faction` | Tous | Fiche complète d'une faction jouable |
| `/strates` | Tous | Carte narrative des cinq Strates de l'Enfer |

---

## Système de rangs et points

| Faction | Rangs | Points min → max |
|---|---|---|
| Shinigami | 7 rangs | 500 → 10 000 |
| Togabito | 4 rangs | 500 → 10 000 |
| Arrancar | 5 rangs | 800 → 10 000 |
| Quincy | 4 rangs | 500 → 10 000 |

La montée en rang est détectée automatiquement après `/points-ajouter` et notifie le staff.  
Le vainqueur d'un combat est enregistré automatiquement dans les statistiques.

---

## Déploiement VPS

### Avec screen (simple)
```bash
screen -S infernum
python main.py
# Ctrl+A puis D pour détacher
```

### Avec systemd (recommandé)
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
```bash
systemctl enable infernum
systemctl start infernum
journalctl -u infernum -f
```

---

## Comportements automatiques

| Déclencheur | Action automatique |
|---|---|
| Nouveau membre rejoint | Rôle Observateur + message de bienvenue |
| Fiche validée | Narration d'accueil publiée dans journal-de-l-enfer |
| Points dépassent un seuil | Alerte montée en rang dans canal staff |
| Rang attribué | Narration de promotion + DM au joueur |
| Arc ouvert | Narration d'ouverture publiée dans journal-de-l-enfer |
| Arc clôturé | Résumé épique archivé dans archives-des-arcs |
| Combat clôturé | Stats joueurs mises à jour automatiquement |
| Fil de combat inactif 7j | Archivage automatique du fil Discord |

---

## Notes techniques

- Les boutons (faction, abonnements, combat) sont **persistants** : ils survivent aux redémarrages du bot grâce aux `custom_id` statiques.
- Les données sont stockées en JSON dans `data/`. Pour une production avec beaucoup d'utilisateurs, envisager une migration vers SQLite.
- Le bot utilise le modèle `claude-sonnet-4-5`. Chaque narration coûte ~1-3 secondes et ~500-1000 tokens.
