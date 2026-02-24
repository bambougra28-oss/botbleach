"""
INFERNUM AETERNA — Cog Personnage
- /personnage       — dashboard d'un personnage
- /fiche-soumettre  — soumettre sa fiche (modal)
- /fiche-valider    — [STAFF] valider une fiche
- /rang-attribuer   — [STAFF] changer le rang
- /points-ajouter   — [STAFF] modifier les points
- /classement       — leaderboard global ou par faction
- /historique       — fiche narrative complète d'un personnage
- /chercher-perso   — recherche par nom ou faction
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timezone

from config import COULEURS
from cogs.construction import trouver_channel
from utils.json_store import JsonStore

PERSONNAGES_FILE = "data/personnages.json"



RANGS_POINTS = {
    "shinigami": [
        ("gakusei",               500,   "🎓 学生 Gakusei"),
        ("shinigami_asserm",     1200,   "☯️ 死神 Shinigami"),
        ("yonseki",              2500,   "🗡️ 四席 Yonseki"),
        ("sanseki",              4000,   "⚔️ 三席 Sanseki"),
        ("fukutaicho",           6500,   "🎖️ 副隊長 Fukutaichō"),
        ("taicho",               8500,   "⭐ 隊長 Taichō"),
        ("sotaicho",            10000,   "👑 総隊長 Sōtaichō"),
    ],
    "togabito": [
        ("zainin",                500,   "💀 罪人 Zainin"),
        ("togabito_damne",       2000,   "🩸 咎人 Togabito"),
        ("tan_togabito",         4500,   "🔗 鍛咎人 Tan-Togabito"),
        ("ko_togabito",          7500,   "⛓️ 古咎人 Ko-Togabito"),
        ("gokuo",               10000,   "👑 獄王 Gokuō"),
    ],
    "arrancar": [
        ("horo",                  500,   "◽ 虚 Horō"),
        ("gillian",              1000,   "🟢 最下大虚 Gillian"),
        ("adjuchas",             2000,   "🔵 中級大虚 Adjuchas"),
        ("vasto_lorde",          3500,   "🟣 最上大虚 Vasto Lorde"),
        ("numeros",              5000,   "○ 数字持ち Números"),
        ("fraccion",             6500,   "◇ 従属官 Fracción"),
        ("privaron_espada",      8000,   "◈ 十刃落ち Privaron Espada"),
        ("espada",               9000,   "💠 十刃 Espada"),
        ("rey",                 10000,   "👑 王 Rey"),
    ],
    "quincy": [
        ("minarai",               500,   "∘ 見習い Minarai"),
        ("quincy_confirme",      1500,   "∗ 滅却師 Quincy"),
        ("jagdarmee",            3000,   "⊕ 狩猟部隊 Jagdarmee"),
        ("sternritter",          6000,   "✧ 星十字騎士団 Sternritter"),
        ("schutzstaffel",        8500,   "✦ 親衛隊 Schutzstaffel"),
        ("seitei",              10000,   "👑 聖帝 Seitei"),
    ],
}

EMOJI_FACTION = {
    "shinigami": "死神",
    "togabito":  "咎人",
    "arrancar":  "破面",
    "quincy":    "滅却師",
}


async def _autocomplete_rang(interaction: discord.Interaction, current: str):
    """Autocomplete dynamique : filtre les rangs selon la faction déjà sélectionnée."""
    faction = None
    for opt in interaction.namespace.__dict__.values():
        if isinstance(opt, str) and opt in RANGS_POINTS:
            faction = opt
            break
    choices = []
    factions_a_parcourir = [faction] if faction else RANGS_POINTS.keys()
    for f in factions_a_parcourir:
        for cle, pts, label in RANGS_POINTS.get(f, []):
            if current.lower() in cle.lower() or current.lower() in label.lower():
                display = f"{label} ({pts:,} pts)" if faction else f"[{f[:4].upper()}] {label}"
                choices.append(app_commands.Choice(name=display[:100], value=cle))
    return choices[:25]


class Personnage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(PERSONNAGES_FILE)
        self.personnages = self._store.data

    async def _sauvegarder(self):
        self._store.data = self.personnages
        await self._store.save()

    def _get_or_create(self, membre: discord.Member) -> dict:
        uid = str(membre.id)
        if uid not in self.personnages:
            self.personnages[uid] = {
                "discord_id": membre.id,
                "discord_nom": membre.display_name,
                "nom_perso": None,
                "faction": None,
                "rang_cle": None,
                "rang_label": None,
                "points": 0,
                "valide": False,
                "date_validation": None,
                "historique_rangs": [],
                "combats_gagnes": 0,
                "combats_total": 0,
                "notes_staff": "",
                "fiche_contenu": "",
            }
        return self.personnages[uid]

    # ══════════════════════════════════════════════════════════════════════════
    #  /personnage
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="personnage", description="Affiche le dashboard d'un personnage.")
    @app_commands.describe(membre="Le membre (défaut : vous)")
    async def personnage(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        cible = membre or interaction.user
        uid = str(cible.id)

        if uid not in self.personnages or not self.personnages[uid].get("nom_perso"):
            await interaction.response.send_message(
                f"❌ Aucun personnage enregistré pour {cible.mention}.", ephemeral=True
            )
            return

        perso = self.personnages[uid]
        faction  = perso.get("faction", "—")
        rang_label = perso.get("rang_label", "—")
        points   = perso.get("points", 0)
        valide   = perso.get("valide", False)
        barre    = _barre_progression(faction, points)

        couleur_faction = {
            "shinigami": COULEURS["blanc_seireitei"],
            "togabito":  COULEURS["pourpre_infernal"],
            "arrancar":  COULEURS["gris_sable"],
            "quincy":    COULEURS["bleu_abyssal"],
        }.get(faction, COULEURS["or_ancien"])

        embed = discord.Embed(title=f"{'✅' if valide else '⏳'} {perso['nom_perso']}", color=couleur_faction)
        embed.set_author(name=cible.display_name, icon_url=cible.display_avatar.url)
        embed.add_field(name="Faction", value=f"{EMOJI_FACTION.get(faction, '')} {faction.capitalize()}" if faction != "—" else "—", inline=True)
        embed.add_field(name="Rang",    value=rang_label or "—", inline=True)
        embed.add_field(name="Points",  value=f"**{points:,}** pts", inline=True)
        # Puissance Spirituelle
        from data.aptitudes import puissance_spirituelle
        ps = puissance_spirituelle(points)
        embed.add_field(name="⚡ Puissance Spirituelle", value=f"**{ps:,}** PS", inline=True)
        embed.add_field(name="Statut",  value="✅ Validé" if valide else "⏳ En attente", inline=True)
        if barre:
            embed.add_field(name="Progression", value=barre, inline=False)
        stats = f"Combats : **{perso.get('combats_total', 0)}** total · **{perso.get('combats_gagnes', 0)}** victoires"
        embed.add_field(name="Statistiques", value=stats, inline=False)
        # Reiryoku — aptitudes
        try:
            from data.aptitudes import budget_reiryoku, reiryoku_depense
            rang_cle = perso.get("rang_cle", "")
            apt_data = perso.get("aptitudes", {})
            debloquees = apt_data.get("debloquees", [])
            bonus_rei = apt_data.get("reiryoku_bonus", 0)
            budget = budget_reiryoku(rang_cle, bonus_rei)
            depense = reiryoku_depense(debloquees)
            if budget > 0:
                rei_txt = f"**{depense}** / {budget} 霊力 ⸻ {len(debloquees)} aptitude{'s' if len(debloquees) != 1 else ''}"
                if depense > budget:
                    rei_txt += " ⚠️ *sur-budget*"
                embed.add_field(name="霊力 Reiryoku", value=rei_txt, inline=False)
        except Exception:
            pass
        if valide and perso.get("date_validation"):
            embed.add_field(name="Validé le", value=perso["date_validation"][:10], inline=True)
        embed.set_footer(text="⸻ Infernum Aeterna · Registre des Âmes ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /modele-fiche
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="modele-fiche", description="Reçois le modèle de fiche personnage en DM.")
    async def modele_fiche(self, interaction: discord.Interaction):
        """Envoie le modèle de fiche complet en DM au demandeur."""
        modele_texte = (
            "```\n"
            "═══════════════════════════════\n"
            "   FICHE PERSONNAGE · INFERNUM AETERNA\n"
            "═══════════════════════════════\n"
            "Nom du personnage :\n"
            "Faction : [Shinigami / Togabito / Arrancar / Quincy]\n"
            "Rang souhaité :\n"
            "Âge apparent :\n\n"
            "HISTOIRE (300 mots minimum) :\n"
            "[Votre texte]\n\n"
            "APPARENCE :\n"
            "[Description physique]\n\n"
            "APTITUDES (3 maximum selon rang) :\n"
            "1.\n"
            "2.\n"
            "3.\n\n"
            "OBJECTIF NARRATIF :\n"
            "[Ce que votre personnage cherche dans le contexte de la Fissure]\n"
            "═══════════════════════════════\n"
            "```"
        )
        embed_modele = discord.Embed(
            title="📋 Modèle de Fiche Personnage",
            description=modele_texte,
            color=COULEURS["blanc_seireitei"]
        )
        embed_modele.set_footer(text="⸻ Infernum Aeterna · Soumission via /fiche-soumettre ⸻")

        embed_instructions = discord.Embed(
            title="📥 Comment soumettre",
            color=COULEURS["or_pale"]
        )
        embed_instructions.add_field(
            name="Étape 1", value="Copiez le modèle et remplissez chaque section.", inline=False
        )
        embed_instructions.add_field(
            name="Étape 2", value="Histoire : minimum 300 mots. Soyez précis sur les aptitudes.", inline=False
        )
        embed_instructions.add_field(
            name="Étape 3",
            value="Allez dans `📥・soumission-de-fiche` et tapez `/fiche-soumettre`.",
            inline=False
        )
        embed_instructions.add_field(
            name="Délai", value="Validation staff sous 48h. Notification en DM.", inline=False
        )

        try:
            await interaction.user.send(embed=embed_modele)
            await interaction.user.send(embed=embed_instructions)
            await interaction.response.send_message(
                "✅ Le modèle de fiche t'a été envoyé en DM !", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                embeds=[embed_modele, embed_instructions], ephemeral=True
            )

    # ══════════════════════════════════════════════════════════════════════════
    #  /fiche-soumettre
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="fiche-soumettre", description="Soumettez votre fiche personnage.")
    async def fiche_soumettre(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ModalFiche())

    # ══════════════════════════════════════════════════════════════════════════
    #  /fiche-valider [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="fiche-valider", description="[STAFF] Valide la fiche d'un membre.")
    @app_commands.describe(
        membre="Le membre à valider", nom_perso="Nom du personnage",
        faction="Faction", rang="Rang initial",
        points_initiaux="Points de départ", notes="Notes internes"
    )
    @app_commands.choices(faction=[
        app_commands.Choice(name="Shinigami", value="shinigami"),
        app_commands.Choice(name="Togabito",  value="togabito"),
        app_commands.Choice(name="Arrancar",  value="arrancar"),
        app_commands.Choice(name="Quincy",    value="quincy"),
    ])
    @app_commands.autocomplete(rang=_autocomplete_rang)
    @app_commands.default_permissions(manage_roles=True)
    async def fiche_valider(
        self, interaction: discord.Interaction,
        membre: discord.Member, nom_perso: str, faction: str, rang: str,
        points_initiaux: Optional[int] = 0, notes: Optional[str] = ""
    ):
        await interaction.response.defer(ephemeral=True)

        # Validation cohérence faction/rang
        rangs_valides = {cle for cle, _, _ in RANGS_POINTS.get(faction, [])}
        if rang not in rangs_valides:
            await interaction.followup.send(
                f"❌ Le rang **{rang}** n'existe pas pour la faction **{faction}**.\n"
                f"Rangs valides : {', '.join(rangs_valides)}",
                ephemeral=True
            )
            return

        perso = self._get_or_create(membre)
        perso.update({
            "nom_perso": nom_perso, "faction": faction,
            "rang_cle": rang, "rang_label": _label_rang(faction, rang),
            "points": points_initiaux, "valide": True,
            "date_validation": datetime.now(timezone.utc).isoformat(),
            "notes_staff": notes or "",
        })
        perso["historique_rangs"].append({
            "rang": rang, "date": datetime.now(timezone.utc).isoformat(), "raison": "Validation initiale"
        })
        await self._sauvegarder()

        from cogs.construction import charger_roles
        roles_ids = charger_roles()

        # Retirer En Attente, ajouter faction + rang + validé
        # NOTE : ne PAS retirer le rôle voyageur — 26 channels (PORTAIL, CHRONIQUES,
        # ADMINISTRATION, COMMUNAUTÉ, CHRONIQUES VIVANTES) dépendent de ce rôle
        # pour leur visibilité, même après validation du personnage.
        role_attente = interaction.guild.get_role(roles_ids.get("en_attente", 0))
        if role_attente and role_attente in membre.roles:
            await membre.remove_roles(role_attente)

        roles_a_ajouter = []
        for cle in [faction, rang, "personnage_valide"]:
            role = interaction.guild.get_role(roles_ids.get(cle, 0))
            if role:
                roles_a_ajouter.append(role)
        if roles_a_ajouter:
            await membre.add_roles(*roles_a_ajouter, reason=f"Validation : {nom_perso}")

        # Narration automatique
        cog_narrateur = self.bot.cogs.get("Narrateur")
        if cog_narrateur:
            resume = f"Nom : {nom_perso}\nFaction : {faction}\nRang initial : {_label_rang(faction, rang)}\nFiche : {perso.get('fiche_contenu', '')[:300]}"
            await cog_narrateur.narration_validation_auto(interaction.guild, resume, nom_perso)

        # Publier dans fiches-validées
        ch_fiches = trouver_channel(interaction.guild, "fiches-validees")
        if ch_fiches:
            embed = discord.Embed(
                title=f"✅ {nom_perso} · Fiche Validée",
                description=perso.get("fiche_contenu", "")[:1800] or "*Fiche non disponible.*",
                color=COULEURS["or_ancien"]
            )
            embed.add_field(name="Faction", value=faction.capitalize(), inline=True)
            embed.add_field(name="Rang",    value=_label_rang(faction, rang) or rang, inline=True)
            embed.set_author(name=membre.display_name, icon_url=membre.display_avatar.url)
            embed.set_footer(text=f"Validé le {datetime.now(timezone.utc).strftime('%d/%m/%Y')}")
            await ch_fiches.send(embed=embed)

        # Notifier le joueur en DM
        try:
            await membre.send(
                embed=discord.Embed(
                    title="✅ Votre fiche a été validée !",
                    description=(
                        f"Bienvenue dans les Chroniques, **{nom_perso}**.\n\n"
                        f"Faction : **{faction.capitalize()}** · Rang : **{_label_rang(faction, rang)}**\n"
                        f"Points initiaux : **{points_initiaux:,}**\n\n"
                        f"Vous pouvez maintenant accéder aux zones RP de votre faction.\n"
                        f"「 Que votre histoire commence. 」"
                    ),
                    color=COULEURS["or_ancien"]
                )
            )
        except discord.Forbidden:
            pass  # DM désactivés

        await interaction.followup.send(f"✅ Fiche de **{nom_perso}** ({membre.mention}) validée.", ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  /points-ajouter [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="points-ajouter", description="[STAFF] Ajoute ou retire des points.")
    @app_commands.describe(membre="Le membre ciblé", montant="Points (négatif pour retirer)", raison="Raison")
    @app_commands.default_permissions(manage_roles=True)
    async def points_ajouter(
        self, interaction: discord.Interaction,
        membre: discord.Member, montant: int, raison: Optional[str] = "Attribution manuelle"
    ):
        uid = str(membre.id)
        if uid not in self.personnages:
            await interaction.response.send_message("❌ Aucun personnage pour ce membre.", ephemeral=True)
            return

        perso = self.personnages[uid]
        ancien = perso["points"]
        perso["points"] = max(0, ancien + montant)
        await self._sauvegarder()

        signe = "+" if montant >= 0 else ""
        await interaction.response.send_message(
            f"✅ **{perso['nom_perso']}** : {ancien:,} → **{perso['points']:,}** pts ({signe}{montant})\n*{raison}*",
            ephemeral=True
        )
        await self._verifier_montee_rang(interaction, membre, perso)

    # ══════════════════════════════════════════════════════════════════════════
    #  /rang-attribuer [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="rang-attribuer", description="[STAFF] Attribue un rang à un personnage.")
    @app_commands.describe(membre="Le membre ciblé", rang="Rang à attribuer", raison="Raison")
    @app_commands.autocomplete(rang=_autocomplete_rang)
    @app_commands.default_permissions(manage_roles=True)
    async def rang_attribuer(
        self, interaction: discord.Interaction,
        membre: discord.Member, rang: str, raison: Optional[str] = "Attribution manuelle"
    ):
        uid = str(membre.id)
        if uid not in self.personnages:
            await interaction.response.send_message("❌ Aucun personnage pour ce membre.", ephemeral=True)
            return

        perso = self.personnages[uid]
        faction = perso.get("faction")
        ancien_rang = perso.get("rang_label", "—")
        perso["rang_cle"]   = rang
        perso["rang_label"] = _label_rang(faction, rang) or rang
        perso["historique_rangs"].append({
            "rang": rang, "date": datetime.now(timezone.utc).isoformat(), "raison": raison
        })
        await self._sauvegarder()

        from cogs.construction import charger_roles
        roles_ids = charger_roles()
        guild = interaction.guild

        # Retirer anciens rangs faction
        for cle, _, _ in RANGS_POINTS.get(faction, []):
            role = guild.get_role(roles_ids.get(cle, 0))
            if role and role in membre.roles:
                await membre.remove_roles(role)

        # Attribuer nouveau rang
        nouveau_role = guild.get_role(roles_ids.get(rang, 0))
        if nouveau_role:
            await membre.add_roles(nouveau_role, reason=raison)

        await interaction.response.send_message(
            f"✅ Rang de **{perso['nom_perso']}** : {ancien_rang} → **{perso['rang_label']}**\n*{raison}*",
            ephemeral=True
        )

        # Narration automatique
        cog_narrateur = self.bot.cogs.get("Narrateur")
        if cog_narrateur:
            details = (
                f"Personnage : {perso['nom_perso']}\nFaction : {faction}\n"
                f"Ancien rang : {ancien_rang}\nNouveau rang : {perso['rang_label']}\nRaison : {raison}"
            )
            await cog_narrateur.narration_rang_auto(guild, details)

        # Notifier le joueur en DM
        try:
            await membre.send(
                embed=discord.Embed(
                    title="⬆️ Votre rang a évolué !",
                    description=(
                        f"**{perso['nom_perso']}**, votre rang vient d'être mis à jour.\n\n"
                        f"{ancien_rang} → **{perso['rang_label']}**\n"
                        f"*{raison}*"
                    ),
                    color=COULEURS["or_ancien"]
                )
            )
        except discord.Forbidden:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  /classement — NOUVEAU
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="classement", description="Affiche le classement des personnages par points.")
    @app_commands.describe(faction="Filtrer par faction (optionnel)")
    @app_commands.choices(faction=[
        app_commands.Choice(name="Toutes les factions", value="tous"),
        app_commands.Choice(name="Shinigami", value="shinigami"),
        app_commands.Choice(name="Togabito",  value="togabito"),
        app_commands.Choice(name="Arrancar",  value="arrancar"),
        app_commands.Choice(name="Quincy",    value="quincy"),
    ])
    async def classement(self, interaction: discord.Interaction, faction: str = "tous"):
        valides = [
            p for p in self.personnages.values()
            if p.get("valide") and p.get("nom_perso")
            and (faction == "tous" or p.get("faction") == faction)
        ]
        valides.sort(key=lambda p: p.get("points", 0), reverse=True)
        top = valides[:10]

        if not top:
            await interaction.response.send_message("Aucun personnage validé pour ce filtre.", ephemeral=True)
            return

        titre = "🏆 Classement Global" if faction == "tous" else f"🏆 Classement · {EMOJI_FACTION.get(faction, '')} {faction.capitalize()}"
        embed = discord.Embed(title=titre, color=COULEURS["or_ancien"])

        from data.aptitudes import puissance_spirituelle

        medailles = ["🥇", "🥈", "🥉"] + ["▸"] * 7
        lignes = []
        for i, p in enumerate(top):
            emoji_f = EMOJI_FACTION.get(p.get("faction", ""), "")
            pts = p.get("points", 0)
            ps = puissance_spirituelle(pts)
            lignes.append(
                f"{medailles[i]} **{p['nom_perso']}** {emoji_f}\n"
                f"  {p.get('rang_label', '—')} · **{pts:,}** pts · ⚡ {ps:,} PS"
            )

        embed.description = "\n".join(lignes)

        # Stats globales
        total_valides = len([p for p in self.personnages.values() if p.get("valide")])
        embed.set_footer(text=f"⸻ {total_valides} personnages validés au total ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /historique — NOUVEAU
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="historique", description="Affiche l'historique narratif complet d'un personnage.")
    @app_commands.describe(membre="Le membre (défaut : vous)")
    async def historique(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        cible = membre or interaction.user
        uid = str(cible.id)

        if uid not in self.personnages or not self.personnages[uid].get("nom_perso"):
            await interaction.response.send_message("❌ Aucun personnage pour ce membre.", ephemeral=True)
            return

        perso = self.personnages[uid]
        faction = perso.get("faction", "—")

        couleur = {
            "shinigami": COULEURS["blanc_seireitei"],
            "togabito":  COULEURS["pourpre_infernal"],
            "arrancar":  COULEURS["gris_sable"],
            "quincy":    COULEURS["bleu_abyssal"],
        }.get(faction, COULEURS["or_ancien"])

        embed = discord.Embed(
            title=f"📜 Chroniques de {perso['nom_perso']}",
            color=couleur
        )
        embed.set_author(name=cible.display_name, icon_url=cible.display_avatar.url)

        # Identité
        embed.add_field(
            name="Identité",
            value=(
                f"Faction : {EMOJI_FACTION.get(faction, '')} **{faction.capitalize()}**\n"
                f"Rang actuel : **{perso.get('rang_label', '—')}**\n"
                f"Points : **{perso.get('points', 0):,}**\n"
                f"Validé le : {perso.get('date_validation', '—')[:10] if perso.get('date_validation') else '—'}"
            ),
            inline=False
        )

        # Historique des rangs
        hist_rangs = perso.get("historique_rangs", [])
        if hist_rangs:
            rangs_txt = "\n".join(
                f"`{r.get('date', '')[:10]}` → **{_label_rang(faction, r.get('rang', '')) or r.get('rang', '?')}** · *{r.get('raison', '')}*"
                for r in hist_rangs[-6:]  # 6 derniers
            )
            embed.add_field(name=f"📈 Historique des Rangs ({len(hist_rangs)} total)", value=rangs_txt, inline=False)

        # Statistiques de combat
        embed.add_field(
            name="⚔️ Combat",
            value=(
                f"Total : **{perso.get('combats_total', 0)}**\n"
                f"Victoires : **{perso.get('combats_gagnes', 0)}**\n"
                f"Défaites : **{max(0, perso.get('combats_total', 0) - perso.get('combats_gagnes', 0))}**"
            ),
            inline=True
        )

        # Barre de progression
        barre = _barre_progression(faction, perso.get("points", 0))
        if barre:
            embed.add_field(name="📊 Progression", value=barre, inline=False)

        embed.set_footer(text="⸻ Infernum Aeterna · Chroniques des Âmes ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /chercher-perso — NOUVEAU
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="chercher-perso", description="Recherche un personnage par nom ou faction.")
    @app_commands.describe(
        nom="Nom du personnage (partiel accepté)",
        faction="Filtrer par faction"
    )
    @app_commands.choices(faction=[
        app_commands.Choice(name="Toutes", value="tous"),
        app_commands.Choice(name="Shinigami", value="shinigami"),
        app_commands.Choice(name="Togabito",  value="togabito"),
        app_commands.Choice(name="Arrancar",  value="arrancar"),
        app_commands.Choice(name="Quincy",    value="quincy"),
    ])
    async def chercher_perso(
        self, interaction: discord.Interaction,
        nom: Optional[str] = None, faction: str = "tous"
    ):
        if not nom and faction == "tous":
            await interaction.response.send_message("Précisez un nom ou une faction.", ephemeral=True)
            return

        resultats = []
        for p in self.personnages.values():
            if not p.get("valide") or not p.get("nom_perso"):
                continue
            if faction != "tous" and p.get("faction") != faction:
                continue
            if nom and nom.lower() not in p.get("nom_perso", "").lower():
                continue
            resultats.append(p)

        if not resultats:
            await interaction.response.send_message("❌ Aucun personnage trouvé.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Résultats ({len(resultats)} trouvé{'s' if len(resultats) > 1 else ''})",
            color=COULEURS["gris_acier"]
        )
        for p in resultats[:8]:
            f = p.get("faction", "—")
            embed.add_field(
                name=f"{EMOJI_FACTION.get(f, '')} {p['nom_perso']}",
                value=(
                    f"Rang : {p.get('rang_label', '—')}\n"
                    f"Points : **{p.get('points', 0):,}**\n"
                    f"Joueur : <@{p.get('discord_id', 0)}>"
                ),
                inline=True
            )
        if len(resultats) > 8:
            embed.set_footer(text=f"… et {len(resultats) - 8} autre(s). Affinez votre recherche.")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  RELATIONS INTER-PERSONNAGES
    # ══════════════════════════════════════════════════════════════════════════

    TYPES_RELATION = {
        "rival":        "⚔️ Rival",
        "allie":        "🤝 Allié",
        "mentor":       "📖 Mentor",
        "disciple":     "🎓 Disciple",
        "ennemi_jure":  "💀 Ennemi juré",
        "lien_sang":    "🩸 Lien de sang",
        "camarade":     "🌸 Camarade",
        "amour":        "💜 Lien d'âme",
    }

    @app_commands.command(name="relation-declarer", description="Déclare une relation RP avec un autre personnage.")
    @app_commands.describe(
        membre="Le joueur avec qui déclarer la relation",
        type_relation="Type de relation",
        description="Description de la relation (optionnel)"
    )
    @app_commands.choices(type_relation=[
        app_commands.Choice(name=label, value=cle)
        for cle, label in {
            "rival": "⚔️ Rival", "allie": "🤝 Allié", "mentor": "📖 Mentor",
            "disciple": "🎓 Disciple", "ennemi_jure": "💀 Ennemi juré",
            "lien_sang": "🩸 Lien de sang", "camarade": "🌸 Camarade", "amour": "💜 Lien d'âme",
        }.items()
    ])
    async def relation_declarer(
        self, interaction: discord.Interaction,
        membre: discord.Member, type_relation: str,
        description: Optional[str] = None,
    ):
        uid = str(interaction.user.id)
        uid_cible = str(membre.id)

        if uid == uid_cible:
            await interaction.response.send_message("❌ Vous ne pouvez pas déclarer une relation avec vous-même.", ephemeral=True)
            return
        if uid not in self.personnages or not self.personnages[uid].get("valide"):
            await interaction.response.send_message("❌ Vous n'avez pas de personnage validé.", ephemeral=True)
            return
        if uid_cible not in self.personnages or not self.personnages[uid_cible].get("valide"):
            await interaction.response.send_message("❌ Ce membre n'a pas de personnage validé.", ephemeral=True)
            return

        perso = self.personnages[uid]
        perso_cible = self.personnages[uid_cible]

        # Initialiser la liste de relations si absente
        if "relations" not in perso:
            perso["relations"] = []

        # Vérifier si la relation existe déjà
        for rel in perso["relations"]:
            if rel.get("cible_id") == membre.id and rel.get("type") == type_relation:
                await interaction.response.send_message("❌ Cette relation existe déjà.", ephemeral=True)
                return

        # Limiter à 10 relations
        if len(perso["relations"]) >= 10:
            await interaction.response.send_message("❌ Maximum 10 relations par personnage.", ephemeral=True)
            return

        label = self.TYPES_RELATION.get(type_relation, type_relation)
        perso["relations"].append({
            "cible_id": membre.id,
            "cible_nom": perso_cible.get("nom_perso", membre.display_name),
            "type": type_relation,
            "label": label,
            "description": description or "",
            "date": datetime.now(timezone.utc).isoformat(),
        })
        await self._sauvegarder()

        embed = discord.Embed(
            title=f"{label} · Lien Déclaré",
            description=(
                f"**{perso['nom_perso']}** a déclaré une relation avec **{perso_cible['nom_perso']}**.\n\n"
                + (f"*{description}*" if description else "")
            ),
            color=COULEURS["or_ancien"]
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Relations ⸻")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="relations", description="Affiche les relations d'un personnage.")
    @app_commands.describe(membre="Le membre (défaut : vous)")
    async def relations(self, interaction: discord.Interaction, membre: Optional[discord.Member] = None):
        cible = membre or interaction.user
        uid = str(cible.id)

        if uid not in self.personnages or not self.personnages[uid].get("valide"):
            await interaction.response.send_message("❌ Aucun personnage validé.", ephemeral=True)
            return

        perso = self.personnages[uid]
        rels = perso.get("relations", [])

        if not rels:
            await interaction.response.send_message(
                f"**{perso['nom_perso']}** n'a aucune relation déclarée.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🔗 Relations de {perso['nom_perso']}",
            color=COULEURS["or_ancien"]
        )
        for rel in rels[:10]:
            val = f"Avec **{rel.get('cible_nom', '?')}**"
            if rel.get("description"):
                val += f"\n*{rel['description'][:100]}*"
            embed.add_field(name=rel.get("label", "?"), value=val, inline=True)
        embed.set_footer(text="⸻ Infernum Aeterna · Relations ⸻")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="relation-retirer", description="Retire une relation avec un personnage.")
    @app_commands.describe(membre="Le joueur dont retirer la relation")
    async def relation_retirer(self, interaction: discord.Interaction, membre: discord.Member):
        uid = str(interaction.user.id)
        if uid not in self.personnages:
            await interaction.response.send_message("❌ Aucun personnage.", ephemeral=True)
            return

        perso = self.personnages[uid]
        rels = perso.get("relations", [])
        nouvelles = [r for r in rels if r.get("cible_id") != membre.id]

        if len(nouvelles) == len(rels):
            await interaction.response.send_message("❌ Aucune relation trouvée avec ce membre.", ephemeral=True)
            return

        perso["relations"] = nouvelles
        await self._sauvegarder()
        await interaction.response.send_message(
            f"✅ Relation(s) avec **{membre.display_name}** retirée(s).", ephemeral=True
        )

    # ── Vérification montée en rang ────────────────────────────────────────────
    async def _verifier_montee_rang(self, interaction, membre, perso):
        faction = perso.get("faction")
        points  = perso.get("points", 0)
        rangs   = RANGS_POINTS.get(faction, [])
        rang_actuel = perso.get("rang_cle")
        rang_merite = rang_actuel

        for cle, seuil, label in rangs:
            if points >= seuil:
                rang_merite = cle

        if rang_merite and rang_merite != rang_actuel:
            label_nouveau = _label_rang(faction, rang_merite)
            embed = discord.Embed(
                title="⬆️ Montée en Rang Disponible",
                description=(
                    f"**{perso['nom_perso']}** a atteint **{points:,}** points.\n"
                    f"Rang actuel : {perso.get('rang_label', rang_actuel)}\n"
                    f"Rang mérité : **{label_nouveau}**\n\n"
                    f"Utilisez `/rang-attribuer` pour confirmer."
                ),
                color=COULEURS["or_ancien"]
            )
            ch_staff = trouver_channel(interaction.guild, "validations") or trouver_channel(interaction.guild, "discussions-staff")
            if ch_staff:
                await ch_staff.send(embed=embed)


# ══════════════════════════════════════════════════════════════════════════════
#  MODAL FICHE
# ══════════════════════════════════════════════════════════════════════════════

class ModalFiche(discord.ui.Modal, title="Soumettre une Fiche Personnage"):
    nom_perso = discord.ui.TextInput(label="Nom du personnage", placeholder="Nom complet", max_length=80)
    faction   = discord.ui.TextInput(label="Faction", placeholder="Shinigami / Togabito / Arrancar / Quincy", max_length=20)
    contenu   = discord.ui.TextInput(
        label="Fiche complète (modèle rempli)",
        style=discord.TextStyle.paragraph,
        placeholder="Collez ici votre fiche remplie.",
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Validation faction
        faction_input = self.faction.value.lower().strip()
        factions_valides = {"shinigami", "togabito", "arrancar", "quincy"}
        if faction_input not in factions_valides:
            await interaction.response.send_message(
                f"❌ Faction invalide : **{self.faction.value}**.\n"
                f"Factions acceptées : {', '.join(sorted(factions_valides))}.",
                ephemeral=True
            )
            return

        perso_cog = interaction.client.cogs.get("Personnage")
        if perso_cog:
            perso = perso_cog._get_or_create(interaction.user)
            perso["nom_perso"]      = self.nom_perso.value
            perso["faction"]        = faction_input
            perso["fiche_contenu"]  = self.contenu.value
            perso["valide"]         = False
            await perso_cog._sauvegarder()

        from cogs.construction import charger_roles
        roles_ids = charger_roles()
        rid = roles_ids.get("en_attente")
        if rid:
            role = interaction.guild.get_role(rid)
            if role:
                await interaction.user.add_roles(role)

        # Poster dans soumission-de-fiche + notifier staff en DM
        embed_fiche = discord.Embed(
            title=f"📋 Nouvelle Fiche · {self.nom_perso.value}",
            description=self.contenu.value[:2000],
            color=COULEURS["or_pale"]
        )
        embed_fiche.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed_fiche.add_field(name="Faction demandée", value=self.faction.value, inline=True)
        embed_fiche.add_field(name="Discord", value=interaction.user.mention, inline=True)

        ch_soumission = trouver_channel(interaction.guild, "soumission-de-fiche") or trouver_channel(interaction.guild, "validations")
        if ch_soumission:
            await ch_soumission.send(embed=embed_fiche)

        # DM au staff avec rôle Gardien des Portes ou Émissaire
        guild = interaction.guild
        notif_embed = discord.Embed(
            title="📥 Nouvelle fiche à valider",
            description=(
                f"**Joueur :** {interaction.user.mention} ({interaction.user})\n"
                f"**Personnage :** {self.nom_perso.value}\n"
                f"**Faction :** {self.faction.value}\n\n"
                f"Consultez le canal de soumission pour valider."
            ),
            color=COULEURS["or_pale"]
        )
        staff_role_ids = set()
        for cle_staff in ("gardien_des_portes", "emissaire"):
            rid = roles_ids.get(cle_staff)
            if rid:
                staff_role_ids.add(rid)
        if staff_role_ids:
            for membre_guild in guild.members:
                if any(r.id in staff_role_ids for r in membre_guild.roles):
                    try:
                        await membre_guild.send(embed=notif_embed)
                    except discord.Forbidden:
                        pass

        await interaction.response.send_message(
            "✅ Votre fiche a été soumise. Le staff a été notifié et vous reviendra sous 48h.",
            ephemeral=True
        )


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _label_rang(faction: Optional[str], rang_cle: str) -> Optional[str]:
    if not faction:
        return rang_cle
    for cle, _, label in RANGS_POINTS.get(faction, []):
        if cle == rang_cle:
            return label
    return rang_cle


def _barre_progression(faction: Optional[str], points: int) -> Optional[str]:
    rangs = RANGS_POINTS.get(faction)
    if not rangs:
        return None
    rang_actuel_label = None
    prochain_seuil = None
    prochain_rang_label = None
    seuil_actuel = 0
    for i, (cle, seuil, label) in enumerate(rangs):
        if points >= seuil:
            rang_actuel_label = label
            seuil_actuel = seuil
            if i + 1 < len(rangs):
                prochain_seuil = rangs[i + 1][1]
                prochain_rang_label = rangs[i + 1][2]
    if not prochain_seuil:
        return f"{rang_actuel_label} · **Rang Maximum** ✦"
    progress = points - seuil_actuel
    total = prochain_seuil - seuil_actuel
    pct = min(int(progress / total * 10), 10)
    barre = "█" * pct + "░" * (10 - pct)
    return f"`{barre}` {points:,}/{prochain_seuil:,} → **{prochain_rang_label}**"


async def setup(bot):
    await bot.add_cog(Personnage(bot))
