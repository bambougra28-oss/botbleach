"""
INFERNUM AETERNA — Cog Narrateur
- /narrer [type] [contenu] — génère une narration épique via Claude
- /flash [message]         — publie une alerte narrative courte
- narration_validation_auto() — déclencheur depuis Personnage
- narration_rang_auto()        — déclencheur depuis Personnage
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import anthropic
import asyncio
import logging

from config import COULEURS, ANTHROPIC_KEY, CLAUDE_MODEL, NARRATEUR_SYSTEM
from cogs.construction import trouver_channel

log = logging.getLogger("infernum")

TYPES_NARRATION = {
    "validation": "Validation d'un nouveau personnage",
    "rang":       "Montée en rang",
    "combat":     "Compte-rendu épique d'un combat",
    "evenement":  "Annonce d'un événement majeur",
    "fissure":    "Perturbation de la Fissure",
    "mort":       "Mort narrative d'un personnage",
    "revelation": "Révélation lore majeure",
    "libre":      "Narration libre",
}

_RAPPEL_OC = (
    "\n\n⚠ RAPPEL : Ce personnage est un PERSONNAGE ORIGINAL (OC) créé par un joueur. "
    "Ce n'est PAS un personnage canon de Bleach même si son nom y ressemble. "
    "Utilise UNIQUEMENT les informations fournies ci-dessus. "
    "N'invente aucun pouvoir, technique, Zanpakutō, relation ou événement non mentionné. "
    "Ne fais aucune référence à un personnage canon de Bleach."
)

PROMPTS = {
    "validation": lambda c: (
        f"Un NOUVEAU PERSONNAGE ORIGINAL (OC) vient d'être validé sur le serveur RP. "
        f"Voici les SEULES informations disponibles :\n\n{c}\n\n"
        "Produis une narration d'accueil annonçant l'arrivée de cette âme dans les Trois Mondes. "
        "Mentionne sa faction et son rang tels qu'indiqués ci-dessus. "
        "Si son histoire est résumée, évoque-la en restant fidèle au texte fourni — n'extrapole pas. "
        "Situe son arrivée dans le contexte de la Fissure et des tensions actuelles."
        + _RAPPEL_OC
    ),
    "rang": lambda c: (
        f"Un PERSONNAGE ORIGINAL (OC) vient de monter en rang. "
        f"Voici les SEULES informations :\n\n{c}\n\n"
        "Produis une narration solennelle. Mentionne uniquement le nouveau rang et la faction indiqués. "
        "Évoque la gravité de cette responsabilité dans le contexte de la Fissure. "
        "Ne décris aucune épreuve ou combat qui ne serait pas mentionné dans le contexte."
        + _RAPPEL_OC
    ),
    "combat": lambda c: (
        f"Un combat entre PERSONNAGES ORIGINAUX (OC) vient de se terminer. "
        f"Voici les SEULES informations :\n\n{c}\n\n"
        "Produis une narration épique du duel. Ne décris que ce qui est mentionné dans le résumé. "
        "N'invente aucune technique, aucun pouvoir, aucun Zanpakutō non cité. "
        "Conclus sur les répercussions dans le contexte du serveur."
        + _RAPPEL_OC
    ),
    "evenement": lambda c: (
        f"Un événement narratif majeur se déclenche dans le monde d'Infernum Aeterna. "
        f"Voici les informations :\n\n{c}\n\n"
        "Annonce cet événement avec la solennité d'un oracle. "
        "Reste strictement dans le cadre décrit. N'ajoute aucun détail non mentionné."
        + _RAPPEL_OC
    ),
    "fissure": lambda c: (
        f"La Fissure connaît une évolution. Voici les informations :\n\n{c}\n\n"
        "Décris cette perturbation : vibrations, signal du Jigoku no Rinki, "
        "pressentiments des âmes les plus anciennes. "
        "Reste dans le cadre du lore du serveur."
        + _RAPPEL_OC
    ),
    "mort": lambda c: (
        f"Un PERSONNAGE ORIGINAL (OC) vient de mourir (mort narrative). "
        f"Voici les SEULES informations :\n\n{c}\n\n"
        "Produis une narration funèbre. Rends hommage à ce personnage en te basant "
        "UNIQUEMENT sur les éléments fournis. N'invente aucun souvenir, aucune relation, "
        "aucun exploit non mentionné. Évoque ce que sa disparition laisse dans le monde."
        + _RAPPEL_OC
    ),
    "revelation": lambda c: (
        f"Une révélation lore majeure se produit dans Infernum Aeterna :\n\n{c}\n\n"
        "Annonce cette vérité avec gravité. Reste cryptique et pesant. "
        "Ne développe que ce qui est explicitement mentionné."
        + _RAPPEL_OC
    ),
    "libre": lambda c: c + _RAPPEL_OC,
}

COULEURS_TYPE = {
    "validation": "or_ancien",
    "rang":       "blanc_seireitei",
    "combat":     "rouge_chaine",
    "evenement":  "pourpre_infernal",
    "fissure":    "pourpre_infernal",
    "mort":       None,
    "revelation": "or_ancien",
    "libre":      "gris_acier",
}

TITRES_TYPE = {
    "validation": "✦ Une nouvelle âme entre dans les Chroniques",
    "rang":       "⬆️ L'ascension est gravée dans les Chroniques",
    "combat":     "⚔️ Le Combat est consigné dans les Chroniques",
    "evenement":  "⚡ Les Chroniques Vivantes s'éveillent",
    "fissure":    "🩸 La Fissure frémit",
    "mort":       "✝ Les Chroniques pleurent une âme",
    "revelation": "👁️ Une Vérité Ancienne remonte",
    "libre":      "📜 Le Narrateur prend la parole",
}


class Narrateur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._client = None
        if ANTHROPIC_KEY:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=30.0)
        else:
            log.warning("ANTHROPIC_KEY absente — narration désactivée")
        self._semaphore = asyncio.Semaphore(3)

    # ── Génération ──────────────────────────────────────────────────────────────
    async def generer_narration(self, type_narration: str, contenu: str, longueur: str = "normale") -> str:
        if not self._client:
            return "⚠️ Narrateur indisponible (clé API manquante)."

        prompt_fn = PROMPTS.get(type_narration, PROMPTS["libre"])
        prompt    = prompt_fn(contenu)

        instructions = {
            "courte":  "2 paragraphes courts, sentence finale lapidaire.",
            "normale": "3 à 4 paragraphes, sentence finale lapidaire.",
            "longue":  "5 à 6 paragraphes, pleine puissance épique, sentence finale lapidaire.",
        }
        prompt += f"\n\n{instructions.get(longueur, instructions['normale'])}"

        async with self._semaphore:
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=1200,
                        system=NARRATEUR_SYSTEM,
                        messages=[{"role": "user", "content": prompt}]
                    )
                ),
                timeout=35.0
            )
        return response.content[0].text

    # ── Construction embed ───────────────────────────────────────────────────────
    def _construire_embed(self, type_narration: str, texte: str, auteur: Optional[str] = None) -> discord.Embed:
        cle_couleur = COULEURS_TYPE.get(type_narration)
        couleur     = COULEURS.get(cle_couleur, 0x2C2C2C) if cle_couleur else 0x2C2C2C

        embed = discord.Embed(
            title=TITRES_TYPE.get(type_narration, "📜 Chroniques"),
            description=texte,
            color=couleur
        )
        embed.set_footer(
            text="⸻ Infernum Aeterna · Chroniques Vivantes ⸻"
            + (f"  |  Déclenché par {auteur}" if auteur else "")
        )
        return embed

    # ── Canal narrateur ──────────────────────────────────────────────────────────
    def _trouver_channel_narrateur(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        return trouver_channel(guild, "journal-de-l-enfer")

    # ══════════════════════════════════════════════════════════════════════════
    #  /narrer
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="narrer", description="[STAFF] Déclenche une narration épique.")
    @app_commands.describe(
        type_narration="Type d'événement",
        contenu="Contexte à transmettre au Narrateur",
        longueur="Longueur de la narration",
        channel="Channel de publication (défaut : journal-de-l-enfer)"
    )
    @app_commands.choices(type_narration=[
        app_commands.Choice(name=v, value=k) for k, v in TYPES_NARRATION.items()
    ])
    @app_commands.choices(longueur=[
        app_commands.Choice(name="Courte (2 §)",   value="courte"),
        app_commands.Choice(name="Normale (3-4 §)", value="normale"),
        app_commands.Choice(name="Longue (5-6 §)", value="longue"),
    ])
    @app_commands.default_permissions(manage_messages=True)
    async def narrer(
        self, interaction: discord.Interaction,
        type_narration: str, contenu: str,
        longueur: str = "normale", channel: Optional[discord.TextChannel] = None
    ):
        await interaction.response.defer(ephemeral=True)

        try:
            texte = await self.generer_narration(type_narration, contenu, longueur)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur génération : {e}", ephemeral=True)
            return

        embed = self._construire_embed(type_narration, texte, str(interaction.user))
        dest  = channel or self._trouver_channel_narrateur(interaction.guild)
        if not dest:
            await interaction.followup.send("❌ Channel narrateur introuvable.", ephemeral=True)
            return

        await dest.send(embed=embed)
        await interaction.followup.send(f"✅ Narration publiée dans {dest.mention}.", ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  /flash
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="flash", description="[STAFF] Publie une alerte narrative courte.")
    @app_commands.describe(message="Message d'alerte à diffuser")
    @app_commands.default_permissions(manage_messages=True)
    async def flash(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        dest = trouver_channel(guild, "flash-evenements") or trouver_channel(guild, "flash")
        if not dest:
            dest = self._trouver_channel_narrateur(guild)
        if not dest:
            await interaction.followup.send("❌ Channel flash introuvable.", ephemeral=True)
            return

        embed = discord.Embed(description=f"⚡  {message}", color=COULEURS["rouge_chaine"])
        embed.set_footer(text="⸻ Infernum Aeterna · Flash Événement ⸻")
        await dest.send(embed=embed)
        await interaction.followup.send(f"✅ Flash publié dans {dest.mention}.", ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  DÉCLENCHEURS AUTOMATIQUES
    # ══════════════════════════════════════════════════════════════════════════

    async def narration_validation_auto(self, guild: discord.Guild, fiche_resume: str, nom_perso: str):
        try:
            texte = await self.generer_narration("validation", fiche_resume, "normale")
            embed = self._construire_embed("validation", texte)
            dest  = self._trouver_channel_narrateur(guild)
            if dest:
                await dest.send(embed=embed)
        except Exception as e:
            log.error("Erreur validation auto : %s", e)

    async def narration_rang_auto(self, guild: discord.Guild, details_rang: str):
        try:
            texte = await self.generer_narration("rang", details_rang, "courte")
            embed = self._construire_embed("rang", texte)
            dest  = self._trouver_channel_narrateur(guild)
            if dest:
                await dest.send(embed=embed)
        except Exception as e:
            log.error("Erreur rang auto : %s", e)


async def setup(bot):
    await bot.add_cog(Narrateur(bot))
