# TÂCHE 01 — Peupler les channels Lore & Administration au /setup

**Priorité : HAUTE**  
**Fichier à modifier : `cogs/construction.py`**  
**Lire avant : `cogs/lore.py` (GLOSSAIRE, FICHES_FACTION, STRATES, LORE_DATA), `cogs/personnage.py` (RANGS_POINTS)**

---

## Problème

Après `/setup`, les channels CHRONIQUES et ADMINISTRATION sont tous vides.  
Le lore complet existe déjà dans `cogs/lore.py` mais n'est accessible qu'en commandes.  
Un serveur RP dont les channels de lore sont vides au premier lancement est inutilisable.

---

## Implémentation

### 1. Ajouter dans `construction.py` après `_envoyer_instructions_fiche()`

```python
async def _peupler_channels_lore(guild: discord.Guild):
    """Poste le lore dans les channels CHRONIQUES et ADMINISTRATION."""
    from cogs.lore import GLOSSAIRE, FICHES_FACTION, STRATES
    from cogs.personnage import RANGS_POINTS

    def find_ch(partial: str):
        for ch in guild.text_channels:
            if partial in ch.name:
                return ch
        return None

    async def poster(channel, embed):
        if not channel:
            return
        try:
            msg = await channel.send(embed=embed)
            await msg.pin()
            await asyncio.sleep(0.4)
        except Exception as e:
            print(f"[Lore Setup] {getattr(channel,'name','?')} : {e}")
```

### 2. Appel dans `setup()` — ajouter juste avant le résumé final

```python
await _peupler_channels_lore(guild)
```

---

## Channels à peupler — détail complet

### 📖・infernum-aeterna — LORE_DATA de lore.py

Lire la fonction `lore()` dans `cogs/lore.py` à partir de `LORE_DATA = {`.  
Poster un embed par clé dans cet ordre : `origine`, `fissure`, `reio`, `division_zero`, `konso_reisai`.  
Reprendre exactement les `title`, `description`, `fields` utilisés dans la commande `/lore`.

### ⚜️・les-quatre-factions — FICHES_FACTION

```python
ch = find_ch("les-quatre-factions")
for faction_key in ["shinigami", "togabito", "arrancar", "quincy"]:
    fiche = FICHES_FACTION[faction_key]
    e = discord.Embed(title=fiche["titre"], color=fiche["couleur"])
    for nom_section, texte_section in fiche["sections"]:
        e.add_field(name=nom_section, value=texte_section, inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Factions ⸻")
    await poster(ch, e)
```

### 🗺️・geographie-des-mondes — STRATES + zones

```python
ch = find_ch("geographie")
# Embed 1 : Les 5 Strates
e = discord.Embed(title="🗺️ Les Cinq Strates de l'Enfer", color=COULEURS["pourpre_infernal"])
for strate in STRATES:
    e.add_field(name=strate["nom"], value=strate["description"], inline=False)
e.set_footer(text="⸻ Infernum Aeterna · Géographie ⸻")
await poster(ch, e)

# Embed 2 : Zones hors-Enfer (rédiger directement)
e2 = discord.Embed(
    title="🌍 Les Trois Mondes",
    description=(
        "**Soul Society** — Royaume des Shinigami. "
        "Seireitei au centre, Rukongai en périphérie. "
        "Gouverné par le Gotei 13, fragilisé par la vérité du Konsō Reisai.\n\n"
        "**Hueco Mundo** — Désert éternel des Hollow. "
        "Las Noches en son cœur. Résonance croissante avec le Jigoku no Rinki "
        "depuis l'ouverture de la Fissure.\n\n"
        "**Monde des Vivants** — Karakura et ses alentours. "
        "Portails actifs détectés. Contamination spirituelle progressive.\n\n"
        "**La Frontière** — Espace entre les mondes. "
        "Épicentre de la Fissure. Territoire sans loi."
    ),
    color=COULEURS["gris_acier"]
)
e2.set_footer(text="⸻ Infernum Aeterna · Géographie ⸻")
await poster(ch, e2)
```

### 📜・glossaire — GLOSSAIRE par groupes

```python
ch = find_ch("glossaire")
entrees = list(GLOSSAIRE.items())
# Grouper par 5 pour rester lisible
for i in range(0, len(entrees), 5):
    groupe = entrees[i:i+5]
    e = discord.Embed(
        title=f"📜 Glossaire ({i+1}–{min(i+5, len(entrees))})",
        color=COULEURS["or_pale"]
    )
    for cle, (kanji, definition) in groupe:
        e.add_field(name=f"**{cle.replace('_',' ').title()}** {kanji}", value=definition, inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Glossaire ⸻")
    await poster(ch, e)
```

### ⚔️・systeme-et-competences — LORE_DATA["systeme"] + RANGS_POINTS

```python
ch = find_ch("systeme")
# Embed 1 : règles générales — depuis LORE_DATA["systeme"] dans lore.py
# (reprendre exactement le contenu de la commande /lore avec value="systeme")

# Embed 2 : tableau des rangs
e = discord.Embed(title="📊 Rangs par Faction", color=COULEURS["or_ancien"])
for faction, rangs in RANGS_POINTS.items():
    lignes = "\n".join(f"{label} — {pts:,} pts" for _, pts, label in rangs)
    e.add_field(name=faction.capitalize(), value=lignes, inline=True)
e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
await poster(ch, e)
```

### 🦴・bestiaire-infernal — Rédiger ces 3 embeds

```python
ch = find_ch("bestiaire")

embeds_bestiaire = [
    {
        "titre": "倶舎那陀 — Les Kushanāda",
        "desc": (
            "Créatures titanesques aux allures de magistrats cosmiques. "
            "Ils ne punissent pas — ils maintiennent. "
            "Leur seul but : empêcher quiconque de s'échapper des Strates."
        ),
        "fields": [
            ("Apparence", "Silhouettes de juges aux yeux vides, portant des masses rituelles. "
                          "Taille variable selon la Strate — plus profond, plus imposants."),
            ("Comportement", "Passifs en l'absence de tentative d'évasion. "
                             "Réactivité instantanée dès qu'une âme approche des limites."),
            ("Anomalie", "Depuis l'ouverture de la Fissure, certains Kushanāda semblent hésiter. "
                         "Comme si leurs instructions entraient en conflit avec quelque chose de nouveau."),
        ],
        "couleur": "gris_acier"
    },
    {
        "titre": "地獄の燐気 — Le Jigoku no Rinki",
        "desc": (
            "Sphères noires de Reishi corrompu suintant des murs de l'Enfer depuis la Fissure. "
            "Contact prolongé dissout progressivement l'identité spirituelle."
        ),
        "fields": [
            ("Symptômes", "Mémoire fragmentée, puissance instable, "
                          "réminiscences involontaires d'avant la mort."),
            ("Danger", "Irréversible au stade avancé. "
                       "L'âme commence à se fondre dans la matière infernale."),
            ("Usage contrôlé", "Certains Togabito anciens ont appris à le canaliser. "
                                "Risque extrême. Pouvoir disproportionné."),
        ],
        "couleur": "pourpre_infernal"
    },
    {
        "titre": "虚 — Les Hollow Infernaux",
        "desc": (
            "Hollow ayant sombré en Enfer plutôt que d'être purifiés. "
            "Mutation profonde due au Reishi infernal. "
            "Plus dangereux et moins prévisibles que leurs équivalents standard."
        ),
        "fields": [
            ("Différences", "Masque partiellement dissous. Cero noir. "
                            "Instinct partiellement remplacé par une logique primitive."),
            ("Comportement", "Ni sauvages ni organisés — quelque chose entre les deux. "
                             "Semblent reconnaître une hiérarchie non formalisée."),
            ("Mystère", "Certains semblent reconnaître les Togabito anciens "
                        "et ne pas les attaquer. Raison inconnue."),
        ],
        "couleur": "noir_absolu"
    },
]

for data in embeds_bestiaire:
    e = discord.Embed(title=data["titre"], description=data["desc"], color=COULEURS[data["couleur"]])
    for nom, val in data["fields"]:
        e.add_field(name=nom, value=val, inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Bestiaire ⸻")
    await poster(ch, e)
```

### ⚖️・pacte-des-ames — Règles narratives

```python
ch = find_ch("pacte")
e = discord.Embed(
    title="⚖️ Le Pacte des Âmes",
    description=(
        "En entrant dans **Infernum Aeterna**, chaque âme prête les serments suivants.\n\u200b"
    ),
    color=COULEURS["or_ancien"]
)
serments = [
    ("① Respect narratif",    "Je respecte le fil narratif de chaque joueur sans l'interrompre sans accord."),
    ("② Consentement",        "Je n'impose aucune action à un personnage sans le consentement de son joueur."),
    ("③ Transparence",        "J'informe le staff avant toute mort narrative ou séquence traumatisante."),
    ("④ Cohérence lore",      "Je reste en accord avec le lore du serveur et consulte en cas de doute."),
    ("⑤ Séparation IC/HorRP", "Je n'utilise pas d'informations hors-RP dans le jeu (no méta-gaming)."),
    ("⑥ Signalement",         "Je signale tout manquement au staff plutôt que d'y répondre seul."),
    ("⑦ Accueil",             "J'accueille les nouveaux joueurs avec la même patience qu'on m'a accordée."),
    ("⑧ Espace partagé",      "Je ne monopolise pas les zones narratives importantes."),
    ("⑨ Respect des décisions","J'accepte les décisions du staff même en désaccord, puis j'en débats par écrit."),
    ("⑩ Contribution",        "Je contribue activement à faire de ce serveur une expérience mémorable."),
]
for nom, texte in serments:
    e.add_field(name=nom, value=texte, inline=False)
e.add_field(name="\u200b", value="*「 Ces serments ne sont pas des règles. Ils sont la fondation. 」*", inline=False)
e.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
await poster(ch, e)
```

### 📋・modele-de-fiche — Modèle + instructions

```python
ch = find_ch("modele-de-fiche")

# Embed 1 : le modèle
modele = (
    "```\n"
    "═══════════════════════════════\n"
    "   FICHE PERSONNAGE — INFERNUM AETERNA\n"
    "═══════════════════════════════\n"
    "Nom du personnage :\n"
    "Faction : [Shinigami / Togabito / Arrancar / Quincy]\n"
    "Rang souhaité :\n"
    "Âge apparent :\n\n"
    "HISTOIRE (300 mots minimum) :\n"
    "[Votre texte]\n\n"
    "APPARENCE :\n"
    "[Description physique]\n\n"
    "APTITUDES (3 maximum selon rang) :\n"
    "1.\n"
    "2.\n"
    "3.\n\n"
    "OBJECTIF NARRATIF :\n"
    "[Ce que votre personnage cherche dans le contexte de la Fissure]\n"
    "═══════════════════════════════\n"
    "```"
)
e1 = discord.Embed(title="📋 Modèle de Fiche Personnage", description=modele, color=COULEURS["blanc_seireitei"])
e1.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
await poster(ch, e1)

# Embed 2 : instructions
e2 = discord.Embed(title="📥 Comment soumettre votre fiche", color=COULEURS["or_pale"])
e2.add_field(name="Étape 1", value="Copiez le modèle ci-dessus dans un éditeur de texte.", inline=False)
e2.add_field(name="Étape 2", value="Remplissez chaque section. Minimum 300 mots pour l'Histoire.", inline=False)
e2.add_field(name="Étape 3", value="Rendez-vous dans `📥・soumission-de-fiche`.", inline=False)
e2.add_field(name="Étape 4", value="Tapez `/fiche-soumettre` et collez votre fiche dans le formulaire.", inline=False)
e2.add_field(name="Délai", value="Le staff valide sous 48h. Vous recevrez une notification en DM.", inline=False)
e2.add_field(name="Après validation", value="Rôle faction + accès aux zones RP attribués automatiquement.", inline=False)
e2.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
await poster(ch, e2)
```

---

## Validation

- [ ] `📖・infernum-aeterna` : 5 embeds épinglés
- [ ] `⚜️・les-quatre-factions` : 4 embeds épinglés
- [ ] `🗺️・geographie-des-mondes` : 2 embeds épinglés
- [ ] `📜・glossaire` : 4 embeds (19 termes / 5 par embed)
- [ ] `⚔️・systeme-et-competences` : 2 embeds épinglés
- [ ] `🦴・bestiaire-infernal` : 3 embeds épinglés
- [ ] `⚖️・pacte-des-âmes` : 1 embed épinglé
- [ ] `📋・modele-de-fiche` : 2 embeds épinglés
- [ ] Setup total < 5 minutes
- [ ] 0 exception dans les logs Python
