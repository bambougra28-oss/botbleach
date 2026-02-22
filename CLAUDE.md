# INFERNUM AETERNA — Guide Claude Code

> Ce fichier est lu automatiquement par Claude Code à chaque session.
> Ne pas supprimer. Mettre à jour après chaque tâche complétée.

---

## Contexte projet
Bot Discord de jeu de rôle — univers Bleach, arc de l'Enfer, timeline alternative.  
Python 3.11+ · discord.py 2.x · Anthropic SDK (Claude Sonnet)  
Serveur cible : **Jigoku no Sekai** — RP francophone.

## Démarrage rapide
```bash
cd infernum_bot
pip install -r requirements.txt
cp .env.example .env   # remplir DISCORD_TOKEN, ANTHROPIC_API_KEY, GUILD_ID
python main.py
# Dans Discord → /setup  (construit tout le serveur en ~3 min)
```

---

## Architecture
```
infernum_bot/
├── CLAUDE.md               ← ce fichier (lu par Claude Code)
├── main.py                 ← InfernumBot, chargement 9 cogs, on_member_join
├── config.py               ← COULEURS, NARRATEUR_SYSTEM, MODERATION_SYSTEM, clés env
├── requirements.txt        ← discord.py, anthropic, python-dotenv
├── web/
│   └── index.html          ← page lore statique (GitHub Pages) — 7 onglets, lore intégral
├── .env.example
├── README.md
│
├── cogs/
│   ├── construction.py     ← /setup /purge-serveur /scan-channels /sync-roles /refresh-lore + boutons
│   ├── narrateur.py        ← /narrer /flash + auto narration_validation/rang
│   ├── combat.py           ← /combat /tour /clore-combat + archivage 7j
│   ├── personnage.py       ← /personnage /fiche-* /classement /historique /chercher-perso
│   ├── zones.py            ← /zone-creer /zone-archiver /zones-actives
│   ├── ambiance.py         ← messages IA auto (task loop 10min)
│   ├── evenements.py       ← /arc-* /fissure-etat /portail-* /etat-serveur
│   ├── lore.py             ← /lore /glossaire /fiche-faction /strates
│   └── moderation.py       ← /mod-warn /mod-timeout /mod-historique /mod-config /mod-rapport + auto
│
├── utils/
│   ├── __init__.py
│   └── json_store.py        ← JsonStore — persistence JSON avec asyncio.Lock
│
├── data/
│   ├── structure_serveur.py  ← ROLES[] + CATEGORIES[] — topologie complète
│   ├── roles_ids.json         ← {cle_role: discord_id} — généré par /setup
│   ├── channels_ids.json      ← {cle_channel: discord_id} — généré par /setup ou /scan-channels
│   ├── personnages.json       ← {discord_id: {...perso}} — généré runtime
│   ├── combats_actifs.json    ← {thread_id: {...combat}} — généré runtime
│   ├── evenements.json        ← arc + archives + fissure — généré runtime
│   ├── ambiance.json          ← channels actifs — généré runtime
│   ├── zones_dynamiques.json  ← zones créées — généré runtime
│   └── moderation.json        ← config + warnings + infractions + raid_log — généré runtime
│
├── tests/
│   └── test_integration.py   ← tests sans connexion Discord
│
└── claude_code/
    ├── prompts/            ← tâches à traiter dans l'ordre numérique
    └── docs/               ← référence technique détaillée
```

---

## Conventions de code (respecter impérativement)

### Imports inter-cogs
```python
# ✅ Correct — via bot.cogs
cog = self.bot.cogs.get("Narrateur")
if cog:
    await cog.methode(...)

# ✅ Exceptions établies — fonctions utilitaires de construction
from cogs.construction import charger_roles, trouver_channel, charger_channels

# ❌ Interdit — import direct de cog
from cogs.narrateur import Narrateur
```

### Persistence JSON (JsonStore)
```python
# Pattern standard — utiliser JsonStore pour la thread-safety
from utils.json_store import JsonStore

FICHIER = "data/nom.json"

class MonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(FICHIER)
        self.data = self._store.data  # dict standard

    async def _sauvegarder(self):
        self._store.data = self.data
        await self._store.save()  # async, protégé par Lock
```

### Résolution de channels (trouver_channel)
```python
# ✅ Résolution par ID (channels_ids.json) avec fallback substring
from cogs.construction import trouver_channel

ch = trouver_channel(guild, "journal-de-l-enfer")
if ch:
    await ch.send(embed=embed)

# ❌ Ne plus faire de boucle substring manuelle
for ch in guild.text_channels:
    if "journal" in ch.name:  # ANCIEN PATTERN — NE PAS UTILISER
        ...
```

### Embeds
```python
# ✅ Toujours
embed.set_footer(text="⸻ Infernum Aeterna · [Section] ⸻")

# ✅ Couleurs : toujours depuis config.COULEURS, jamais de hex inline
from config import COULEURS
embed = discord.Embed(color=COULEURS["or_ancien"])

# Clés disponibles dans COULEURS :
# or_ancien, or_pale, rouge_chaine, pourpre_infernal, blanc_seireitei,
# gris_acier, gris_sable, bleu_abyssal, vert_sombre, noir_absolu
```

### Commandes slash
```python
# Staff : manage_messages
@app_commands.default_permissions(manage_messages=True)

# Admin : administrator
@app_commands.default_permissions(administrator=True)

# Public : aucun décorateur de permission
```

### Narration IA
```python
# Types valides : validation | rang | combat | evenement | fissure | mort | revelation | libre
# Longueurs : courte | normale | longue
cog_narrateur = self.bot.cogs.get("Narrateur")
if cog_narrateur:
    texte = await cog_narrateur.generer_narration("validation", resume, "normale")
    embed  = cog_narrateur._construire_embed("validation", texte)
    dest   = trouver_channel(guild, "journal-de-l-enfer")
    if dest:
        await dest.send(embed=embed)
```

---

## Données de référence

### Rangs et points par faction (100% canon manga)
| Shinigami | Pts | Togabito | Pts | Arrancar | Pts | Quincy | Pts |
|---|---|---|---|---|---|---|---|
| 🎓 Gakusei (Étudiant) | 500 | 💀 Zainin | 500 | ◽ Horō | 500 | ∘ Minarai | 500 |
| ☯️ Shinigami | 1 200 | 🩸 Togabito | 2 000 | 🟢 Gillian | 1 000 | ∗ Quincy | 1 500 |
| 🗡️ Yonseki (4e Siège) | 2 500 | 🔗 Tan-Togabito | 4 500 | 🔵 Adjuchas | 2 000 | ⊕ Jagdarmee | 3 000 |
| ⚔️ Sanseki (3e Siège) | 4 000 | ⛓️ Ko-Togabito | 7 500 | 🟣 Vasto Lorde | 3 500 | ✧ Sternritter | 6 000 |
| 🎖️ Fukutaichō | 6 500 | 👑 Gokuō | 10 000 | ○ Números | 5 000 | ✦ Schutzstaffel | 8 500 |
| ⭐ Taichō | 8 500 | | | ◇ Fracción | 6 500 | 👑 Seitei | 10 000 |
| 👑 Sōtaichō | 10 000 | | | ◈ Privaron Espada | 8 000 | | |
| | | | | 💠 Espada | 9 000 | | |
| | | | | 👑 Rey | 10 000 | | |

### Niveaux Fissure
`1` Stable · `2` Instable · `3` Critique · `4` Brisée · `5` Apocalypse

### Factions (clés internes)
`shinigami` | `togabito` | `arrancar` | `quincy`

### Channels clés (résolution via `trouver_channel()` — ID puis fallback substring)
| Clé | Usage |
|---|---|
| `journal-de-l-enfer` | Narrations épiques (bot only) |
| `flash-evenements` | Alertes courtes (bot only) |
| `soumission-de-fiche` | Réception fiches joueurs |
| `validations` | Alertes staff nouvelles fiches |
| `fiches-validees` | Archives publiques personnages |
| `discussions-staff` | Canal staff principal |
| `etat-de-la-fissure` | État Fissure (message bot remplaçable) |
| `archives-des-arcs` | Résumés arcs terminés |
| `calendrier-des-arcs` | Arc en cours |
| `fissure-du-monde` | Message de bienvenue on_member_join |
| `infernum-aeterna` | Lore fondateur |
| `les-quatre-factions` | Fiches factions |
| `glossaire` | Terminologie japonaise |
| `modele-de-fiche` | Modèle à copier |
| `pacte-des-ames` | Règles du serveur |

> **Note :** Lancer `/scan-channels` pour générer `channels_ids.json` sans relancer `/setup`.

---

## Ce qui fonctionne — ne pas modifier sans raison

- **Boutons persistants** : `BoutonsFaction`, `BoutonCombat`, `BoutonsAbonnements`
  Les `custom_id` sont statiques (`faction_shinigami`, `initier_combat`, `abo_annonces`…)
  Enregistrés dans `setup_hook()` — survivent au redémarrage ✅

- **Tâches automatiques** : `boucle_ambiance` (10min), `boucle_archivage` (12h),
  `boucle_analyse_ia` (5min, modération), `boucle_nettoyage` (24h, purge warnings)

- **Déclencheurs narration** : `narration_validation_auto()` et `narration_rang_auto()`
  Appelés depuis `personnage.py`, publient dans `journal-de-l-enfer`

- **Stats combat** : `_maj_stats_personnages()` dans `combat.py`
  Incrémente `combats_total` et `combats_gagnes` dans `personnages.json`

- **on_member_join** dans `main.py` : rôle `observateur` + message de bienvenue

- **JsonStore** : persistence JSON thread-safe avec `asyncio.Lock` dans `utils/json_store.py`
  Utilisé par tous les cogs (personnage, combat, ambiance, evenements, zones, moderation)

- **trouver_channel()** : résolution de channels par ID (cache JSON) + fallback substring
  Exporté depuis `cogs/construction.py`, utilisé partout à la place des boucles manuelles

- **Commandes non-destructives** : `/scan-channels`, `/sync-roles`, `/refresh-lore`
  Permettent de mettre à jour le serveur sans relancer `/setup`

- **Page web lore** : `web/index.html` — page statique avec le lore intégral (~15 000 mots)
  7 onglets : Prologue, Shinigami, Togabito, Arrancar, Quincy, Division Zéro, Création
  Deep linking (`#shinigami`, `#togabito`, etc.), responsive, Noto Serif JP, dark theme
  Déployable sur GitHub Pages tel quel (zéro dépendance externe sauf Google Font)

- **Lore cog enrichi** : `cogs/lore.py` — 25 entrées glossaire, 10 sujets LORE_DATA,
  fiches faction narratives, lien web intégral sur chaque embed via `_ajouter_lien_web()`
  `LORE_WEB_URL` à mettre à jour quand GitHub Pages est configuré

---

## Tâches prioritaires (voir claude_code/prompts/)

| # | Fichier | Priorité | Statut |
|---|---|---|---|
| 01 | `01_peupler_channels_lore.md` | 🔴 HAUTE | ✅ Fait |
| 02 | `02_boutons_persistants_restart.md` | 🔴 HAUTE | ✅ Fait |
| 03 | `03_commande_modele_fiche.md` | 🟡 MOYENNE | ✅ Fait |
| 04 | `04_lore_data_extraction.md` | 🟡 MOYENNE | ✅ Fait |
| 05 | `05_tests_integration.md` | 🟢 BASSE | ✅ Fait |

### Optimisation v2 (complétée)

| Phase | Tâche | Statut |
|---|---|---|
| 1.1 | Stack trace logging dans error handler | ✅ |
| 1.2 | Validation API key Anthropic (narrateur, ambiance, evenements) | ✅ |
| 1.3 | Validation faction dans ModalFiche | ✅ |
| 1.4 | Rang autocomplete dynamique (remplace choices, >25 rangs) | ✅ |
| 1.5 | Fix résolution adversaire dans combat (regex mention) | ✅ |
| 1.6 | Staff role IDs au lieu de noms hardcodés | ✅ |
| 1.7 | Timeout + rate limiting API Anthropic (Semaphore + wait_for) | ✅ |
| 1.8 | JsonStore — persistence JSON thread-safe | ✅ |
| 2.1 | Infrastructure channels_ids.json + trouver_channel() | ✅ |
| 2.2 | /scan-channels | ✅ |
| 2.3 | /sync-roles | ✅ |
| 2.4 | /refresh-lore | ✅ |
| 2.5 | Nettoyage channels morts dans ambiance | ✅ |
| 3.1 | Migration substring → trouver_channel() (tous les cogs) | ✅ |
| 3.2 | Tests mis à jour (JsonStore, exports, factions) | ✅ |
| 3.3 | CLAUDE.md mis à jour | ✅ |

### Modération autonome (v3)

| Composant | Statut |
|---|---|
| Tier 1 — Heuristique on_message (spam, duplicates, mentions, invites, raids) | ✅ |
| Tier 2 — Analyse IA par lots (Claude Haiku, 5min) | ✅ |
| Tier 3 — Commandes staff (/mod-warn, /mod-timeout, /mod-historique, /mod-config, /mod-rapport) | ✅ |
| Escalade auto (3 warns/24h → timeout, 3+ infractions → alerte owner) | ✅ |
| config.py — MODERATION_MODEL, OWNER_ID, MODERATION_SYSTEM, rouge_moderation | ✅ |
| Tests intégration modération | ✅ |

---

## Système de modération (cogs/moderation.py)

### Architecture 3 tiers
- **Tier 1** : Heuristique instantanée (`on_message`, `on_member_join`). Zéro appel IA.
  Spam flood (5+msg/10s), duplicates (3x/30s), char spam (50+), mass mentions (5+), invites, raids (8+joins/15s)
- **Tier 2** : Analyse IA par lots (`boucle_analyse_ia`, 5min). Claude Haiku. Semaphore(2) séparé.
  Détecte : toxicité OOC, hors-sujet, NSFW, power-gaming, discrimination
- **Tier 3** : Commandes staff manuelles (manage_messages) et admin (administrator)

### Escalade
```
Warning → 3 warnings/24h → Infraction auto (timeout 30min)
                          → 3+ infractions → Alerte critique owner (MP)
```

### Persistence — `data/moderation.json`
```json
{
  "config": {"actif": true, "channels_surveilles": [], "seuil_spam": 5, "seuil_raid": 8, "intervalle_ia_minutes": 5},
  "warnings": {"user_id": [{"date": "ISO", "raison": "...", "source": "ia|heuristique|staff", "message_id": "..."}]},
  "infractions": {"user_id": [{"date": "ISO", "type": "timeout", "duree": 1800, "raison": "...", "source": "..."}]},
  "raid_log": [{"date": "ISO", "joins": 12, "action": "lockdown", "duree": 300}]
}
```

### Variables d'env requises
- `OWNER_ID` — ID Discord de l'owner (pour les alertes critiques en MP)

---

## Erreurs fréquentes à éviter

```python
# ❌ followup après suppression du channel source
await interaction.followup.send(...)  # → HTTPException 400 Unknown Channel

# ✅ Répondre AVANT toute opération destructive
await interaction.response.send_message("En cours…", ephemeral=True)
# ... opérations ...

# ❌ Rate limit Discord
await channel.send(embed)  # × 70 fois sans pause → 429 Too Many Requests

# ✅ Toujours pauser entre les posts en masse
await channel.send(embed)
await asyncio.sleep(0.4)

# ❌ Embed trop long
embed.description = tres_long_texte  # > 4096 chars → erreur

# ✅ Découper
for chunk in [texte[i:i+3900] for i in range(0, len(texte), 3900)]:
    embed = discord.Embed(description=chunk, color=couleur)
    await channel.send(embed=embed)
    await asyncio.sleep(0.3)
```
