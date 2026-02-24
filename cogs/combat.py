"""
INFERNUM AETERNA — Cog Combat
- /combat          — initie un fil de combat
- /tour            — signale la fin d'un tour
- /clore-combat    — clôture + résumé + narration optionnelle
- /combats-actifs  — liste des combats en cours [STAFF]
- Archivage automatique des fils inactifs depuis 7 jours (task loop)
- Mise à jour automatique des stats de personnage après clôture
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import asyncio, re
from datetime import datetime, timezone, timedelta

from config import COULEURS
from utils.json_store import JsonStore

COMBATS_FILE = "data/combats_actifs.json"



class Combat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(COMBATS_FILE)
        self.combats_actifs = self._store.data
        self.boucle_archivage.start()

    def cog_unload(self):
        self.boucle_archivage.cancel()

    # ══════════════════════════════════════════════════════════════════════════
    #  BOUCLE — archivage automatique des fils inactifs (>7j sans /tour)
    # ══════════════════════════════════════════════════════════════════════════

    @tasks.loop(hours=12)
    async def boucle_archivage(self):
        maintenant = datetime.now(timezone.utc)
        for combat_id, combat in list(self.combats_actifs.items()):
            if combat.get("statut") != "actif":
                continue
            evenements = combat.get("evenements", [])
            if evenements:
                dernier_ts = evenements[-1].get("timestamp", combat.get("debut", ""))
            else:
                dernier_ts = combat.get("debut", "")
            try:
                dernier = datetime.fromisoformat(dernier_ts.replace("Z", "+00:00"))
                if dernier.tzinfo is None:
                    dernier = dernier.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            if (maintenant - dernier) > timedelta(days=7):
                thread = self.bot.get_channel(int(combat_id))
                if thread and isinstance(thread, discord.Thread):
                    embed = discord.Embed(
                        description=(
                            "「 Ce combat a sombré dans le silence. "
                            "Inactif depuis plus de sept jours, il est désormais archivé. 」"
                        ),
                        color=0x1A1A1A
                    )
                    embed.set_footer(text="⸻ Archivage automatique · Infernum Aeterna ⸻")
                    try:
                        await thread.send(embed=embed)
                        await thread.edit(archived=True, locked=False)
                    except Exception:
                        pass
                combat["statut"] = "archive_auto"
                combat["archive_auto"] = maintenant.isoformat()
        await self._store.save()

    @boucle_archivage.before_loop
    async def before_archivage(self):
        await self.bot.wait_until_ready()

    # ══════════════════════════════════════════════════════════════════════════
    #  CRÉATION D'UN FIL DE COMBAT
    # ══════════════════════════════════════════════════════════════════════════

    async def creer_fil_combat(
        self,
        interaction: discord.Interaction,
        adversaire_mention: str,
        titre: str,
        contexte: str = ""
    ):
        guild = interaction.guild
        channel = interaction.channel

        # Résolution de l'adversaire par mention ou nom exact
        adversaire = None
        match = re.match(r"<@!?(\d+)>", adversaire_mention.strip())
        if match:
            uid = int(match.group(1))
            adversaire = guild.get_member(uid)
        else:
            # Fallback : correspondance exacte sur display_name ou name
            nom_cherche = adversaire_mention.strip().lower()
            for member in guild.members:
                if member.display_name.lower() == nom_cherche or member.name.lower() == nom_cherche:
                    adversaire = member
                    break

        if not adversaire:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Adversaire introuvable : **{adversaire_mention}**.\n"
                    f"Utilisez une @mention ou le nom exact du membre.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Adversaire introuvable : **{adversaire_mention}**.",
                    ephemeral=True
                )
            return

        initiateur = interaction.user

        try:
            thread = await channel.create_thread(
                name=f"⚔️ {titre}",
                type=discord.ChannelType.public_thread,
                reason=f"Combat : {titre}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Impossible de créer un fil dans ce channel.", ephemeral=True
            )
            return

        # Calcul Puissance Spirituelle
        from data.aptitudes import puissance_spirituelle, palier_combat
        cog_perso = self.bot.cogs.get("Personnage")
        ps_init, ps_adv = 1, 1
        if cog_perso:
            perso_init = cog_perso.personnages.get(str(initiateur.id), {})
            perso_adv = cog_perso.personnages.get(str(adversaire.id), {})
            ps_init = puissance_spirituelle(perso_init.get("points", 0))
            ps_adv = puissance_spirituelle(perso_adv.get("points", 0))
        palier = palier_combat(ps_init, ps_adv)

        combat_id = str(thread.id)
        self.combats_actifs[combat_id] = {
            "titre":           titre,
            "initiateur_id":   initiateur.id,
            "initiateur_nom":  initiateur.display_name,
            "adversaire_id":   adversaire.id,
            "adversaire_nom":  adversaire.display_name,
            "contexte":        contexte,
            "tour":            0,
            "statut":          "actif",
            "channel_id":      channel.id,
            "thread_id":       thread.id,
            "debut":           datetime.now(timezone.utc).isoformat(),
            "evenements":      [],
            "ps_initiateur":   ps_init,
            "ps_adversaire":   ps_adv,
            "palier":          palier["nom"],
        }
        await self._store.save()

        # Texte palier pour l'embed
        ecart = abs(ps_init - ps_adv)
        palier_txt = (
            f"**{initiateur.display_name}** : {ps_init:,} PS\n"
            f"**{adversaire.display_name}** : {ps_adv:,} PS\n"
            f"{palier['kanji']} **{palier['nom']}** (écart : {ecart:,})\n"
            f"Éveil : {palier['effet_p1']} · Maîtrise : {palier['effet_p2']} · Transcendance : {palier['effet_p3']}"
        )

        embed = discord.Embed(
            title=f"⚔️ {titre}",
            description=(
                f"**Initiateur :** {initiateur.mention}\n"
                f"**Adversaire :** {adversaire.mention}\n\n"
                + (f"*{contexte}*\n\n" if contexte else "")
                + "「 Que la lutte commence. Le Narrateur observe. 」"
            ),
            color=COULEURS["rouge_chaine"]
        )
        embed.add_field(name="📊 Tour",    value="0 · Pré-combat",  inline=True)
        embed.add_field(name="📌 Statut",  value="⚔️ Actif",        inline=True)
        embed.add_field(name="⚡ Puissance Spirituelle", value=palier_txt, inline=False)
        embed.set_footer(text="Utilisez /tour pour signaler votre tour · /clore-combat pour terminer")

        view = ViewCombatActif(combat_id)
        msg = await thread.send(embed=embed, view=view)
        await msg.pin()

        await thread.add_user(initiateur)
        await thread.add_user(adversaire)

        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"✅ Fil de combat créé : {thread.mention}", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"✅ Fil de combat créé : {thread.mention}", ephemeral=True
            )

    # ══════════════════════════════════════════════════════════════════════════
    #  /combat
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="combat", description="Initie un fil de combat avec un adversaire.")
    @app_commands.describe(
        adversaire="Le membre avec qui combattre",
        titre="Titre narratif du combat",
        contexte="Contexte narratif (optionnel)"
    )
    async def combat_cmd(
        self,
        interaction: discord.Interaction,
        adversaire: discord.Member,
        titre: str,
        contexte: Optional[str] = ""
    ):
        await self.creer_fil_combat(interaction, adversaire.mention, titre, contexte or "")

    # ══════════════════════════════════════════════════════════════════════════
    #  /tour
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="tour", description="Signale la fin de votre tour dans ce fil de combat.")
    @app_commands.describe(action="Résumé de votre action ce tour")
    async def tour(self, interaction: discord.Interaction, action: str):
        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "❌ Cette commande doit être utilisée dans un fil de combat.", ephemeral=True
            )
            return

        combat_id = str(thread.id)
        if combat_id not in self.combats_actifs:
            await interaction.response.send_message("❌ Aucun combat enregistré pour ce fil.", ephemeral=True)
            return

        combat = self.combats_actifs[combat_id]
        if combat["statut"] != "actif":
            await interaction.response.send_message("❌ Ce combat est terminé.", ephemeral=True)
            return

        combat["tour"] += 1
        combat["evenements"].append({
            "tour":      combat["tour"],
            "joueur":    interaction.user.display_name,
            "action":    action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await self._store.save()

        embed = discord.Embed(
            description=f"**Tour {combat['tour']}** · {interaction.user.mention}\n\n*{action}*",
            color=COULEURS["or_pale"]
        )
        embed.set_footer(text="⸻ En attente de réponse ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /clore-combat
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="clore-combat", description="Clôture le combat dans ce fil.")
    @app_commands.describe(
        vainqueur="Le vainqueur du combat",
        conclusion="Conclusion narrative (optionnel)"
    )
    async def clore_combat(
        self,
        interaction: discord.Interaction,
        vainqueur: Optional[discord.Member] = None,
        conclusion: Optional[str] = None
    ):
        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "❌ Cette commande doit être dans un fil de combat.", ephemeral=True
            )
            return

        combat_id = str(thread.id)
        if combat_id not in self.combats_actifs:
            await interaction.response.send_message("❌ Aucun combat enregistré.", ephemeral=True)
            return

        combat = self.combats_actifs[combat_id]
        combat["statut"]    = "termine"
        combat["vainqueur"] = vainqueur.display_name if vainqueur else "Indéterminé"
        combat["conclusion"]= conclusion or ""
        combat["fin"]       = datetime.now(timezone.utc).isoformat()
        await self._store.save()

        # Mettre à jour les stats des personnages
        await self._maj_stats_personnages(combat, vainqueur)

        embed = discord.Embed(
            title=f"⚔️ Combat Terminé · {combat['titre']}",
            description=(
                f"**Tours joués :** {combat['tour']}\n"
                f"**Vainqueur :** {vainqueur.mention if vainqueur else 'Indéterminé'}\n\n"
                + (f"*{conclusion}*\n\n" if conclusion else "")
                + "「 Le Narrateur a observé ce duel. 」"
            ),
            color=COULEURS["or_ancien"]
        )
        await interaction.response.defer()
        await thread.send(embed=embed)

        view = ViewDemandeNarration(combat)
        await thread.send(
            "Voulez-vous que le Narrateur consigne ce combat dans les Chroniques Vivantes ?",
            view=view
        )

        await asyncio.sleep(2)
        await thread.edit(archived=True, locked=True)

    # ── Mise à jour des stats de personnage après combat ──────────────────────

    async def _maj_stats_personnages(self, combat: dict, vainqueur: Optional[discord.Member]):
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return
        persos = cog_perso.personnages
        participants = [
            str(combat.get("initiateur_id")),
            str(combat.get("adversaire_id")),
        ]
        vainqueur_id = str(vainqueur.id) if vainqueur else None

        for uid in participants:
            if uid and uid in persos:
                persos[uid]["combats_total"] = persos[uid].get("combats_total", 0) + 1
                if uid == vainqueur_id:
                    persos[uid]["combats_gagnes"] = persos[uid].get("combats_gagnes", 0) + 1
        await cog_perso._sauvegarder()

    # ══════════════════════════════════════════════════════════════════════════
    #  /combats-actifs [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="combats-actifs", description="[STAFF] Liste les combats en cours.")
    @app_commands.default_permissions(manage_messages=True)
    async def combats_actifs_cmd(self, interaction: discord.Interaction):
        actifs = {k: v for k, v in self.combats_actifs.items() if v.get("statut") == "actif"}
        if not actifs:
            await interaction.response.send_message("Aucun combat actif.", ephemeral=True)
            return

        embed = discord.Embed(title=f"⚔️ Combats Actifs ({len(actifs)})", color=COULEURS["rouge_chaine"])
        for cid, combat in list(actifs.items())[:10]:
            dernier_tour = "—"
            if combat.get("evenements"):
                dernier_tour = combat["evenements"][-1].get("timestamp", "—")[:10]
            embed.add_field(
                name=combat["titre"],
                value=(
                    f"{combat['initiateur_nom']} vs {combat['adversaire_nom']}\n"
                    f"Tour **{combat['tour']}** · Dernier : {dernier_tour}\n"
                    f"<#{combat['thread_id']}>"
                ),
                inline=False
            )
        embed.set_footer(text="Les fils inactifs depuis 7 jours sont archivés automatiquement.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ══════════════════════════════════════════════════════════════════════════════
#  VUES
# ══════════════════════════════════════════════════════════════════════════════

class ViewCombatActif(discord.ui.View):
    def __init__(self, combat_id: str):
        super().__init__(timeout=None)
        self.combat_id = combat_id

    @discord.ui.button(label="📋 Infos Combat", style=discord.ButtonStyle.secondary, custom_id="infos_combat")
    async def infos(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog_combat = interaction.client.cogs.get("Combat")
        combat = cog_combat.combats_actifs.get(str(interaction.channel.id)) if cog_combat else None
        if not combat:
            await interaction.response.send_message("Aucune donnée.", ephemeral=True)
            return
        embed = discord.Embed(title=f"📋 {combat['titre']}", color=COULEURS["gris_acier"])
        embed.add_field(name="Tour",       value=str(combat["tour"]),  inline=True)
        embed.add_field(name="Statut",     value=combat["statut"],     inline=True)
        embed.add_field(name="Initiateur", value=combat["initiateur_nom"], inline=True)
        embed.add_field(name="Adversaire", value=combat["adversaire_nom"], inline=True)
        if combat.get("contexte"):
            embed.add_field(name="Contexte", value=combat["contexte"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ViewDemandeNarration(discord.ui.View):
    def __init__(self, combat: dict):
        super().__init__(timeout=300)
        self.combat = combat

    @discord.ui.button(label="✍️ Narrer ce combat", style=discord.ButtonStyle.primary)
    async def narrer(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog_narrateur = interaction.client.cogs.get("Narrateur")
        if not cog_narrateur:
            await interaction.response.send_message("❌ Narrateur indisponible.", ephemeral=True)
            return

        await interaction.response.defer()
        button.disabled = True
        await interaction.message.edit(view=self)
        resume = (
            f"Combat : {self.combat['titre']}\n"
            f"Combattants : {self.combat['initiateur_nom']} vs {self.combat['adversaire_nom']}\n"
            f"Tours joués : {self.combat['tour']}\n"
            f"Vainqueur : {self.combat.get('vainqueur', 'indéterminé')}\n"
            f"Contexte : {self.combat.get('contexte', '')}\n"
            f"Conclusion : {self.combat.get('conclusion', '')}\n"
            f"Événements : {', '.join(e['action'][:80] for e in self.combat.get('evenements', [])[:5])}"
        )
        texte = await cog_narrateur.generer_narration("combat", resume, "longue")
        embed  = cog_narrateur._construire_embed("combat", texte)

        guild = interaction.guild
        dest  = cog_narrateur._trouver_channel_narrateur(guild)
        if dest:
            await dest.send(embed=embed)
            await interaction.followup.send(f"✅ Narration publiée dans {dest.mention}.", ephemeral=True)
        else:
            await interaction.followup.send(embed=embed)

    @discord.ui.button(label="❌ Non merci", style=discord.ButtonStyle.secondary)
    async def annuler(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Narration ignorée.", view=None)


async def setup(bot):
    await bot.add_cog(Combat(bot))
