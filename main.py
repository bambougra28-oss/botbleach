"""
INFERNUM AETERNA — Bot Discord
Point d'entrée principal.
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging

from config import DISCORD_TOKEN, GUILD_ID, COULEURS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("infernum")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


class InfernumBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.guild_id = GUILD_ID

    async def setup_hook(self):
        cogs = [
            "cogs.construction",
            "cogs.narrateur",
            "cogs.combat",
            "cogs.personnage",
            "cogs.ambiance",
            "cogs.evenements",
            "cogs.lore",
            "cogs.zones",
            "cogs.moderation",
            # ── Nouveaux systèmes ──
            "cogs.scenes",
            "cogs.missions",

            "cogs.pnj",
            "cogs.territoire",
            "cogs.journal",
            "cogs.aptitudes",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info(f"✅ {cog}")
            except Exception as e:
                log.error(f"❌ {cog} : {e}")

        # Enregistrer les Views persistantes (survie au redémarrage)
        from cogs.construction import BoutonCombat, BoutonsAbonnements, BoutonPacte
        self.add_view(BoutonPacte())
        self.add_view(BoutonCombat("tous"))
        self.add_view(BoutonsAbonnements())

        # Views persistantes des nouveaux systèmes
        try:
            from cogs.scenes import BoutonScene
            self.add_view(BoutonScene())
        except Exception as e:
            log.warning(f"⚠️ BoutonScene non enregistré : {e}")

        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info(f"🔄 {len(synced)} commandes synchronisées")

    async def on_ready(self):
        log.info(f"✅ {self.user} prêt.")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="la Fissure s'élargir…")
        )

    async def on_app_command_error(self, interaction, error):
        log.error("Erreur commande /%s : %s", getattr(interaction.command, "name", "?"), error, exc_info=error)

        # Message utilisateur typé
        original = getattr(error, "original", error)
        if isinstance(error, app_commands.errors.MissingPermissions):
            msg = "❌ Permissions insuffisantes pour cette commande."
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            msg = f"⏳ Commande en cooldown — réessayez dans {error.retry_after:.0f}s."
        else:
            msg = f"❌ Une erreur est survenue : {original}"

        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass

    async def on_member_join(self, member):
        from cogs.construction import charger_roles, trouver_channel
        roles_ids = charger_roles()
        rid = roles_ids.get("observateur")
        if rid:
            role = member.guild.get_role(rid)
            if role:
                await member.add_roles(role, reason="Nouveau membre")
        ch = trouver_channel(member.guild, "fissure-du-monde")
        if ch:
            embed = discord.Embed(
                title="地獄の門 — Une âme traverse la Fissure",
                description=(
                    f"Les Portes ont frémi. Une nouvelle âme traverse la Fissure "
                    f"— portée par un souffle qui ne lui appartient pas encore.\n\n"
                    f"{member.mention}, bienvenue dans **Infernum Aeterna**.\n\n"
                    f"Le monde que vous connaissiez n'existe plus. Les Trois Mondes "
                    f"vacillent, l'Enfer déborde, et quelque chose frappe aux Portes "
                    f"depuis l'autre côté. Ici, vous écrirez votre propre légende "
                    f"— que vous le vouliez ou non."
                ),
                color=COULEURS["pourpre_infernal"]
            )
            embed.add_field(
                name="⚖️ Première étape — Le Pacte",
                value="Lisez et acceptez le Pacte des Âmes dans `⚖️・pacte-des-âmes` pour accéder au serveur.",
                inline=False
            )
            embed.add_field(
                name="🎭 Découvrir les Factions",
                value="Explorez `🎭・choisir-son-destin` pour découvrir les quatre chemins possibles.",
                inline=False
            )
            embed.add_field(
                name="📋 Forger votre identité",
                value="Créez votre personnage dans `📋・modele-de-fiche` puis soumettez-le dans `📥・soumission-de-fiche`. Le staff validera votre fiche et vous attribuera vos rôles.",
                inline=False
            )
            embed.set_footer(text="⸻ Infernum Aeterna · 「 Tout commencement est un jugement. 」 ⸻")
            await ch.send(embed=embed)


async def main():
    bot = InfernumBot()
    if not DISCORD_TOKEN:
        log.critical("❌ DISCORD_TOKEN manquant — arrêt.")
        return
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
