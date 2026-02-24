"""
INFERNUM AETERNA — Cog Journal
Système de journal personnel pour les personnages validés.

- /journal          — affiche ou crée le journal du personnage
- /journal-ecrire   — ajoute une entrée manuscrite au journal
- /journal-lire     — affiche le lien vers le journal d'un membre
- /journal-stats    — statistiques du journal

Méthode publique :
- poster_evenement() — appelée par d'autres cogs pour consigner automatiquement
  les événements clés (validation, rang, combat, mission, mort, custom)
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timezone
import logging

from config import COULEURS
from cogs.construction import trouver_channel, charger_channels
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

JOURNAUX_FILE = "data/journaux.json"

# ─── Correspondances faction ────────────────────────────────────────────────

KANJI_FACTION = {
    "shinigami": "死神",
    "togabito": "咎人",
    "arrancar": "破面",
    "quincy": "滅却師",
}

COULEUR_FACTION = {
    "shinigami": "blanc_seireitei",
    "togabito": "pourpre_infernal",
    "arrancar": "gris_sable",
    "quincy": "bleu_abyssal",
}

# ─── Icônes et titres par type d'événement ──────────────────────────────────

TYPES_EVENEMENT = {
    "validation": {"icone": "✦", "titre": "Entrée dans les Chroniques"},
    "rang":       {"icone": "⬆️", "titre": "Ascension"},
    "combat":     {"icone": "⚔️", "titre": "Combat"},
    "mission":    {"icone": "📋", "titre": "Mission"},
    "mort":       {"icone": "✝", "titre": "Fin"},
    "custom":     {"icone": "📜", "titre": "Événement"},
}

FORUM_CHANNEL_KEY = "journaux-des-ames"


class Journal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(JOURNAUX_FILE, default={"journaux": {}})
        self.journaux = self._store.data.setdefault("journaux", {})

    async def _sauvegarder(self):
        self._store.data = {"journaux": self.journaux}
        await self._store.save()

    # ════════════════════════════════════════════════════════════════════════
    #  RÉSOLUTION DU CHANNEL FORUM
    # ════════════════════════════════════════════════════════════════════════

    def _trouver_forum(self, guild: discord.Guild) -> Optional[discord.ForumChannel]:
        """Résout le forum 'journaux-des-ames' par ID (channels_ids.json) puis fallback substring."""
        channels_ids = charger_channels()
        ch_id = channels_ids.get(FORUM_CHANNEL_KEY)
        if ch_id:
            ch = guild.get_channel(ch_id)
            if ch and isinstance(ch, discord.ForumChannel):
                return ch
        # Fallback : chercher parmi les forums de la guild
        for forum in guild.forums:
            if FORUM_CHANNEL_KEY in forum.name:
                return forum
        return None

    # ════════════════════════════════════════════════════════════════════════
    #  RÉCUPÉRATION DES DONNÉES PERSONNAGE
    # ════════════════════════════════════════════════════════════════════════

    def _get_perso(self, user_id: int) -> Optional[dict]:
        """Récupère les données d'un personnage validé depuis le cog Personnage."""
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return None
        perso = cog_perso.personnages.get(str(user_id))
        if perso and perso.get("valide") and perso.get("nom_perso"):
            return perso
        return None

    # ════════════════════════════════════════════════════════════════════════
    #  COULEUR PAR FACTION
    # ════════════════════════════════════════════════════════════════════════

    def _couleur_faction(self, faction: Optional[str]) -> int:
        """Renvoie la couleur Discord correspondant à la faction."""
        cle_couleur = COULEUR_FACTION.get(faction, "or_ancien")
        return COULEURS.get(cle_couleur, COULEURS["or_ancien"])

    # ════════════════════════════════════════════════════════════════════════
    #  CRÉATION / RÉCUPÉRATION DE THREAD JOURNAL
    # ════════════════════════════════════════════════════════════════════════

    async def _obtenir_ou_creer_thread(
        self, guild: discord.Guild, user_id: int
    ) -> Optional[discord.Thread]:
        """Récupère le thread journal existant, ou en crée un nouveau.

        Gère le cas où le thread a été supprimé (recrée automatiquement).
        Renvoie None si le forum n'existe pas ou si le personnage n'est pas validé.
        """
        uid = str(user_id)
        perso = self._get_perso(user_id)
        if not perso:
            return None

        nom_perso = perso["nom_perso"]
        faction = perso.get("faction")

        # Vérifier si un thread existe déjà
        if uid in self.journaux:
            thread_id = self.journaux[uid].get("thread_id")
            if thread_id:
                thread = guild.get_channel_or_thread(thread_id)
                if thread and isinstance(thread, discord.Thread):
                    # Mettre à jour le nom du perso au cas où il aurait changé
                    self.journaux[uid]["nom_perso"] = nom_perso
                    self.journaux[uid]["faction"] = faction
                    await self._sauvegarder()
                    return thread
                # Le thread a été supprimé — on le recrée
                log.warning("Journal thread %s introuvable pour %s, recréation.", thread_id, nom_perso)

        # Créer un nouveau thread
        thread = await self._creer_thread_journal(guild, user_id, nom_perso, faction)
        return thread

    async def _creer_thread_journal(
        self, guild: discord.Guild, user_id: int, nom_perso: str, faction: Optional[str]
    ) -> Optional[discord.Thread]:
        """Crée un thread journal dans le forum ou en fallback dans un channel texte."""
        uid = str(user_id)
        kanji = KANJI_FACTION.get(faction, "")
        faction_label = faction.capitalize() if faction else "Inconnu"
        couleur = self._couleur_faction(faction)

        # Embed d'introduction
        intro_embed = discord.Embed(
            title=f"📔 Journal de {nom_perso}",
            description=(
                f"Chroniques personnelles de **{nom_perso}**, "
                f"{kanji} {faction_label}.\n\n"
                f"Ce journal est le fil rouge de votre histoire. Écrivez-y vos réflexions, "
                f"vos doutes, vos victoires. Les moments clés de votre parcours y seront "
                f"également consignés automatiquement.\n\n"
                f"「 Chaque âme porte en elle un récit qui mérite d'être écrit. 」"
            ),
            color=couleur,
        )
        intro_embed.set_footer(text="⸻ Infernum Aeterna · Journal ⸻")

        thread = None

        # Tentative 1 : forum channel
        forum = self._trouver_forum(guild)
        if forum and isinstance(forum, discord.ForumChannel):
            try:
                result = await forum.create_thread(
                    name=f"📔 {nom_perso} · Journal",
                    embed=intro_embed,
                    reason=f"Journal personnel de {nom_perso}",
                )
                # create_thread sur un ForumChannel renvoie un tuple (thread, message)
                thread = result.thread if hasattr(result, "thread") else result
                # Épingler le message d'introduction
                if hasattr(result, "message") and result.message:
                    try:
                        await result.message.pin()
                    except discord.HTTPException:
                        pass
                log.info("Journal forum créé pour %s (thread %s).", nom_perso, thread.id)
            except discord.HTTPException as e:
                log.error("Impossible de créer le thread forum pour %s : %s", nom_perso, e)
                thread = None

        # Tentative 2 : fallback — thread dans un channel texte
        if thread is None:
            ch_fallback = trouver_channel(guild, FORUM_CHANNEL_KEY)
            if ch_fallback and isinstance(ch_fallback, discord.TextChannel):
                try:
                    thread = await ch_fallback.create_thread(
                        name=f"📔 {nom_perso} · Journal",
                        type=discord.ChannelType.public_thread,
                        reason=f"Journal personnel de {nom_perso}",
                    )
                    msg = await thread.send(embed=intro_embed)
                    try:
                        await msg.pin()
                    except discord.HTTPException:
                        pass
                    log.info("Journal thread (fallback) créé pour %s (thread %s).", nom_perso, thread.id)
                except discord.HTTPException as e:
                    log.error("Impossible de créer le thread fallback pour %s : %s", nom_perso, e)
                    thread = None

        if thread is None:
            log.warning(
                "Aucun channel '%s' trouvé (forum ou texte) dans la guild %s. "
                "Journal pour %s non créé.",
                FORUM_CHANNEL_KEY, guild.name, nom_perso,
            )
            return None

        # Sauvegarder les métadonnées du journal
        self.journaux[uid] = {
            "thread_id": thread.id,
            "nom_perso": nom_perso,
            "faction": faction,
            "entrees": 0,
            "date_creation": datetime.now(timezone.utc).isoformat(),
        }
        await self._sauvegarder()
        return thread

    # ════════════════════════════════════════════════════════════════════════
    #  MÉTHODE PUBLIQUE — poster_evenement
    # ════════════════════════════════════════════════════════════════════════

    async def poster_evenement(
        self, guild: discord.Guild, user_id: int, type_evt: str, contenu: str
    ):
        """Poste une entrée automatique dans le journal d'un personnage.

        Types supportés : validation, rang, combat, mission, mort, custom.
        Appelée par : personnage.py (validation, rang), combat.py (clôture),
                      missions.py (mission validée), et tout cog souhaitant
                      consigner un événement.
        """
        perso = self._get_perso(user_id)
        if not perso:
            log.debug("poster_evenement ignoré — personnage %s non validé ou introuvable.", user_id)
            return

        thread = await self._obtenir_ou_creer_thread(guild, user_id)
        if not thread:
            return

        faction = perso.get("faction")
        nom_perso = perso["nom_perso"]
        couleur = self._couleur_faction(faction)

        evt_info = TYPES_EVENEMENT.get(type_evt, TYPES_EVENEMENT["custom"])
        icone = evt_info["icone"]
        titre = evt_info["titre"]

        maintenant = datetime.now(timezone.utc)
        date_str = maintenant.strftime("%d/%m/%Y à %H:%M")

        embed = discord.Embed(
            title=f"{icone} {titre}",
            description=contenu,
            color=couleur,
            timestamp=maintenant,
        )
        embed.set_author(name=nom_perso)
        embed.set_footer(text=f"⸻ Infernum Aeterna · Journal · {date_str} ⸻")

        try:
            await thread.send(embed=embed)
        except discord.HTTPException as e:
            log.error("Impossible de poster dans le journal de %s (thread %s) : %s", nom_perso, thread.id, e)
            return

        # Incrémenter le compteur d'entrées
        uid = str(user_id)
        if uid in self.journaux:
            self.journaux[uid]["entrees"] = self.journaux[uid].get("entrees", 0) + 1
            await self._sauvegarder()

    # ════════════════════════════════════════════════════════════════════════
    #  /journal — Afficher ou créer son journal
    # ════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="journal",
        description="Affiche votre journal personnel ou le crée s'il n'existe pas."
    )
    async def journal(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        perso = self._get_perso(user_id)

        if not perso:
            await interaction.followup.send(
                "❌ Vous n'avez pas de personnage validé. "
                "Soumettez votre fiche via `/fiche-soumettre` et attendez la validation du staff.",
                ephemeral=True,
            )
            return

        thread = await self._obtenir_ou_creer_thread(interaction.guild, user_id)
        if not thread:
            await interaction.followup.send(
                "❌ Impossible de trouver ou créer votre journal. "
                f"Le channel forum `{FORUM_CHANNEL_KEY}` est introuvable sur ce serveur.\n"
                "Contactez le staff pour qu'il soit créé.",
                ephemeral=True,
            )
            return

        uid = str(user_id)
        journal_data = self.journaux.get(uid, {})
        nom_perso = perso["nom_perso"]
        faction = perso.get("faction")
        kanji = KANJI_FACTION.get(faction, "")
        couleur = self._couleur_faction(faction)
        entrees = journal_data.get("entrees", 0)
        date_creation = journal_data.get("date_creation", "")

        # Formater la date de création
        date_affichee = "—"
        if date_creation:
            try:
                dt = datetime.fromisoformat(date_creation)
                date_affichee = dt.strftime("%d/%m/%Y")
            except ValueError:
                date_affichee = date_creation[:10]

        embed = discord.Embed(
            title=f"📔 Journal de {nom_perso}",
            description=(
                f"{kanji} **{faction.capitalize() if faction else 'Inconnu'}**\n\n"
                f"Votre journal personnel est actif. Chaque moment clé de votre parcours "
                f"y est consigné, et vous pouvez y ajouter vos propres réflexions "
                f"avec `/journal-ecrire`.\n\n"
                f"📎 **[Accéder au journal]({thread.jump_url})**"
            ),
            color=couleur,
        )
        embed.add_field(name="Entrées", value=f"**{entrees}**", inline=True)
        embed.add_field(name="Créé le", value=date_affichee, inline=True)
        embed.set_footer(text="⸻ Infernum Aeterna · Journal ⸻")

        await interaction.followup.send(embed=embed, ephemeral=True)

    # ════════════════════════════════════════════════════════════════════════
    #  /journal-ecrire — Ajouter une entrée manuscrite
    # ════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="journal-ecrire",
        description="Écrivez une entrée dans votre journal personnel."
    )
    @app_commands.describe(
        titre="Titre de l'entrée (court)",
        contenu="Contenu de votre entrée (monologue, réflexion, récit…)"
    )
    async def journal_ecrire(
        self, interaction: discord.Interaction,
        titre: str,
        contenu: str,
    ):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        perso = self._get_perso(user_id)

        if not perso:
            await interaction.followup.send(
                "❌ Vous n'avez pas de personnage validé.", ephemeral=True
            )
            return

        thread = await self._obtenir_ou_creer_thread(interaction.guild, user_id)
        if not thread:
            await interaction.followup.send(
                "❌ Impossible d'accéder à votre journal. "
                f"Le channel `{FORUM_CHANNEL_KEY}` est introuvable.",
                ephemeral=True,
            )
            return

        nom_perso = perso["nom_perso"]
        faction = perso.get("faction")
        couleur = self._couleur_faction(faction)

        maintenant = datetime.now(timezone.utc)
        date_str = maintenant.strftime("%d/%m/%Y à %H:%M")

        # Construire l'embed de l'entrée
        embed = discord.Embed(
            title=f"🖊️ {titre}",
            description=contenu,
            color=couleur,
            timestamp=maintenant,
        )
        embed.set_author(name=nom_perso)
        embed.set_footer(text=f"⸻ Infernum Aeterna · Journal · {date_str} ⸻")

        try:
            await thread.send(embed=embed)
        except discord.HTTPException as e:
            log.error("Erreur envoi journal-ecrire pour %s : %s", nom_perso, e)
            await interaction.followup.send(
                "❌ Une erreur est survenue lors de l'envoi de votre entrée.",
                ephemeral=True,
            )
            return

        # Incrémenter le compteur
        uid = str(user_id)
        if uid in self.journaux:
            self.journaux[uid]["entrees"] = self.journaux[uid].get("entrees", 0) + 1
            await self._sauvegarder()

        await interaction.followup.send(
            f"✅ Entrée « **{titre}** » ajoutée à votre journal.\n"
            f"📎 [Voir le journal]({thread.jump_url})",
            ephemeral=True,
        )

    # ════════════════════════════════════════════════════════════════════════
    #  /journal-lire — Consulter le journal d'un membre
    # ════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="journal-lire",
        description="Affiche le lien vers le journal d'un membre."
    )
    @app_commands.describe(membre="Le membre dont vous voulez consulter le journal (par défaut : vous)")
    async def journal_lire(
        self, interaction: discord.Interaction,
        membre: Optional[discord.Member] = None,
    ):
        cible = membre or interaction.user
        uid = str(cible.id)

        perso = self._get_perso(cible.id)
        if not perso:
            if cible.id == interaction.user.id:
                await interaction.response.send_message(
                    "❌ Vous n'avez pas de personnage validé.", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ {cible.display_name} n'a pas de personnage validé.", ephemeral=True
                )
            return

        nom_perso = perso["nom_perso"]
        faction = perso.get("faction")

        # Vérifier si un journal existe
        journal_data = self.journaux.get(uid)
        if not journal_data or not journal_data.get("thread_id"):
            if cible.id == interaction.user.id:
                await interaction.response.send_message(
                    "📔 Votre journal n'a pas encore été créé. "
                    "Utilisez `/journal` pour le créer.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"📔 **{nom_perso}** n'a pas encore de journal.",
                    ephemeral=True,
                )
            return

        # Vérifier que le thread existe toujours
        thread = interaction.guild.get_channel_or_thread(journal_data["thread_id"])
        if not thread:
            # Le thread a été supprimé
            if cible.id == interaction.user.id:
                await interaction.response.send_message(
                    "📔 Votre journal a été supprimé. Utilisez `/journal` pour le recréer.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"📔 Le journal de **{nom_perso}** n'est plus accessible.",
                    ephemeral=True,
                )
            return

        kanji = KANJI_FACTION.get(faction, "")
        couleur = self._couleur_faction(faction)
        entrees = journal_data.get("entrees", 0)

        embed = discord.Embed(
            title=f"📔 Journal de {nom_perso}",
            description=(
                f"{kanji} **{faction.capitalize() if faction else 'Inconnu'}**\n\n"
                f"📎 **[Lire le journal]({thread.jump_url})**\n\n"
                f"Entrées : **{entrees}**"
            ),
            color=couleur,
        )
        embed.set_author(name=cible.display_name, icon_url=cible.display_avatar.url)
        embed.set_footer(text="⸻ Infernum Aeterna · Journal ⸻")

        await interaction.response.send_message(embed=embed)

    # ════════════════════════════════════════════════════════════════════════
    #  /journal-stats — Statistiques du journal
    # ════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="journal-stats",
        description="Affiche les statistiques de votre journal."
    )
    async def journal_stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        uid = str(user_id)
        perso = self._get_perso(user_id)

        if not perso:
            await interaction.followup.send(
                "❌ Vous n'avez pas de personnage validé.", ephemeral=True
            )
            return

        nom_perso = perso["nom_perso"]
        faction = perso.get("faction")
        couleur = self._couleur_faction(faction)
        kanji = KANJI_FACTION.get(faction, "")

        journal_data = self.journaux.get(uid)
        if not journal_data or not journal_data.get("thread_id"):
            await interaction.followup.send(
                "📔 Votre journal n'existe pas encore. Utilisez `/journal` pour le créer.",
                ephemeral=True,
            )
            return

        entrees = journal_data.get("entrees", 0)
        date_creation = journal_data.get("date_creation", "")

        # Date de création formatée
        date_creation_str = "—"
        if date_creation:
            try:
                dt = datetime.fromisoformat(date_creation)
                date_creation_str = dt.strftime("%d/%m/%Y")
            except ValueError:
                date_creation_str = date_creation[:10]

        # Estimation du nombre de mots : parcourir le thread pour compter
        thread = interaction.guild.get_channel_or_thread(journal_data["thread_id"])
        total_mots = 0
        derniere_entree_str = "—"
        if thread:
            try:
                async for message in thread.history(limit=200):
                    # Compter les mots dans les embeds (les entrées sont en embeds)
                    for emb in message.embeds:
                        if emb.description:
                            total_mots += len(emb.description.split())
                        if emb.title:
                            total_mots += len(emb.title.split())
                    # Compter aussi le contenu texte brut
                    if message.content:
                        total_mots += len(message.content.split())

                # Dernière entrée (hors message épinglé d'introduction)
                derniere_entree = None
                async for message in thread.history(limit=10, oldest_first=False):
                    if not message.pinned and (message.embeds or message.content):
                        derniere_entree = message
                        break
                if derniere_entree:
                    derniere_entree_str = derniere_entree.created_at.strftime("%d/%m/%Y à %H:%M")
            except discord.HTTPException:
                pass

        # Statistiques moyennes du serveur
        total_journaux = len(self.journaux)
        total_entrees_serveur = sum(j.get("entrees", 0) for j in self.journaux.values())
        moyenne_entrees = round(total_entrees_serveur / total_journaux, 1) if total_journaux > 0 else 0

        # Comparaison
        if entrees > moyenne_entrees:
            comparaison = f"Au-dessus de la moyenne du serveur (**{moyenne_entrees}** entrées)"
        elif entrees < moyenne_entrees:
            comparaison = f"En dessous de la moyenne du serveur (**{moyenne_entrees}** entrées)"
        else:
            comparaison = f"Dans la moyenne du serveur (**{moyenne_entrees}** entrées)"

        embed = discord.Embed(
            title=f"📊 Statistiques · Journal de {nom_perso}",
            color=couleur,
        )
        embed.set_author(
            name=f"{kanji} {faction.capitalize() if faction else 'Inconnu'}",
        )

        embed.add_field(name="Entrées totales", value=f"**{entrees}**", inline=True)
        embed.add_field(name="Mots estimés", value=f"~**{total_mots:,}**", inline=True)
        embed.add_field(name="Créé le", value=date_creation_str, inline=True)
        embed.add_field(name="Dernière entrée", value=derniere_entree_str, inline=True)
        embed.add_field(name="Journaux sur le serveur", value=f"**{total_journaux}**", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # spacer
        embed.add_field(name="Comparaison", value=comparaison, inline=False)

        if thread:
            embed.add_field(
                name="Lien",
                value=f"📎 **[Accéder au journal]({thread.jump_url})**",
                inline=False,
            )

        embed.set_footer(text="⸻ Infernum Aeterna · Journal ⸻")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Journal(bot))
