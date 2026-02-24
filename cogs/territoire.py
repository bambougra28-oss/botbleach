"""
INFERNUM AETERNA — Cog Territoire
Système de guerre de factions / contrôle territorial.
Les zones contestées accumulent de l'influence en fonction de l'activité RP
des joueurs. Quand une faction domine, des bonus narratifs s'activent.

Commandes :
  /territoire            — affiche la carte des territoires (public)
  /influence             — [STAFF] ajuste manuellement l'influence
  /territoire-reset      — [ADMIN] réinitialise la saison
  /territoire-historique — affiche l'historique des changements de dominance
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import logging
from datetime import datetime, timezone, timedelta

from config import COULEURS
from cogs.construction import trouver_channel
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

TERRITOIRE_FILE = "data/territoire.json"

# ── Factions jouables ────────────────────────────────────────────────────────
FACTIONS = ("shinigami", "togabito", "arrancar", "quincy")

FACTION_EMOJI = {
    "shinigami": "🟡",
    "togabito":  "🟣",
    "arrancar":  "⚪",
    "quincy":    "🔵",
}

FACTION_COULEUR = {
    "shinigami": COULEURS["blanc_seireitei"],
    "togabito":  COULEURS["pourpre_infernal"],
    "arrancar":  COULEURS["gris_sable"],
    "quincy":    COULEURS["bleu_abyssal"],
}

# ── Zones contestées ────────────────────────────────────────────────────────
ZONES_CONTESTEES = {
    "no-mans-land":          {"nom": "🌑 No Man's Land",          "categorie": "FRONTIERE"},
    "la-fissure-principale": {"nom": "🔴 La Fissure Principale",  "categorie": "FRONTIERE"},
    "ville-principale":      {"nom": "🏙️ Ville Principale",       "categorie": "MONDE DES VIVANTS"},
    "zones-isolees":         {"nom": "🌲 Zones Isolées",          "categorie": "MONDE DES VIVANTS"},
    "confrontations":        {"nom": "⚔️ Confrontations",         "categorie": "MONDE DES VIVANTS"},
    "combats-de-frontiere":  {"nom": "⚔️ Combats de Frontière",   "categorie": "FRONTIERE"},
}

# Seuil minimal d'avance pour qu'une faction soit déclarée dominante
SEUIL_DOMINANCE = 20

# Cooldown d'influence : 1 gain par joueur par zone toutes les 30 minutes
COOLDOWN_MINUTES = 30

# Nombre minimum de mots dans un message RP pour compter
MIN_MOTS_RP = 50


def _structure_zone_defaut() -> dict:
    """Retourne la structure par défaut d'une zone de territoire."""
    return {
        "influence": {f: 0 for f in FACTIONS},
        "dominante": None,
        "historique": [],
    }


def _structure_defaut() -> dict:
    """Retourne la structure complète par défaut du fichier territoire."""
    return {
        "zones": {cle: _structure_zone_defaut() for cle in ZONES_CONTESTEES},
        "saison": 1,
        "date_debut_saison": datetime.now(timezone.utc).isoformat(),
    }


# ── Barres visuelles ASCII ───────────────────────────────────────────────────

def _barre_influence(valeur: int, maximum: int) -> str:
    """Construit une barre ASCII de 10 blocs proportionnelle au maximum."""
    if maximum <= 0:
        return "░░░░░░░░░░"
    nb_pleins = min(round(valeur / maximum * 10), 10) if valeur > 0 else 0
    return "█" * nb_pleins + "░" * (10 - nb_pleins)


def _calculer_dominante(zone_data: dict) -> Optional[str]:
    """Détermine la faction dominante d'une zone.

    La faction avec le plus d'influence domine à condition d'avoir
    au moins SEUIL_DOMINANCE points d'avance sur la deuxième.
    """
    influence = zone_data.get("influence", {})
    if not influence:
        return None

    classement = sorted(influence.items(), key=lambda x: x[1], reverse=True)

    if len(classement) < 2:
        return None

    premiere_faction, premier_score = classement[0]
    _, second_score = classement[1]

    if premier_score <= 0:
        return None

    if premier_score - second_score >= SEUIL_DOMINANCE:
        return premiere_faction

    return None


# ══════════════════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════════════════

class Territoire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(TERRITOIRE_FILE, default=_structure_defaut())
        self.data = self._store.data

        # Assurer que toutes les zones existent dans les données chargées
        if "zones" not in self.data:
            self.data["zones"] = {}
        for cle in ZONES_CONTESTEES:
            if cle not in self.data["zones"]:
                self.data["zones"][cle] = _structure_zone_defaut()

        if "saison" not in self.data:
            self.data["saison"] = 1
        if "date_debut_saison" not in self.data:
            self.data["date_debut_saison"] = datetime.now(timezone.utc).isoformat()

        # Cooldowns en mémoire : {(user_id, zone_cle): datetime}
        self._cooldowns: dict[tuple[int, str], datetime] = {}

        # Suivi des changements des dernières 24h pour le rapport quotidien
        self._changements_recents: list[dict] = []

        # Lancer la boucle de rapport quotidien
        self.boucle_rapport_territoire.start()

    def cog_unload(self):
        self.boucle_rapport_territoire.cancel()

    async def _sauvegarder(self):
        self._store.data = self.data
        await self._store.save()

    # ══════════════════════════════════════════════════════════════════════════
    #  MÉTHODE PUBLIQUE — utilisable par d'autres cogs
    # ══════════════════════════════════════════════════════════════════════════

    async def ajouter_influence(self, zone_cle: str, faction: str, montant: int, raison: str):
        """Ajoute de l'influence à une faction dans une zone.

        Appelable par les cogs combat/scenes quand des événements se produisent
        dans des zones contestées.
        """
        if zone_cle not in self.data["zones"]:
            log.warning("Territoire: zone inconnue '%s'", zone_cle)
            return
        if faction not in FACTIONS:
            log.warning("Territoire: faction inconnue '%s'", faction)
            return

        zone_data = self.data["zones"][zone_cle]
        ancienne_dominante = zone_data.get("dominante")

        # Appliquer l'influence (ne pas descendre sous 0)
        ancien_score = zone_data["influence"].get(faction, 0)
        zone_data["influence"][faction] = max(0, ancien_score + montant)

        # Recalculer la dominance
        nouvelle_dominante = _calculer_dominante(zone_data)
        zone_data["dominante"] = nouvelle_dominante

        await self._sauvegarder()

        # Vérifier si la dominance a changé
        if nouvelle_dominante != ancienne_dominante and nouvelle_dominante is not None:
            await self._notifier_changement_dominance(
                zone_cle, ancienne_dominante, nouvelle_dominante, raison
            )

        log.info(
            "Territoire: %s %+d influence %s dans %s (%s)",
            faction, montant, raison, zone_cle,
            zone_data["influence"][faction]
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  NOTIFICATION DE CHANGEMENT DE DOMINANCE
    # ══════════════════════════════════════════════════════════════════════════

    async def _notifier_changement_dominance(
        self,
        zone_cle: str,
        ancienne: Optional[str],
        nouvelle: str,
        raison: str,
    ):
        """Annonce un changement de dominance dans flash-evenements et l'historique."""
        zone_info = ZONES_CONTESTEES.get(zone_cle, {})
        zone_nom = zone_info.get("nom", zone_cle)
        emoji = FACTION_EMOJI.get(nouvelle, "")
        couleur = FACTION_COULEUR.get(nouvelle, COULEURS["or_ancien"])

        maintenant = datetime.now(timezone.utc)

        # Enregistrer dans l'historique de la zone
        zone_data = self.data["zones"][zone_cle]
        zone_data["historique"].append({
            "date": maintenant.isoformat(),
            "ancienne": ancienne,
            "nouvelle": nouvelle,
            "raison": raison,
        })
        # Limiter l'historique à 50 entrées par zone
        if len(zone_data["historique"]) > 50:
            zone_data["historique"] = zone_data["historique"][-50:]

        await self._sauvegarder()

        # Suivi pour le rapport quotidien
        self._changements_recents.append({
            "date": maintenant.isoformat(),
            "zone": zone_nom,
            "ancienne": ancienne,
            "nouvelle": nouvelle,
        })

        # Publier dans flash-evenements
        for guild in self.bot.guilds:
            ch = trouver_channel(guild, "flash-evenements")
            if not ch:
                continue

            ancien_texte = ""
            if ancienne:
                ancien_emoji = FACTION_EMOJI.get(ancienne, "")
                ancien_texte = f"\n*Ancienne dominante : {ancien_emoji} {ancienne.capitalize()}*"

            embed = discord.Embed(
                title="🏴 Changement de Dominance Territoriale",
                description=(
                    f"**{zone_nom}** passe sous le contrôle de "
                    f"{emoji} **{nouvelle.capitalize()}** !"
                    f"{ancien_texte}\n\n"
                    f"「 Les lignes de front se redessinent. 」"
                ),
                color=couleur,
                timestamp=maintenant,
            )
            embed.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")
            try:
                await ch.send(embed=embed)
            except discord.HTTPException as e:
                log.error("Territoire: erreur envoi notification dominance : %s", e)

    # ══════════════════════════════════════════════════════════════════════════
    #  LISTENER — tracking d'influence par messages RP
    # ══════════════════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorer les bots
        if message.author.bot:
            return

        # Ignorer les DM
        if not message.guild:
            return

        # Vérifier que le channel correspond à une zone contestée
        channel_name = message.channel.name.lower()
        zone_cle = None
        for cle in ZONES_CONTESTEES:
            if cle in channel_name:
                zone_cle = cle
                break

        if zone_cle is None:
            return

        # Vérifier le nombre de mots (minimum 50 pour compter comme du RP)
        mots = message.content.split()
        if len(mots) < MIN_MOTS_RP:
            return

        # Déterminer la faction de l'auteur via le cog Personnage
        faction = self._obtenir_faction(message.author)
        if not faction:
            return

        # Vérifier le cooldown (30 min par joueur par zone)
        cle_cooldown = (message.author.id, zone_cle)
        maintenant = datetime.now(timezone.utc)

        if cle_cooldown in self._cooldowns:
            dernier_gain = self._cooldowns[cle_cooldown]
            if (maintenant - dernier_gain).total_seconds() < COOLDOWN_MINUTES * 60:
                return

        # Enregistrer le cooldown et ajouter l'influence
        self._cooldowns[cle_cooldown] = maintenant
        await self.ajouter_influence(zone_cle, faction, 1, f"message RP de {message.author}")

    def _obtenir_faction(self, membre: discord.Member) -> Optional[str]:
        """Récupère la faction d'un joueur depuis le cog Personnage."""
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return None

        uid = str(membre.id)
        perso = cog_perso.personnages.get(uid)
        if not perso or not perso.get("valide"):
            return None

        faction = perso.get("faction")
        if faction not in FACTIONS:
            return None

        return faction

    # ══════════════════════════════════════════════════════════════════════════
    #  /territoire — carte publique des territoires
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="territoire",
        description="Affiche la carte des territoires contestés et l'influence des factions."
    )
    async def territoire_cmd(self, interaction: discord.Interaction):
        saison = self.data.get("saison", 1)
        date_debut = self.data.get("date_debut_saison", "")[:10]

        embed = discord.Embed(
            title=f"🗺️ Carte des Territoires · Saison {saison}",
            description=(
                f"*Depuis le {date_debut}*\n"
                f"Seuil de dominance : **{SEUIL_DOMINANCE}** points d'avance\n"
                f"───────────────────────────────────"
            ),
            color=COULEURS["or_ancien"],
        )

        # Regrouper les zones par catégorie
        categories: dict[str, list[str]] = {}
        for cle, info in ZONES_CONTESTEES.items():
            cat = info["categorie"]
            categories.setdefault(cat, []).append(cle)

        # Compteur global de dominance
        dominance_globale: dict[str, int] = {f: 0 for f in FACTIONS}

        for categorie, cles_zones in categories.items():
            bloc = ""
            for zone_cle in cles_zones:
                zone_info = ZONES_CONTESTEES[zone_cle]
                zone_data = self.data["zones"].get(zone_cle, _structure_zone_defaut())
                influence = zone_data.get("influence", {})
                dominante = zone_data.get("dominante")

                if dominante:
                    dominance_globale[dominante] += 1

                # Trouver le maximum pour calibrer les barres
                max_influence = max(influence.values()) if influence.values() else 1
                if max_influence <= 0:
                    max_influence = 1

                # Titre de la zone avec dominante
                if dominante:
                    emoji_dom = FACTION_EMOJI.get(dominante, "")
                    bloc += f"**{zone_info['nom']}** · {emoji_dom} {dominante.capitalize()} domine\n"
                else:
                    bloc += f"**{zone_info['nom']}** · *Contestée*\n"

                # Barres d'influence pour chaque faction
                for faction in FACTIONS:
                    emoji = FACTION_EMOJI[faction]
                    score = influence.get(faction, 0)
                    barre = _barre_influence(score, max_influence)
                    # Mettre en gras si c'est la faction dominante
                    if faction == dominante:
                        bloc += f"  {emoji} **{barre}  {score}**  {faction.capitalize()}\n"
                    else:
                        bloc += f"  {emoji} {barre}  {score}  {faction.capitalize()}\n"

                bloc += "\n"

            # Ajouter le bloc comme champ de l'embed
            embed.add_field(
                name=f"── {categorie} ──",
                value=bloc.strip(),
                inline=False,
            )

        # Résumé global
        zones_total = len(ZONES_CONTESTEES)
        zones_controlees = sum(1 for z in self.data["zones"].values() if z.get("dominante"))
        zones_contestees = zones_total - zones_controlees

        resume_lignes = []
        # Trier les factions par nombre de zones contrôlées
        factions_triees = sorted(dominance_globale.items(), key=lambda x: x[1], reverse=True)
        for faction, nb_zones in factions_triees:
            emoji = FACTION_EMOJI[faction]
            if nb_zones > 0:
                resume_lignes.append(f"{emoji} **{faction.capitalize()}** : {nb_zones} zone{'s' if nb_zones > 1 else ''}")
            else:
                resume_lignes.append(f"{emoji} {faction.capitalize()} : aucune zone")

        resume_lignes.append(f"\n⚔️ Zones contestées : **{zones_contestees}** / {zones_total}")

        embed.add_field(
            name="── BILAN GLOBAL ──",
            value="\n".join(resume_lignes),
            inline=False,
        )

        embed.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /influence — ajustement manuel [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="influence",
        description="[STAFF] Ajuste manuellement l'influence d'une faction dans une zone."
    )
    @app_commands.describe(
        zone="Zone contestée",
        faction="Faction ciblée",
        montant="Points d'influence à ajouter (négatif pour retirer)",
        raison="Raison de l'ajustement",
    )
    @app_commands.choices(
        zone=[
            app_commands.Choice(name=info["nom"], value=cle)
            for cle, info in ZONES_CONTESTEES.items()
        ],
        faction=[
            app_commands.Choice(name=f.capitalize(), value=f)
            for f in FACTIONS
        ],
    )
    @app_commands.default_permissions(manage_messages=True)
    async def influence_cmd(
        self,
        interaction: discord.Interaction,
        zone: str,
        faction: str,
        montant: int,
        raison: str,
    ):
        if zone not in self.data["zones"]:
            await interaction.response.send_message(
                f"❌ Zone inconnue : **{zone}**.", ephemeral=True
            )
            return

        zone_data = self.data["zones"][zone]
        ancien_score = zone_data["influence"].get(faction, 0)
        ancienne_dominante = zone_data.get("dominante")

        # Appliquer (ne pas descendre sous 0)
        zone_data["influence"][faction] = max(0, ancien_score + montant)
        nouveau_score = zone_data["influence"][faction]

        # Recalculer la dominance
        nouvelle_dominante = _calculer_dominante(zone_data)
        zone_data["dominante"] = nouvelle_dominante

        await self._sauvegarder()

        # Notification si dominance change
        if nouvelle_dominante != ancienne_dominante and nouvelle_dominante is not None:
            await self._notifier_changement_dominance(
                zone, ancienne_dominante, nouvelle_dominante,
                f"ajustement staff : {raison}"
            )

        signe = "+" if montant >= 0 else ""
        zone_nom = ZONES_CONTESTEES[zone]["nom"]
        emoji = FACTION_EMOJI.get(faction, "")

        embed = discord.Embed(
            title="📊 Influence Ajustée",
            description=(
                f"**Zone :** {zone_nom}\n"
                f"**Faction :** {emoji} {faction.capitalize()}\n"
                f"**Modification :** {signe}{montant} ({ancien_score} → **{nouveau_score}**)\n"
                f"**Raison :** {raison}\n"
            ),
            color=FACTION_COULEUR.get(faction, COULEURS["or_ancien"]),
        )

        # Afficher la dominance actuelle
        if nouvelle_dominante:
            dom_emoji = FACTION_EMOJI.get(nouvelle_dominante, "")
            embed.add_field(
                name="Dominante",
                value=f"{dom_emoji} {nouvelle_dominante.capitalize()}",
                inline=True,
            )
        else:
            embed.add_field(name="Dominante", value="*Contestée*", inline=True)

        embed.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  /territoire-reset — réinitialisation de saison [ADMIN]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="territoire-reset",
        description="[ADMIN] Réinitialise tous les territoires et lance une nouvelle saison."
    )
    @app_commands.default_permissions(administrator=True)
    async def territoire_reset_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        maintenant = datetime.now(timezone.utc)
        ancienne_saison = self.data.get("saison", 1)

        # Archiver l'état actuel dans l'historique de chaque zone
        for zone_cle, zone_data in self.data["zones"].items():
            dominante = zone_data.get("dominante")
            zone_data["historique"].append({
                "date": maintenant.isoformat(),
                "ancienne": dominante,
                "nouvelle": None,
                "raison": f"Fin de saison {ancienne_saison}, réinitialisation",
            })
            # Limiter l'historique
            if len(zone_data["historique"]) > 50:
                zone_data["historique"] = zone_data["historique"][-50:]

        # Réinitialiser les influences
        for zone_cle in ZONES_CONTESTEES:
            self.data["zones"][zone_cle]["influence"] = {f: 0 for f in FACTIONS}
            self.data["zones"][zone_cle]["dominante"] = None

        # Incrémenter la saison
        self.data["saison"] = ancienne_saison + 1
        self.data["date_debut_saison"] = maintenant.isoformat()

        await self._sauvegarder()

        # Vider les cooldowns et les changements récents
        self._cooldowns.clear()
        self._changements_recents.clear()

        # Publier l'annonce dans flash-evenements
        guild = interaction.guild
        ch_flash = trouver_channel(guild, "flash-evenements")

        embed_annonce = discord.Embed(
            title=f"🔄 Nouvelle Saison Territoriale · Saison {self.data['saison']}",
            description=(
                f"La saison **{ancienne_saison}** est terminée.\n"
                f"Toutes les influences ont été réinitialisées.\n\n"
                f"Les factions repartent à zéro dans la lutte pour le contrôle des "
                f"zones contestées. Chaque message RP, chaque combat, chaque scène "
                f"compte.\n\n"
                f"「 Le monde se réinitialise, mais les cicatrices demeurent. 」"
            ),
            color=COULEURS["or_ancien"],
            timestamp=maintenant,
        )
        embed_annonce.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")

        if ch_flash:
            try:
                await ch_flash.send(embed=embed_annonce)
            except discord.HTTPException as e:
                log.error("Territoire: erreur envoi annonce reset : %s", e)

        await interaction.followup.send(
            f"✅ Saison {ancienne_saison} archivée. "
            f"Saison **{self.data['saison']}** lancée, toutes les influences remises à 0.",
            ephemeral=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /territoire-historique — historique des changements de dominance
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="territoire-historique",
        description="Affiche les derniers changements de dominance territoriale."
    )
    async def territoire_historique_cmd(self, interaction: discord.Interaction):
        # Collecter tous les événements de toutes les zones
        tous_evenements: list[dict] = []
        for zone_cle, zone_data in self.data["zones"].items():
            zone_nom = ZONES_CONTESTEES.get(zone_cle, {}).get("nom", zone_cle)
            for evt in zone_data.get("historique", []):
                tous_evenements.append({
                    "date": evt.get("date", ""),
                    "zone": zone_nom,
                    "ancienne": evt.get("ancienne"),
                    "nouvelle": evt.get("nouvelle"),
                    "raison": evt.get("raison", ""),
                })

        # Trier par date décroissante et prendre les 10 derniers
        tous_evenements.sort(key=lambda x: x["date"], reverse=True)
        derniers = tous_evenements[:10]

        if not derniers:
            await interaction.response.send_message(
                "Aucun changement de dominance enregistré pour cette saison.",
                ephemeral=True,
            )
            return

        saison = self.data.get("saison", 1)
        embed = discord.Embed(
            title=f"📜 Historique Territorial · Saison {saison}",
            color=COULEURS["or_ancien"],
        )

        lignes = []
        for evt in derniers:
            date_str = evt["date"][:10] if evt["date"] else "?"
            heure_str = evt["date"][11:16] if len(evt["date"]) > 16 else ""

            ancienne = evt["ancienne"]
            nouvelle = evt["nouvelle"]

            if nouvelle:
                emoji_new = FACTION_EMOJI.get(nouvelle, "")
                if ancienne:
                    emoji_old = FACTION_EMOJI.get(ancienne, "")
                    transition = f"{emoji_old} {ancienne.capitalize()} → {emoji_new} **{nouvelle.capitalize()}**"
                else:
                    transition = f"*Contestée* → {emoji_new} **{nouvelle.capitalize()}**"
            else:
                # Fin de saison ou perte de dominance
                if ancienne:
                    emoji_old = FACTION_EMOJI.get(ancienne, "")
                    transition = f"{emoji_old} {ancienne.capitalize()} → *Contestée*"
                else:
                    transition = "*Réinitialisation*"

            ligne = f"`{date_str} {heure_str}` **{evt['zone']}**\n  {transition}"
            if evt.get("raison"):
                ligne += f"\n  *{evt['raison'][:80]}*"
            lignes.append(ligne)

        embed.description = "\n\n".join(lignes)
        embed.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")
        await interaction.response.send_message(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  BOUCLE — rapport territorial quotidien (toutes les 24h)
    # ══════════════════════════════════════════════════════════════════════════

    @tasks.loop(hours=24)
    async def boucle_rapport_territoire(self):
        """Publie un résumé quotidien des territoires dans flash-evenements,
        uniquement si des changements ont eu lieu dans les dernières 24h."""

        if not self._changements_recents:
            return

        maintenant = datetime.now(timezone.utc)
        seuil = maintenant - timedelta(hours=24)

        # Filtrer les changements des dernières 24h
        changements_24h = []
        for evt in self._changements_recents:
            try:
                date_evt = datetime.fromisoformat(evt["date"])
                if date_evt.tzinfo is None:
                    date_evt = date_evt.replace(tzinfo=timezone.utc)
                if date_evt >= seuil:
                    changements_24h.append(evt)
            except (ValueError, KeyError):
                continue

        if not changements_24h:
            # Nettoyer les anciens changements
            self._changements_recents.clear()
            return

        # Construire le rapport
        saison = self.data.get("saison", 1)
        embed = discord.Embed(
            title=f"📊 Rapport Territorial Quotidien · Saison {saison}",
            description=f"*{maintenant.strftime('%d/%m/%Y')}*",
            color=COULEURS["or_ancien"],
            timestamp=maintenant,
        )

        # Résumé des changements
        lignes_changements = []
        for evt in changements_24h:
            nouvelle = evt.get("nouvelle")
            ancienne = evt.get("ancienne")
            zone = evt.get("zone", "?")
            if nouvelle:
                emoji_new = FACTION_EMOJI.get(nouvelle, "")
                lignes_changements.append(
                    f"{emoji_new} **{nouvelle.capitalize()}** prend **{zone}**"
                )
            elif ancienne:
                emoji_old = FACTION_EMOJI.get(ancienne, "")
                lignes_changements.append(
                    f"{emoji_old} {ancienne.capitalize()} perd **{zone}**"
                )

        if lignes_changements:
            embed.add_field(
                name=f"Changements ({len(changements_24h)})",
                value="\n".join(lignes_changements[:10]),
                inline=False,
            )

        # État actuel des zones
        dominance_globale: dict[str, int] = {f: 0 for f in FACTIONS}
        for zone_data in self.data["zones"].values():
            dom = zone_data.get("dominante")
            if dom:
                dominance_globale[dom] += 1

        etat_lignes = []
        for faction in FACTIONS:
            emoji = FACTION_EMOJI[faction]
            nb = dominance_globale[faction]
            etat_lignes.append(f"{emoji} {faction.capitalize()} : **{nb}** zone{'s' if nb != 1 else ''}")

        embed.add_field(
            name="État actuel",
            value="\n".join(etat_lignes),
            inline=False,
        )

        embed.set_footer(text="⸻ Infernum Aeterna · Territoires ⸻")

        # Publier dans flash-evenements
        for guild in self.bot.guilds:
            ch = trouver_channel(guild, "flash-evenements")
            if ch:
                try:
                    await ch.send(embed=embed)
                except discord.HTTPException as e:
                    log.error("Territoire: erreur envoi rapport quotidien : %s", e)

        # Nettoyer les changements traités
        self._changements_recents.clear()

    @boucle_rapport_territoire.before_loop
    async def before_rapport(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Territoire(bot))
