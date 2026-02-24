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
├── main.py                 ← InfernumBot, chargement 15 cogs, on_member_join
├── config.py               ← COULEURS, NARRATEUR_SYSTEM, MODERATION_SYSTEM, PNJ_SYSTEM, clés env
├── requirements.txt        ← discord.py, anthropic, python-dotenv
├── web/
│   └── index.html          ← page lore statique (GitHub Pages) — 7 onglets, lore intégral
├── .env.example
├── README.md
│
├── cogs/
│   ├── construction.py     ← /setup /purge-serveur /scan-channels /sync-roles /refresh-lore /sync-permissions + boutons
│   ├── narrateur.py        ← /narrer /flash + auto narration_validation/rang
│   ├── combat.py           ← /combat /tour /clore-combat + archivage 7j
│   ├── personnage.py       ← /personnage /fiche-* /classement /historique /chercher-perso /relation-*
│   ├── zones.py            ← /zone-creer /zone-archiver /zones-actives
│   ├── ambiance.py         ← messages IA auto (task loop 10min)
│   ├── evenements.py       ← /arc-* /fissure-etat /portail-* /etat-serveur /evenement-planifier /evenements-liste
│   ├── lore.py             ← /lore /glossaire /fiche-faction /strates
│   ├── moderation.py       ← /mod-warn /mod-timeout /mod-historique /mod-config /mod-rapport + auto
│   │   ── Nouveaux systèmes ──
│   ├── scenes.py           ← /scene-creer /scene-rejoindre /scene-clore /scenes-actives + BoutonScene
│   ├── missions.py         ← /mission-creer /mission-accepter /mission-rapport /mission-valider /missions-actives
│   ├── pnj.py              ← /pnj-invoquer /pnj-parler /pnj-congedier /pnj-liste (IA Claude)
│   ├── territoire.py       ← /territoire /influence /territoire-reset /territoire-historique + tracking RP
│   └── journal.py          ← /journal /journal-ecrire /journal-lire /journal-stats + poster_evenement()
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
│   ├── moderation.json        ← config + warnings + infractions + raid_log — généré runtime
│   ├── scenes.json            ← {scenes: {thread_id: {...}}} — généré runtime
│   ├── missions.json          ← {missions: {mid: {...}}, compteur} — généré runtime
│   ├── pnj.json               ← {sessions: {thread_id: {...}}, quotas} — généré runtime
│   ├── territoire.json        ← {zones: {cle: {influence, dominante}}, saison} — généré runtime
│   └── journaux.json          ← {journaux: {uid: {thread_id, entrees...}}} — généré runtime
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
| `tableau-des-missions` | Missions actives (bot only) |
| `journaux-des-ames` | Forum journaux personnels |

> **Note :** Lancer `/scan-channels` pour générer `channels_ids.json` sans relancer `/setup`.

---

## Ce qui fonctionne — ne pas modifier sans raison

- **Boutons persistants** : `BoutonPacte`, `BoutonCombat`, `BoutonsAbonnements`, `BoutonScene`
  Les `custom_id` sont statiques (`pacte_serment`, `initier_combat`, `abo_annonces`, `lancer_scene`…)
  Enregistrés dans `setup_hook()` — survivent au redémarrage ✅
  Note : `BoutonsFaction` a été retiré — la faction est choisie dans la fiche personnage

- **Tâches automatiques** : `boucle_ambiance` (10min), `boucle_archivage` (12h),
  `boucle_analyse_ia` (5min, modération), `boucle_nettoyage` (24h, purge warnings),
  `boucle_archivage_scenes` (6h, archive scènes 14j+), `boucle_rappels` (5min, rappels événements),
  `boucle_rapport_territoire` (24h, rapport quotidien territoires)

- **Déclencheurs narration** : `narration_validation_auto()` et `narration_rang_auto()`
  Appelés depuis `personnage.py`, publient dans `journal-de-l-enfer`

- **Stats combat** : `_maj_stats_personnages()` dans `combat.py`
  Incrémente `combats_total` et `combats_gagnes` dans `personnages.json`

- **on_member_join** dans `main.py` : rôle `observateur` + embed narratif immersif dans `#fissure-du-monde`

- **JsonStore** : persistence JSON thread-safe avec `asyncio.Lock` dans `utils/json_store.py`
  Utilisé par tous les cogs (personnage, combat, ambiance, evenements, zones, moderation)

- **trouver_channel()** : résolution de channels par ID (cache JSON) + fallback substring
  Exporté depuis `cogs/construction.py`, utilisé partout à la place des boucles manuelles

- **Commandes non-destructives** : `/scan-channels`, `/sync-roles`, `/refresh-lore`, `/sync-permissions`
  Permettent de mettre à jour le serveur sans relancer `/setup`

- **Page web lore** : `web/index.html` — page statique avec le lore intégral (~15 000 mots)
  7 onglets : Prologue, Shinigami, Togabito, Arrancar, Quincy, Division Zéro, Création
  Deep linking (`#shinigami`, `#togabito`, etc.), responsive, Noto Serif JP, dark theme
  Déployable sur GitHub Pages tel quel (zéro dépendance externe sauf Google Font)

- **Lore cog enrichi** : `cogs/lore.py` — 25 entrées glossaire, 10 sujets LORE_DATA,
  fiches faction narratives, lien web intégral sur chaque embed via `_ajouter_lien_web()`
  `LORE_WEB_URL` à mettre à jour quand GitHub Pages est configuré

---

## Flux d'accueil (onboarding)

```
Arrivée → rôle observateur + embed narratif dans #fissure-du-monde
  ↓
#fissure-du-monde : embed statique (setup) — panorama du serveur + 3 étapes + lien lore
  ↓
#pacte-des-âmes : 3 embeds narratifs (intro + serments regroupés + confirmation)
  → Bouton "⚖️ Prêter Serment" (BoutonPacte, persistent, custom_id=pacte_serment)
  → Assigne le rôle voyageur → débloque #choisir-son-destin, #abonnements, #esprits-perdus
  ↓
#choisir-son-destin : présentation narrative des 4 factions (lecture seule, SANS boutons)
  → La faction est choisie DANS la fiche personnage, pas via boutons
  ↓
#modele-de-fiche : guide narratif + template code block + étapes de soumission
  ↓
#soumission-de-fiche : /fiche-soumettre → staff valide → attribution des rôles
```

**Gating par rôle :**
- `observateur` (assigné à l'arrivée) : voit `#fissure-du-monde` et `#pacte-des-âmes`
- `voyageur` (assigné par le bouton Pacte) : voit en plus `#choisir-son-destin`, `#abonnements`, `#esprits-perdus`
- Le champ `role_requis_voir` dans `structure_serveur.py` contrôle la visibilité par channel

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

### Systèmes v4 — Gameplay & Immersion (complétée)

| Système | Cog | Statut |
|---|---|---|
| Forums RP (14 zones texte → forums avec tags) | construction.py + structure_serveur.py | ✅ |
| Scènes RP (/scene-creer, BoutonScene, archivage auto 14j) | scenes.py | ✅ |
| Relations inter-personnages (/relation-declarer, /relations) | personnage.py | ✅ |
| Événements planifiés (/evenement-planifier, rappels DM) | evenements.py | ✅ |
| Missions & Quêtes (CRUD complet, rapport, validation staff) | missions.py | ✅ |
| PNJ interactifs (IA Claude, 8 PNJ catalogue, sessions thread) | pnj.py | ✅ |
| Guerre de factions / Territoires (influence, dominance, saisons) | territoire.py | ✅ |
| Journal personnel (forum thread auto, poster_evenement) | journal.py | ✅ |
| /sync-permissions (appliquer permissions sans /setup) | construction.py | ✅ |
| Tests intégration nouveaux systèmes (30 tests total) | test_integration.py | ✅ |

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

## Nouveaux systèmes v4 — Référence rapide

### Scènes RP (cogs/scenes.py)
- **Zones RP** : 14 forums Discord (ex: `le-seireitei`, `no-mans-land`) avec tags (En cours, Terminé, Combat, Solo, Ouvert, Fermé)
- **Création** : `/scene-creer` ou `BoutonScene` (modal, custom_id=`lancer_scene`)
- **Tracking** : on_message incrémente `nb_posts`, ajoute les participants auto, sauvegarde toutes les 5 posts
- **Clôture** : `/scene-clore` (créateur ou staff) → proposition narration si 5+ posts → archivage thread
- **Auto-archivage** : `boucle_archivage_scenes` (6h) — archive les scènes inactives 14+ jours

### Missions (cogs/missions.py)
- **IDs auto** : M-001, M-002... (compteur persistant)
- **Workflow** : staff `/mission-creer` → joueur `/mission-accepter` → `/mission-rapport` → staff `/mission-valider`
- **Vérifications** : personnage validé, faction compatible, places dispo, expiration
- **Notification** : rapport → embed dans `#validations` pour le staff
- **Autocomplete** : 3 fonctions d'autocomplete pour les IDs de mission

### PNJ Interactifs (cogs/pnj.py)
- **Catalogue** : 8 PNJ (kushanada, garde_seireitei, marchand_rukongai, hollow_errant, damne_ancien, quincy_refugie, esprit_perdu, personnalise)
- **Quota** : 3 invocations/jour/joueur, 10 échanges max/session
- **IA** : Claude Sonnet via Anthropic SDK, Semaphore(2), timeout 35s
- **Session** : thread dédié, historique conversationnel, congédiement avec adieu IA

### Territoire (cogs/territoire.py)
- **6 zones contestées** : No Man's Land, Fissure, Ville, Zones isolées, Confrontations, Combats de Frontière
- **Influence** : +1 par post RP (50+ mots, cooldown 30min/joueur/zone)
- **Dominance** : faction avec 20+ points d'avance → notification `#flash-evenements`
- **Saisons** : `/territoire-reset` remet tout à zéro, incrémente la saison
- **Méthode publique** : `cog_terr.ajouter_influence(zone_cle, faction, montant, raison)`
- **Rapport quotidien** : `boucle_rapport_territoire` (24h) — publie si changements

### Journal (cogs/journal.py)
- **Thread auto** : créé dans le forum `journaux-des-ames` au premier besoin
- **poster_evenement()** : méthode publique pour les autres cogs
  ```python
  cog_journal = self.bot.cogs.get("Journal")
  if cog_journal:
      await cog_journal.poster_evenement(guild, user_id, "combat", "Victoire contre X")
  ```
- **Types** : validation, rang, combat, mission, mort, custom

### Relations (dans cogs/personnage.py)
- **8 types** : rival, allié, mentor, disciple, ennemi_juré, lien_sang, camarade, amour
- **Max** : 10 relations par personnage
- **Stockage** : dans `personnages.json`, champ `relations[]`

### Événements planifiés (dans cogs/evenements.py)
- `/evenement-planifier` : crée un event avec date (JJ/MM/YYYY HH:MM), inscription
- `BoutonInscription` : persistent, custom_id=`evt_inscription`
- `boucle_rappels` : DM + flash-evenements à 24h et 1h avant l'événement

---

## Puissance Spirituelle (PS)

Indicateur chiffré de force relative pour guider la narration en combat.

### Formule
`PS = points // 100` (minimum 1)

Exemples : 500 pts → 5 PS · 2000 pts → 20 PS · 10000 pts → 100 PS

### Paliers de combat (écart de PS entre combattants)

| Écart | Nom | Kanji | P1 | P2 | P3 |
|-------|-----|-------|----|----|-----|
| 0-10 | Équilibre | 均衡 | normal | normal | normal |
| 11-25 | Ascendant | 優勢 | réduit | normal | normal |
| 26-40 | Domination | 制圧 | inefficace | réduit | normal |
| 41-60 | Écrasement | 圧倒 | inefficace | inefficace | réduit |
| 61+ | Abîme | 深淵 | inefficace | inefficace | inefficace |

Les effets sont des **guides narratifs**, pas des mécaniques automatiques :
- `normal` = fonctionne pleinement
- `réduit` = efficacité diminuée (dégâts moindres, durée réduite)
- `inefficace` = sans effet significatif sauf circonstances exceptionnelles

### PS des PNJ prédéfinis

| PNJ | PS | Justification |
|-----|-----|------|
| Kushanāda | 90 | Gardien millénaire |
| Damné Ancien | 60 | Togabito millénaire |
| PNJ Personnalisé | 50 | Défaut staff |
| Quincy Réfugié | 30 | Entraîné mais affaibli |
| Garde du Seireitei | 20 | Shinigami moyen |
| Hollow Errant | 12 | Hollow commun |
| Marchand du Rukongai | 3 | Civil |
| Esprit Perdu | 2 | Âme errante |

### Utilisation dans le code
```python
from data.aptitudes import puissance_spirituelle, palier_combat
ps = puissance_spirituelle(points)              # int >= 1
palier = palier_combat(ps_a, ps_b)              # dict depuis PALIERS_COMBAT
# palier["nom"], palier["kanji"], palier["effet_p1"], etc.
```

### Où c'est affiché
- `/personnage` — champ "⚡ Puissance Spirituelle"
- `/classement` — PS à côté des points
- Création de combat — embed avec palier et effets sur P1/P2/P3
- `/pnj-liste` et invocation PNJ — PS dans le catalogue et l'embed

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
