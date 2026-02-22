"""
INFERNUM AETERNA — Cog Aptitudes (Système Reiryoku)
Gestion des aptitudes raciales par faction.

Commandes :
  /aptitudes           — Dashboard budget 霊力 + aptitudes débloquées
  /voie                — Arbre complet d'une Voie
  /aptitude-info       — Détail narratif d'une aptitude
  /aptitude-debloquer  — Dépenser du 霊力 pour débloquer
  /aptitude-retirer    — Retirer une aptitude (remboursement)
  /aptitude-attribuer  — [STAFF] Forcer un déblocage
  /aptitude-reset      — [STAFF] Réinitialiser toutes les aptitudes
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from config import COULEURS
from cogs.construction import trouver_channel
from utils.json_store import JsonStore
from data.aptitudes import (
    VOIES_PAR_FACTION, VOIES_INDEX, APTITUDES_INDEX, APTITUDE_VOIE,
    get_aptitude, get_voie, voies_pour_faction,
    budget_reiryoku, reiryoku_depense, peut_debloquer, peut_retirer, est_sur_budget,
)
from data.aptitudes.constants import (
    REIRYOKU_PAR_RANG, COULEURS_FACTION, EMOJI_FACTION,
    EMOJI_PALIER, NOM_PALIER,
)

PERSONNAGES_FILE = "data/personnages.json"
APTITUDES_WEB_URL = "https://bambougra28-oss.github.io/botbleach/web/aptitudes.html"


# ══════════════════════════════════════════════════════════════════════════════
#  AUTOCOMPLETE
# ══════════════════════════════════════════════════════════════════════════════

def _get_perso(cog, user_id: int) -> dict | None:
    """Récupère le personnage d'un joueur depuis le cog Personnage."""
    perso_cog = cog.bot.cogs.get("Personnage")
    if not perso_cog:
        return None
    return perso_cog.personnages.get(str(user_id))


async def _autocomplete_voie(interaction: discord.Interaction, current: str):
    """Autocomplete filtré par faction du joueur."""
    cog = interaction.client.cogs.get("Aptitudes")
    if not cog:
        return []
    perso = _get_perso(cog, interaction.user.id)
    faction = perso.get("faction") if perso else None
    choices = []
    factions = [faction] if faction else VOIES_PAR_FACTION.keys()
    for f in factions:
        for voie in VOIES_PAR_FACTION.get(f, []):
            label = f"{voie['kanji']} {voie['nom']} — {voie['sous_titre']}"
            if current.lower() in label.lower() or current.lower() in voie["id"]:
                choices.append(app_commands.Choice(name=label[:100], value=voie["id"]))
    return choices[:25]


async def _autocomplete_debloquer(interaction: discord.Interaction, current: str):
    """N'affiche que les aptitudes débloquables pour le joueur."""
    cog = interaction.client.cogs.get("Aptitudes")
    if not cog:
        return []
    perso = _get_perso(cog, interaction.user.id)
    if not perso or not perso.get("faction"):
        return []
    faction = perso["faction"]
    rang = perso.get("rang_cle", "")
    debloquees = perso.get("aptitudes", {}).get("debloquees", [])
    choices = []
    for voie in VOIES_PAR_FACTION.get(faction, []):
        for apt in voie["aptitudes"]:
            if apt["id"] in debloquees:
                continue
            ok, _ = peut_debloquer(apt["id"], debloquees, rang, faction)
            if not ok:
                continue
            label = f"{EMOJI_PALIER[apt['palier']]} {apt['nom']} ({apt['kanji']}) — {apt['cout']}霊力"
            if current.lower() in label.lower() or current.lower() in apt["id"]:
                choices.append(app_commands.Choice(name=label[:100], value=apt["id"]))
    return choices[:25]


async def _autocomplete_retirer(interaction: discord.Interaction, current: str):
    """N'affiche que les aptitudes actuellement débloquées."""
    cog = interaction.client.cogs.get("Aptitudes")
    if not cog:
        return []
    perso = _get_perso(cog, interaction.user.id)
    if not perso:
        return []
    debloquees = perso.get("aptitudes", {}).get("debloquees", [])
    choices = []
    for apt_id in debloquees:
        apt = APTITUDES_INDEX.get(apt_id)
        if not apt:
            continue
        label = f"{EMOJI_PALIER[apt['palier']]} {apt['nom']} ({apt['kanji']})"
        if current.lower() in label.lower() or current.lower() in apt_id:
            choices.append(app_commands.Choice(name=label[:100], value=apt_id))
    return choices[:25]


async def _autocomplete_info(interaction: discord.Interaction, current: str):
    """Toutes les aptitudes, préfixées par faction."""
    choices = []
    for faction, voies in VOIES_PAR_FACTION.items():
        prefix = EMOJI_FACTION.get(faction, "")
        for voie in voies:
            for apt in voie["aptitudes"]:
                label = f"{prefix} {apt['nom']} ({apt['kanji']})"
                if current.lower() in label.lower() or current.lower() in apt["id"]:
                    choices.append(app_commands.Choice(name=label[:100], value=apt["id"]))
    return choices[:25]


async def _autocomplete_attribuer(interaction: discord.Interaction, current: str):
    """Toutes les aptitudes pour le staff."""
    return await _autocomplete_info(interaction, current)


# ══════════════════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════════════════

class Aptitudes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _perso_store(self):
        """Accède au store du cog Personnage."""
        perso_cog = self.bot.cogs.get("Personnage")
        return perso_cog if perso_cog else None

    def _get_aptitudes(self, perso: dict) -> dict:
        """Retourne le sous-dict aptitudes, le crée si absent."""
        if "aptitudes" not in perso:
            perso["aptitudes"] = {"debloquees": [], "reiryoku_bonus": 0}
        return perso["aptitudes"]

    async def _sauvegarder(self):
        """Sauvegarde via le cog Personnage."""
        perso_cog = self._perso_store()
        if perso_cog:
            await perso_cog._sauvegarder()

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitudes — Dashboard
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitudes", description="Affiche le dashboard Reiryoku et aptitudes d'un personnage.")
    @app_commands.describe(membre="Le membre (défaut : vous)")
    async def aptitudes_cmd(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        cible = membre or interaction.user
        perso = _get_perso(self, cible.id)

        if not perso or not perso.get("faction") or not perso.get("valide"):
            await interaction.response.send_message(
                f"❌ Aucun personnage validé pour {cible.mention}.", ephemeral=True
            )
            return

        faction = perso["faction"]
        rang = perso.get("rang_cle", "")
        apt_data = self._get_aptitudes(perso)
        debloquees = apt_data.get("debloquees", [])
        bonus = apt_data.get("reiryoku_bonus", 0)

        budget = budget_reiryoku(rang, bonus)
        depense = reiryoku_depense(debloquees)
        restant = budget - depense
        sur_budget = depense > budget

        couleur = COULEURS_FACTION.get(faction, COULEURS["or_ancien"])
        emoji_f = EMOJI_FACTION.get(faction, "")

        embed = discord.Embed(
            title=f"霊力 Reiryoku — {perso.get('nom_perso', '?')}",
            color=couleur,
        )
        embed.set_author(name=cible.display_name, icon_url=cible.display_avatar.url)

        # Budget
        barre_pct = min(int(depense / budget * 10), 10) if budget > 0 else 0
        barre = "█" * barre_pct + "░" * (10 - barre_pct)
        budget_txt = f"`{barre}` **{depense}** / {budget} 霊力"
        if sur_budget:
            budget_txt += "\n⚠️ **Sur-budget** — aptitudes en excès"
        embed.add_field(name="Budget Reiryoku", value=budget_txt, inline=False)

        # Aptitudes par Voie
        voies = voies_pour_faction(faction)
        for voie in voies:
            apts_voie = [a for a in voie["aptitudes"] if a["id"] in debloquees]
            total_voie = len(voie["aptitudes"])
            if apts_voie:
                lignes = []
                for a in apts_voie:
                    lignes.append(f"{EMOJI_PALIER[a['palier']]} {a['nom']} ({a['kanji']})")
                val = "\n".join(lignes)
            else:
                val = "*Aucune*"
            embed.add_field(
                name=f"{voie['kanji']} {voie['nom']} — {len(apts_voie)}/{total_voie}",
                value=val,
                inline=True,
            )

        embed.set_footer(text=f"⸻ Infernum Aeterna · {emoji_f} {faction.capitalize()} · {len(debloquees)} aptitude{'s' if len(debloquees) != 1 else ''} ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /voie — Arbre d'une Voie
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="voie", description="Affiche l'arbre complet d'une Voie.")
    @app_commands.describe(voie="La Voie à consulter")
    @app_commands.autocomplete(voie=_autocomplete_voie)
    async def voie_cmd(self, interaction: discord.Interaction, voie: str):
        voie_data = get_voie(voie)
        if not voie_data:
            await interaction.response.send_message("❌ Voie inconnue.", ephemeral=True)
            return

        # Récupérer les aptitudes du joueur (optionnel, pour marquage)
        perso = _get_perso(self, interaction.user.id)
        debloquees = set()
        if perso:
            debloquees = set(perso.get("aptitudes", {}).get("debloquees", []))

        couleur = voie_data.get("couleur", COULEURS["or_ancien"])
        embed = discord.Embed(
            title=f"{voie_data['kanji']} {voie_data['nom']} — {voie_data['sous_titre']}",
            description=voie_data["description"],
            color=couleur,
        )

        for apt in voie_data["aptitudes"]:
            est_debloque = apt["id"] in debloquees
            marqueur = "✅" if est_debloque else "🔒"
            palier_label = f"{EMOJI_PALIER[apt['palier']]} P{apt['palier']} — {NOM_PALIER[apt['palier']]}"

            # Description abrégée (première phrase)
            desc = apt["description"]
            premiere_phrase = desc.split(".")[0] + "." if "." in desc else desc[:120]

            prereqs_txt = ""
            if apt["prereqs"]:
                noms = []
                for pid in apt["prereqs"]:
                    p = APTITUDES_INDEX.get(pid)
                    noms.append(p["nom"] if p else pid)
                prereqs_txt = f"\n*Prérequis : {', '.join(noms)}*"

            rang_txt = ""
            if apt.get("rang_min"):
                rang_txt = f"\n*Rang minimum : {apt['rang_min']}*"

            embed.add_field(
                name=f"{marqueur} {apt['nom']} ({apt['kanji']}) — {palier_label} · {apt['cout']}霊力",
                value=f"{premiere_phrase}{prereqs_txt}{rang_txt}",
                inline=False,
            )

        # Lien web
        voie_web_id = voie_data['id'].split('_', 1)[1] if '_' in voie_data['id'] else voie_data['id']
        web_frag = f"#{voie_data['faction']}/{voie_web_id}"
        embed.add_field(name="\u200b", value=f"🌐 [Voir l'arbre interactif]({APTITUDES_WEB_URL}{web_frag})", inline=False)

        embed.set_footer(text=f"⸻ Infernum Aeterna · {voie_data['faction'].capitalize()} ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitude-info — Détail narratif
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitude-info", description="Affiche le détail narratif d'une aptitude.")
    @app_commands.describe(aptitude="L'aptitude à consulter")
    @app_commands.autocomplete(aptitude=_autocomplete_info)
    async def aptitude_info(self, interaction: discord.Interaction, aptitude: str):
        apt = get_aptitude(aptitude)
        if not apt:
            await interaction.response.send_message("❌ Aptitude inconnue.", ephemeral=True)
            return

        voie = APTITUDE_VOIE.get(aptitude)
        faction = voie["faction"] if voie else "?"
        couleur = COULEURS_FACTION.get(faction, COULEURS["or_ancien"])

        embed = discord.Embed(
            title=f"{apt['kanji']} {apt['nom']}",
            description=apt["description"],
            color=couleur,
        )

        # Méta
        embed.add_field(
            name="Palier",
            value=f"{EMOJI_PALIER[apt['palier']]} P{apt['palier']} — {NOM_PALIER[apt['palier']]}",
            inline=True,
        )
        embed.add_field(name="Coût", value=f"{apt['cout']} 霊力", inline=True)
        if voie:
            embed.add_field(
                name="Voie",
                value=f"{voie['kanji']} {voie['nom']}",
                inline=True,
            )

        # Prérequis
        if apt["prereqs"]:
            noms = []
            for pid in apt["prereqs"]:
                p = APTITUDES_INDEX.get(pid)
                noms.append(f"{p['nom']} ({p['kanji']})" if p else pid)
            embed.add_field(name="Prérequis", value="\n".join(noms), inline=False)

        # Condition RP
        if apt.get("condition_rp"):
            embed.add_field(name="Condition RP", value=f"*{apt['condition_rp']}*", inline=False)

        # Rang minimum
        if apt.get("rang_min"):
            embed.add_field(name="Rang minimum", value=apt["rang_min"], inline=True)

        # Lien web
        if voie:
            voie_web_id = voie['id'].split('_', 1)[1] if '_' in voie['id'] else voie['id']
            embed.add_field(name="\u200b", value=f"🌐 [Voir sur le web]({APTITUDES_WEB_URL}#{faction}/{voie_web_id})", inline=False)

        embed.set_footer(text=f"⸻ Infernum Aeterna · {EMOJI_FACTION.get(faction, '')} {faction.capitalize()} ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitude-debloquer — Dépenser du Reiryoku
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitude-debloquer", description="Dépensez du 霊力 pour débloquer une aptitude.")
    @app_commands.describe(aptitude="L'aptitude à débloquer")
    @app_commands.autocomplete(aptitude=_autocomplete_debloquer)
    async def aptitude_debloquer(self, interaction: discord.Interaction, aptitude: str):
        perso = _get_perso(self, interaction.user.id)
        if not perso or not perso.get("valide") or not perso.get("faction"):
            await interaction.response.send_message("❌ Aucun personnage validé.", ephemeral=True)
            return

        faction = perso["faction"]
        rang = perso.get("rang_cle", "")
        apt_data = self._get_aptitudes(perso)
        debloquees = apt_data["debloquees"]

        ok, raison = peut_debloquer(aptitude, debloquees, rang, faction)
        if not ok:
            await interaction.response.send_message(f"❌ {raison}", ephemeral=True)
            return

        apt = get_aptitude(aptitude)
        debloquees.append(aptitude)
        await self._sauvegarder()

        budget = budget_reiryoku(rang, apt_data.get("reiryoku_bonus", 0))
        depense = reiryoku_depense(debloquees)

        embed = discord.Embed(
            title=f"✅ {apt['kanji']} {apt['nom']} — Débloquée",
            description=apt["description"][:300],
            color=COULEURS_FACTION.get(faction, COULEURS["or_ancien"]),
        )
        embed.add_field(
            name="Budget",
            value=f"**{depense}** / {budget} 霊力 ({budget - depense} restant)",
            inline=False,
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Aptitudes ⸻")
        await interaction.response.send_message(embed=embed)

        # Narration automatique pour P3
        if apt["palier"] == 3:
            cog_narrateur = self.bot.cogs.get("Narrateur")
            if cog_narrateur:
                voie = APTITUDE_VOIE.get(aptitude)
                voie_nom = f"{voie['kanji']} {voie['nom']}" if voie else "?"
                details = (
                    f"Personnage : {perso.get('nom_perso', '?')}\n"
                    f"Faction : {faction}\n"
                    f"Aptitude P3 : {apt['kanji']} {apt['nom']}\n"
                    f"Voie : {voie_nom}\n"
                    f"Description : {apt['description'][:200]}"
                )
                await cog_narrateur.narration_rang_auto(interaction.guild, details)

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitude-retirer — Remboursement
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitude-retirer", description="Retire une aptitude et récupère le 霊力.")
    @app_commands.describe(aptitude="L'aptitude à retirer")
    @app_commands.autocomplete(aptitude=_autocomplete_retirer)
    async def aptitude_retirer(self, interaction: discord.Interaction, aptitude: str):
        perso = _get_perso(self, interaction.user.id)
        if not perso or not perso.get("valide"):
            await interaction.response.send_message("❌ Aucun personnage validé.", ephemeral=True)
            return

        apt_data = self._get_aptitudes(perso)
        debloquees = apt_data["debloquees"]

        ok, raison = peut_retirer(aptitude, debloquees)
        if not ok:
            await interaction.response.send_message(f"❌ {raison}", ephemeral=True)
            return

        apt = get_aptitude(aptitude)
        debloquees.remove(aptitude)
        await self._sauvegarder()

        rang = perso.get("rang_cle", "")
        budget = budget_reiryoku(rang, apt_data.get("reiryoku_bonus", 0))
        depense = reiryoku_depense(debloquees)

        await interaction.response.send_message(
            f"✅ **{apt['kanji']} {apt['nom']}** retirée. "
            f"+{apt['cout']} 霊力 récupéré. Budget : **{depense}** / {budget} 霊力.",
            ephemeral=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitude-attribuer [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitude-attribuer", description="[STAFF] Force le déblocage d'une aptitude.")
    @app_commands.describe(membre="Le membre ciblé", aptitude="L'aptitude à attribuer")
    @app_commands.autocomplete(aptitude=_autocomplete_attribuer)
    @app_commands.default_permissions(manage_messages=True)
    async def aptitude_attribuer(
        self, interaction: discord.Interaction,
        membre: discord.Member, aptitude: str,
    ):
        perso = _get_perso(self, membre.id)
        if not perso or not perso.get("valide"):
            await interaction.response.send_message(f"❌ Aucun personnage validé pour {membre.mention}.", ephemeral=True)
            return

        apt = get_aptitude(aptitude)
        if not apt:
            await interaction.response.send_message("❌ Aptitude inconnue.", ephemeral=True)
            return

        apt_data = self._get_aptitudes(perso)
        if aptitude in apt_data["debloquees"]:
            await interaction.response.send_message("❌ Aptitude déjà débloquée.", ephemeral=True)
            return

        apt_data["debloquees"].append(aptitude)
        await self._sauvegarder()

        await interaction.response.send_message(
            f"✅ **{apt['kanji']} {apt['nom']}** attribuée à **{perso.get('nom_perso', '?')}** ({membre.mention}).",
            ephemeral=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /aptitude-reset [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="aptitude-reset", description="[STAFF] Réinitialise toutes les aptitudes d'un membre.")
    @app_commands.describe(membre="Le membre ciblé")
    @app_commands.default_permissions(manage_messages=True)
    async def aptitude_reset(self, interaction: discord.Interaction, membre: discord.Member):
        perso = _get_perso(self, membre.id)
        if not perso:
            await interaction.response.send_message(f"❌ Aucun personnage pour {membre.mention}.", ephemeral=True)
            return

        apt_data = self._get_aptitudes(perso)
        nb = len(apt_data.get("debloquees", []))
        apt_data["debloquees"] = []
        apt_data["reiryoku_bonus"] = 0
        await self._sauvegarder()

        await interaction.response.send_message(
            f"✅ **{nb}** aptitude{'s' if nb != 1 else ''} réinitialisée{'s' if nb != 1 else ''} pour "
            f"**{perso.get('nom_perso', '?')}** ({membre.mention}).",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Aptitudes(bot))
