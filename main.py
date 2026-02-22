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
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info(f"✅ {cog}")
            except Exception as e:
                log.error(f"❌ {cog} : {e}")

        # Enregistrer les Views persistantes (survie au redémarrage)
        from cogs.construction import BoutonsFaction, BoutonCombat, BoutonsAbonnements
        self.add_view(BoutonsFaction())
        self.add_view(BoutonCombat("tous"))
        self.add_view(BoutonsAbonnements())

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
                description=(
                    f"Une nouvelle âme traverse la Fissure.\n\n"
                    f"{member.mention}, bienvenue dans **Infernum Aeterna**.\n"
                    f"Rendez-vous dans `🎭・choisir-son-destin` pour rejoindre une faction,\n"
                    f"puis soumettez votre fiche dans `📥・soumission-de-fiche`.\n\n"
                    f"「 Tout commencement est un jugement. 」"
                ),
                color=COULEURS["pourpre_infernal"]
            )
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
