"""
INFERNUM AETERNA — Cog Modération
Système de modération autonome à 3 tiers :
  Tier 1 — Heuristique instantanée (on_message, on_member_join)
  Tier 2 — Analyse IA par lots (Claude Haiku, toutes les 5 min)
  Tier 3 — Commandes staff (/mod-warn, /mod-timeout, /mod-historique, /mod-config, /mod-rapport)

Escalade automatique : 3 warnings/24h → infraction (timeout 30min)
                       3+ infractions  → alerte critique owner
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import anthropic
import asyncio
import json
import re
import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from config import (
    COULEURS, ANTHROPIC_KEY, MODERATION_MODEL, MODERATION_SYSTEM, OWNER_ID,
)
from utils.json_store import JsonStore
from cogs.construction import trouver_channel

log = logging.getLogger("infernum")

MODERATION_FILE = "data/moderation.json"

# ─── Structure par défaut ────────────────────────────────────────────────────
DEFAULT_DATA = {
    "config": {
        "actif": True,
        "channels_surveilles": [],
        "seuil_spam": 5,
        "seuil_raid": 8,
        "intervalle_ia_minutes": 5,
    },
    "warnings": {},
    "infractions": {},
    "raid_log": [],
}

# ─── Regex invite Discord ────────────────────────────────────────────────────
RE_INVITE = re.compile(
    r"(discord\.gg|discord\.com/invite|discordapp\.com/invite)/[A-Za-z0-9\-]+",
    re.IGNORECASE,
)


# ══════════════════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════════════════

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Persistence
        self._store = JsonStore(MODERATION_FILE, default=DEFAULT_DATA)
        self.data = self._store.data
        # Assurer la structure minimale
        for cle in DEFAULT_DATA:
            val = DEFAULT_DATA[cle]
            if isinstance(val, (dict, list)):
                self.data.setdefault(cle, val.copy())
            else:
                self.data.setdefault(cle, val)

        # Client Anthropic (Haiku) — séparé du Narrateur
        self._client = None
        if ANTHROPIC_KEY:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=30.0)
        else:
            log.warning("ANTHROPIC_KEY absente — modération IA désactivée")
        self._semaphore = asyncio.Semaphore(2)

        # Buffer messages pour analyse IA (channel_id → liste de dicts)
        self._buffer = defaultdict(list)

        # Compteurs anti-spam en mémoire (user_id → liste timestamps)
        self._spam_timestamps = defaultdict(list)
        # Compteurs messages dupliqués (user_id → liste (contenu, timestamp))
        self._spam_duplicates = defaultdict(list)
        # Compteurs joins pour détection raid (liste timestamps)
        self._join_timestamps = []

        # Démarrer les boucles
        self.boucle_analyse_ia.start()
        self.boucle_nettoyage.start()

    def cog_unload(self):
        self.boucle_analyse_ia.cancel()
        self.boucle_nettoyage.cancel()

    @property
    def _config(self):
        return self.data.setdefault("config", DEFAULT_DATA["config"].copy())

    # ══════════════════════════════════════════════════════════════════════════
    #  TIER 1 — Heuristique instantanée
    # ══════════════════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer bots, DMs, système inactif
        if message.author.bot or not message.guild:
            return
        if not self._config.get("actif", True):
            return

        # Ignorer les channels non-surveillés (si liste configurée)
        channels = self._config.get("channels_surveilles", [])
        if channels and str(message.channel.id) not in channels:
            return

        maintenant = datetime.now(timezone.utc)
        uid = str(message.author.id)

        # ── Spam flood : 5+ msgs / 10s ──────────────────────────────────────
        seuil_spam = self._config.get("seuil_spam", 5)
        self._spam_timestamps[uid].append(maintenant)
        # Purger les timestamps > 10s
        self._spam_timestamps[uid] = [
            ts for ts in self._spam_timestamps[uid]
            if (maintenant - ts).total_seconds() < 10
        ]
        if len(self._spam_timestamps[uid]) >= seuil_spam:
            self._spam_timestamps[uid].clear()
            await self._action_spam_flood(message)
            return

        # ── Messages dupliqués : 3x même contenu / 30s ──────────────────────
        contenu = message.content.strip().lower()
        if contenu:
            self._spam_duplicates[uid].append((contenu, maintenant))
            self._spam_duplicates[uid] = [
                (c, ts) for c, ts in self._spam_duplicates[uid]
                if (maintenant - ts).total_seconds() < 30
            ]
            duplicates = [c for c, _ in self._spam_duplicates[uid] if c == contenu]
            if len(duplicates) >= 3:
                self._spam_duplicates[uid].clear()
                await self._action_duplicates(message)
                return

        # ── Spam caractères : 50+ chars identiques ──────────────────────────
        if contenu and len(contenu) >= 50:
            if len(set(contenu.replace(" ", ""))) <= 2:
                await self._action_char_spam(message)
                return

        # ── Mass mentions : 5+ mentions / msg ───────────────────────────────
        if len(message.mentions) + len(message.role_mentions) >= 5:
            await self._action_mass_mentions(message)
            return

        # ── Invites Discord dans channels RP ─────────────────────────────────
        if RE_INVITE.search(message.content):
            await self._action_invite(message)
            return

        # ── Ajouter au buffer IA (Tier 2) ───────────────────────────────────
        if contenu and len(contenu) > 5:
            self._buffer[str(message.channel.id)].append({
                "user_id": uid,
                "user_name": str(message.author),
                "message_id": str(message.id),
                "content": message.content[:500],  # Limiter la taille
                "timestamp": maintenant.isoformat(),
            })

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self._config.get("actif", True):
            return

        maintenant = datetime.now(timezone.utc)

        # ── Détection raid : 8+ joins / 15s ─────────────────────────────────
        self._join_timestamps.append(maintenant)
        self._join_timestamps = [
            ts for ts in self._join_timestamps
            if (maintenant - ts).total_seconds() < 15
        ]
        seuil_raid = self._config.get("seuil_raid", 8)
        if len(self._join_timestamps) >= seuil_raid:
            self._join_timestamps.clear()
            await self._activer_lockdown(member.guild)

        # ── Compte neuf (< 24h) → log staff ─────────────────────────────────
        age = maintenant - member.created_at.replace(tzinfo=timezone.utc)
        if age < timedelta(hours=24):
            embed = discord.Embed(
                title="⚠️ Compte récent détecté",
                description=(
                    f"{member.mention} (`{member}`) vient de rejoindre.\n"
                    f"Compte créé il y a **{age.total_seconds() / 3600:.1f}h**."
                ),
                color=COULEURS["or_pale"],
                timestamp=maintenant,
            )
            embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
            await self._alerte_staff(member.guild, embed)

    # ── Actions Tier 1 ───────────────────────────────────────────────────────

    async def _action_spam_flood(self, message):
        """Spam flood détecté → timeout 5min + suppression + alerte staff."""
        try:
            # Supprimer les messages récents du spammeur dans le channel
            async for msg in message.channel.history(limit=20):
                if msg.author.id == message.author.id:
                    try:
                        await msg.delete()
                    except discord.HTTPException:
                        pass
            # Timeout 5 minutes
            if isinstance(message.author, discord.Member):
                await message.author.timeout(
                    timedelta(minutes=5), reason="Spam flood détecté (auto)"
                )
        except discord.HTTPException as e:
            log.error("Modération: erreur action spam flood: %s", e)

        await self._avertir(
            message.author, message.guild,
            "Spam flood (5+ messages en 10s)", "heuristique",
            message_id=str(message.id),
        )
        # Alerte staff
        embed = discord.Embed(
            title="🚨 Spam Flood Détecté",
            description=(
                f"**Utilisateur :** {message.author.mention}\n"
                f"**Channel :** {message.channel.mention}\n"
                f"**Action :** Timeout 5min + suppression"
            ),
            color=COULEURS["rouge_moderation"],
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
        await self._alerte_staff(message.guild, embed)

    async def _action_duplicates(self, message):
        """Messages dupliqués → suppression + avertissement DM."""
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        await self._avertir(
            message.author, message.guild,
            "Messages dupliqués (3x même contenu en 30s)", "heuristique",
            message_id=str(message.id),
        )

    async def _action_char_spam(self, message):
        """Spam de caractères identiques → suppression + avertissement DM."""
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        await self._avertir(
            message.author, message.guild,
            "Spam de caractères répétés", "heuristique",
            message_id=str(message.id),
        )

    async def _action_mass_mentions(self, message):
        """Mass mentions → suppression + avertissement DM."""
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        await self._avertir(
            message.author, message.guild,
            "Mentions massives (5+ mentions dans un message)", "heuristique",
            message_id=str(message.id),
        )

    async def _action_invite(self, message):
        """Invite Discord dans channel RP → suppression + avertissement DM."""
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        await self._avertir(
            message.author, message.guild,
            "Lien d'invitation Discord non autorisé", "heuristique",
            message_id=str(message.id),
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  TIER 2 — Analyse IA par lots
    # ══════════════════════════════════════════════════════════════════════════

    @tasks.loop(minutes=5)
    async def boucle_analyse_ia(self):
        if not self._client or not self._config.get("actif", True):
            return
        if not self._buffer:
            return

        # Copier et vider le buffer
        batch = dict(self._buffer)
        self._buffer.clear()

        for guild in self.bot.guilds:
            await self._analyser_batch(guild, batch)

    @boucle_analyse_ia.before_loop
    async def before_analyse_ia(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def boucle_nettoyage(self):
        """Purge les warnings de plus de 30 jours."""
        limite = datetime.now(timezone.utc) - timedelta(days=30)
        warnings = self.data.setdefault("warnings", {})
        modifie = False
        for uid in list(warnings.keys()):
            avant = len(warnings[uid])
            warnings[uid] = [
                w for w in warnings[uid]
                if datetime.fromisoformat(w["date"]) > limite
            ]
            if len(warnings[uid]) != avant:
                modifie = True
            if not warnings[uid]:
                del warnings[uid]
                modifie = True
        if modifie:
            self._store.data = self.data
            await self._store.save()

    @boucle_nettoyage.before_loop
    async def before_nettoyage(self):
        await self.bot.wait_until_ready()

    async def _analyser_batch(self, guild, batch):
        """Envoie le lot de messages à Haiku et traite les violations."""
        # Construire le texte du lot
        lignes = []
        for ch_id, msgs in batch.items():
            channel = guild.get_channel(int(ch_id))
            ch_name = channel.name if channel else ch_id
            for msg in msgs:
                lignes.append(
                    f"[#{ch_name}] {msg['user_name']} (uid:{msg['user_id']}, mid:{msg['message_id']}): {msg['content']}"
                )

        if not lignes:
            return

        prompt = (
            "Analyse les messages suivants d'un serveur RP Bleach francophone.\n"
            "Identifie UNIQUEMENT les vraies violations (pas le RP en jeu).\n\n"
            + "\n".join(lignes)
        )

        try:
            async with self._semaphore:
                loop = asyncio.get_running_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self._client.messages.create(
                            model=MODERATION_MODEL,
                            max_tokens=1000,
                            system=MODERATION_SYSTEM,
                            messages=[{"role": "user", "content": prompt}],
                        ),
                    ),
                    timeout=35.0,
                )
            texte = response.content[0].text.strip()
            violations = json.loads(texte)
        except (json.JSONDecodeError, asyncio.TimeoutError, Exception) as e:
            log.error("Modération IA: erreur analyse batch: %s", e)
            return

        if not isinstance(violations, list):
            return

        for v in violations:
            if not isinstance(v, dict):
                continue
            severite = v.get("severite", "low")
            uid = v.get("user_id", "")
            raison = v.get("raison", "Violation détectée par IA")
            type_v = v.get("type", "autre")

            member = guild.get_member(int(uid)) if uid.isdigit() else None
            if not member:
                continue

            if severite == "low":
                # Log uniquement
                self._log_warning(uid, raison, "ia", v.get("message_id", ""))
                await self._sauvegarder()

            elif severite == "medium":
                await self._avertir(member, guild, f"[{type_v}] {raison}", "ia",
                                    message_id=v.get("message_id", ""))
                embed = discord.Embed(
                    title="⚠️ Violation détectée (IA)",
                    description=(
                        f"**Utilisateur :** {member.mention}\n"
                        f"**Type :** {type_v}\n"
                        f"**Raison :** {raison}"
                    ),
                    color=COULEURS["or_pale"],
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
                await self._alerte_staff(guild, embed)

            elif severite == "high":
                await self._avertir(member, guild, f"[{type_v}] {raison}", "ia",
                                    message_id=v.get("message_id", ""))
                embed = discord.Embed(
                    title="🔴 Violation grave (IA)",
                    description=(
                        f"**Utilisateur :** {member.mention}\n"
                        f"**Type :** {type_v}\n"
                        f"**Raison :** {raison}"
                    ),
                    color=COULEURS["rouge_moderation"],
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
                await self._alerte_staff(guild, embed)
                await self._alerte_owner(guild, f"🔴 Violation grave de {member} : {raison}")

            elif severite == "critical":
                await self._infraction(
                    member, guild, f"[{type_v}] {raison}", 1800, "ia"
                )

    # ══════════════════════════════════════════════════════════════════════════
    #  TIER 3 — Commandes staff
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mod-warn",
        description="[STAFF] Avertir un utilisateur manuellement.",
    )
    @app_commands.describe(
        utilisateur="L'utilisateur à avertir",
        raison="Raison de l'avertissement",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def mod_warn(
        self, interaction: discord.Interaction,
        utilisateur: discord.Member, raison: str,
    ):
        await self._avertir(utilisateur, interaction.guild, raison, "staff")
        await interaction.response.send_message(
            f"✅ Avertissement envoyé à {utilisateur.mention}, *{raison}*",
            ephemeral=True,
        )

    @app_commands.command(
        name="mod-timeout",
        description="[STAFF] Timeout un utilisateur avec log complet.",
    )
    @app_commands.describe(
        utilisateur="L'utilisateur à timeout",
        duree="Durée en minutes",
        raison="Raison du timeout",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def mod_timeout(
        self, interaction: discord.Interaction,
        utilisateur: discord.Member, duree: int, raison: str,
    ):
        await self._infraction(
            utilisateur, interaction.guild, raison, duree * 60, "staff"
        )
        await interaction.response.send_message(
            f"✅ Timeout {duree}min appliqué à {utilisateur.mention}, *{raison}*",
            ephemeral=True,
        )

    @app_commands.command(
        name="mod-historique",
        description="[STAFF] Voir l'historique de modération d'un utilisateur.",
    )
    @app_commands.describe(utilisateur="L'utilisateur à inspecter")
    @app_commands.default_permissions(manage_messages=True)
    async def mod_historique(
        self, interaction: discord.Interaction, utilisateur: discord.Member,
    ):
        uid = str(utilisateur.id)
        warnings = self.data.get("warnings", {}).get(uid, [])
        infractions = self.data.get("infractions", {}).get(uid, [])

        if not warnings and not infractions:
            await interaction.response.send_message(
                f"✅ {utilisateur.mention} n'a aucun historique de modération.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📋 Historique · {utilisateur}",
            color=COULEURS["gris_acier"],
            timestamp=datetime.now(timezone.utc),
        )

        if warnings:
            dernieres = warnings[-10:]  # 10 derniers
            txt = "\n".join(
                f"• `{w['date'][:10]}` [{w['source']}] {w['raison']}"
                for w in dernieres
            )
            if len(warnings) > 10:
                txt += f"\n… et {len(warnings) - 10} de plus"
            embed.add_field(name=f"⚠️ Warnings ({len(warnings)})", value=txt, inline=False)

        if infractions:
            dernieres = infractions[-10:]
            txt = "\n".join(
                f"• `{i['date'][:10]}` [{i['source']}] {i['type']} {i.get('duree', 0) // 60}min · {i['raison']}"
                for i in dernieres
            )
            if len(infractions) > 10:
                txt += f"\n… et {len(infractions) - 10} de plus"
            embed.add_field(name=f"🔴 Infractions ({len(infractions)})", value=txt, inline=False)

        embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="mod-config",
        description="[ADMIN] Configurer le système de modération.",
    )
    @app_commands.describe(
        actif="Activer ou désactiver la modération",
        seuil_spam="Messages/10s pour déclencher l'anti-spam (défaut: 5)",
        seuil_raid="Joins/15s pour déclencher l'anti-raid (défaut: 8)",
        intervalle_ia="Intervalle analyse IA en minutes (défaut: 5)",
    )
    @app_commands.default_permissions(administrator=True)
    async def mod_config(
        self, interaction: discord.Interaction,
        actif: bool = None,
        seuil_spam: int = None,
        seuil_raid: int = None,
        intervalle_ia: int = None,
    ):
        cfg = self._config
        modifs = []
        if actif is not None:
            cfg["actif"] = actif
            modifs.append(f"Actif: **{actif}**")
        if seuil_spam is not None:
            cfg["seuil_spam"] = max(2, seuil_spam)
            modifs.append(f"Seuil spam: **{cfg['seuil_spam']}**")
        if seuil_raid is not None:
            cfg["seuil_raid"] = max(3, seuil_raid)
            modifs.append(f"Seuil raid: **{cfg['seuil_raid']}**")
        if intervalle_ia is not None:
            cfg["intervalle_ia_minutes"] = max(1, intervalle_ia)
            modifs.append(f"Intervalle IA: **{cfg['intervalle_ia_minutes']}min**")
            # Redémarrer la boucle avec le nouvel intervalle
            self.boucle_analyse_ia.change_interval(minutes=cfg["intervalle_ia_minutes"])

        self._store.data = self.data
        await self._store.save()

        if modifs:
            await interaction.response.send_message(
                "✅ Configuration mise à jour :\n" + "\n".join(modifs),
                ephemeral=True,
            )
        else:
            # Afficher la config actuelle
            channels = cfg.get("channels_surveilles", [])
            nb_ch = len(channels) if channels else "tous"
            await interaction.response.send_message(
                f"**Configuration modération :**\n"
                f"• Actif : **{cfg.get('actif', True)}**\n"
                f"• Channels surveillés : **{nb_ch}**\n"
                f"• Seuil spam : **{cfg.get('seuil_spam', 5)}** msgs/10s\n"
                f"• Seuil raid : **{cfg.get('seuil_raid', 8)}** joins/15s\n"
                f"• Intervalle IA : **{cfg.get('intervalle_ia_minutes', 5)}** min",
                ephemeral=True,
            )

    @app_commands.command(
        name="mod-rapport",
        description="[STAFF] Statistiques de modération.",
    )
    @app_commands.describe(
        periode="Période du rapport",
    )
    @app_commands.choices(periode=[
        app_commands.Choice(name="24h", value=1),
        app_commands.Choice(name="7 jours", value=7),
        app_commands.Choice(name="30 jours", value=30),
    ])
    @app_commands.default_permissions(manage_messages=True)
    async def mod_rapport(
        self, interaction: discord.Interaction, periode: int = 7,
    ):
        limite = datetime.now(timezone.utc) - timedelta(days=periode)

        # Compter les warnings récents
        nb_warnings = 0
        users_warns = set()
        for uid, ws in self.data.get("warnings", {}).items():
            for w in ws:
                if datetime.fromisoformat(w["date"]) > limite:
                    nb_warnings += 1
                    users_warns.add(uid)

        # Compter les infractions récentes
        nb_infractions = 0
        users_infr = set()
        for uid, infrs in self.data.get("infractions", {}).items():
            for i in infrs:
                if datetime.fromisoformat(i["date"]) > limite:
                    nb_infractions += 1
                    users_infr.add(uid)

        # Compter les raids
        nb_raids = sum(
            1 for r in self.data.get("raid_log", [])
            if datetime.fromisoformat(r["date"]) > limite
        )

        label = {1: "24h", 7: "7 jours", 30: "30 jours"}.get(periode, f"{periode}j")

        embed = discord.Embed(
            title=f"📊 Rapport de modération · {label}",
            color=COULEURS["gris_acier"],
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(
            name="⚠️ Warnings",
            value=f"**{nb_warnings}** warnings\n{len(users_warns)} utilisateurs",
            inline=True,
        )
        embed.add_field(
            name="🔴 Infractions",
            value=f"**{nb_infractions}** infractions\n{len(users_infr)} utilisateurs",
            inline=True,
        )
        embed.add_field(
            name="🛡️ Raids",
            value=f"**{nb_raids}** détectés",
            inline=True,
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  Fonctions internes
    # ══════════════════════════════════════════════════════════════════════════

    def _log_warning(self, user_id, raison, source, message_id=""):
        """Enregistre un warning dans les données (sans DM)."""
        warnings = self.data.setdefault("warnings", {})
        warnings.setdefault(user_id, []).append({
            "date": datetime.now(timezone.utc).isoformat(),
            "raison": raison,
            "source": source,
            "message_id": message_id,
        })

    async def _sauvegarder(self):
        self._store.data = self.data
        await self._store.save()

    async def _avertir(self, user, guild, raison, source, message_id=""):
        """Envoie un DM d'avertissement + log + vérifie escalade."""
        uid = str(user.id)
        self._log_warning(uid, raison, source, message_id)
        await self._sauvegarder()

        # DM à l'utilisateur
        try:
            await user.send(
                f"⚠️ **Avertissement** · Serveur *{guild.name}*\n"
                f"Raison : {raison}\n\n"
                f"Merci de respecter les règles du serveur."
            )
        except discord.HTTPException:
            pass  # DMs fermés

        # Vérifier escalade : 3 warnings en 24h → infraction auto
        if self._verifier_escalade(uid):
            member = guild.get_member(int(uid))
            if member:
                await self._infraction(
                    member, guild,
                    "Escalade automatique (3 avertissements en 24h)",
                    1800,  # 30 minutes
                    "escalade",
                )

    async def _infraction(self, member, guild, raison, duree, source):
        """Applique un timeout + log + alerte staff + check alerte owner."""
        uid = str(member.id)
        infractions = self.data.setdefault("infractions", {})
        infractions.setdefault(uid, []).append({
            "date": datetime.now(timezone.utc).isoformat(),
            "type": "timeout",
            "duree": duree,
            "raison": raison,
            "source": source,
        })
        await self._sauvegarder()

        # Timeout Discord
        try:
            await member.timeout(
                timedelta(seconds=duree),
                reason=f"[Modération] {raison}",
            )
        except discord.HTTPException as e:
            log.error("Modération: erreur timeout %s: %s", member, e)

        # Alerte staff
        embed = discord.Embed(
            title="🔴 Infraction enregistrée",
            description=(
                f"**Utilisateur :** {member.mention}\n"
                f"**Durée :** {duree // 60} min\n"
                f"**Raison :** {raison}\n"
                f"**Source :** {source}"
            ),
            color=COULEURS["rouge_moderation"],
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
        await self._alerte_staff(guild, embed)

        # Si 3+ infractions → alerte critique owner
        nb = len(infractions.get(uid, []))
        if nb >= 3:
            await self._alerte_owner(
                guild,
                f"🚨 **ALERTE CRITIQUE** · {member} ({member.id}) a atteint "
                f"**{nb} infractions**. Dernière : {raison}\n"
                f"Action manuelle recommandée (ban potentiel).",
            )

    def _verifier_escalade(self, user_id):
        """Retourne True si l'utilisateur a 3+ warnings dans les dernières 24h."""
        warnings = self.data.get("warnings", {}).get(user_id, [])
        limite = datetime.now(timezone.utc) - timedelta(hours=24)
        recents = [
            w for w in warnings
            if datetime.fromisoformat(w["date"]) > limite
        ]
        return len(recents) >= 3

    async def _alerte_staff(self, guild, embed):
        """Envoie un embed dans le channel staff."""
        ch = trouver_channel(guild, "discussions-staff")
        if ch:
            try:
                await ch.send(embed=embed)
            except discord.HTTPException as e:
                log.error("Modération: erreur alerte staff: %s", e)

    async def _alerte_owner(self, guild, message):
        """Envoie un MP à l'owner du serveur."""
        owner = None
        if OWNER_ID:
            owner = guild.get_member(OWNER_ID) or self.bot.get_user(OWNER_ID)
        if not owner:
            owner = guild.owner
        if owner:
            try:
                await owner.send(message)
            except discord.HTTPException:
                log.error("Modération: impossible de MP l'owner")

    async def _activer_lockdown(self, guild):
        """Active le lockdown anti-raid : verification_level max + alerte."""
        maintenant = datetime.now(timezone.utc)
        try:
            await guild.edit(
                verification_level=discord.VerificationLevel.highest,
                reason="[Modération] Lockdown anti-raid automatique",
            )
        except discord.HTTPException as e:
            log.error("Modération: erreur lockdown: %s", e)

        # Log raid
        self.data.setdefault("raid_log", []).append({
            "date": maintenant.isoformat(),
            "joins": self._config.get("seuil_raid", 8),
            "action": "lockdown",
            "duree": 300,
        })
        await self._sauvegarder()

        # Alerte staff
        embed = discord.Embed(
            title="🛡️ LOCKDOWN ANTI-RAID ACTIVÉ",
            description=(
                "Afflux massif de connexions détecté.\n"
                "Le niveau de vérification a été mis au maximum.\n\n"
                "⚠️ **Pensez à le réduire manuellement une fois le raid passé.**"
            ),
            color=COULEURS["rouge_moderation"],
            timestamp=maintenant,
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Modération ⸻")
        await self._alerte_staff(guild, embed)

        # Alerte owner
        await self._alerte_owner(
            guild,
            "🚨 **RAID DÉTECTÉ** · Lockdown activé automatiquement.\n"
            "Le niveau de vérification du serveur est maintenant au maximum.\n"
            "Vérifiez les nouveaux membres et réduisez le niveau quand le raid est terminé.",
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
