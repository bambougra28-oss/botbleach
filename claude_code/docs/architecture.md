# Architecture & Patterns — Infernum Aeterna

## Flux d'une interaction typique

```
Utilisateur tape /commande
        ↓
discord.py route vers le cog correspondant
        ↓
Cog vérifie permissions + état (JSON)
        ↓
Cog effectue action (modifier JSON, poster embed, créer thread…)
        ↓
Si narrateur nécessaire → bot.cogs.get("Narrateur").generer_narration(...)
        ↓
Résultat posté dans le channel approprié
```

## Pattern "trouver un channel par nom partiel"

Utilisé dans de nombreux cogs pour localiser les channels sans stocker leurs IDs.

```python
def _trouver_channel(guild: discord.Guild, partial: str) -> discord.TextChannel | None:
    for ch in guild.text_channels:
        if partial in ch.name:
            return ch
    return None
```

## Pattern "charger les rôles depuis JSON"

`charger_roles()` est la seule fonction partagée entre cogs via import direct.

```python
# Dans n'importe quel cog
from cogs.construction import charger_roles

roles_ids = charger_roles()  # → {"shinigami": 123456789, "capitaine": 987654321, ...}
guild = interaction.guild
role = guild.get_role(roles_ids.get("shinigami"))
```

## Pattern "notifier le staff"

```python
from cogs.construction import charger_roles

async def _notifier_staff(guild, embed):
    for ch in guild.text_channels:
        if "validations" in ch.name or "discussions-staff" in ch.name:
            await ch.send(embed=embed)
            break
```

## Pattern "DM + fallback éphémère"

```python
try:
    await member.send(embed=embed)
except discord.Forbidden:
    pass  # DM désactivés, silencieux
```

## Pattern "tâche async non bloquante"

Pour les narrations IA (longues ~2s) qui ne doivent pas bloquer la réponse :

```python
async def _publier_narration():
    try:
        texte = await cog_narrateur.generer_narration("evenement", contenu, "longue")
        embed = cog_narrateur._construire_embed("evenement", texte)
        dest  = cog_narrateur._trouver_channel_narrateur(guild)
        if dest:
            await dest.send(embed=embed)
    except Exception as e:
        print(f"[Narration] Erreur : {e}")

asyncio.create_task(_publier_narration())
# ← L'interaction retourne immédiatement, la narration arrive quelques secondes après
```

## Limites Discord à respecter

| Limite | Valeur | Contournement |
|---|---|---|
| Embed description | 4096 chars | Découper en plusieurs embeds |
| Embed field value | 1024 chars | Découper en plusieurs fields |
| Embed fields | 25 max | Plusieurs embeds |
| Rate limit messages | ~5/sec | `await asyncio.sleep(0.4)` entre posts |
| Nombre de pins par channel | 50 | Pas plus de 50 épingles par channel |
| Longueur modal TextInput | 4000 chars | Limiter max_length |
| Commandes slash par serveur | 100 | Actuellement 35, marge suffisante |

## Structure d'un personnage (personnages.json)

```json
{
  "discord_id_string": {
    "nom_perso":       "Nom du personnage",
    "faction":         "shinigami",
    "rang":            "capitaine",
    "rang_label":      "👑 Capitaine",
    "points":          10000,
    "valide":          true,
    "fiche_contenu":   "Texte de la fiche soumise",
    "date_validation": "2026-02-22T10:00:00+00:00",
    "combats_total":   0,
    "combats_gagnes":  0,
    "notes_staff":     "",
    "historique_rangs": [
      {
        "rang":   "academie",
        "label":  "🎓 Académie",
        "date":   "2026-02-22T10:00:00+00:00",
        "raison": "Validation initiale"
      }
    ]
  }
}
```

## Structure d'un combat (combats_actifs.json)

```json
{
  "thread_id_string": {
    "titre":          "Le Duel des Abysses",
    "initiateur_id":  123456789,
    "initiateur_nom": "Joueur A",
    "adversaire_id":  987654321,
    "adversaire_nom": "Joueur B",
    "contexte":       "Contexte narratif",
    "tour":           3,
    "statut":         "actif",
    "channel_id":     111111111,
    "thread_id":      222222222,
    "debut":          "2026-02-22T10:00:00+00:00",
    "evenements": [
      {
        "tour":      1,
        "joueur":    "Joueur A",
        "action":    "Description de l'action",
        "timestamp": "2026-02-22T10:01:00+00:00"
      }
    ],
    "vainqueur":   "Joueur A",
    "conclusion":  "Texte de clôture",
    "fin":         "2026-02-22T11:00:00+00:00"
  }
}
```

## Statuts possibles d'un combat

| Statut | Description |
|---|---|
| `actif` | Combat en cours |
| `termine` | Clôturé manuellement via /clore-combat |
| `archive_auto` | Archivé automatiquement après 7j d'inactivité |

## Couleurs par faction (pour les embeds)

```python
COULEUR_PAR_FACTION = {
    "shinigami": COULEURS["blanc_seireitei"],
    "togabito":  COULEURS["pourpre_infernal"],
    "arrancar":  COULEURS["gris_sable"],
    "quincy":    COULEURS["bleu_abyssal"],
}
```
