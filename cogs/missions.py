"""
INFERNUM AETERNA -- Cog Missions
Systeme de missions/quetes pour le serveur RP.

Commandes :
- /mission-creer       [STAFF] Cree une nouvelle mission
- /mission-accepter    Accepter une mission active
- /mission-rapport     Soumettre un rapport de mission
- /mission-valider     [STAFF] Valider le rapport d'un participant
- /missions-actives    Lister les missions disponibles
- /mes-missions        Voir ses missions en cours
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging

from config import COULEURS
from cogs.construction import trouver_channel
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

MISSIONS_FILE = "data/missions.json"

# Couleurs par difficulte
COULEURS_DIFFICULTE = {
    "facile":      0x57F287,
    "normale":     0xFEE75C,
    "difficile":   0xFF8C00,
    "legendaire":  0xED4245,
}

# Emojis par difficulte
EMOJIS_DIFFICULTE = {
    "facile":      "\U0001f7e2",   # green circle
    "normale":     "\U0001f7e1",   # yellow circle
    "difficile":   "\U0001f7e0",   # orange circle
    "legendaire":  "\U0001f534",   # red circle
}

# Kanji par faction (pour l'affichage)
KANJI_FACTION = {
    "shinigami": "\u6b7b\u795e",
    "togabito":  "\u7a0e\u4eba",
    "arrancar":  "\u7834\u9762",
    "quincy":    "\u6ec5\u5374\u5e2b",
    "toutes":    "\u5168\u6d3e\u95a5",
}


def _default_data():
    """Structure par defaut du fichier missions.json."""
    return {"missions": {}, "compteur": 0}


async def _autocomplete_mission_active(interaction: discord.Interaction, current: str):
    """Autocomplete : liste les missions actives correspondant au texte saisi."""
    store = JsonStore(MISSIONS_FILE, default=_default_data())
    missions = store.data.get("missions", {})
    choices = []
    for mid, m in missions.items():
        if m.get("statut") != "active":
            continue
        label = f"[{mid}] {m.get('titre', '?')}"
        if current.lower() in label.lower() or current.lower() in mid.lower():
            choices.append(app_commands.Choice(name=label[:100], value=mid))
    return choices[:25]


async def _autocomplete_mission_en_cours(interaction: discord.Interaction, current: str):
    """Autocomplete : liste les missions ou l'utilisateur est participant en_cours."""
    uid = str(interaction.user.id)
    store = JsonStore(MISSIONS_FILE, default=_default_data())
    missions = store.data.get("missions", {})
    choices = []
    for mid, m in missions.items():
        if m.get("statut") != "active":
            continue
        participant = m.get("participants", {}).get(uid)
        if not participant or participant.get("statut") != "en_cours":
            continue
        label = f"[{mid}] {m.get('titre', '?')}"
        if current.lower() in label.lower() or current.lower() in mid.lower():
            choices.append(app_commands.Choice(name=label[:100], value=mid))
    return choices[:25]


async def _autocomplete_mission_staff(interaction: discord.Interaction, current: str):
    """Autocomplete : liste les missions actives (pour commandes staff)."""
    return await _autocomplete_mission_active(interaction, current)


class Missions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(MISSIONS_FILE, default=_default_data())
        self.data = self._store.data
        # Assurer la structure de base
        self.data.setdefault("missions", {})
        self.data.setdefault("compteur", 0)

    async def _sauvegarder(self):
        self._store.data = self.data
        await self._store.save()

    # ══════════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _generer_id(self) -> str:
        """Auto-increment M-001, M-002, etc."""
        self.data["compteur"] = self.data.get("compteur", 0) + 1
        return f"M-{self.data['compteur']:03d}"

    def _construire_embed_mission(self, mission: dict) -> discord.Embed:
        """Construit l'embed riche d'une mission pour le tableau."""
        mid = mission["id"]
        titre = mission.get("titre", "Sans titre")
        description = mission.get("description", "")
        difficulte = mission.get("difficulte", "normale")
        factions = mission.get("factions", ["toutes"])
        recompense_pts = mission.get("recompense_points", 0)
        recompense_txt = mission.get("recompense_texte", "")
        max_p = mission.get("max_participants", 5)
        participants = mission.get("participants", {})
        nb_inscrits = len(participants)
        date_limite = mission.get("date_limite")

        couleur = COULEURS_DIFFICULTE.get(difficulte, COULEURS["or_ancien"])
        emoji_diff = EMOJIS_DIFFICULTE.get(difficulte, "\u26aa")

        # Barre de places
        places_prises = min(nb_inscrits, max_p)
        barre_remplie = "\u2588" * places_prises
        barre_vide = "\u2591" * (max_p - places_prises)
        barre_places = f"`{barre_remplie}{barre_vide}` {nb_inscrits}/{max_p}"

        # Factions formatees
        if "toutes" in factions:
            factions_str = f"{KANJI_FACTION.get('toutes', '')} Toutes les factions"
        else:
            parties = []
            for f in factions:
                kanji = KANJI_FACTION.get(f, "")
                parties.append(f"{kanji} {f.capitalize()}")
            factions_str = " \u00b7 ".join(parties)

        embed = discord.Embed(
            title=f"{emoji_diff} {titre}",
            description=description,
            color=couleur
        )
        embed.add_field(
            name="Identifiant",
            value=f"`{mid}`",
            inline=True
        )
        embed.add_field(
            name="Difficulte",
            value=f"{emoji_diff} **{difficulte.capitalize()}**",
            inline=True
        )
        embed.add_field(
            name="Recompense",
            value=f"**{recompense_pts:,}** pts" + (f"\n*{recompense_txt}*" if recompense_txt else ""),
            inline=True
        )
        embed.add_field(
            name="Factions",
            value=factions_str,
            inline=True
        )
        embed.add_field(
            name="Places",
            value=barre_places,
            inline=True
        )
        if date_limite:
            embed.add_field(
                name="Date limite",
                value=f"`{date_limite[:10]}`",
                inline=True
            )

        # Liste des participants inscrits
        if participants:
            lignes_p = []
            for uid, pdata in list(participants.items())[:10]:
                nom = pdata.get("nom_perso", "Inconnu")
                statut_p = pdata.get("statut", "en_cours")
                emoji_statut = {
                    "en_cours": "\u23f3",
                    "soumis": "\U0001f4e8",
                    "valide": "\u2705",
                    "echoue": "\u274c",
                }.get(statut_p, "\u2753")
                lignes_p.append(f"{emoji_statut} {nom}")
            embed.add_field(
                name="Participants",
                value="\n".join(lignes_p),
                inline=False
            )

        embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
        return embed

    def _verifier_expiration(self, mission: dict) -> bool:
        """Verifie si la mission est expiree. Met a jour le statut si necessaire.
        Retourne True si la mission est expiree."""
        if mission.get("statut") != "active":
            return mission.get("statut") == "expiree"
        date_limite = mission.get("date_limite")
        if date_limite:
            try:
                dt_limite = datetime.fromisoformat(date_limite)
                if datetime.now(timezone.utc) > dt_limite:
                    mission["statut"] = "expiree"
                    return True
            except (ValueError, TypeError):
                pass
        return False

    def _get_faction_personnage(self, uid: str) -> Optional[str]:
        """Recupere la faction du personnage d'un utilisateur via le cog Personnage."""
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return None
        perso = cog_perso.personnages.get(uid)
        if not perso:
            return None
        return perso.get("faction")

    def _get_nom_personnage(self, uid: str) -> Optional[str]:
        """Recupere le nom du personnage d'un utilisateur via le cog Personnage."""
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return None
        perso = cog_perso.personnages.get(uid)
        if not perso:
            return None
        return perso.get("nom_perso")

    def _personnage_valide(self, uid: str) -> bool:
        """Verifie si l'utilisateur a un personnage valide."""
        cog_perso = self.bot.cogs.get("Personnage")
        if not cog_perso:
            return False
        perso = cog_perso.personnages.get(uid)
        if not perso:
            return False
        return perso.get("valide", False) and perso.get("nom_perso")

    # ══════════════════════════════════════════════════════════════════════════
    #  /mission-creer [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mission-creer",
        description="[STAFF] Cree une nouvelle mission sur le tableau des missions."
    )
    @app_commands.describe(
        titre="Titre de la mission",
        description="Description narrative de la mission",
        difficulte="Niveau de difficulte",
        factions="Faction(s) concernee(s)",
        recompense_points="Points de recompense",
        recompense_texte="Description du bonus narratif (optionnel)",
        max_participants="Nombre max de participants (defaut : 5)",
        duree_jours="Duree en jours avant expiration (optionnel)"
    )
    @app_commands.choices(
        difficulte=[
            app_commands.Choice(name="Facile",      value="facile"),
            app_commands.Choice(name="Normale",     value="normale"),
            app_commands.Choice(name="Difficile",   value="difficile"),
            app_commands.Choice(name="Legendaire",  value="legendaire"),
        ],
        factions=[
            app_commands.Choice(name="Toutes les factions", value="toutes"),
            app_commands.Choice(name="Shinigami",           value="shinigami"),
            app_commands.Choice(name="Togabito",            value="togabito"),
            app_commands.Choice(name="Arrancar",            value="arrancar"),
            app_commands.Choice(name="Quincy",              value="quincy"),
        ]
    )
    @app_commands.default_permissions(manage_messages=True)
    async def mission_creer(
        self, interaction: discord.Interaction,
        titre: str,
        description: str,
        difficulte: str,
        factions: str,
        recompense_points: int,
        recompense_texte: Optional[str] = None,
        max_participants: Optional[int] = 5,
        duree_jours: Optional[int] = None
    ):
        await interaction.response.defer(ephemeral=True)

        # Generer l'ID unique
        mission_id = self._generer_id()

        # Calculer la date limite si duree specifiee
        date_limite = None
        if duree_jours and duree_jours > 0:
            date_limite = (datetime.now(timezone.utc) + timedelta(days=duree_jours)).isoformat()

        # Normaliser les factions en liste
        factions_list = [factions] if factions != "toutes" else ["toutes"]

        # Creer l'entree mission
        mission = {
            "id": mission_id,
            "titre": titre,
            "description": description,
            "difficulte": difficulte,
            "factions": factions_list,
            "recompense_points": recompense_points,
            "recompense_texte": recompense_texte or "",
            "createur_id": interaction.user.id,
            "date_creation": datetime.now(timezone.utc).isoformat(),
            "date_limite": date_limite,
            "statut": "active",
            "participants": {},
            "max_participants": max(1, max_participants or 5),
        }

        self.data["missions"][mission_id] = mission
        await self._sauvegarder()

        # Poster l'embed dans le tableau des missions
        ch_missions = trouver_channel(interaction.guild, "tableau-des-missions")
        if ch_missions:
            embed = self._construire_embed_mission(mission)
            await ch_missions.send(embed=embed)
            log.info("Mission %s creee par %s, postee dans #%s",
                     mission_id, interaction.user, ch_missions.name)
        else:
            log.warning("Channel tableau-des-missions introuvable pour poster la mission %s", mission_id)

        await interaction.followup.send(
            f"\u2705 Mission **{titre}** (`{mission_id}`) creee avec succes."
            + (f"\nPostee dans {ch_missions.mention}." if ch_missions else "\n\u26a0\ufe0f Channel `tableau-des-missions` introuvable."),
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /mission-accepter (public)
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mission-accepter",
        description="Accepter une mission active."
    )
    @app_commands.describe(mission_id="Identifiant de la mission")
    @app_commands.autocomplete(mission_id=_autocomplete_mission_active)
    async def mission_accepter(self, interaction: discord.Interaction, mission_id: str):
        await interaction.response.defer(ephemeral=True)
        uid = str(interaction.user.id)

        # Verifier que l'utilisateur a un personnage valide
        if not self._personnage_valide(uid):
            await interaction.followup.send(
                "\u274c Vous devez avoir un personnage valide pour accepter une mission.\n"
                "Soumettez votre fiche via `/fiche-soumettre` et attendez la validation du staff.",
                ephemeral=True
            )
            return

        # Verifier que la mission existe
        mission = self.data["missions"].get(mission_id)
        if not mission:
            await interaction.followup.send(
                f"\u274c Mission `{mission_id}` introuvable.",
                ephemeral=True
            )
            return

        # Verifier l'expiration
        if self._verifier_expiration(mission):
            await self._sauvegarder()
            await interaction.followup.send(
                f"\u274c La mission `{mission_id}` a expire.",
                ephemeral=True
            )
            return

        # Verifier que la mission est active
        if mission.get("statut") != "active":
            await interaction.followup.send(
                f"\u274c La mission `{mission_id}` n'est plus active (statut : {mission.get('statut')}).",
                ephemeral=True
            )
            return

        # Verifier que l'utilisateur n'est pas deja inscrit
        if uid in mission.get("participants", {}):
            await interaction.followup.send(
                f"\u274c Vous participez deja a la mission **{mission.get('titre')}**.",
                ephemeral=True
            )
            return

        # Verifier le nombre max de participants
        participants = mission.get("participants", {})
        max_p = mission.get("max_participants", 5)
        if len(participants) >= max_p:
            await interaction.followup.send(
                f"\u274c La mission **{mission.get('titre')}** est complete ({max_p}/{max_p} participants).",
                ephemeral=True
            )
            return

        # Verifier la compatibilite de faction
        faction_joueur = self._get_faction_personnage(uid)
        factions_mission = mission.get("factions", ["toutes"])
        if "toutes" not in factions_mission and faction_joueur not in factions_mission:
            factions_str = ", ".join(f.capitalize() for f in factions_mission)
            await interaction.followup.send(
                f"\u274c Votre faction (**{(faction_joueur or 'inconnue').capitalize()}**) "
                f"ne correspond pas aux factions de cette mission ({factions_str}).",
                ephemeral=True
            )
            return

        # Inscrire le participant
        nom_perso = self._get_nom_personnage(uid) or interaction.user.display_name
        mission.setdefault("participants", {})[uid] = {
            "nom_perso": nom_perso,
            "date_acceptation": datetime.now(timezone.utc).isoformat(),
            "rapport": None,
            "statut": "en_cours",
        }
        await self._sauvegarder()

        # Confirmation au joueur
        emoji_diff = EMOJIS_DIFFICULTE.get(mission.get("difficulte", "normale"), "\u26aa")
        await interaction.followup.send(
            f"\u2705 **{nom_perso}** a rejoint la mission {emoji_diff} **{mission.get('titre')}** (`{mission_id}`).\n"
            f"Soumettez votre rapport avec `/mission-rapport` une fois la mission accomplie.",
            ephemeral=True
        )

        # Notification dans le tableau des missions (mise a jour visuelle)
        ch_missions = trouver_channel(interaction.guild, "tableau-des-missions")
        if ch_missions:
            embed_notif = discord.Embed(
                title=f"\U0001f4e5 Nouveau participant \u2014 {mission.get('titre')}",
                description=(
                    f"**{nom_perso}** ({interaction.user.mention}) a accepte la mission `{mission_id}`.\n"
                    f"Places : **{len(mission['participants'])}/{max_p}**"
                ),
                color=COULEURS_DIFFICULTE.get(mission.get("difficulte", "normale"), COULEURS["or_ancien"])
            )
            embed_notif.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
            await ch_missions.send(embed=embed_notif)

        log.info("Mission %s : %s (%s) a rejoint", mission_id, nom_perso, uid)

    # ══════════════════════════════════════════════════════════════════════════
    #  /mission-rapport (public)
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mission-rapport",
        description="Soumettre un rapport pour une mission en cours."
    )
    @app_commands.describe(
        mission_id="Identifiant de la mission",
        rapport="Votre rapport narratif de mission"
    )
    @app_commands.autocomplete(mission_id=_autocomplete_mission_en_cours)
    async def mission_rapport(self, interaction: discord.Interaction, mission_id: str, rapport: str):
        await interaction.response.defer(ephemeral=True)
        uid = str(interaction.user.id)

        # Verifier que la mission existe
        mission = self.data["missions"].get(mission_id)
        if not mission:
            await interaction.followup.send(
                f"\u274c Mission `{mission_id}` introuvable.",
                ephemeral=True
            )
            return

        # Verifier que l'utilisateur est participant
        participant = mission.get("participants", {}).get(uid)
        if not participant:
            await interaction.followup.send(
                f"\u274c Vous ne participez pas a la mission `{mission_id}`.",
                ephemeral=True
            )
            return

        # Verifier le statut du participant
        if participant.get("statut") != "en_cours":
            statut_actuel = participant.get("statut", "inconnu")
            if statut_actuel == "soumis":
                await interaction.followup.send(
                    f"\u274c Vous avez deja soumis un rapport pour cette mission. "
                    f"Attendez la validation du staff.",
                    ephemeral=True
                )
            elif statut_actuel == "valide":
                await interaction.followup.send(
                    f"\u274c Votre rapport pour cette mission a deja ete valide.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"\u274c Impossible de soumettre un rapport (statut : {statut_actuel}).",
                    ephemeral=True
                )
            return

        # Sauvegarder le rapport
        participant["rapport"] = rapport
        participant["statut"] = "soumis"
        participant["date_rapport"] = datetime.now(timezone.utc).isoformat()
        await self._sauvegarder()

        nom_perso = participant.get("nom_perso", interaction.user.display_name)

        # Confirmation au joueur
        await interaction.followup.send(
            f"\u2705 Rapport soumis pour la mission **{mission.get('titre')}** (`{mission_id}`).\n"
            f"Le staff sera notifie et validera votre rapport.",
            ephemeral=True
        )

        # Notifier le staff dans le canal validations
        ch_validations = trouver_channel(interaction.guild, "validations")
        if ch_validations:
            embed = discord.Embed(
                title=f"\U0001f4e8 Rapport de Mission \u2014 {mission.get('titre')}",
                description=(
                    f"**Participant :** {nom_perso} ({interaction.user.mention})\n"
                    f"**Mission :** `{mission_id}` \u2014 {mission.get('titre')}\n"
                    f"**Difficulte :** {EMOJIS_DIFFICULTE.get(mission.get('difficulte', ''), '')} "
                    f"{mission.get('difficulte', 'normale').capitalize()}\n"
                    f"**Recompense :** {mission.get('recompense_points', 0):,} pts\n\n"
                    f"**Rapport :**\n{rapport[:1800]}"
                ),
                color=COULEURS["or_pale"]
            )
            embed.add_field(
                name="Action",
                value=f"Utilisez `/mission-valider mission_id:{mission_id} membre:@{interaction.user.display_name} resultat:...`",
                inline=False
            )
            embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
            await ch_validations.send(embed=embed)

        log.info("Mission %s : rapport soumis par %s (%s)", mission_id, nom_perso, uid)

    # ══════════════════════════════════════════════════════════════════════════
    #  /mission-valider [STAFF]
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mission-valider",
        description="[STAFF] Valider le rapport d'un participant."
    )
    @app_commands.describe(
        mission_id="Identifiant de la mission",
        membre="Le membre dont le rapport est a valider",
        resultat="Resultat de la validation"
    )
    @app_commands.autocomplete(mission_id=_autocomplete_mission_staff)
    @app_commands.choices(resultat=[
        app_commands.Choice(name="Succes",  value="succes"),
        app_commands.Choice(name="Echec",   value="echec"),
    ])
    @app_commands.default_permissions(manage_messages=True)
    async def mission_valider(
        self, interaction: discord.Interaction,
        mission_id: str,
        membre: discord.Member,
        resultat: str
    ):
        await interaction.response.defer(ephemeral=True)
        uid = str(membre.id)

        # Verifier que la mission existe
        mission = self.data["missions"].get(mission_id)
        if not mission:
            await interaction.followup.send(
                f"\u274c Mission `{mission_id}` introuvable.",
                ephemeral=True
            )
            return

        # Verifier que le membre est participant
        participant = mission.get("participants", {}).get(uid)
        if not participant:
            await interaction.followup.send(
                f"\u274c {membre.mention} ne participe pas a la mission `{mission_id}`.",
                ephemeral=True
            )
            return

        # Verifier que le rapport a ete soumis
        if participant.get("statut") not in ("soumis", "en_cours"):
            await interaction.followup.send(
                f"\u274c Le participant a deja ete traite (statut : {participant.get('statut')}).",
                ephemeral=True
            )
            return

        nom_perso = participant.get("nom_perso", membre.display_name)
        recompense = mission.get("recompense_points", 0)

        if resultat == "succes":
            participant["statut"] = "valide"
            participant["date_validation"] = datetime.now(timezone.utc).isoformat()
            participant["validateur_id"] = interaction.user.id

            # Attribution des points via le cog Personnage
            cog_perso = self.bot.cogs.get("Personnage")
            if cog_perso and uid in cog_perso.personnages:
                cog_perso.personnages[uid]["points"] = cog_perso.personnages[uid].get("points", 0) + recompense
                await cog_perso._sauvegarder()
                log.info("Mission %s : +%d pts attribues a %s (%s)", mission_id, recompense, nom_perso, uid)
            else:
                log.warning("Mission %s : cog Personnage indisponible ou personnage %s introuvable pour attribution points", mission_id, uid)

            # Embed de resultat
            embed_result = discord.Embed(
                title=f"\u2705 Mission Accomplie \u2014 {mission.get('titre')}",
                description=(
                    f"**{nom_perso}** ({membre.mention}) a accompli la mission `{mission_id}` avec succes.\n\n"
                    f"**Recompense :** +**{recompense:,}** pts"
                    + (f"\n*{mission.get('recompense_texte')}*" if mission.get("recompense_texte") else "")
                ),
                color=COULEURS_DIFFICULTE.get(mission.get("difficulte", "normale"), COULEURS["or_ancien"])
            )
            embed_result.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")

            # Poster dans le tableau des missions
            ch_missions = trouver_channel(interaction.guild, "tableau-des-missions")
            if ch_missions:
                await ch_missions.send(embed=embed_result)

            # Notifier le joueur en DM
            try:
                embed_dm = discord.Embed(
                    title=f"\u2705 Mission accomplie : {mission.get('titre')}",
                    description=(
                        f"Felicitations, **{nom_perso}**. Votre rapport a ete valide.\n\n"
                        f"**Recompense :** +**{recompense:,}** pts"
                        + (f"\n*{mission.get('recompense_texte')}*" if mission.get("recompense_texte") else "")
                        + f"\n\nVotre progression a ete mise a jour."
                    ),
                    color=COULEURS["or_ancien"]
                )
                embed_dm.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
                await membre.send(embed=embed_dm)
            except discord.Forbidden:
                pass  # DM desactives

        else:  # echec
            participant["statut"] = "echoue"
            participant["date_validation"] = datetime.now(timezone.utc).isoformat()
            participant["validateur_id"] = interaction.user.id

            # Embed de resultat
            embed_result = discord.Embed(
                title=f"\u274c Mission Echouee \u2014 {mission.get('titre')}",
                description=(
                    f"**{nom_perso}** ({membre.mention}) n'a pas rempli les objectifs "
                    f"de la mission `{mission_id}`."
                ),
                color=COULEURS["rouge_chaine"]
            )
            embed_result.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")

            ch_missions = trouver_channel(interaction.guild, "tableau-des-missions")
            if ch_missions:
                await ch_missions.send(embed=embed_result)

            # Notifier le joueur en DM
            try:
                embed_dm = discord.Embed(
                    title=f"\u274c Mission echouee : {mission.get('titre')}",
                    description=(
                        f"**{nom_perso}**, votre rapport pour la mission `{mission_id}` "
                        f"n'a pas ete retenu par le staff.\n\n"
                        f"Vous pouvez retenter lorsqu'une nouvelle mission sera disponible."
                    ),
                    color=COULEURS["rouge_chaine"]
                )
                embed_dm.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
                await membre.send(embed=embed_dm)
            except discord.Forbidden:
                pass

        await self._sauvegarder()

        # Verifier si tous les participants ont ete traites
        tous_traites = all(
            p.get("statut") in ("valide", "echoue")
            for p in mission.get("participants", {}).values()
        )
        if tous_traites and mission.get("participants"):
            mission["statut"] = "terminee"
            mission["date_cloture"] = datetime.now(timezone.utc).isoformat()
            await self._sauvegarder()

            # Embed de cloture
            nb_succes = sum(1 for p in mission["participants"].values() if p.get("statut") == "valide")
            nb_echec = sum(1 for p in mission["participants"].values() if p.get("statut") == "echoue")
            embed_cloture = discord.Embed(
                title=f"\U0001f3c1 Mission Terminee \u2014 {mission.get('titre')}",
                description=(
                    f"La mission `{mission_id}` est desormais close.\n\n"
                    f"\u2705 **{nb_succes}** succes \u00b7 \u274c **{nb_echec}** echec(s)\n"
                    f"Difficulte : {EMOJIS_DIFFICULTE.get(mission.get('difficulte', ''), '')} "
                    f"{mission.get('difficulte', 'normale').capitalize()}"
                ),
                color=COULEURS["gris_acier"]
            )
            embed_cloture.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
            ch_missions = trouver_channel(interaction.guild, "tableau-des-missions")
            if ch_missions:
                await ch_missions.send(embed=embed_cloture)

            log.info("Mission %s terminee : %d succes, %d echecs", mission_id, nb_succes, nb_echec)

        resultat_txt = "validee (\u2705 succes)" if resultat == "succes" else "rejetee (\u274c echec)"
        await interaction.followup.send(
            f"\u2705 Participation de **{nom_perso}** a la mission `{mission_id}` {resultat_txt}."
            + (f"\n\U0001f3c1 Tous les participants ont ete traites \u2014 mission terminee." if tous_traites and mission.get("participants") else ""),
            ephemeral=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /missions-actives (public)
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="missions-actives",
        description="Affiche la liste des missions actives."
    )
    @app_commands.describe(faction="Filtrer par faction (optionnel)")
    @app_commands.choices(faction=[
        app_commands.Choice(name="Toutes les factions", value="toutes"),
        app_commands.Choice(name="Shinigami",           value="shinigami"),
        app_commands.Choice(name="Togabito",            value="togabito"),
        app_commands.Choice(name="Arrancar",            value="arrancar"),
        app_commands.Choice(name="Quincy",              value="quincy"),
    ])
    async def missions_actives(self, interaction: discord.Interaction, faction: str = "toutes"):
        await interaction.response.defer()

        missions = self.data.get("missions", {})
        actives = []

        for mid, m in missions.items():
            # Verifier et mettre a jour l'expiration
            self._verifier_expiration(m)
            if m.get("statut") != "active":
                continue
            # Filtre par faction
            if faction != "toutes":
                factions_mission = m.get("factions", ["toutes"])
                if "toutes" not in factions_mission and faction not in factions_mission:
                    continue
            actives.append(m)

        await self._sauvegarder()  # Sauvegarder les eventuels changements d'expiration

        if not actives:
            filtre_txt = f" pour la faction **{faction.capitalize()}**" if faction != "toutes" else ""
            embed = discord.Embed(
                title="\U0001f4cb Missions Actives",
                description=f"*Aucune mission active{filtre_txt} pour le moment.*\n\n"
                            f"Consultez ce canal regulierement.",
                color=COULEURS["gris_acier"]
            )
            embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
            await interaction.followup.send(embed=embed)
            return

        # Trier par date de creation (plus recentes d'abord)
        actives.sort(key=lambda m: m.get("date_creation", ""), reverse=True)

        # Construire l'embed de liste
        titre_filtre = f" \u2014 {KANJI_FACTION.get(faction, '')} {faction.capitalize()}" if faction != "toutes" else ""
        embed = discord.Embed(
            title=f"\U0001f4cb Missions Actives{titre_filtre}",
            description=f"**{len(actives)}** mission(s) disponible(s). "
                        f"Utilisez `/mission-accepter` pour participer.",
            color=COULEURS["or_ancien"]
        )

        for m in actives[:10]:  # Max 10 dans l'embed
            mid = m["id"]
            diff = m.get("difficulte", "normale")
            emoji_diff = EMOJIS_DIFFICULTE.get(diff, "\u26aa")
            max_p = m.get("max_participants", 5)
            nb_p = len(m.get("participants", {}))
            places = f"{nb_p}/{max_p}"
            recompense = m.get("recompense_points", 0)

            # Factions courtes
            factions_m = m.get("factions", ["toutes"])
            if "toutes" in factions_m:
                fac_str = "Toutes"
            else:
                fac_str = "/".join(f.capitalize()[:4] for f in factions_m)

            embed.add_field(
                name=f"{emoji_diff} `{mid}` \u2014 {m.get('titre', '?')}",
                value=(
                    f"Difficulte : **{diff.capitalize()}** \u00b7 "
                    f"Places : **{places}** \u00b7 "
                    f"Recompense : **{recompense:,}** pts\n"
                    f"Factions : {fac_str}"
                    + (f" \u00b7 Expire le `{m['date_limite'][:10]}`" if m.get("date_limite") else "")
                ),
                inline=False
            )

        if len(actives) > 10:
            embed.add_field(
                name="\u2026",
                value=f"*{len(actives) - 10} autre(s) mission(s) non affichee(s).*",
                inline=False
            )

        embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
        await interaction.followup.send(embed=embed)

    # ══════════════════════════════════════════════════════════════════════════
    #  /mes-missions (public)
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mes-missions",
        description="Affiche vos missions en cours et terminees."
    )
    async def mes_missions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        uid = str(interaction.user.id)

        # Collecter toutes les missions ou le joueur participe
        mes_missions = []
        for mid, m in self.data.get("missions", {}).items():
            participant = m.get("participants", {}).get(uid)
            if participant:
                mes_missions.append((m, participant))

        if not mes_missions:
            embed = discord.Embed(
                title="\U0001f4cb Mes Missions",
                description=(
                    "*Vous n'avez accepte aucune mission pour le moment.*\n\n"
                    "Consultez les missions disponibles avec `/missions-actives` "
                    "et acceptez-en une avec `/mission-accepter`."
                ),
                color=COULEURS["gris_acier"]
            )
            embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Trier : en_cours et soumis d'abord, puis valide/echoue
        ordre_statut = {"en_cours": 0, "soumis": 1, "valide": 2, "echoue": 3}
        mes_missions.sort(key=lambda x: ordre_statut.get(x[1].get("statut", ""), 99))

        nom_perso = self._get_nom_personnage(uid) or interaction.user.display_name
        embed = discord.Embed(
            title=f"\U0001f4cb Missions de {nom_perso}",
            description=f"**{len(mes_missions)}** mission(s) au total.",
            color=COULEURS["or_ancien"]
        )

        for m, p in mes_missions[:15]:  # Max 15
            mid = m["id"]
            diff = m.get("difficulte", "normale")
            emoji_diff = EMOJIS_DIFFICULTE.get(diff, "\u26aa")
            statut = p.get("statut", "inconnu")
            emoji_statut = {
                "en_cours": "\u23f3 En cours",
                "soumis":   "\U0001f4e8 Rapport soumis",
                "valide":   "\u2705 Succes",
                "echoue":   "\u274c Echec",
            }.get(statut, "\u2753 Inconnu")

            recompense = m.get("recompense_points", 0)
            pts_str = f"+{recompense:,} pts" if statut == "valide" else f"{recompense:,} pts"

            embed.add_field(
                name=f"{emoji_diff} `{mid}` \u2014 {m.get('titre', '?')}",
                value=(
                    f"Statut : {emoji_statut}\n"
                    f"Recompense : **{pts_str}**"
                    + (f"\nAccepte le `{p.get('date_acceptation', '')[:10]}`" if p.get("date_acceptation") else "")
                ),
                inline=False
            )

        if len(mes_missions) > 15:
            embed.add_field(
                name="\u2026",
                value=f"*{len(mes_missions) - 15} autre(s) non affichee(s).*",
                inline=False
            )

        embed.set_footer(text="\u2e3b Infernum Aeterna \u00b7 Missions \u2e3b")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Missions(bot))
