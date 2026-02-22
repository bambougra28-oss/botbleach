"""
INFERNUM AETERNA — Cog Zones Dynamiques
Création et archivage de salons RP temporaires par le staff.
Fonctionnalité centrale du cahier des charges : permettre au staff
d'ouvrir des espaces narratifs ad hoc sans reconfigurer le serveur.

Commandes :
  /zone-creer   — crée un salon temporaire dans une catégorie existante
  /zone-archiver — archive (ferme) un salon dynamique
  /zones-actives — liste toutes les zones dynamiques en cours
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json
import os
from datetime import datetime, timezone

from config import COULEURS
from cogs.construction import charger_roles
from utils.json_store import JsonStore

ZONES_FILE = "data/zones_dynamiques.json"

CATEGORIES_CIBLES = {
    "enfer":        "LES STRATES",
    "soul_society": "SOUL SOCIETY",
    "hueco_mundo":  "HUECO MUNDO",
    "vivants":      "MONDE DES VIVANTS",
    "frontiere":    "LA FRONTIÈRE",
    "quincy":       "SURVIVANTS QUINCY",
}


def _charger() -> dict:
    if not os.path.exists(ZONES_FILE):
        return {"zones": []}
    with open(ZONES_FILE) as f:
        return json.load(f)


def _sauvegarder(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(ZONES_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class Zones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(ZONES_FILE, default={"zones": []})
        self.data = self._store.data

    # ══════════════════════════════════════════════════════════════════════════
    #  /zone-creer
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="zone-creer",
        description="[STAFF] Crée un salon RP temporaire dans une catégorie existante."
    )
    @app_commands.describe(
        nom="Nom du salon (sans emoji, il sera ajouté automatiquement)",
        secteur="Secteur de création",
        description="Description narrative du lieu (apparaît en message épinglé)",
        factions="Factions autorisées à écrire (laisser vide = tous les personnages validés)",
        prive="Si activé, seuls les staff et les factions désignées voient le salon",
    )
    @app_commands.choices(secteur=[
        app_commands.Choice(name="Enfer — Les Strates",       value="enfer"),
        app_commands.Choice(name="Soul Society",               value="soul_society"),
        app_commands.Choice(name="Hueco Mundo",                value="hueco_mundo"),
        app_commands.Choice(name="Monde des Vivants",          value="vivants"),
        app_commands.Choice(name="La Frontière",               value="frontiere"),
        app_commands.Choice(name="Survivants Quincy",          value="quincy"),
    ])
    @app_commands.default_permissions(manage_channels=True)
    async def zone_creer(
        self,
        interaction: discord.Interaction,
        nom: str,
        secteur: str,
        description: str,
        factions: Optional[str] = None,
        prive: bool = False,
    ):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # ── Trouver la catégorie cible ─────────────────────────────────────────
        mot_cle = CATEGORIES_CIBLES.get(secteur, "")
        categorie = None
        for cat in guild.categories:
            if mot_cle.lower() in cat.name.lower():
                categorie = cat
                break

        if not categorie:
            await interaction.followup.send(
                f"❌ Catégorie '{mot_cle}' introuvable. Lancez `/setup` d'abord.",
                ephemeral=True
            )
            return

        # ── Construction des permissions ───────────────────────────────────────
        roles_ids = charger_roles()
        everyone = guild.default_role
        overwrites = {}

        if prive:
            overwrites[everyone] = discord.PermissionOverwrite(view_channel=False)
        else:
            overwrites[everyone] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

        # Staff toujours accès complet
        for cle_staff in ("architecte", "gardien_des_portes", "emissaire"):
            rid = roles_ids.get(cle_staff)
            if rid:
                role = guild.get_role(rid)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True, send_messages=True, manage_messages=True
                    )

        # Factions désignées ou personnages validés par défaut
        if factions:
            faction_list = [f.strip().lower() for f in factions.split(",")]
            for faction in faction_list:
                rid = roles_ids.get(faction)
                if rid:
                    role = guild.get_role(rid)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True, send_messages=True
                        )
        else:
            rid_valide = roles_ids.get("personnage_valide")
            if rid_valide:
                role_valide = guild.get_role(rid_valide)
                if role_valide:
                    overwrites[role_valide] = discord.PermissionOverwrite(
                        view_channel=True, send_messages=True
                    )

        # ── Créer le salon ─────────────────────────────────────────────────────
        nom_propre = f"📍・{nom.lower().replace(' ', '-')}"
        try:
            channel = await guild.create_text_channel(
                name=nom_propre,
                category=categorie,
                topic=description,
                overwrites=overwrites,
                reason=f"Zone dynamique créée par {interaction.user}"
            )
        except discord.Forbidden:
            await interaction.followup.send("❌ Permissions insuffisantes.", ephemeral=True)
            return

        # ── Message épinglé d'introduction ────────────────────────────────────
        embed = discord.Embed(
            title=f"📍 {nom}",
            description=description,
            color=COULEURS["pourpre_infernal"]
        )
        embed.add_field(
            name="Accès",
            value=factions.replace(",", " · ") if factions else "Personnages validés",
            inline=True
        )
        embed.add_field(name="Créée par", value=interaction.user.mention, inline=True)
        embed.add_field(
            name="Archivage",
            value="Utilisez `/zone-archiver` pour fermer ce salon.",
            inline=False
        )
        embed.set_footer(text="⸻ Zone Dynamique · Infernum Aeterna ⸻")
        msg = await channel.send(embed=embed)
        await msg.pin()

        # ── Enregistrer la zone ────────────────────────────────────────────────
        self.data["zones"].append({
            "channel_id": channel.id,
            "channel_nom": channel.name,
            "secteur": secteur,
            "createur": str(interaction.user),
            "createur_id": interaction.user.id,
            "description": description,
            "factions": factions or "tous",
            "prive": prive,
            "creation": datetime.now(timezone.utc).isoformat(),
            "archivee": False,
        })
        await self._store.save()

        await interaction.followup.send(
            f"✅ Zone **{nom}** créée dans la catégorie **{categorie.name}** : {channel.mention}",
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /zone-archiver
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="zone-archiver",
        description="[STAFF] Archive (ferme) un salon de zone dynamique."
    )
    @app_commands.describe(
        channel="Le salon à archiver",
        conclusion="Message de clôture narrative (optionnel)"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def zone_archiver(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        conclusion: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        # Vérifier que c'est bien une zone dynamique
        zone = next(
            (z for z in self.data["zones"] if z["channel_id"] == channel.id and not z.get("archivee")),
            None
        )
        if not zone:
            await interaction.followup.send(
                "❌ Ce salon n'est pas une zone dynamique active.", ephemeral=True
            )
            return

        # Message de clôture
        embed = discord.Embed(
            description=(
                conclusion or
                "「 Ce lieu se referme. Ce qui s'y est passé demeure dans les Chroniques. 」"
            ),
            color=0x1A1A1A
        )
        embed.set_footer(text=f"Zone archivée par {interaction.user} · {datetime.now(timezone.utc).strftime('%d/%m/%Y')}")
        await channel.send(embed=embed)

        # Rendre le salon invisible et verrouillé
        await channel.set_permissions(
            interaction.guild.default_role,
            view_channel=False
        )
        await channel.edit(
            name=f"🔒・{channel.name.replace('📍・', '')}",
            reason=f"Zone archivée par {interaction.user}"
        )

        # Mettre à jour les données
        zone["archivee"] = True
        zone["archivage"] = datetime.now(timezone.utc).isoformat()
        zone["conclusion"] = conclusion or ""
        await self._store.save()

        await interaction.followup.send(
            f"✅ Zone **{channel.name}** archivée.", ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /zones-actives
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="zones-actives",
        description="[STAFF] Liste toutes les zones dynamiques actuellement ouvertes."
    )
    @app_commands.default_permissions(manage_channels=True)
    async def zones_actives(self, interaction: discord.Interaction):
        actives = [z for z in self.data["zones"] if not z.get("archivee")]

        if not actives:
            await interaction.response.send_message(
                "Aucune zone dynamique active.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📍 Zones Dynamiques Actives ({len(actives)})",
            color=COULEURS["or_ancien"]
        )
        for zone in actives[:10]:
            embed.add_field(
                name=zone["channel_nom"],
                value=(
                    f"<#{zone['channel_id']}>\n"
                    f"Secteur : {zone['secteur']} · Accès : {zone['factions']}\n"
                    f"Créée le {zone['creation'][:10]} par {zone['createur']}"
                ),
                inline=False
            )
        embed.set_footer(text="⸻ Infernum Aeterna · Gestion des Zones ⸻")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Zones(bot))
