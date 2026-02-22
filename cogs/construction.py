"""
INFERNUM AETERNA — Cog Construction
Commande /setup : construit l'intégralité du serveur Discord
(rôles, catégories, channels, permissions).
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import os
import logging
from typing import Optional

from config import COULEURS
from data.structure_serveur import ROLES, CATEGORIES

log = logging.getLogger("infernum")


# ─── Stockage des IDs des rôles créés ─────────────────────────────────────────
ROLES_IDS_FILE = "data/roles_ids.json"


def sauvegarder_roles(mapping: dict):
    os.makedirs("data", exist_ok=True)
    with open(ROLES_IDS_FILE, "w") as f:
        json.dump(mapping, f, indent=2)


def charger_roles() -> dict:
    if not os.path.exists(ROLES_IDS_FILE):
        return {}
    with open(ROLES_IDS_FILE) as f:
        return json.load(f)


# ─── Stockage des IDs des channels créés ──────────────────────────────────────
CHANNELS_IDS_FILE = "data/channels_ids.json"


def sauvegarder_channels(mapping: dict):
    os.makedirs("data", exist_ok=True)
    with open(CHANNELS_IDS_FILE, "w") as f:
        json.dump(mapping, f, indent=2)


def charger_channels() -> dict:
    if not os.path.exists(CHANNELS_IDS_FILE):
        return {}
    with open(CHANNELS_IDS_FILE) as f:
        return json.load(f)


def trouver_channel(guild: discord.Guild, cle: str) -> Optional[discord.TextChannel]:
    """Résout un channel par ID (JSON) avec fallback substring sur le nom."""
    channels_ids = charger_channels()
    # Tentative par ID exact
    ch_id = channels_ids.get(cle)
    if ch_id:
        ch = guild.get_channel(ch_id)
        if ch:
            return ch
    # Fallback substring
    for ch in guild.text_channels:
        if cle in ch.name:
            return ch
    return None


class Construction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /setup ────────────────────────────────────────────────────────────────
    @app_commands.command(
        name="setup",
        description="[ADMIN] Construit l'intégralité du serveur Infernum Aeterna."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        # Répondre IMMÉDIATEMENT avant toute suppression de channel
        await interaction.response.send_message(
            "⚙️ Construction du serveur **Infernum Aeterna** en cours…\n"
            "Le serveur va être reconstruit entièrement. Cela prend 2-3 minutes.\n"
            "*Ne pas relancer la commande.*",
            ephemeral=True
        )
        guild = interaction.guild
        log = []

        # ── 1. Nettoyer les rôles existants (hors @everyone et bots) ──────────
        roles_a_garder = {"@everyone"}
        for role in guild.roles:
            if role.is_bot_managed() or role.name in roles_a_garder or role.name == "@everyone":
                continue
            try:
                await role.delete(reason="Setup Infernum Aeterna")
                await asyncio.sleep(0.3)
            except discord.Forbidden:
                log.append(f"⚠️ Rôle non supprimable : {role.name}")

        # ── 2. Créer les rôles ─────────────────────────────────────────────────
        roles_map = {}
        for role_def in sorted(ROLES, key=lambda r: r["position"], reverse=True):
            try:
                role = await guild.create_role(
                    name=role_def["nom"],
                    color=discord.Color(role_def["couleur"]),
                    hoist=role_def.get("hoist", False),
                    mentionable=role_def.get("mentionable", False),
                    reason="Setup Infernum Aeterna"
                )
                roles_map[role_def["cle"]] = role
                await asyncio.sleep(0.3)
            except Exception as e:
                log.append(f"❌ Rôle {role_def['nom']} : {e}")

        sauvegarder_roles({k: v.id for k, v in roles_map.items()})

        # ── 3. Supprimer TOUS les channels existants ───────────────────────────
        # On le fait silencieusement — plus de followup après ici
        for channel in list(guild.channels):
            try:
                await channel.delete(reason="Setup Infernum Aeterna")
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                log.append(f"⚠️ Channel non supprimable : {channel.name}")

        # ── 4. Créer catégories et channels ───────────────────────────────────
        role_everyone = guild.default_role
        channel_staff = None  # On le capture pour poster le résumé
        channels_map = {}     # Collecte des IDs pour channels_ids.json

        for cat_def in CATEGORIES:
            perms_cat = _construire_permissions_categorie(cat_def, roles_map, role_everyone)
            try:
                categorie = await guild.create_category(
                    name=cat_def["nom"],
                    overwrites=perms_cat,
                    reason="Setup Infernum Aeterna"
                )
            except Exception as e:
                log.append(f"❌ Catégorie {cat_def['nom']} : {e}")
                continue

            await asyncio.sleep(0.3)

            for ch_def in cat_def.get("channels", []):
                try:
                    overrides = _construire_permissions_channel(ch_def, cat_def, roles_map, role_everyone)

                    if ch_def.get("type") == "forum":
                        channel = await guild.create_forum(
                            name=ch_def["nom"],
                            category=categorie,
                            topic=ch_def.get("sujet", ""),
                            overwrites=overrides,
                            reason="Setup Infernum Aeterna"
                        )
                    else:
                        channel = await guild.create_text_channel(
                            name=ch_def["nom"],
                            category=categorie,
                            topic=ch_def.get("sujet", ""),
                            overwrites=overrides,
                            reason="Setup Infernum Aeterna"
                        )
                    await asyncio.sleep(0.25)
                    await _envoyer_message_initial(channel, ch_def, roles_map)

                    # Enregistrer l'ID du channel (clé = nom nettoyé)
                    cle_ch = _cle_channel(ch_def["nom"])
                    channels_map[cle_ch] = channel.id

                    # Capturer le canal staff pour le résumé final
                    if "configuration-bot" in ch_def["nom"] or "discussions-staff" in ch_def["nom"]:
                        channel_staff = channel

                except Exception as e:
                    log.append(f"❌ Channel {ch_def['nom']} : {e}")

        # ── 4b. Sauvegarder les IDs des channels ─────────────────────────────
        sauvegarder_channels(channels_map)

        # ── 5. Peupler les channels lore & administration ────────────────────
        await _peupler_channels_lore(guild)

        # ── Résumé — posté dans le canal staff nouvellement créé ──────────────
        embed = discord.Embed(
            title="⛩️ Infernum Aeterna — Construction terminée",
            description=(
                f"**{len(roles_map)}** rôles créés\n"
                f"**{sum(len(c['channels']) for c in CATEGORIES)}** channels créés\n"
                f"**{len(CATEGORIES)}** catégories créées"
            ),
            color=COULEURS["or_ancien"]
        )
        if log:
            embed.add_field(
                name="⚠️ Avertissements",
                value="\n".join(log[:10]) + ("\n…" if len(log) > 10 else ""),
                inline=False
            )
        embed.set_footer(text="La Fissure s'est ouverte. Le monde tremble.")

        if channel_staff:
            await channel_staff.send(embed=embed)
        else:
            # Fallback : premier channel textuel trouvé
            for ch in guild.text_channels:
                await ch.send(embed=embed)
                break

    # ── /purge-serveur ─────────────────────────────────────────────────────────
    @app_commands.command(
        name="purge-serveur",
        description="[ADMIN] Supprime tous les channels et catégories (sans toucher aux rôles)."
    )
    @app_commands.default_permissions(administrator=True)
    async def purge_serveur(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        for channel in guild.channels:
            try:
                await channel.delete(reason="Purge Infernum Aeterna")
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                pass
        await interaction.followup.send("✅ Serveur purgé.", ephemeral=True)

    # ── /scan-channels ────────────────────────────────────────────────────────
    @app_commands.command(
        name="scan-channels",
        description="[ADMIN] Scanne les channels existants et génère channels_ids.json (non destructif)."
    )
    @app_commands.default_permissions(administrator=True)
    async def scan_channels(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        mapping = {}
        for ch in guild.text_channels:
            cle = _cle_channel(ch.name)
            if cle:
                mapping[cle] = ch.id
        for ch in guild.forums:
            cle = _cle_channel(ch.name)
            if cle:
                mapping[cle] = ch.id
        sauvegarder_channels(mapping)
        await interaction.followup.send(
            f"✅ **{len(mapping)}** channels scannés et sauvegardés dans `channels_ids.json`.",
            ephemeral=True
        )

    # ── /sync-roles ───────────────────────────────────────────────────────────
    @app_commands.command(
        name="sync-roles",
        description="[ADMIN] Crée les rôles manquants sans toucher aux existants (additif)."
    )
    @app_commands.default_permissions(administrator=True)
    async def sync_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        resultats = await self._sync_roles_impl(guild)
        await interaction.followup.send(
            f"✅ Sync terminée : **{resultats['crees']}** créé(s), "
            f"**{resultats['maj']}** mis à jour, "
            f"**{resultats['ignores']}** inchangé(s), "
            f"**{resultats['supprimes']}** obsolète(s) supprimé(s).",
            ephemeral=True
        )

    async def _sync_roles_impl(self, guild: discord.Guild) -> dict:
        """Synchronise les rôles du serveur avec ROLES dans structure_serveur.py.
        Crée les manquants, met à jour les existants (nom, couleur, hoist, mentionable),
        supprime les rôles obsolètes qui étaient dans roles_ids.json mais plus dans ROLES.
        """
        roles_ids = charger_roles()
        cles_attendues = {r["cle"] for r in ROLES}
        crees, maj, ignores, supprimes = 0, 0, 0, 0

        for role_def in sorted(ROLES, key=lambda r: r["position"], reverse=True):
            cle = role_def["cle"]
            nom_attendu = role_def["nom"]
            couleur_attendue = role_def["couleur"]
            hoist_attendu = role_def.get("hoist", False)
            mention_attendue = role_def.get("mentionable", False)

            # Chercher le rôle existant par ID sauvegardé ou par nom
            existant = None
            if cle in roles_ids:
                existant = guild.get_role(roles_ids[cle])
            if not existant:
                for r in guild.roles:
                    if r.name == nom_attendu:
                        existant = r
                        break

            if existant:
                roles_ids[cle] = existant.id
                # Vérifier si une mise à jour est nécessaire
                besoin_maj = (
                    existant.name != nom_attendu
                    or existant.color.value != couleur_attendue
                    or existant.hoist != hoist_attendu
                    or existant.mentionable != mention_attendue
                )
                if besoin_maj:
                    try:
                        await existant.edit(
                            name=nom_attendu,
                            color=discord.Color(couleur_attendue),
                            hoist=hoist_attendu,
                            mentionable=mention_attendue,
                            reason="Actualisation Infernum Aeterna"
                        )
                        maj += 1
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        log.error("sync-roles: erreur MAJ %s : %s", nom_attendu, e)
                else:
                    ignores += 1
                continue

            # Rôle inexistant → créer
            try:
                role = await guild.create_role(
                    name=nom_attendu,
                    color=discord.Color(couleur_attendue),
                    hoist=hoist_attendu,
                    mentionable=mention_attendue,
                    reason="Sync rôles Infernum Aeterna"
                )
                roles_ids[cle] = role.id
                crees += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                log.error("sync-roles: erreur création %s : %s", nom_attendu, e)

        # Supprimer les rôles obsolètes (dans roles_ids.json mais plus dans ROLES)
        cles_obsoletes = set(roles_ids.keys()) - cles_attendues
        for cle_obs in cles_obsoletes:
            role_obs = guild.get_role(roles_ids[cle_obs])
            if role_obs:
                try:
                    await role_obs.delete(reason="Rôle obsolète — Actualisation Infernum Aeterna")
                    supprimes += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    log.error("sync-roles: erreur suppression %s : %s", cle_obs, e)
            del roles_ids[cle_obs]

        sauvegarder_roles(roles_ids)
        return {"crees": crees, "maj": maj, "ignores": ignores, "supprimes": supprimes}

    # ── /actualiser ──────────────────────────────────────────────────────────
    @app_commands.command(
        name="actualiser",
        description="[ADMIN] Met à jour rôles, channels et lore pour coller au code actuel."
    )
    @app_commands.describe(
        cible="Quoi actualiser (défaut : tout)",
    )
    @app_commands.choices(cible=[
        app_commands.Choice(name="Tout (rôles + channels + lore)", value="tout"),
        app_commands.Choice(name="Rôles uniquement", value="roles"),
        app_commands.Choice(name="Channels (scan IDs)", value="channels"),
        app_commands.Choice(name="Lore uniquement", value="lore"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def actualiser(self, interaction: discord.Interaction, cible: str = "tout"):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        rapport = []

        # ── 1. Rôles ────────────────────────────────────────────────────────
        if cible in ("tout", "roles"):
            r = await self._sync_roles_impl(guild)
            rapport.append(
                f"**Rôles** : {r['crees']} créé(s), {r['maj']} mis à jour, "
                f"{r['ignores']} inchangé(s), {r['supprimes']} obsolète(s) supprimé(s)"
            )

        # ── 2. Channels (scan IDs) ──────────────────────────────────────────
        if cible in ("tout", "channels"):
            mapping = {}
            for ch in guild.text_channels:
                cle = _cle_channel(ch.name)
                if cle:
                    mapping[cle] = ch.id
            for ch in guild.forums:
                cle = _cle_channel(ch.name)
                if cle:
                    mapping[cle] = ch.id
            sauvegarder_channels(mapping)
            rapport.append(f"**Channels** : {len(mapping)} channel(s) indexé(s)")

        # ── 3. Lore ─────────────────────────────────────────────────────────
        if cible in ("tout", "lore"):
            cles_lore = [
                "infernum-aeterna", "les-quatre-factions", "geographie",
                "glossaire", "systeme", "bestiaire", "pacte", "modele-de-fiche"
            ]
            nettoyees = 0
            for cle in cles_lore:
                ch = trouver_channel(guild, cle)
                if not ch:
                    continue
                try:
                    async for msg in ch.history(limit=50):
                        if msg.author == self.bot.user:
                            if msg.pinned:
                                try:
                                    await msg.unpin()
                                except Exception:
                                    pass
                            await msg.delete()
                            nettoyees += 1
                            await asyncio.sleep(0.3)
                except Exception as e:
                    log.error("actualiser lore: nettoyage %s : %s", cle, e)

            await _peupler_channels_lore(guild)
            rapport.append(f"**Lore** : {nettoyees} ancien(s) message(s) nettoyé(s), lore republié")

        # ── Résumé ──────────────────────────────────────────────────────────
        embed = discord.Embed(
            title="⛩️ Actualisation terminée",
            description="\n".join(f"• {l}" for l in rapport),
            color=COULEURS["or_ancien"]
        )
        embed.set_footer(text="⸻ Infernum Aeterna ⸻")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /refresh-lore ─────────────────────────────────────────────────────────
    @app_commands.command(
        name="refresh-lore",
        description="[ADMIN] Reposte tout le lore sans reconstruire le serveur."
    )
    @app_commands.default_permissions(administrator=True)
    async def refresh_lore(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # Nettoyer les anciens messages du bot dans les channels lore
        cles_lore = [
            "infernum-aeterna", "les-quatre-factions", "geographie",
            "glossaire", "systeme", "bestiaire", "pacte", "modele-de-fiche"
        ]
        for cle in cles_lore:
            ch = trouver_channel(guild, cle)
            if not ch:
                continue
            try:
                async for msg in ch.history(limit=50):
                    if msg.author == self.bot.user:
                        if msg.pinned:
                            try:
                                await msg.unpin()
                            except Exception:
                                pass
                        await msg.delete()
                        await asyncio.sleep(0.3)
            except Exception as e:
                log.error("refresh-lore: nettoyage %s : %s", cle, e)

        # Re-peupler
        await _peupler_channels_lore(guild)
        await interaction.followup.send("✅ Lore rafraîchi dans tous les channels.", ephemeral=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS — PERMISSIONS
# ══════════════════════════════════════════════════════════════════════════════

def _construire_permissions_categorie(cat_def, roles_map, role_everyone):
    """Construit le dict d'overwrites pour une catégorie."""
    perms = {}
    cat_perms = cat_def.get("permissions", {})

    # @everyone
    if cat_perms.get("everyone_view", True):
        perms[role_everyone] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=cat_perms.get("everyone_send", False)
        )
    else:
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)

    # Staff toujours accès
    for cle_staff in ("architecte", "gardien_des_portes"):
        if cle_staff in roles_map:
            perms[roles_map[cle_staff]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_messages=True
            )

    return perms


def _construire_permissions_channel(ch_def, cat_def, roles_map, role_everyone):
    """Construit le dict d'overwrites pour un channel."""
    perms = {}
    cat_perms = cat_def.get("permissions", {})

    # Base everyone depuis la catégorie
    if cat_perms.get("everyone_view", True):
        perms[role_everyone] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=ch_def.get("lecture_seule", False) is False and cat_perms.get("everyone_send", False)
        )
    else:
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)

    # Channels lecture seule
    if ch_def.get("lecture_seule", False):
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

    # Channels de faction
    if "factions" in ch_def:
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        for cle_faction in ch_def["factions"]:
            if cle_faction in roles_map:
                perms[roles_map[cle_faction]] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True
                )

    # Staff override
    for cle_staff in ("architecte", "gardien_des_portes"):
        if cle_staff in roles_map:
            perms[roles_map[cle_staff]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_messages=True, manage_threads=True
            )

    # Catégorie staff-only
    if not cat_perms.get("everyone_view", True):
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)
        for cle_staff in ("architecte", "gardien_des_portes", "emissaire", "chroniqueur"):
            if cle_staff in roles_map:
                perms[roles_map[cle_staff]] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True
                )

    return perms


async def _envoyer_message_initial(channel, ch_def, roles_map):
    """Envoie un message épinglé selon le type de channel."""
    try:
        if ch_def.get("boutons_faction"):
            await _envoyer_boutons_faction(channel, roles_map)
        elif ch_def.get("combat"):
            await _envoyer_bouton_combat(channel, ch_def)
        elif ch_def.get("abonnements"):
            await _envoyer_boutons_abonnements(channel, roles_map)
        elif ch_def.get("valide_perso"):
            await _envoyer_instructions_fiche(channel)
    except Exception:
        pass


async def _envoyer_boutons_faction(channel, roles_map):
    embed = discord.Embed(
        title="⸻ Choisir son Destin ⸻",
        description=(
            "Chaque âme appartient à un monde.\n"
            "Choisissez votre faction pour accéder aux zones correspondantes.\n\n"
            "「 Vous pourrez changer de faction avant validation de votre fiche. 」"
        ),
        color=COULEURS["or_ancien"]
    )
    view = BoutonsFaction()
    msg = await channel.send(embed=embed, view=view)
    await msg.pin()


async def _envoyer_bouton_combat(channel, ch_def):
    faction = ch_def.get("faction_combat", "tous")
    embed = discord.Embed(
        title="⚔️ Initier un Combat",
        description=(
            "Cliquez sur le bouton ci-dessous pour ouvrir un fil de combat.\n"
            "Un fil privé sera créé avec votre adversaire désigné.\n\n"
            "「 Tout combat doit être validé par un Émissaire ou supérieur. 」"
        ),
        color=COULEURS["rouge_chaine"]
    )
    view = BoutonCombat(faction)
    msg = await channel.send(embed=embed, view=view)
    await msg.pin()


async def _envoyer_boutons_abonnements(channel, roles_map):
    embed = discord.Embed(
        title="🔔 Abonnements aux Notifications",
        description=(
            "Gérez vos notifications en cliquant sur les boutons.\n"
            "Chaque clic alterne entre abonné et désabonné."
        ),
        color=COULEURS["bleu_abyssal"]
    )
    view = BoutonsAbonnements()
    msg = await channel.send(embed=embed, view=view)
    await msg.pin()


async def _envoyer_instructions_fiche(channel):
    embed = discord.Embed(
        title="📋 Soumettre une Fiche Personnage",
        description=(
            "Copiez le modèle disponible dans `📋・modele-de-fiche` et soumettez-le ici.\n\n"
            "Le staff répondra dans les 48 heures.\n"
            "Votre fiche sera archivée dans `✅・fiches-validees` après validation.\n\n"
            "「 Aucune réécriture ne sera imposée sans consultation. 」"
        ),
        color=COULEURS["blanc_seireitei"]
    )
    await channel.send(embed=embed)


# ══════════════════════════════════════════════════════════════════════════════
#  PEUPLEMENT DES CHANNELS LORE & ADMINISTRATION
# ══════════════════════════════════════════════════════════════════════════════

async def _peupler_channels_lore(guild: discord.Guild):
    """Poste le lore dans les channels CHRONIQUES et ADMINISTRATION après /setup."""
    from cogs.lore import GLOSSAIRE, FICHES_FACTION, STRATES, LORE_DATA
    from cogs.personnage import RANGS_POINTS

    def find_ch(partial: str):
        for ch in guild.text_channels:
            if partial in ch.name:
                return ch
        return None

    async def poster(channel, embed):
        if not channel:
            return
        try:
            msg = await channel.send(embed=embed)
            await msg.pin()
            await asyncio.sleep(0.4)
        except Exception as e:
            print(f"[Lore Setup] {getattr(channel, 'name', '?')} : {e}")

    # ── 0. Lien web lore ──────────────────────────────────────────────────────
    from cogs.lore import LORE_WEB_URL, _ajouter_lien_web

    # ── 1. infernum-aeterna — embed lien web + 5 embeds lore fondateur ──────
    ch = find_ch("infernum-aeterna")

    # Embed d'accueil avec lien vers le lore complet
    e_web = discord.Embed(
        title="⛩️ Chroniques des Quatre Races",
        description=(
            "Bienvenue dans les chroniques d'**Infernum Aeterna**.\n\n"
            "Les résumés ci-dessous présentent les fondations de notre lore. "
            "Le texte intégral — quinze mille mots, quatre chroniques, chaque "
            "mot pesé — est accessible sur notre page dédiée."
        ),
        color=COULEURS["or_ancien"]
    )
    e_web.add_field(
        name="📜 Lore intégral",
        value=f"**[Ouvrir les Chroniques des Quatre Races]({LORE_WEB_URL})**",
        inline=False
    )
    e_web.add_field(
        name="Accès direct par faction",
        value=(
            f"[序章 Prologue]({LORE_WEB_URL}#prologue) · "
            f"[死神 Shinigami]({LORE_WEB_URL}#shinigami) · "
            f"[咎人 Togabito]({LORE_WEB_URL}#togabito)\n"
            f"[破面 Arrancar]({LORE_WEB_URL}#arrancar) · "
            f"[滅却師 Quincy]({LORE_WEB_URL}#quincy) · "
            f"[零番隊 Division Zéro]({LORE_WEB_URL}#division-zero)\n"
            f"[創造 Guide de Création]({LORE_WEB_URL}#creation)"
        ),
        inline=False
    )
    e_web.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")
    await poster(ch, e_web)

    for cle in ["origine", "fissure", "reio", "division_zero", "konso_reisai"]:
        data = LORE_DATA[cle]
        e = discord.Embed(title=data["titre"], description=data["description"], color=data["couleur"])
        for nom_champ, valeur_champ in data.get("fields", []):
            e.add_field(name=nom_champ, value=valeur_champ, inline=False)
        e.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")
        _ajouter_lien_web(e, data.get("web_fragment", ""))
        await poster(ch, e)

    # ── 2. les-quatre-factions — 4 embeds ────────────────────────────────────
    ch = find_ch("les-quatre-factions")
    for faction_key in ["shinigami", "togabito", "arrancar", "quincy"]:
        fiche = FICHES_FACTION[faction_key]
        e = discord.Embed(title=fiche["titre"], color=fiche["couleur"])
        for nom_section, texte_section in fiche["sections"]:
            e.add_field(name=nom_section, value=texte_section, inline=False)
        e.set_footer(text="⸻ Infernum Aeterna · Factions ⸻")
        _ajouter_lien_web(e, fiche.get("web_fragment", ""))
        await poster(ch, e)

    # ── 3. geographie-des-mondes — 2 embeds ──────────────────────────────────
    ch = find_ch("geographie")
    e = discord.Embed(title="🗺️ Les Cinq Strates de l'Enfer", color=COULEURS["pourpre_infernal"])
    for strate in STRATES:
        e.add_field(
            name=f"{strate['emoji']} {strate['nom']}",
            value=strate["desc"],
            inline=False
        )
    e.set_footer(text="⸻ Infernum Aeterna · Géographie ⸻")
    _ajouter_lien_web(e, "togabito")
    await poster(ch, e)

    e2 = discord.Embed(
        title="🌍 Les Trois Mondes",
        description=(
            "**Soul Society** — Royaume des Shinigami. "
            "Seireitei au centre, Rukongai en périphérie. "
            "Gouverné par le Gotei 13, fragilisé par la vérité du Konsō Reisai.\n\n"
            "**Hueco Mundo** — Désert éternel des Hollow. "
            "Las Noches en son cœur. Résonance croissante avec le Jigoku no Rinki "
            "depuis l'ouverture de la Fissure.\n\n"
            "**Monde des Vivants** — Karakura et ses alentours. "
            "Portails actifs détectés. Contamination spirituelle progressive.\n\n"
            "**La Frontière** — Espace entre les mondes. "
            "Épicentre de la Fissure. Territoire sans loi."
        ),
        color=COULEURS["gris_acier"]
    )
    e2.set_footer(text="⸻ Infernum Aeterna · Géographie ⸻")
    await poster(ch, e2)

    # ── 4. glossaire — embeds par groupes de 5 ───────────────────────────────
    ch = find_ch("glossaire")
    entrees = list(GLOSSAIRE.items())
    for i in range(0, len(entrees), 5):
        groupe = entrees[i:i + 5]
        e = discord.Embed(
            title=f"📜 Glossaire ({i + 1}–{min(i + 5, len(entrees))})",
            color=COULEURS["or_pale"]
        )
        for cle, (kanji, definition) in groupe:
            e.add_field(
                name=f"**{cle.replace('_', ' ').title()}** {kanji}",
                value=definition,
                inline=False
            )
        e.set_footer(text="⸻ Infernum Aeterna · Glossaire ⸻")
        await poster(ch, e)

    # ── 5. systeme-et-competences — 2 embeds ─────────────────────────────────
    ch = find_ch("systeme")
    data_sys = LORE_DATA["systeme"]
    e = discord.Embed(title=data_sys["titre"], description=data_sys["description"], color=data_sys["couleur"])
    for nom_champ, valeur_champ in data_sys.get("fields", []):
        e.add_field(name=nom_champ, value=valeur_champ, inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
    await poster(ch, e)

    e = discord.Embed(title="📊 Rangs par Faction", color=COULEURS["or_ancien"])
    for faction, rangs in RANGS_POINTS.items():
        lignes = "\n".join(f"{label} — {pts:,} pts" for _, pts, label in rangs)
        e.add_field(name=faction.capitalize(), value=lignes, inline=True)
    e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
    await poster(ch, e)

    # ── 6. bestiaire-infernal — 3 embeds ─────────────────────────────────────
    ch = find_ch("bestiaire")
    embeds_bestiaire = [
        {
            "titre": "倶舎那陀 — Les Kushanāda",
            "desc": (
                "Créatures titanesques aux allures de magistrats cosmiques. "
                "Ils ne punissent pas — ils maintiennent. "
                "Leur seul but : empêcher quiconque de s'échapper des Strates."
            ),
            "fields": [
                ("Apparence", "Silhouettes de juges aux yeux vides, portant des masses rituelles. "
                              "Taille variable selon la Strate — plus profond, plus imposants."),
                ("Comportement", "Passifs en l'absence de tentative d'évasion. "
                                 "Réactivité instantanée dès qu'une âme approche des limites."),
                ("Anomalie", "Depuis l'ouverture de la Fissure, certains Kushanāda semblent hésiter. "
                             "Comme si leurs instructions entraient en conflit avec quelque chose de nouveau."),
            ],
            "couleur": "gris_acier"
        },
        {
            "titre": "地獄の淋気 — Le Jigoku no Rinki",
            "desc": (
                "Sphères noires de Reishi corrompu suintant des murs de l'Enfer depuis la Fissure. "
                "Contact prolongé dissout progressivement l'identité spirituelle."
            ),
            "fields": [
                ("Symptômes", "Mémoire fragmentée, puissance instable, "
                              "réminiscences involontaires d'avant la mort."),
                ("Danger", "Irréversible au stade avancé. "
                           "L'âme commence à se fondre dans la matière infernale."),
                ("Usage contrôlé", "Certains Togabito anciens ont appris à le canaliser. "
                                    "Risque extrême. Pouvoir disproportionné."),
            ],
            "couleur": "pourpre_infernal"
        },
        {
            "titre": "虚 — Les Hollow Infernaux",
            "desc": (
                "Hollow ayant sombré en Enfer plutôt que d'être purifiés. "
                "Mutation profonde due au Reishi infernal. "
                "Plus dangereux et moins prévisibles que leurs équivalents standard."
            ),
            "fields": [
                ("Différences", "Masque partiellement dissous. Cero noir. "
                                "Instinct partiellement remplacé par une logique primitive."),
                ("Comportement", "Ni sauvages ni organisés — quelque chose entre les deux. "
                                 "Semblent reconnaître une hiérarchie non formalisée."),
                ("Mystère", "Certains semblent reconnaître les Togabito anciens "
                            "et ne pas les attaquer. Raison inconnue."),
            ],
            "couleur": "noir_abyssal"
        },
    ]
    for data in embeds_bestiaire:
        e = discord.Embed(title=data["titre"], description=data["desc"], color=COULEURS[data["couleur"]])
        for nom, val in data["fields"]:
            e.add_field(name=nom, value=val, inline=False)
        e.set_footer(text="⸻ Infernum Aeterna · Bestiaire ⸻")
        await poster(ch, e)

    # ── 7. pacte-des-ames — 1 embed ──────────────────────────────────────────
    ch = find_ch("pacte")
    e = discord.Embed(
        title="⚖️ Le Pacte des Âmes",
        description=(
            "En entrant dans **Infernum Aeterna**, chaque âme prête les serments suivants.\n\u200b"
        ),
        color=COULEURS["or_ancien"]
    )
    serments = [
        ("① Respect narratif",     "Je respecte le fil narratif de chaque joueur sans l'interrompre sans accord."),
        ("② Consentement",         "Je n'impose aucune action à un personnage sans le consentement de son joueur."),
        ("③ Transparence",         "J'informe le staff avant toute mort narrative ou séquence traumatisante."),
        ("④ Cohérence lore",       "Je reste en accord avec le lore du serveur et consulte en cas de doute."),
        ("⑤ Séparation IC/HorRP",  "Je n'utilise pas d'informations hors-RP dans le jeu (no méta-gaming)."),
        ("⑥ Signalement",          "Je signale tout manquement au staff plutôt que d'y répondre seul."),
        ("⑦ Accueil",              "J'accueille les nouveaux joueurs avec la même patience qu'on m'a accordée."),
        ("⑧ Espace partagé",       "Je ne monopolise pas les zones narratives importantes."),
        ("⑨ Respect des décisions", "J'accepte les décisions du staff même en désaccord, puis j'en débats par écrit."),
        ("⑩ Contribution",         "Je contribue activement à faire de ce serveur une expérience mémorable."),
    ]
    for nom, texte in serments:
        e.add_field(name=nom, value=texte, inline=False)
    e.add_field(name="\u200b", value="*「 Ces serments ne sont pas des règles. Ils sont la fondation. 」*", inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
    await poster(ch, e)

    # ── 8. modele-de-fiche — 2 embeds ────────────────────────────────────────
    ch = find_ch("modele-de-fiche")
    modele = (
        "```\n"
        "═══════════════════════════════\n"
        "   FICHE PERSONNAGE — INFERNUM AETERNA\n"
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
    e1 = discord.Embed(title="📋 Modèle de Fiche Personnage", description=modele, color=COULEURS["blanc_seireitei"])
    e1.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e1)

    e2 = discord.Embed(title="📥 Comment soumettre votre fiche", color=COULEURS["or_pale"])
    e2.add_field(name="Étape 1", value="Copiez le modèle ci-dessus dans un éditeur de texte.", inline=False)
    e2.add_field(name="Étape 2", value="Remplissez chaque section. Minimum 300 mots pour l'Histoire.", inline=False)
    e2.add_field(name="Étape 3", value="Rendez-vous dans `📥・soumission-de-fiche`.", inline=False)
    e2.add_field(name="Étape 4", value="Tapez `/fiche-soumettre` et collez votre fiche dans le formulaire.", inline=False)
    e2.add_field(name="Délai", value="Le staff valide sous 48h. Vous recevrez une notification en DM.", inline=False)
    e2.add_field(name="Après validation", value="Rôle faction + accès aux zones RP attribués automatiquement.", inline=False)
    e2.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e2)


# ══════════════════════════════════════════════════════════════════════════════
#  VUES (boutons persistants)
# ══════════════════════════════════════════════════════════════════════════════

class BoutonsFaction(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        factions = [
            ("死神 Shinigami", "shinigami", discord.ButtonStyle.secondary),
            ("咎人 Togabito",  "togabito",  discord.ButtonStyle.danger),
            ("破面 Arrancar",  "arrancar",  discord.ButtonStyle.secondary),
            ("滅却師 Quincy",  "quincy",    discord.ButtonStyle.primary),
        ]
        for label, cle, style in factions:
            btn = discord.ui.Button(label=label, style=style, custom_id=f"faction_{cle}")
            btn.callback = self._make_callback(cle)
            self.add_item(btn)

    def _make_callback(self, cle):
        async def callback(interaction: discord.Interaction):
            roles_ids = charger_roles()
            guild = interaction.guild
            role_id = roles_ids.get(cle)
            if not role_id:
                await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
                return
            role = guild.get_role(role_id)
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable sur ce serveur.", ephemeral=True)
                return
            member = interaction.user
            factions_cles = ["shinigami", "togabito", "arrancar", "quincy"]
            roles_a_retirer = [
                guild.get_role(roles_ids[c])
                for c in factions_cles
                if c in roles_ids and guild.get_role(roles_ids[c]) in member.roles
            ]
            roles_a_retirer = [r for r in roles_a_retirer if r]
            if roles_a_retirer:
                await member.remove_roles(*roles_a_retirer, reason="Changement de faction")
            await member.add_roles(role, reason=f"Faction choisie : {cle}")
            await interaction.response.send_message(
                f"⚔️ Vous avez rejoint la faction **{role.name}**.", ephemeral=True
            )
        return callback


class BoutonCombat(discord.ui.View):
    def __init__(self, faction):
        super().__init__(timeout=None)
        self.faction = faction

    @discord.ui.button(label="⚔️ Initier un Combat", style=discord.ButtonStyle.danger, custom_id="initier_combat")
    async def initier(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Le vrai traitement est dans le cog Combat
        await interaction.response.send_modal(ModalCombat())


class ModalCombat(discord.ui.Modal, title="Initier un Combat"):
    adversaire = discord.ui.TextInput(
        label="Mention de l'adversaire (@pseudo)",
        placeholder="@Nom#0000",
        required=True,
        max_length=100
    )
    titre_combat = discord.ui.TextInput(
        label="Titre du combat",
        placeholder="Ex : Le Duel des Abysses",
        required=True,
        max_length=100
    )
    contexte = discord.ui.TextInput(
        label="Contexte narratif (optionnel)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Délégué au cog Combat via le bot
        cog_combat = interaction.client.cogs.get("Combat")
        if cog_combat:
            await cog_combat.creer_fil_combat(interaction, self.adversaire.value, self.titre_combat.value, self.contexte.value)
        else:
            await interaction.response.send_message("❌ Module de combat indisponible.", ephemeral=True)


class BoutonsAbonnements(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        abonnements = [
            ("📣 Annonces",       "abonne_annonces"),
            ("🎲 Événements",     "evenement_actif"),
            ("🎭 RP Ouvert",      "rp_ouvert"),
            ("🔔 Narrateur",      "narrateur_ping"),
        ]
        for label, cle in abonnements:
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, custom_id=f"abo_{cle}")
            btn.callback = self._make_callback(cle)
            self.add_item(btn)

    def _make_callback(self, cle):
        async def callback(interaction: discord.Interaction):
            roles_ids = charger_roles()
            guild = interaction.guild
            role_id = roles_ids.get(cle)
            if not role_id:
                await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
                return
            role = guild.get_role(role_id)
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable sur ce serveur.", ephemeral=True)
                return
            member = interaction.user
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(f"🔕 Désabonné de **{role.name}**.", ephemeral=True)
            else:
                await member.add_roles(role)
                await interaction.response.send_message(f"🔔 Abonné à **{role.name}**.", ephemeral=True)
        return callback


def _cle_channel(nom: str) -> str:
    """Transforme un nom de channel Discord en clé normalisée pour channels_ids.json.
    Ex: '📖・infernum-aeterna' → 'infernum-aeterna'
    """
    import re
    # Retirer emojis et séparateur ・
    cleaned = re.sub(r"[^\w\s-]", "", nom).strip().lstrip("・").strip()
    # Prendre la partie après le dernier espace ou ・ si c'est un emoji suivi de texte
    parts = nom.split("・", 1)
    if len(parts) == 2:
        cleaned = parts[1].strip()
    return cleaned.lower().replace(" ", "-")


async def setup(bot):
    await bot.add_cog(Construction(bot))
