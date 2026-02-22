"""
INFERNUM AETERNA — Cog Événements
Gestion des arcs narratifs, de l'état de la Fissure et des portails événementiels.

Commandes :
  /arc-ouvrir        — démarre un nouvel arc narratif
  /arc-clore         — clôture un arc avec résumé automatique
  /arc-actuel        — affiche l'arc en cours
  /fissure-etat      — met à jour l'état public de la Fissure
  /portail-ouvrir    — rend un channel événementiel visible
  /portail-fermer    — archive le channel événementiel
  /etat-serveur      — tableau de bord global du serveur
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import anthropic
import asyncio
import json
import os
import logging
from datetime import datetime, timezone

from config import COULEURS, ANTHROPIC_KEY, CLAUDE_MODEL, NARRATEUR_SYSTEM
from cogs.construction import trouver_channel
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

EVENEMENTS_FILE = "data/evenements.json"

# ── Niveaux de la Fissure ──────────────────────────────────────────────────────
NIVEAUX_FISSURE = {
    1: ("Stable",     0x57F287, "La Fissure est contenue. Légères irrégularités du Reishi."),
    2: ("Instable",   0xFEE75C, "Des ondulations traversent les Trois Mondes. La Fissure s'élargit."),
    3: ("Critique",   0xFF8C00, "Le Jigoku no Rinki se propage. Les Kushanāda deviennent erratiques."),
    4: ("Brisée",     0xED4245, "La Fissure est hors de contrôle. Des âmes s'échappent de l'Enfer."),
    5: ("Apocalypse", 0x8B0000, "Les Portes de l'Enfer sont ouvertes. Les Trois Mondes vacillent."),
}


def _charger() -> dict:
    if not os.path.exists(EVENEMENTS_FILE):
        return {"arc_actuel": None, "arcs_archives": [], "fissure_niveau": 2, "portails_actifs": []}
    with open(EVENEMENTS_FILE) as f:
        return json.load(f)


def _sauvegarder(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(EVENEMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class Evenements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(EVENEMENTS_FILE, default={"arc_actuel": None, "arcs_archives": [], "fissure_niveau": 2, "portails_actifs": []})
        self.data = self._store.data
        self._client = None
        if ANTHROPIC_KEY:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=30.0)
        else:
            log.warning("ANTHROPIC_KEY absente — résumés d'arc désactivés")
        self._semaphore = asyncio.Semaphore(3)

    async def _save(self):
        self._store.data = self.data
        await self._store.save()

    # ── Résumé d'arc via Claude ────────────────────────────────────────────────
    async def _generer_resume_arc(self, arc: dict) -> str:
        if not self._client:
            return "Résumé indisponible (clé API manquante)."

        evenements_str = "\n".join(f"- {e}" for e in arc.get("evenements", []))
        prompt = (
            f"Résume cet arc narratif du serveur RP Infernum Aeterna (univers alternatif inspiré de Bleach).\n\n"
            f"Titre de l'arc : {arc.get('titre', '?')}\n"
            f"Durée : {arc.get('debut', '?')} → {arc.get('fin', '?')}\n"
            f"Description initiale : {arc.get('description', '')}\n"
            f"Événements notables :\n{evenements_str or 'Aucun enregistré.'}\n\n"
            "Écris un résumé épique de 3 paragraphes en français littéraire. "
            "Adopte le ton d'un chroniqueur qui consigne l'Histoire des Trois Mondes pour l'éternité. "
            "Termine par une sentence lapidaire qui capture l'essence de cet arc.\n\n"
            "⚠ CONTRAINTES :\n"
            "- Base-toi UNIQUEMENT sur les informations ci-dessus.\n"
            "- N'invente aucun événement, personnage ou détail non listé.\n"
            "- Ne mentionne AUCUN personnage canon de Bleach.\n"
            "- Tous les personnages mentionnés dans les événements sont des OC."
        )
        async with self._semaphore:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=800,
                        system=NARRATEUR_SYSTEM,
                        messages=[{"role": "user", "content": prompt}]
                    )
                ),
                timeout=35.0
            )
        return response.content[0].text.strip()

    # ══════════════════════════════════════════════════════════════════════════
    #  ARCS NARRATIFS
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="arc-ouvrir", description="[STAFF] Démarre un nouvel arc narratif.")
    @app_commands.describe(
        titre="Titre de l'arc",
        description="Description narrative de l'arc",
        niveau_fissure="Niveau initial de la Fissure pour cet arc",
    )
    @app_commands.choices(niveau_fissure=[
        app_commands.Choice(name=f"Niveau {n} — {v[0]}", value=n)
        for n, v in NIVEAUX_FISSURE.items()
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def arc_ouvrir(
        self,
        interaction: discord.Interaction,
        titre: str,
        description: str,
        niveau_fissure: int = 2,
    ):
        if self.data.get("arc_actuel"):
            await interaction.response.send_message(
                "❌ Un arc est déjà en cours. Utilisez `/arc-clore` d'abord.", ephemeral=True
            )
            return

        arc = {
            "titre": titre,
            "description": description,
            "debut": datetime.now(timezone.utc).isoformat(),
            "fin": None,
            "niveau_fissure": niveau_fissure,
            "evenements": [],
        }
        self.data["arc_actuel"] = arc
        self.data["fissure_niveau"] = niveau_fissure
        await self._save()

        niveau_info = NIVEAUX_FISSURE[niveau_fissure]
        embed = discord.Embed(
            title=f"📖 Nouvel Arc — {titre}",
            description=description,
            color=niveau_info[1]
        )
        embed.add_field(name="État de la Fissure", value=f"Niveau {niveau_fissure} — **{niveau_info[0]}**", inline=True)
        embed.add_field(name="Début", value=datetime.now(timezone.utc).strftime("%d/%m/%Y"), inline=True)
        embed.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")

        # Publier dans le canal calendrier
        ch_cal = trouver_channel(interaction.guild, "calendrier-des-arcs") or trouver_channel(interaction.guild, "calendrier")
        if ch_cal:
            await ch_cal.send(embed=embed)

        # Déclencher une narration d'ouverture d'arc et la publier
        cog_narrateur = self.bot.cogs.get("Narrateur")
        if cog_narrateur:
            async def _publier_narration_arc():
                try:
                    texte = await cog_narrateur.generer_narration(
                        "evenement", f"Ouverture de l'arc : {titre}\n{description}", "longue"
                    )
                    embed_narr = cog_narrateur._construire_embed("evenement", texte)
                    dest = cog_narrateur._trouver_channel_narrateur(interaction.guild)
                    if dest:
                        await dest.send(embed=embed_narr)
                except Exception as e:
                    log.error("Erreur narration arc : %s", e)
            asyncio.create_task(_publier_narration_arc())

        await interaction.response.send_message(f"✅ Arc **{titre}** ouvert.", ephemeral=True)

    @app_commands.command(name="arc-clore", description="[STAFF] Clôture l'arc en cours avec résumé automatique.")
    @app_commands.describe(conclusion="Conclusion narrative de l'arc")
    @app_commands.default_permissions(manage_guild=True)
    async def arc_clore(self, interaction: discord.Interaction, conclusion: str):
        arc = self.data.get("arc_actuel")
        if not arc:
            await interaction.response.send_message("❌ Aucun arc en cours.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        arc["fin"] = datetime.now(timezone.utc).isoformat()
        arc["conclusion"] = conclusion
        arc["evenements"].append(f"Conclusion : {conclusion}")

        resume = await self._generer_resume_arc(arc)

        self.data["arcs_archives"].append(arc)
        self.data["arc_actuel"] = None
        await self._save()

        embed = discord.Embed(
            title=f"📚 Arc Terminé — {arc['titre']}",
            description=resume,
            color=COULEURS["or_ancien"]
        )
        embed.add_field(name="Début", value=arc["debut"][:10], inline=True)
        embed.add_field(name="Fin",   value=arc["fin"][:10],   inline=True)
        embed.set_footer(text="⸻ Infernum Aeterna · Archives des Arcs ⸻")

        ch_archives = trouver_channel(interaction.guild, "archives-des-arcs") or trouver_channel(interaction.guild, "archives")
        if ch_archives:
            await ch_archives.send(embed=embed)

        await interaction.followup.send(f"✅ Arc **{arc['titre']}** clôturé et archivé.", ephemeral=True)

    @app_commands.command(name="arc-actuel", description="Affiche l'arc narratif en cours.")
    async def arc_actuel(self, interaction: discord.Interaction):
        arc = self.data.get("arc_actuel")
        if not arc:
            await interaction.response.send_message("Aucun arc en cours.", ephemeral=True)
            return
        niveau = self.data.get("fissure_niveau", 2)
        niveau_info = NIVEAUX_FISSURE.get(niveau, NIVEAUX_FISSURE[2])
        embed = discord.Embed(
            title=f"📖 Arc en cours — {arc['titre']}",
            description=arc.get("description", ""),
            color=niveau_info[1]
        )
        embed.add_field(name="Fissure", value=f"Niveau {niveau} — **{niveau_info[0]}**\n*{niveau_info[2]}*", inline=False)
        embed.add_field(name="Début",   value=arc["debut"][:10], inline=True)
        if arc.get("evenements"):
            derniers = arc["evenements"][-3:]
            embed.add_field(name="Derniers événements", value="\n".join(f"• {e}" for e in derniers), inline=False)
        embed.set_footer(text="⸻ Infernum Aeterna ⸻")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="arc-evenement", description="[STAFF] Ajoute un événement notable à l'arc en cours.")
    @app_commands.describe(evenement="Description courte de l'événement")
    @app_commands.default_permissions(manage_messages=True)
    async def arc_evenement(self, interaction: discord.Interaction, evenement: str):
        arc = self.data.get("arc_actuel")
        if not arc:
            await interaction.response.send_message("❌ Aucun arc en cours.", ephemeral=True)
            return
        arc["evenements"].append(f"[{datetime.now(timezone.utc).strftime('%d/%m')}] {evenement}")
        await self._save()
        await interaction.response.send_message(f"✅ Événement ajouté à l'arc **{arc['titre']}**.", ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  ÉTAT DE LA FISSURE
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="fissure-etat", description="[STAFF] Met à jour l'état public de la Fissure.")
    @app_commands.describe(
        niveau="Niveau de danger de la Fissure",
        description="Description narrative de l'état actuel",
    )
    @app_commands.choices(niveau=[
        app_commands.Choice(name=f"Niveau {n} — {v[0]}", value=n)
        for n, v in NIVEAUX_FISSURE.items()
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def fissure_etat(
        self,
        interaction: discord.Interaction,
        niveau: int,
        description: Optional[str] = None,
    ):
        self.data["fissure_niveau"] = niveau
        if self.data.get("arc_actuel"):
            self.data["arc_actuel"]["niveau_fissure"] = niveau
        await self._save()

        niveau_info = NIVEAUX_FISSURE[niveau]
        desc = description or niveau_info[2]
        embed = discord.Embed(
            title=f"🩸 État de la Fissure — Niveau {niveau} : {niveau_info[0]}",
            description=desc,
            color=niveau_info[1]
        )
        embed.set_footer(
            text=f"Mis à jour le {datetime.now(timezone.utc).strftime('%d/%m/%Y à %H:%M')} UTC"
        )

        # Mettre à jour le canal état de la fissure
        canal_trouve = trouver_channel(interaction.guild, "etat-de-la-fissure")
        if canal_trouve:
            # Supprimer le dernier message du bot pour garder propre
            async for msg in canal_trouve.history(limit=5):
                if msg.author == self.bot.user:
                    await msg.delete()
                    break
            await canal_trouve.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Fissure mise à jour : Niveau {niveau} — **{niveau_info[0]}**"
            + (f" dans {canal_trouve.mention}" if canal_trouve else ""),
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  PORTAILS ÉVÉNEMENTIELS
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="portail-ouvrir", description="[STAFF] Ouvre un channel événementiel (le rend visible).")
    @app_commands.describe(
        channel="Channel à activer",
        message="Message d'annonce dans le channel",
    )
    @app_commands.default_permissions(manage_channels=True)
    async def portail_ouvrir(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: Optional[str] = None,
    ):
        # Rendre visible à tous les membres avec personnage validé
        from cogs.construction import charger_roles
        roles_ids = charger_roles()
        guild = interaction.guild
        role_valide_id = roles_ids.get("personnage_valide")
        role_valide = guild.get_role(role_valide_id) if role_valide_id else None

        overwrite_everyone = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        overwrite_valide = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        await channel.set_permissions(guild.default_role, overwrite=overwrite_everyone)
        if role_valide:
            await channel.set_permissions(role_valide, overwrite=overwrite_valide)

        if channel.id not in self.data.get("portails_actifs", []):
            self.data.setdefault("portails_actifs", []).append(channel.id)
            await self._save()

        # Message d'ouverture
        embed = discord.Embed(
            description=message or "「 Un portail vient de s'ouvrir. Ce lieu n'était pas accessible. Il l'est désormais. 」",
            color=COULEURS["pourpre_infernal"]
        )
        await channel.send(embed=embed)

        # Ping événement actif
        role_event_id = roles_ids.get("evenement_actif")
        if role_event_id:
            role_event = guild.get_role(role_event_id)
            if role_event:
                ch_flash = trouver_channel(guild, "flash-evenements") or trouver_channel(guild, "flash")
                if ch_flash:
                    await ch_flash.send(f"{role_event.mention} — Le portail **{channel.name}** vient de s'ouvrir.")

        await interaction.response.send_message(f"✅ Portail {channel.mention} ouvert.", ephemeral=True)

    @app_commands.command(name="portail-fermer", description="[STAFF] Ferme un channel événementiel.")
    @app_commands.describe(channel="Channel à désactiver")
    @app_commands.default_permissions(manage_channels=True)
    async def portail_fermer(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        if channel.id in self.data.get("portails_actifs", []):
            self.data["portails_actifs"].remove(channel.id)
            await self._save()

        embed = discord.Embed(
            description="「 Le portail se referme. Ce qui était accessible ne l'est plus. 」",
            color=0x1A1A1A
        )
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Portail {channel.mention} fermé.", ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TABLEAU DE BORD GLOBAL
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="etat-serveur", description="Tableau de bord global du serveur Infernum Aeterna.")
    async def etat_serveur(self, interaction: discord.Interaction):
        guild = interaction.guild
        niveau = self.data.get("fissure_niveau", 2)
        niveau_info = NIVEAUX_FISSURE.get(niveau, NIVEAUX_FISSURE[2])
        arc = self.data.get("arc_actuel")

        # Comptages
        total_membres = guild.member_count
        from cogs.construction import charger_roles
        roles_ids = charger_roles()
        valides = 0
        attente = 0
        factions_count = {f: 0 for f in ["shinigami", "togabito", "arrancar", "quincy"]}

        for membre in guild.members:
            role_ids_membre = {r.id for r in membre.roles}
            rid_valide = roles_ids.get("personnage_valide")
            rid_attente = roles_ids.get("en_attente")
            if rid_valide and rid_valide in role_ids_membre:
                valides += 1
            if rid_attente and rid_attente in role_ids_membre:
                attente += 1
            for faction in factions_count:
                rid = roles_ids.get(faction)
                if rid and rid in role_ids_membre:
                    factions_count[faction] += 1

        embed = discord.Embed(
            title="⛩️ Infernum Aeterna — État du Serveur",
            color=niveau_info[1]
        )
        embed.add_field(
            name="🩸 Fissure",
            value=f"Niveau **{niveau}** — {niveau_info[0]}\n*{niveau_info[2]}*",
            inline=False
        )
        if arc:
            embed.add_field(
                name="📖 Arc en cours",
                value=f"**{arc['titre']}**\nDepuis le {arc['debut'][:10]}",
                inline=True
            )
        embed.add_field(
            name="👥 Membres",
            value=f"Total : **{total_membres}**\n✅ Validés : **{valides}**\n⏳ En attente : **{attente}**",
            inline=True
        )
        embed.add_field(
            name="⚔️ Factions",
            value=(
                f"死神 Shinigami : **{factions_count['shinigami']}**\n"
                f"咎人 Togabito : **{factions_count['togabito']}**\n"
                f"破面 Arrancar : **{factions_count['arrancar']}**\n"
                f"滅却師 Quincy : **{factions_count['quincy']}**"
            ),
            inline=True
        )
        portails = self.data.get("portails_actifs", [])
        if portails:
            mentions = " ".join(f"<#{p}>" for p in portails[:5])
            embed.add_field(name="🌀 Portails Actifs", value=mentions, inline=False)

        embed.set_footer(text=f"⸻ Mis à jour le {datetime.now(timezone.utc).strftime('%d/%m/%Y à %H:%M')} UTC ⸻")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Evenements(bot))
