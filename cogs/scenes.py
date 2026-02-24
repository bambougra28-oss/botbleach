"""
INFERNUM AETERNA -- Cog Scenes
Gestion des scenes RP : creation, suivi, cloture, archivage automatique.

Commandes :
  /scene-creer      -- cree un fil (forum post) dans la zone choisie
  /scene-rejoindre  -- rejoint une scene existante
  /scene-clore      -- cloture et archive une scene
  /scenes-actives   -- liste les scenes en cours

Bouton persistant :
  BoutonScene (custom_id="lancer_scene") -- ouvre un modal de creation

Task loop :
  boucle_archivage_scenes -- archive les scenes inactives depuis 14+ jours

Listener :
  on_message -- incremente nb_posts et ajoute les participants automatiquement
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from config import COULEURS
from cogs.construction import trouver_channel, charger_channels
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

SCENES_FILE = "data/scenes.json"

# ── Zones RP disponibles pour la creation de scenes ──────────────────────────
ZONES_RP = [
    ("le-seireitei", "Le Seireitei"),
    ("grandes-divisions", "Grandes Divisions"),
    ("desert-de-las-noches", "Desert de Las Noches"),
    ("pratus-premier-niveau", "Pratus -- 1ere Strate"),
    ("carnale-deuxieme-niveau", "Carnale -- 2eme Strate"),
    ("sulfura-troisieme-niveau", "Sulfura -- 3eme Strate"),
    ("profundus-quatrieme-niveau", "Profundus -- 4eme Strate"),
    ("les-chaines-philosophie", "Les Chaines -- Philosophie"),
    ("le-refuge", "Le Refuge Quincy"),
    ("ville-principale", "Ville Principale"),
    ("zones-isolees", "Zones Isolees"),
    ("no-mans-land", "No Man's Land"),
    ("la-fissure-principale", "La Fissure Principale"),
]

# Choices pour les commandes slash
ZONE_CHOICES = [
    app_commands.Choice(name=label, value=cle) for cle, label in ZONES_RP
]

TYPE_SCENE_CHOICES = [
    app_commands.Choice(name="Ouverte", value="ouverte"),
    app_commands.Choice(name="Fermee", value="fermee"),
    app_commands.Choice(name="Combat", value="combat"),
    app_commands.Choice(name="Solo", value="solo"),
]

# Emojis associes aux types de scene
TYPE_EMOJIS = {
    "ouverte": "🟢",
    "fermee": "🔴",
    "combat": "⚔️",
    "solo": "🔵",
}

# Labels lisibles pour les types
TYPE_LABELS = {
    "ouverte": "Ouverte",
    "fermee": "Fermee",
    "combat": "Combat",
    "solo": "Solo",
}


def _trouver_forum(guild: discord.Guild, cle_zone: str) -> Optional[discord.ForumChannel]:
    """Cherche un forum channel correspondant a la zone.

    Tente d'abord par ID via channels_ids.json (get_channel retourne tout type),
    puis fallback substring sur les forums de la guild.
    """
    # Tentative par ID (channels_ids.json)
    channels_ids = charger_channels()
    ch_id = channels_ids.get(cle_zone)
    if ch_id:
        ch = guild.get_channel(ch_id)
        if ch and isinstance(ch, discord.ForumChannel):
            return ch

    # Fallback substring sur les forums
    for forum in guild.forums:
        if cle_zone in forum.name.lower():
            return forum

    # Fallback substring sur les channels texte (au cas ou)
    # Certains serveurs utilisent des text channels pour le RP
    return None


def _trouver_channel_texte_ou_forum(guild: discord.Guild, cle_zone: str):
    """Cherche un forum OU un text channel correspondant a la zone.

    Priorite au forum, fallback sur text channel pour creer un thread.
    """
    forum = _trouver_forum(guild, cle_zone)
    if forum:
        return forum

    # Fallback : text channel (on creera un thread dedans)
    channels_ids = charger_channels()
    ch_id = channels_ids.get(cle_zone)
    if ch_id:
        ch = guild.get_channel(ch_id)
        if ch and isinstance(ch, discord.TextChannel):
            return ch

    # Fallback substring sur text channels
    for ch in guild.text_channels:
        if cle_zone in ch.name.lower():
            return ch

    return None


def _zone_label(cle: str) -> str:
    """Retourne le label lisible d'une zone a partir de sa cle."""
    for c, label in ZONES_RP:
        if c == cle:
            return label
    return cle.replace("-", " ").title()


def _tags_forum(forum: discord.ForumChannel, type_scene: str) -> list:
    """Cherche les tags existants du forum qui correspondent au type de scene."""
    tags_trouves = []
    for tag in forum.available_tags:
        nom_lower = tag.name.lower()
        if type_scene in nom_lower or nom_lower in type_scene:
            tags_trouves.append(tag)
    return tags_trouves


class Scenes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(SCENES_FILE, default={"scenes": {}})
        self.data = self._store.data
        # S'assurer que la cle "scenes" existe
        if "scenes" not in self.data:
            self.data["scenes"] = {}
        self.boucle_archivage_scenes.start()

    def cog_unload(self):
        self.boucle_archivage_scenes.cancel()

    async def _sauvegarder(self):
        """Sauvegarde les donnees sur disque via JsonStore."""
        self._store.data = self.data
        await self._store.save()

    # ══════════════════════════════════════════════════════════════════════════
    #  LOGIQUE CENTRALE — creation de scene
    # ══════════════════════════════════════════════════════════════════════════

    async def _creer_scene(
        self,
        guild: discord.Guild,
        createur: discord.Member,
        titre: str,
        zone: str,
        type_scene: str,
        contexte: str = ""
    ) -> Optional[discord.Thread]:
        """Cree une scene RP dans la zone choisie.

        Retourne le thread cree ou None en cas d'echec.
        Utilise par /scene-creer et le modal BoutonScene.
        """
        channel = _trouver_channel_texte_ou_forum(guild, zone)
        if not channel:
            return None

        # Construire l'embed d'ouverture de scene
        type_emoji = TYPE_EMOJIS.get(type_scene, "🎭")
        type_label = TYPE_LABELS.get(type_scene, type_scene.title())
        zone_label = _zone_label(zone)

        embed = discord.Embed(
            title=f"🎭 {titre}",
            description=(
                (f"*{contexte}*\n\n" if contexte else "")
                + f"「 Une nouvelle scene s'ouvre dans les Chroniques. 」"
            ),
            color=COULEURS["or_ancien"]
        )
        embed.add_field(name="Zone", value=zone_label, inline=True)
        embed.add_field(name="Type", value=f"{type_emoji} {type_label}", inline=True)
        embed.add_field(name="Createur", value=createur.mention, inline=True)
        embed.add_field(
            name="Participants",
            value=createur.display_name,
            inline=False
        )
        embed.add_field(
            name="Instructions",
            value=(
                "Utilisez `/scene-rejoindre` pour rejoindre cette scene.\n"
                "Utilisez `/scene-clore` pour la terminer."
            ),
            inline=False
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Scenes RP ⸻")

        thread = None
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            if isinstance(channel, discord.ForumChannel):
                # Creation d'un post dans le forum
                tags = _tags_forum(channel, type_scene)
                result = await channel.create_thread(
                    name=f"🎭 {titre}",
                    content=None,
                    embed=embed,
                    applied_tags=tags[:5] if tags else [],
                    reason=f"Scene RP creee par {createur}"
                )
                # create_thread sur ForumChannel retourne un tuple (thread, message)
                if isinstance(result, tuple):
                    thread = result[0]
                    msg = result[1]
                else:
                    thread = result
                    # Poster l'embed manuellement si le contenu n'a pas ete envoye
                    msg = await thread.send(embed=embed)
                try:
                    await msg.pin()
                except Exception:
                    pass

            elif isinstance(channel, discord.TextChannel):
                # Creation d'un thread dans un text channel
                thread = await channel.create_thread(
                    name=f"🎭 {titre}",
                    type=discord.ChannelType.public_thread,
                    reason=f"Scene RP creee par {createur}"
                )
                msg = await thread.send(embed=embed)
                try:
                    await msg.pin()
                except Exception:
                    pass

        except discord.Forbidden:
            log.error("Scenes: permissions insuffisantes pour creer un thread dans %s", channel.name)
            return None
        except Exception as e:
            log.error("Scenes: erreur creation thread dans %s : %s", channel.name, e, exc_info=True)
            return None

        if not thread:
            return None

        # Ajouter le createur au thread
        try:
            await thread.add_user(createur)
        except Exception:
            pass

        # Enregistrer la scene dans les donnees
        thread_id = str(thread.id)
        self.data["scenes"][thread_id] = {
            "titre": titre,
            "createur_id": createur.id,
            "createur_nom": createur.display_name,
            "participants": [createur.id],
            "zone": zone,
            "type_scene": type_scene,
            "statut": "en_cours",
            "date_creation": now_iso,
            "date_fin": None,
            "nb_posts": 0,
            "tags": [type_scene],
            "contexte": contexte or "",
            "channel_id": channel.id,
        }
        await self._sauvegarder()

        return thread

    # ══════════════════════════════════════════════════════════════════════════
    #  /scene-creer
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="scene-creer",
        description="Cree une scene RP dans la zone choisie."
    )
    @app_commands.describe(
        titre="Titre de la scene",
        zone="Zone ou se deroule la scene",
        type_scene="Type de scene (Ouverte, Fermee, Combat, Solo)",
        contexte="Contexte narratif de la scene (optionnel)"
    )
    @app_commands.choices(zone=ZONE_CHOICES, type_scene=TYPE_SCENE_CHOICES)
    async def scene_creer(
        self,
        interaction: discord.Interaction,
        titre: str,
        zone: str,
        type_scene: str,
        contexte: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        thread = await self._creer_scene(
            guild=guild,
            createur=interaction.user,
            titre=titre,
            zone=zone,
            type_scene=type_scene,
            contexte=contexte or ""
        )

        if not thread:
            await interaction.followup.send(
                f"❌ Impossible de creer la scene. Le channel de zone **{_zone_label(zone)}** "
                f"est introuvable. Verifiez que le serveur a ete configure avec `/setup`.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✅ Scene **{titre}** creee : {thread.mention}\n"
            f"「 Les Chroniques enregistrent un nouveau recit. 」",
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /scene-rejoindre
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="scene-rejoindre",
        description="Rejoindre une scene RP existante."
    )
    @app_commands.describe(
        scene="ID du thread ou titre de la scene (recherche partielle)"
    )
    async def scene_rejoindre(self, interaction: discord.Interaction, scene: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user

        # Recherche de la scene par ID ou par titre
        scene_id = None
        scene_data = None

        # Tentative par ID exact
        if scene.isdigit():
            if scene in self.data["scenes"]:
                scene_id = scene
                scene_data = self.data["scenes"][scene]

        # Fallback : recherche par titre (partiel, insensible a la casse)
        if not scene_data:
            recherche = scene.lower()
            for tid, sdata in self.data["scenes"].items():
                if sdata.get("statut") != "en_cours":
                    continue
                if recherche in sdata.get("titre", "").lower():
                    scene_id = tid
                    scene_data = sdata
                    break

        if not scene_data or not scene_id:
            await interaction.followup.send(
                f"❌ Scene introuvable : **{scene}**.\n"
                f"Utilisez l'ID du thread ou un mot du titre.",
                ephemeral=True
            )
            return

        if scene_data.get("statut") != "en_cours":
            await interaction.followup.send(
                "❌ Cette scene est terminee.",
                ephemeral=True
            )
            return

        # Verifier si le joueur est deja participant
        if member.id in scene_data.get("participants", []):
            await interaction.followup.send(
                "Vous participez deja a cette scene.",
                ephemeral=True
            )
            return

        # Verifier si la scene est fermee ou solo
        if scene_data.get("type_scene") == "solo":
            await interaction.followup.send(
                "❌ Cette scene est en mode **Solo**, elle n'accepte pas de participants supplementaires.",
                ephemeral=True
            )
            return

        # Ajouter le participant
        scene_data.setdefault("participants", []).append(member.id)
        await self._sauvegarder()

        # Trouver le thread et poster un embed d'annonce
        thread = guild.get_thread(int(scene_id))
        if not thread:
            # Tenter de fetch le thread
            try:
                thread = await guild.fetch_channel(int(scene_id))
            except Exception:
                thread = None

        if thread:
            try:
                await thread.add_user(member)
            except Exception:
                pass

            embed = discord.Embed(
                description=(
                    f"**{member.display_name}** rejoint la scene.\n\n"
                    f"「 Une nouvelle ame entre dans le recit. 」"
                ),
                color=COULEURS["or_pale"]
            )
            nb_participants = len(scene_data.get("participants", []))
            embed.add_field(
                name="Participants",
                value=f"{nb_participants} ame(s) presentes",
                inline=True
            )
            embed.set_footer(text="⸻ Infernum Aeterna · Scenes RP ⸻")
            await thread.send(embed=embed)

        await interaction.followup.send(
            f"✅ Vous avez rejoint la scene **{scene_data['titre']}**."
            + (f" : {thread.mention}" if thread else ""),
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /scene-clore
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="scene-clore",
        description="Cloture une scene RP (createur ou staff)."
    )
    @app_commands.describe(
        conclusion="Message de cloture narrative (optionnel)"
    )
    async def scene_clore(
        self,
        interaction: discord.Interaction,
        conclusion: Optional[str] = None
    ):
        # La commande doit etre utilisee dans le thread de la scene
        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "❌ Cette commande doit etre utilisee dans le fil d'une scene RP.",
                ephemeral=True
            )
            return

        scene_id = str(thread.id)
        scene_data = self.data["scenes"].get(scene_id)

        if not scene_data:
            await interaction.response.send_message(
                "❌ Ce fil n'est pas une scene RP enregistree.",
                ephemeral=True
            )
            return

        if scene_data.get("statut") != "en_cours":
            await interaction.response.send_message(
                "❌ Cette scene est deja terminee.",
                ephemeral=True
            )
            return

        # Verifier les droits : createur ou staff (manage_messages)
        is_creator = interaction.user.id == scene_data.get("createur_id")
        is_staff = interaction.user.guild_permissions.manage_messages
        if not is_creator and not is_staff:
            await interaction.response.send_message(
                "❌ Seul le createur de la scene ou un membre du staff peut la clore.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        # Mettre a jour les donnees
        now_iso = datetime.now(timezone.utc).isoformat()
        scene_data["statut"] = "terminee"
        scene_data["date_fin"] = now_iso
        await self._sauvegarder()

        # Embed de cloture
        nb_participants = len(scene_data.get("participants", []))
        embed = discord.Embed(
            title=f"🏁 Scene Terminee · {scene_data['titre']}",
            description=(
                (f"*{conclusion}*\n\n" if conclusion else "")
                + "「 Ce recit se referme. Ce qui fut ecrit demeure dans les Chroniques. 」"
            ),
            color=COULEURS["gris_acier"]
        )
        embed.add_field(name="Posts", value=str(scene_data.get("nb_posts", 0)), inline=True)
        embed.add_field(name="Participants", value=str(nb_participants), inline=True)
        embed.add_field(
            name="Duree",
            value=_duree_lisible(scene_data.get("date_creation", now_iso), now_iso),
            inline=True
        )
        embed.set_footer(
            text=f"Close par {interaction.user.display_name} · "
                 f"⸻ Infernum Aeterna · Scenes RP ⸻"
        )
        await thread.send(embed=embed)

        # Tenter une narration via le cog Narrateur (optionnel)
        if scene_data.get("nb_posts", 0) >= 5:
            cog_narrateur = self.bot.cogs.get("Narrateur")
            if cog_narrateur:
                try:
                    participants_noms = []
                    for pid in scene_data.get("participants", []):
                        member = interaction.guild.get_member(pid)
                        if member:
                            participants_noms.append(member.display_name)
                    resume = (
                        f"Scene RP : {scene_data['titre']}\n"
                        f"Zone : {_zone_label(scene_data.get('zone', ''))}\n"
                        f"Type : {TYPE_LABELS.get(scene_data.get('type_scene', ''), 'Libre')}\n"
                        f"Participants : {', '.join(participants_noms) if participants_noms else 'inconnus'}\n"
                        f"Nombre de posts : {scene_data.get('nb_posts', 0)}\n"
                        f"Contexte : {scene_data.get('contexte', '')}\n"
                        f"Conclusion : {conclusion or 'Aucune'}"
                    )
                    # Proposer la narration via un bouton
                    view = ViewDemandeNarrationScene(resume)
                    await thread.send(
                        "Voulez-vous que le Narrateur consigne cette scene dans les Chroniques ?",
                        view=view
                    )
                except Exception as e:
                    log.warning("Scenes: erreur proposition narration : %s", e)

        # Archiver le thread apres un court delai
        await asyncio.sleep(2)
        try:
            await thread.edit(archived=True, locked=True)
        except Exception as e:
            log.warning("Scenes: impossible d'archiver le thread %s : %s", scene_id, e)

    # ══════════════════════════════════════════════════════════════════════════
    #  /scenes-actives
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="scenes-actives",
        description="Liste les scenes RP en cours."
    )
    @app_commands.describe(
        zone="Filtrer par zone (optionnel)",
    )
    @app_commands.choices(zone=ZONE_CHOICES)
    async def scenes_actives(
        self,
        interaction: discord.Interaction,
        zone: Optional[str] = None,
    ):
        # Collecter les scenes actives
        actives = []
        for tid, sdata in self.data["scenes"].items():
            if sdata.get("statut") != "en_cours":
                continue
            if zone and sdata.get("zone") != zone:
                continue
            actives.append((tid, sdata))

        if not actives:
            filtre_msg = f" dans la zone **{_zone_label(zone)}**" if zone else ""
            await interaction.response.send_message(
                f"Aucune scene active{filtre_msg}.",
                ephemeral=True
            )
            return

        # Trier par date de creation (plus recentes d'abord)
        actives.sort(key=lambda x: x[1].get("date_creation", ""), reverse=True)

        # Pagination (max 10 par page)
        page_size = 10
        total = len(actives)
        pages = (total + page_size - 1) // page_size

        embeds = []
        for page_num in range(pages):
            start = page_num * page_size
            end = min(start + page_size, total)
            page_scenes = actives[start:end]

            embed = discord.Embed(
                title=f"🎭 Scenes Actives ({total})"
                      + (f" · {_zone_label(zone)}" if zone else ""),
                color=COULEURS["or_ancien"]
            )

            for tid, sdata in page_scenes:
                type_emoji = TYPE_EMOJIS.get(sdata.get("type_scene", ""), "🎭")
                type_label = TYPE_LABELS.get(sdata.get("type_scene", ""), "Libre")
                nb_p = len(sdata.get("participants", []))
                date_str = sdata.get("date_creation", "")[:10]

                embed.add_field(
                    name=f"{type_emoji} {sdata.get('titre', 'Sans titre')}",
                    value=(
                        f"<#{tid}>\n"
                        f"Zone : {_zone_label(sdata.get('zone', ''))}\n"
                        f"Participants : {nb_p} · Posts : {sdata.get('nb_posts', 0)}\n"
                        f"Creee le {date_str} par {sdata.get('createur_nom', '?')}"
                    ),
                    inline=False
                )

            if pages > 1:
                embed.set_footer(
                    text=f"Page {page_num + 1}/{pages} · "
                         f"⸻ Infernum Aeterna · Scenes RP ⸻"
                )
            else:
                embed.set_footer(text="⸻ Infernum Aeterna · Scenes RP ⸻")
            embeds.append(embed)

        # Envoyer la premiere page (ou toutes si une seule)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            # Envoyer avec pagination via boutons
            view = ViewPagination(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  LISTENER — suivi des messages dans les threads de scenes
    # ══════════════════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorer les bots
        if message.author.bot:
            return

        # Verifier si le message est dans un thread suivi
        channel = message.channel
        if not isinstance(channel, discord.Thread):
            return

        thread_id = str(channel.id)
        scene_data = self.data["scenes"].get(thread_id)
        if not scene_data:
            return

        if scene_data.get("statut") != "en_cours":
            return

        # Incrementer le compteur de posts
        scene_data["nb_posts"] = scene_data.get("nb_posts", 0) + 1

        # Ajouter l'auteur aux participants s'il n'y est pas
        author_id = message.author.id
        participants = scene_data.setdefault("participants", [])
        if author_id not in participants:
            participants.append(author_id)

        # Sauvegarder (on ne sauvegarde pas a chaque message pour eviter le spam I/O,
        # on sauvegarde tous les 5 posts pour equilibrer performance et persistence)
        if scene_data["nb_posts"] % 5 == 0:
            await self._sauvegarder()

    # ══════════════════════════════════════════════════════════════════════════
    #  TASK LOOP — archivage automatique des scenes inactives
    # ══════════════════════════════════════════════════════════════════════════

    @tasks.loop(hours=6)
    async def boucle_archivage_scenes(self):
        """Archive les scenes sans activite depuis 14+ jours."""
        maintenant = datetime.now(timezone.utc)
        modifie = False

        for thread_id, scene_data in list(self.data["scenes"].items()):
            if scene_data.get("statut") != "en_cours":
                continue

            # Determiner la date de derniere activite
            date_creation = scene_data.get("date_creation", "")
            try:
                derniere_activite = datetime.fromisoformat(
                    date_creation.replace("Z", "+00:00")
                )
                if derniere_activite.tzinfo is None:
                    derniere_activite = derniere_activite.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            # Tenter de verifier le dernier message du thread
            thread = self.bot.get_channel(int(thread_id))
            if thread and isinstance(thread, discord.Thread):
                # Utiliser last_message_id pour estimer l'activite
                if thread.last_message_id:
                    try:
                        last_msg = await thread.fetch_message(thread.last_message_id)
                        derniere_activite = last_msg.created_at
                    except Exception:
                        pass

            # Verifier si inactif depuis 14 jours
            if (maintenant - derniere_activite) < timedelta(days=14):
                continue

            # Archiver la scene
            log.info("Scenes: archivage auto de '%s' (thread %s) — inactif depuis 14+ jours",
                     scene_data.get("titre", "?"), thread_id)

            scene_data["statut"] = "terminee"
            scene_data["date_fin"] = maintenant.isoformat()
            modifie = True

            # Poster un embed de cloture dans le thread
            if thread and isinstance(thread, discord.Thread):
                embed = discord.Embed(
                    description=(
                        "「 Le silence s'est installe depuis trop longtemps. "
                        "Cette scene est desormais archivee. 」"
                    ),
                    color=0x1A1A1A
                )
                embed.set_footer(
                    text="⸻ Archivage automatique (14 jours d'inactivite) · "
                         "Infernum Aeterna ⸻"
                )
                try:
                    await thread.send(embed=embed)
                    await asyncio.sleep(0.3)
                    await thread.edit(archived=True, locked=True)
                except Exception as e:
                    log.warning("Scenes: erreur archivage thread %s : %s", thread_id, e)

        if modifie:
            await self._sauvegarder()

    @boucle_archivage_scenes.before_loop
    async def before_archivage_scenes(self):
        await self.bot.wait_until_ready()


# ══════════════════════════════════════════════════════════════════════════════
#  VUES & MODALS
# ══════════════════════════════════════════════════════════════════════════════

class BoutonScene(discord.ui.View):
    """Bouton persistant 'Lancer une Scene' — ouvre un modal de creation."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎭 Lancer une Scene",
        style=discord.ButtonStyle.primary,
        custom_id="lancer_scene"
    )
    async def lancer_scene(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModalScene())


class ModalScene(discord.ui.Modal, title="Creer une Scene RP"):
    """Modal de creation de scene, declenche par le bouton persistant."""

    titre = discord.ui.TextInput(
        label="Titre de la scene",
        placeholder="Ex: L'ombre dans le Seireitei",
        required=True,
        max_length=100
    )
    type_scene_input = discord.ui.TextInput(
        label="Type (Ouverte / Fermee / Combat / Solo)",
        placeholder="Ouverte",
        required=True,
        max_length=20,
        default="Ouverte"
    )
    zone_input = discord.ui.TextInput(
        label="Zone (ex: le-seireitei, no-mans-land)",
        placeholder="le-seireitei",
        required=True,
        max_length=50
    )
    contexte_input = discord.ui.TextInput(
        label="Contexte narratif (optionnel)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        cog_scenes = interaction.client.cogs.get("Scenes")
        if not cog_scenes:
            await interaction.followup.send(
                "❌ Module de scenes indisponible.", ephemeral=True
            )
            return

        # Normaliser le type de scene
        type_raw = self.type_scene_input.value.strip().lower()
        type_map = {
            "ouverte": "ouverte",
            "fermee": "fermee",
            "fermée": "fermee",
            "combat": "combat",
            "solo": "solo",
        }
        type_scene = type_map.get(type_raw, "ouverte")

        # Normaliser la zone
        zone_raw = self.zone_input.value.strip().lower().replace(" ", "-")
        # Verifier que la zone existe dans ZONES_RP
        zones_valides = {cle for cle, _ in ZONES_RP}
        if zone_raw not in zones_valides:
            # Recherche partielle
            zone_trouvee = None
            for cle, _ in ZONES_RP:
                if zone_raw in cle or cle in zone_raw:
                    zone_trouvee = cle
                    break
            if zone_trouvee:
                zone_raw = zone_trouvee
            else:
                zones_list = "\n".join(f"  `{cle}` · {label}" for cle, label in ZONES_RP)
                await interaction.followup.send(
                    f"❌ Zone **{self.zone_input.value}** introuvable.\n\n"
                    f"Zones disponibles :\n{zones_list}",
                    ephemeral=True
                )
                return

        thread = await cog_scenes._creer_scene(
            guild=guild,
            createur=interaction.user,
            titre=self.titre.value.strip(),
            zone=zone_raw,
            type_scene=type_scene,
            contexte=self.contexte_input.value.strip() if self.contexte_input.value else ""
        )

        if not thread:
            await interaction.followup.send(
                f"❌ Impossible de creer la scene. Le channel de zone est introuvable.\n"
                f"Verifiez avec un membre du staff.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✅ Scene **{self.titre.value}** creee : {thread.mention}\n"
            f"「 Les Chroniques enregistrent un nouveau recit. 」",
            ephemeral=True
        )


class ViewPagination(discord.ui.View):
    """Vue avec boutons de pagination pour les embeds."""

    def __init__(self, embeds: list):
        super().__init__(timeout=120)
        self.embeds = embeds
        self.page = 0
        self._update_buttons()

    def _update_buttons(self):
        self.btn_prev.disabled = (self.page <= 0)
        self.btn_next.disabled = (self.page >= len(self.embeds) - 1)

    @discord.ui.button(label="◀ Precedent", style=discord.ButtonStyle.secondary, custom_id="page_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Suivant ▶", style=discord.ButtonStyle.secondary, custom_id="page_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(len(self.embeds) - 1, self.page + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class ViewDemandeNarrationScene(discord.ui.View):
    """Boutons pour demander (ou refuser) une narration de cloture de scene."""

    def __init__(self, resume: str):
        super().__init__(timeout=300)
        self.resume = resume

    @discord.ui.button(label="✍️ Narrer cette scene", style=discord.ButtonStyle.primary)
    async def narrer(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog_narrateur = interaction.client.cogs.get("Narrateur")
        if not cog_narrateur:
            await interaction.response.send_message(
                "❌ Narrateur indisponible.", ephemeral=True
            )
            return

        await interaction.response.defer()
        button.disabled = True
        self.children[1].disabled = True  # Desactiver aussi le bouton annuler
        await interaction.message.edit(view=self)

        try:
            texte = await cog_narrateur.generer_narration("libre", self.resume, "normale")
            embed = cog_narrateur._construire_embed("libre", texte)

            guild = interaction.guild
            dest = cog_narrateur._trouver_channel_narrateur(guild)
            if dest:
                await dest.send(embed=embed)
                await interaction.followup.send(
                    f"✅ Narration publiee dans {dest.mention}.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(embed=embed)
        except Exception as e:
            log.error("Scenes: erreur narration : %s", e, exc_info=True)
            await interaction.followup.send(
                "❌ Erreur lors de la generation de la narration.",
                ephemeral=True
            )

    @discord.ui.button(label="❌ Non merci", style=discord.ButtonStyle.secondary)
    async def annuler(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Narration ignoree.", view=None)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _duree_lisible(date_debut_iso: str, date_fin_iso: str) -> str:
    """Calcule la duree entre deux dates ISO et retourne un texte lisible."""
    try:
        debut = datetime.fromisoformat(date_debut_iso.replace("Z", "+00:00"))
        fin = datetime.fromisoformat(date_fin_iso.replace("Z", "+00:00"))
        if debut.tzinfo is None:
            debut = debut.replace(tzinfo=timezone.utc)
        if fin.tzinfo is None:
            fin = fin.replace(tzinfo=timezone.utc)
        delta = fin - debut
        jours = delta.days
        heures = delta.seconds // 3600
        if jours > 0:
            return f"{jours}j {heures}h"
        elif heures > 0:
            minutes = (delta.seconds % 3600) // 60
            return f"{heures}h {minutes}min"
        else:
            minutes = delta.seconds // 60
            return f"{minutes}min"
    except Exception:
        return "Inconnue"


async def setup(bot):
    await bot.add_cog(Scenes(bot))
