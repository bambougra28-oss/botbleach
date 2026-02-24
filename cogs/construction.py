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
import re
import logging
from typing import Optional

from config import COULEURS
from data.structure_serveur import ROLES, CATEGORIES, FORUM_TAGS_RP

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
        warnings = []

        # ── 1+2. Synchroniser les rôles (réutilise les existants) ────────────
        log.info("[SETUP] Phase 1 — Synchronisation des rôles…")
        r = await self._sync_roles_impl(guild)
        log.info("[SETUP] Rôles : %d créé(s), %d mis à jour, %d inchangé(s), %d obsolète(s) supprimé(s)",
                 r["crees"], r["maj"], r["ignores"], r["supprimes"])

        roles_map = _build_roles_map(guild)

        # ── 3. Supprimer TOUS les channels existants ───────────────────────────
        log.info("[SETUP] Phase 3 — Suppression des channels existants…")
        for channel in list(guild.channels):
            try:
                await channel.delete(reason="Setup Infernum Aeterna")
                await asyncio.sleep(0.5)
            except Exception as e:
                warnings.append(f"⚠️ Channel non supprimable : {channel.name}")
                log.warning("[SETUP] Channel non supprimable %s : %s", channel.name, e)

        # ── 4. Créer catégories et channels ───────────────────────────────────
        log.info("[SETUP] Phase 4 — Création des catégories et channels…")
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
                log.info("[SETUP]   Catégorie : %s", cat_def["nom"])
            except Exception as e:
                warnings.append(f"❌ Catégorie {cat_def['nom']} : {e}")
                log.error("[SETUP] Catégorie %s : %s", cat_def['nom'], e)
                continue

            await asyncio.sleep(0.5)

            for ch_def in cat_def.get("channels", []):
                try:
                    overrides = _construire_permissions_channel(ch_def, cat_def, roles_map, role_everyone)

                    if ch_def.get("type") == "forum":
                        # Construire les tags pour les forums RP
                        tags_kwargs = {}
                        if ch_def.get("forum_tags"):
                            tags_kwargs["available_tags"] = [
                                discord.ForumTag(name=t["nom"]) for t in FORUM_TAGS_RP
                            ]
                        channel = await guild.create_forum(
                            name=ch_def["nom"],
                            category=categorie,
                            topic=ch_def.get("sujet", ""),
                            overwrites=overrides,
                            reason="Setup Infernum Aeterna",
                            **tags_kwargs
                        )
                    else:
                        channel = await guild.create_text_channel(
                            name=ch_def["nom"],
                            category=categorie,
                            topic=ch_def.get("sujet", ""),
                            overwrites=overrides,
                            reason="Setup Infernum Aeterna"
                        )
                    await asyncio.sleep(0.5)
                    await _envoyer_message_initial(channel, ch_def, roles_map)

                    # Enregistrer l'ID du channel (clé = nom nettoyé)
                    cle_ch = _cle_channel(ch_def["nom"])
                    channels_map[cle_ch] = channel.id

                    # Capturer le canal staff pour le résumé final
                    if "configuration-bot" in ch_def["nom"] or "discussions-staff" in ch_def["nom"]:
                        channel_staff = channel

                except Exception as e:
                    warnings.append(f"❌ Channel {ch_def['nom']} : {e}")
                    log.error("[SETUP] Channel %s : %s", ch_def['nom'], e, exc_info=True)

        # ── 4b. Sauvegarder les IDs des channels ─────────────────────────────
        sauvegarder_channels(channels_map)
        log.info("[SETUP] %d channels créés, IDs sauvegardés", len(channels_map))

        # ── 5. Peupler les channels lore & administration ────────────────────
        log.info("[SETUP] Phase 5 — Peuplement du lore…")
        try:
            await _peupler_channels_lore(guild)
            log.info("[SETUP] Lore peuplé avec succès")
        except Exception as e:
            warnings.append(f"❌ Peuplement lore : {e}")
            log.error("[SETUP] Peuplement lore : %s", e, exc_info=True)

        # ── Résumé — posté dans le canal staff nouvellement créé ──────────────
        embed = discord.Embed(
            title="⛩️ Infernum Aeterna · Construction terminée",
            description=(
                f"**{len(roles_map)}** rôles synchronisés ({r['crees']} créé(s), {r['maj']} mis à jour)\n"
                f"**{sum(len(c['channels']) for c in CATEGORIES)}** channels créés\n"
                f"**{len(CATEGORIES)}** catégories créées"
            ),
            color=COULEURS["or_ancien"]
        )
        if warnings:
            embed.add_field(
                name="⚠️ Avertissements",
                value="\n".join(warnings[:10]) + ("\n…" if len(warnings) > 10 else ""),
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
                await asyncio.sleep(0.5)
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

        Délai de 5s entre chaque appel API rôle — Discord rate-limit sévèrement
        cet endpoint. discord.py gère les 429 en interne (retry silencieux).
        """
        roles_ids = charger_roles()
        cles_attendues = {r["cle"] for r in ROLES}
        crees, maj, ignores, supprimes = 0, 0, 0, 0
        total = len(ROLES)
        ROLE_DELAY = 5  # secondes entre chaque appel API rôle

        for idx, role_def in enumerate(sorted(ROLES, key=lambda r: r["position"], reverse=True), 1):
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
                    log.info("sync-roles [%d/%d] MAJ en cours : %s …", idx, total, nom_attendu)
                    try:
                        await existant.edit(
                            name=nom_attendu,
                            color=discord.Color(couleur_attendue),
                            hoist=hoist_attendu,
                            mentionable=mention_attendue,
                            reason="Actualisation Infernum Aeterna"
                        )
                        maj += 1
                        log.info("sync-roles [%d/%d] MAJ OK : %s", idx, total, nom_attendu)
                    except Exception as e:
                        log.error("sync-roles: erreur MAJ %s : %s", nom_attendu, e)
                    await asyncio.sleep(ROLE_DELAY)
                else:
                    ignores += 1
                continue

            # Rôle inexistant → créer
            log.info("sync-roles [%d/%d] Création en cours : %s …", idx, total, nom_attendu)
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
                log.info("sync-roles [%d/%d] CRÉÉ : %s", idx, total, nom_attendu)
            except Exception as e:
                log.error("sync-roles: erreur création %s : %s", nom_attendu, e)
            await asyncio.sleep(ROLE_DELAY)

        # Supprimer les rôles obsolètes (dans roles_ids.json mais plus dans ROLES)
        cles_obsoletes = set(roles_ids.keys()) - cles_attendues
        for cle_obs in cles_obsoletes:
            role_obs = guild.get_role(roles_ids[cle_obs])
            if role_obs:
                log.info("sync-roles: suppression obsolète : %s …", cle_obs)
                try:
                    await role_obs.delete(reason="Rôle obsolète — Actualisation Infernum Aeterna")
                    supprimes += 1
                except Exception as e:
                    log.error("sync-roles: erreur suppression %s : %s", cle_obs, e)
                await asyncio.sleep(ROLE_DELAY)
            del roles_ids[cle_obs]

        sauvegarder_roles(roles_ids)
        log.info("sync-roles terminé : %d créé(s), %d MAJ, %d inchangé(s), %d supprimé(s)",
                 crees, maj, ignores, supprimes)
        return {"crees": crees, "maj": maj, "ignores": ignores, "supprimes": supprimes}

    # ── /sync-permissions ─────────────────────────────────────────────────────
    @app_commands.command(
        name="sync-permissions",
        description="[ADMIN] Resynchronise les permissions de tous les channels selon la structure définie."
    )
    @app_commands.default_permissions(administrator=True)
    async def sync_permissions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        resultats = await _sync_permissions_impl(guild)
        embed = discord.Embed(
            title="🔒 Synchronisation des permissions terminée",
            description=(
                f"**{resultats['categories']}** catégorie(s) mise(s) à jour\n"
                f"**{resultats['channels']}** channel(s) mis à jour"
            ),
            color=COULEURS["or_ancien"]
        )
        if resultats["warnings"]:
            embed.add_field(
                name="⚠️ Avertissements",
                value="\n".join(resultats["warnings"][:10]),
                inline=False
            )
        embed.set_footer(text="⸻ Infernum Aeterna ⸻")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /actualiser ──────────────────────────────────────────────────────────
    @app_commands.command(
        name="actualiser",
        description="[ADMIN] Met à jour rôles, channels et/ou lore pour coller au code actuel."
    )
    @app_commands.describe(
        cible="Quoi actualiser (défaut : tout sauf lore)",
    )
    @app_commands.choices(cible=[
        app_commands.Choice(name="Infrastructure (rôles + permissions + channels)", value="infra"),
        app_commands.Choice(name="Rôles uniquement", value="roles"),
        app_commands.Choice(name="Permissions uniquement", value="permissions"),
        app_commands.Choice(name="Channels (scan IDs)", value="channels"),
        app_commands.Choice(name="Lore → choisir les channels", value="lore"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def actualiser(self, interaction: discord.Interaction, cible: str = "infra"):
        guild = interaction.guild

        # ── Lore : afficher le menu de sélection ───────────────────────────
        if cible == "lore":
            # Détecter les channels lore existants sur le serveur
            channels_trouves = []
            for cle in CLES_LORE:
                ch = trouver_channel(guild, cle)
                if ch:
                    channels_trouves.append((cle, ch))

            if not channels_trouves:
                await interaction.response.send_message(
                    "❌ Aucun channel lore trouvé sur ce serveur.", ephemeral=True
                )
                return

            view = SelectLoreView(self.bot, guild, channels_trouves)
            embed = discord.Embed(
                title="📝 Actualisation du Lore",
                description=(
                    f"**{len(channels_trouves)}** channels lore détectés.\n\n"
                    "Sélectionnez les channels à actualiser ci-dessous.\n"
                    "Le contenu existant du bot sera **remplacé** (pas de doublons)."
                ),
                color=COULEURS["or_ancien"]
            )
            embed.set_footer(text="⸻ Infernum Aeterna ⸻")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

        # ── Infrastructure (pas de lore) ───────────────────────────────────
        await interaction.response.defer(ephemeral=True)
        rapport = []

        # 1. Rôles
        if cible in ("infra", "roles"):
            r = await self._sync_roles_impl(guild)
            rapport.append(
                f"**Rôles** : {r['crees']} créé(s), {r['maj']} mis à jour, "
                f"{r['ignores']} inchangé(s), {r['supprimes']} obsolète(s) supprimé(s)"
            )

        # 2. Permissions
        if cible in ("infra", "permissions"):
            r = await _sync_permissions_impl(guild)
            rapport.append(
                f"**Permissions** : {r['categories']} catégorie(s), {r['channels']} channel(s) mis à jour"
                + (f" ({len(r['warnings'])} avertissement(s))" if r['warnings'] else "")
            )

        # 3. Channels (scan IDs)
        if cible in ("infra", "channels"):
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

        # Résumé
        embed = discord.Embed(
            title="⛩️ Actualisation terminée",
            description="\n".join(f"• {l}" for l in rapport),
            color=COULEURS["or_ancien"]
        )
        embed.set_footer(text="⸻ Infernum Aeterna ⸻")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /refresh-lore (raccourci → actualise tout le lore d'un coup) ────────
    @app_commands.command(
        name="refresh-lore",
        description="[ADMIN] Remplace tout le lore dans tous les channels d'un coup."
    )
    @app_commands.default_permissions(administrator=True)
    async def refresh_lore(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        nettoyees = 0
        for cle in CLES_LORE:
            ch = trouver_channel(guild, cle)
            if ch:
                nettoyees += await _nettoyer_channel_bot(ch, self.bot.user)

        await _peupler_channels_lore(guild)
        await interaction.followup.send(
            f"✅ Lore rafraîchi : {nettoyees} ancien(s) message(s) remplacé(s) dans {len(CLES_LORE)} channels.",
            ephemeral=True
        )


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS — ROLES MAP & SYNC PERMISSIONS
# ══════════════════════════════════════════════════════════════════════════════

def _build_roles_map(guild):
    """Construit le mapping {cle_role: discord.Role} depuis roles_ids.json."""
    roles_ids = charger_roles()
    roles_map = {}
    for role_def in ROLES:
        rid = roles_ids.get(role_def["cle"])
        if rid:
            role = guild.get_role(rid)
            if role:
                roles_map[role_def["cle"]] = role
    return roles_map


async def _sync_permissions_impl(guild):
    """Resynchronise les permissions de toutes les catégories et channels existants
    selon la structure définie dans structure_serveur.py.
    Retourne un dict {categories, channels, warnings}.
    """
    roles_map = _build_roles_map(guild)
    everyone = guild.default_role
    cat_count, ch_count = 0, 0
    warnings = []

    for cat_def in CATEGORIES:
        # Trouver la catégorie par substring
        cat_nom = cat_def["nom"]
        categorie = None
        for cat in guild.categories:
            if cat_nom.lower() in cat.name.lower() or cat.name.lower() in cat_nom.lower():
                categorie = cat
                break
        if not categorie:
            warnings.append(f"Catégorie introuvable : {cat_nom}")
            continue

        # Appliquer les permissions catégorie
        perms_cat = _construire_permissions_categorie(cat_def, roles_map, everyone)
        try:
            await categorie.edit(overwrites=perms_cat)
            cat_count += 1
        except Exception as e:
            warnings.append(f"Erreur catégorie {cat_nom} : {e}")
        await asyncio.sleep(0.5)

        # Parcourir les channels de cette catégorie
        for ch_def in cat_def.get("channels", []):
            cle_def = _cle_channel(ch_def["nom"])
            channel = None
            for ch in categorie.channels:
                if _cle_channel(ch.name) == cle_def:
                    channel = ch
                    break
            if not channel:
                warnings.append(f"Channel introuvable : {ch_def['nom']}")
                continue

            perms_ch = _construire_permissions_channel(ch_def, cat_def, roles_map, everyone)
            try:
                await channel.edit(overwrites=perms_ch)
                ch_count += 1
            except Exception as e:
                warnings.append(f"Erreur channel {ch_def['nom']} : {e}")
            await asyncio.sleep(0.5)

    return {"categories": cat_count, "channels": ch_count, "warnings": warnings}


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS — PERMISSIONS
# ══════════════════════════════════════════════════════════════════════════════

def _construire_permissions_categorie(cat_def, roles_map, role_everyone):
    """Construit le dict d'overwrites pour une catégorie."""
    perms = {}
    cat_perms = cat_def.get("permissions", {})
    visible_a = cat_def.get("visible_a")

    if visible_a:
        # Catégorie gatée par un rôle (voyageur, personnage_valide, etc.)
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)
        if visible_a in roles_map:
            perms[roles_map[visible_a]] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=cat_perms.get("everyone_send", False)
            )
    elif cat_perms.get("everyone_view", True):
        perms[role_everyone] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=cat_perms.get("everyone_send", False)
        )
    else:
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)

    # Les 4 rôles staff ont toujours accès complet
    for cle_staff in ("architecte", "gardien_des_portes", "emissaire", "chroniqueur"):
        if cle_staff in roles_map:
            perms[roles_map[cle_staff]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_messages=True
            )

    return perms


def _construire_permissions_channel(ch_def, cat_def, roles_map, role_everyone):
    """Construit le dict d'overwrites pour un channel.

    Logique de permissions :
      1. Base @everyone — hérite de la catégorie (visible_a ou everyone_view)
      2. visible_a channel-level — override plus restrictif que la catégorie
      3. lecture_seule — personne n'écrit sauf staff
      4. evenement — caché par défaut, visible manuellement par le staff
      5. faction_write — UNE faction écrit, personnage_valide voit en lecture
      6. cross_faction — tous les personnages validés écrivent
      7. rank_write — seuls certains rangs écrivent
      8. Staff override — les 4 rôles staff ont accès complet
    """
    perms = {}
    cat_perms = cat_def.get("permissions", {})

    # ── 1. Base @everyone ─────────────────────────────────────────────────
    cat_visible_a = cat_def.get("visible_a")
    ch_visible_a = ch_def.get("visible_a")

    if ch_visible_a or cat_visible_a:
        # Channel ou catégorie gatée par un rôle
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)
        gate_role = ch_visible_a or cat_visible_a
        if gate_role in roles_map:
            # ecriture_gate force send=True sur le rôle gate même si la catégorie
            # est en lecture seule (ex: soumission-de-fiche, esprits-perdus)
            if ch_def.get("ecriture_gate"):
                can_send = not ch_def.get("lecture_seule", False)
            else:
                can_send = (not ch_def.get("lecture_seule", False)
                            and cat_perms.get("everyone_send", False))
            perms[roles_map[gate_role]] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=can_send
            )
    elif not cat_perms.get("everyone_view", True):
        # Catégorie staff-only (ex: STAFF — INVISIBLE)
        perms[role_everyone] = discord.PermissionOverwrite(view_channel=False)
    else:
        perms[role_everyone] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=not ch_def.get("lecture_seule", False)
                          and cat_perms.get("everyone_send", False)
        )

    # ── 2. Lecture seule ──────────────────────────────────────────────────
    if ch_def.get("lecture_seule"):
        if not (cat_visible_a or ch_visible_a):
            # Catégorie non gatée : tout le monde voit, personne n'écrit
            perms[role_everyone] = discord.PermissionOverwrite(
                view_channel=True, send_messages=False
            )
        # Si gatée, la visibilité est déjà restreinte et send_messages=False ci-dessus

    # ── 3. Événement (caché par défaut) ───────────────────────────────────
    if ch_def.get("evenement"):
        # Tout masquer sauf staff — le staff rendra visible manuellement
        perms = {role_everyone: discord.PermissionOverwrite(view_channel=False)}

    # ── 4. faction_write — UNE faction spécifique écrit ───────────────────
    faction = ch_def.get("faction_write")
    if faction:
        if faction in roles_map:
            perms[roles_map[faction]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )
        # personnage_valide peut voir mais pas écrire (touristes RP)
        pv = roles_map.get("personnage_valide")
        if pv:
            perms[pv] = discord.PermissionOverwrite(
                view_channel=True, send_messages=False
            )

    # ── 5. cross_faction — tous les personnages validés écrivent ──────────
    if ch_def.get("cross_faction"):
        pv = roles_map.get("personnage_valide")
        if pv:
            perms[pv] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

    # ── 6. rank_write — seuls certains rangs écrivent ─────────────────────
    ranks = ch_def.get("rank_write")
    if ranks:
        for rank_key in ranks:
            if rank_key in roles_map:
                perms[roles_map[rank_key]] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True
                )

    # ── 6b. faction_view — visibilité restreinte à une faction ──────────
    # Remplace le gate personnage_valide par le rôle de faction (lecture seule)
    # Les autres factions ne voient plus le channel du tout.
    faction_view = ch_def.get("faction_view")
    if faction_view and faction_view in roles_map:
        pv = roles_map.get("personnage_valide")
        if pv and pv in perms:
            del perms[pv]  # retirer le gate générique
        perms[roles_map[faction_view]] = discord.PermissionOverwrite(
            view_channel=True, send_messages=False
        )

    # ── 7. Staff override — les 4 rôles ──────────────────────────────────
    for cle_staff in ("architecte", "gardien_des_portes", "emissaire", "chroniqueur"):
        if cle_staff in roles_map:
            perms[roles_map[cle_staff]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True,
                manage_messages=True, manage_threads=True
            )

    return perms


async def _envoyer_message_initial(channel, ch_def, roles_map):
    """Envoie un message épinglé selon le type de channel."""
    try:
        if ch_def.get("boutons_faction") or ch_def.get("presentation_factions"):
            await _envoyer_presentation_factions(channel, roles_map)
        elif ch_def.get("combat"):
            await _envoyer_bouton_combat(channel, ch_def)
        elif ch_def.get("abonnements"):
            await _envoyer_boutons_abonnements(channel, roles_map)
        elif ch_def.get("valide_perso"):
            await _envoyer_instructions_fiche(channel)
        # Note : les forums RP avec scene_launcher reçoivent le bouton
        # via le cog Scenes dans setup_hook (BoutonScene persistant)
    except Exception as e:
        log.error("[SETUP] Message initial %s : %s", ch_def.get("nom", "?"), e, exc_info=True)


async def _envoyer_presentation_factions(channel, roles_map):
    """Poste la présentation narrative des factions (lecture seule, sans boutons)."""
    from cogs.lore import LORE_WEB_URL
    embed = discord.Embed(
        title="🎭 Les Quatre Destins · 運命を選べ",
        description=(
            "Quatre chemins. Quatre vérités qui ne se rejoignent pas.\n\n"
            "Lisez ce qui suit. Laissez une faction vous parler. Puis rendez-vous "
            "dans `📋・modele-de-fiche` pour donner forme à votre personnage. "
            "Après validation par le staff, vos rôles vous seront attribués."
        ),
        color=COULEURS["or_ancien"]
    )
    embed.add_field(
        name="死神 Shinigami · Les Gardiens",
        value=(
            "Soldats du Seireitei, liés par le devoir et le poids d'un mensonge "
            "millénaire. Leur lame porte un nom. Leur honneur porte des fissures."
        ),
        inline=False
    )
    embed.add_field(
        name="咎人 Togabito · Les Damnés",
        value=(
            "Âmes enchaînées aux Strates, forgées par des siècles de mort et de "
            "résurrection. Certains n'y voient qu'une prison. D'autres ont "
            "commencé à y voir un trône."
        ),
        inline=False
    )
    embed.add_field(
        name="破面 Arrancar · Les Masques Brisés",
        value=(
            "Des Hollow qui ont arraché leur masque pour toucher quelque chose "
            "d'humain en dessous. Las Noches tremble, et le vide dans leur "
            "poitrine résonne avec la Fissure."
        ),
        inline=False
    )
    embed.add_field(
        name="滅却師 Quincy · Les Survivants",
        value=(
            "Héritiers d'un empire décimé, cachés dans l'ombre du Monde des "
            "Vivants. Le Reishi chante dans leur sang, et le sang n'oublie pas."
        ),
        inline=False
    )
    embed.add_field(
        name="📜 En savoir plus",
        value=f"[Lire le lore complet des factions]({LORE_WEB_URL}#creation)",
        inline=False
    )
    embed.set_footer(text="⸻ Infernum Aeterna · Le Destin ⸻")
    msg = await channel.send(embed=embed)
    await msg.pin()


async def _envoyer_bouton_combat(channel, ch_def):
    faction = ch_def.get("faction_write", "tous")
    embed = discord.Embed(
        title="⚔️ Initier un Combat",
        description=(
            "Pressez le bouton ci-dessous pour ouvrir un fil de combat "
            "avec votre adversaire. Un espace privé sera créé, visible "
            "uniquement par les deux combattants et le staff.\n\n"
            "「 Tout affrontement requiert la validation d'un Émissaire. 」"
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
            "Choisissez ce qui vous parvient. Chaque bouton active ou désactive "
            "un type de notification. Un clic pour s'abonner, un second pour se désinscrire."
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
            "Copiez le modèle disponible dans `📋・modele-de-fiche`, "
            "remplissez-le, soumettez-le ici.\n\n"
            "Le staff lira votre fiche et vous répondra sous 48 heures. "
            "Après validation, elle rejoindra les archives de "
            "`✅・fiches-validees` et vos rôles seront attribués.\n\n"
            "「 Aucune réécriture imposée sans consultation. 」"
        ),
        color=COULEURS["blanc_seireitei"]
    )
    await channel.send(embed=embed)


# ══════════════════════════════════════════════════════════════════════════════
#  PEUPLEMENT DES CHANNELS LORE & ADMINISTRATION
# ══════════════════════════════════════════════════════════════════════════════

async def _nettoyer_channel_bot(channel, bot_user):
    """Supprime tous les messages du bot dans un channel (unpin + delete)."""
    if not channel:
        return 0
    count = 0
    try:
        async for msg in channel.history(limit=50):
            if msg.author == bot_user:
                if msg.pinned:
                    try:
                        await msg.unpin()
                    except Exception:
                        pass
                await msg.delete()
                count += 1
                await asyncio.sleep(0.3)
    except Exception as e:
        log.error("nettoyage %s : %s", getattr(channel, 'name', '?'), e)
    return count


# Clés de tous les channels lore, dans l'ordre de peuplement
CLES_LORE = [
    "fissure-du-monde", "infernum-aeterna", "les-quatre-factions", "geographie",
    "glossaire", "systeme", "bestiaire", "pacte", "modele-de-fiche",
    "figures-de-legende", "etat-de-la-fissure", "tableau-des-missions",
    "hierarchie-des-espada", "veille-de-la-fissure", "etat-de-la-frontiere",
    "incidents-repertories", "progression", "objectifs-narratifs", "esprits-perdus"
]

# Labels humains pour le menu de sélection
LABELS_LORE = {
    "fissure-du-monde": "Fissure du Monde (bienvenue)",
    "infernum-aeterna": "Infernum Aeterna (lore fondateur)",
    "les-quatre-factions": "Les Quatre Factions",
    "geographie": "Géographie des Mondes",
    "glossaire": "Glossaire",
    "systeme": "Système et Compétences",
    "bestiaire": "Bestiaire Infernal",
    "pacte": "Pacte des Âmes",
    "modele-de-fiche": "Modèle de Fiche",
    "figures-de-legende": "Figures de Légende",
    "etat-de-la-fissure": "État de la Fissure",
    "tableau-des-missions": "Tableau des Missions",
    "hierarchie-des-espada": "Hiérarchie des Espada",
    "veille-de-la-fissure": "Veille de la Fissure (Quincy)",
    "etat-de-la-frontiere": "État de la Frontière",
    "incidents-repertories": "Incidents Répertoriés",
    "progression": "Progression",
    "objectifs-narratifs": "Objectifs Narratifs",
    "esprits-perdus": "Esprits Perdus (FAQ)",
}


async def _peupler_channels_lore(guild: discord.Guild, cles_cibles: list[str] | None = None):
    """Poste le lore dans les channels CHRONIQUES et ADMINISTRATION.

    Si *cles_cibles* est None → tous les channels.
    Sinon → seulement les channels dont la clé est dans la liste.
    """
    from cogs.lore import GLOSSAIRE, FICHES_FACTION, STRATES, LORE_DATA
    from cogs.personnage import RANGS_POINTS
    from cogs.aptitudes import APTITUDES_WEB_URL

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
            await asyncio.sleep(0.3)
        except Exception as e:
            log.error("[LORE] %s : %s", getattr(channel, 'name', '?'), e)

    def doit(cle: str) -> bool:
        """Retourne True si ce channel doit être peuplé."""
        if cles_cibles is None:
            return True
        return cle in cles_cibles

    # ── 0. Lien web lore ──────────────────────────────────────────────────────
    from cogs.lore import LORE_WEB_URL, _ajouter_lien_web

    # ── 0b. fissure-du-monde — embed statique de bienvenue ──────────────────
    ch_fissure = find_ch("fissure-du-monde")
    if ch_fissure and doit("fissure-du-monde"):
        e_bienvenue = discord.Embed(
            title="🩸 Infernum Aeterna · 地獄の門",
            description=(
                "Les Portes de l'Enfer se sont ouvertes.\n\n"
                "**Infernum Aeterna** est un serveur de jeu de rôle par forum, "
                "univers alternatif inspiré de Bleach. Quatre factions, une "
                "Fissure qui s'élargit, et votre personnage au milieu.\n\n"
                "Trois étapes avant d'entrer dans le récit."
            ),
            color=COULEURS["pourpre_infernal"]
        )
        e_bienvenue.add_field(
            name="⚖️ Étape 1 · Le Pacte",
            value="Rendez-vous dans `⚖️・pacte-des-âmes` et prêtez serment.",
            inline=False
        )
        e_bienvenue.add_field(
            name="🎭 Étape 2 · Les Factions",
            value="Explorez `🎭・choisir-son-destin` pour découvrir les quatre factions.",
            inline=False
        )
        e_bienvenue.add_field(
            name="📋 Étape 3 · Votre Personnage",
            value="Créez-le via `📋・modele-de-fiche` et soumettez-le dans `📥・soumission-de-fiche`. Le staff validera et vous attribuera vos rôles.",
            inline=False
        )
        e_bienvenue.add_field(
            name="📜 Lore complet",
            value=f"[Ouvrir les Chroniques des Quatre Races]({LORE_WEB_URL})",
            inline=False
        )
        e_bienvenue.set_footer(text="⸻ Infernum Aeterna · La Fissure s'élargit ⸻")
        msg_b = await ch_fissure.send(embed=e_bienvenue)
        try:
            await msg_b.pin()
        except Exception:
            pass
        await asyncio.sleep(0.3)

    # ── 1. infernum-aeterna — embed lien web + 5 embeds lore fondateur ──────
    ch = find_ch("infernum-aeterna") if doit("infernum-aeterna") else None

    # Embed d'accueil avec lien vers le lore complet
    e_web = discord.Embed(
        title="⛩️ Chroniques des Quatre Races",
        description=(
            "Les résumés ci-dessous couvrent les fondations du lore d'**Infernum "
            "Aeterna**. Le texte intégral, quinze mille mots en quatre chroniques, "
            "est disponible sur la page dédiée."
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
    ch = find_ch("les-quatre-factions") if doit("les-quatre-factions") else None
    for faction_key in ["shinigami", "togabito", "arrancar", "quincy"]:
        fiche = FICHES_FACTION[faction_key]
        e = discord.Embed(title=fiche["titre"], color=fiche["couleur"])
        for nom_section, texte_section in fiche["sections"]:
            e.add_field(name=nom_section, value=texte_section, inline=False)
        e.set_footer(text="⸻ Infernum Aeterna · Factions ⸻")
        _ajouter_lien_web(e, fiche.get("web_fragment", ""))
        await poster(ch, e)

    # ── 3. geographie-des-mondes — 2 embeds ──────────────────────────────────
    ch = find_ch("geographie") if doit("geographie") else None
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
            "**Soul Society** abrite les Shinigami. Au centre, le Seireitei : "
            "murs blancs, secrets anciens. Autour, le Rukongai où les âmes "
            "ordinaires vivent et meurent une seconde fois. Le Gotei 13 gouverne, "
            "fragilisé par la vérité du Konsō Reisai.\n\n"
            "**Hueco Mundo** est le désert éternel des Hollow. Las Noches s'y "
            "élève, empilée sur des générations de conquérants Arrancar. Depuis "
            "la Fissure, une résonance croissante avec le Jigoku no Rinki "
            "traverse ses sables.\n\n"
            "**Le Monde des Vivants** subit les conséquences sans les comprendre. "
            "Des portails instables s'ouvrent près de Karakura. La contamination "
            "spirituelle progresse, imperceptible pour les humains ordinaires.\n\n"
            "**La Frontière** (境界, Kyōkai). Le vide entre les mondes, révélé par "
            "la Fissure. Des fragments arrachés aux mondes adjacents y dérivent dans "
            "un espace parcouru de courants de Reishi brut. Quatre races s'y croisent. "
            "Aucune ne la contrôle. Chaque semaine, elle grandit."
        ),
        color=COULEURS["gris_acier"]
    )
    e2.set_footer(text="⸻ Infernum Aeterna · Géographie ⸻")
    await poster(ch, e2)

    # ── 4. glossaire — embeds par groupes de 5 ───────────────────────────────
    ch = find_ch("glossaire") if doit("glossaire") else None
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
    ch = find_ch("systeme") if doit("systeme") else None
    data_sys = LORE_DATA["systeme"]
    e = discord.Embed(title=data_sys["titre"], description=data_sys["description"], color=data_sys["couleur"])
    for nom_champ, valeur_champ in data_sys.get("fields", []):
        e.add_field(name=nom_champ, value=valeur_champ, inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
    await poster(ch, e)

    e = discord.Embed(title="📊 Rangs par Faction", color=COULEURS["or_ancien"])
    for faction, rangs in RANGS_POINTS.items():
        lignes = "\n".join(f"{label} · {pts:,} pts" for _, pts, label in rangs)
        e.add_field(name=faction.capitalize(), value=lignes, inline=True)
    e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
    await poster(ch, e)

    # ── 5b. systeme-et-competences — résumé aptitudes + lien web ─────────────
    try:
        e = discord.Embed(
            title="🔮 Aptitudes et Voies de Combat",
            description=(
                "Chaque faction dispose de **quatre Voies** qui définissent le style "
                "de combat de votre personnage. En progressant, vous débloquez un "
                "budget de **Reiryoku** (霊力) à répartir librement entre ces Voies.\n\n"
                "Trois paliers par aptitude :\n"
                "🟢 **Éveil** — les fondamentaux (1 霊力)\n"
                "🔵 **Maîtrise** — la spécialisation (2 霊力)\n"
                "🟣 **Transcendance** — le sommet, réservé aux rangs élevés (3 霊力)\n\n"
                "Chaque Voie compte huit à dix aptitudes réparties sur ces paliers. "
                "Les combinaisons entre Voies forgent l'identité martiale du personnage."
            ),
            color=COULEURS["gris_acier"],
        )
        e.add_field(
            name="Voies par faction",
            value=(
                "⚔️ **Shinigami** — Zanjutsu · Kidō · Hohō · Hakuda\n"
                "🔥 **Togabito** — Jigokusari · Gōka · Saisei · Rinki\n"
                "💀 **Arrancar** — Cero · Hierro · Sonído · Resurrección\n"
                "✡️ **Quincy** — Reishi Sōsa · Blut · Hirenkyaku · Seikei"
            ),
            inline=False,
        )
        e.add_field(
            name="\u200b",
            value=f"🌐 **[Consulter le détail complet des aptitudes]({APTITUDES_WEB_URL})**",
            inline=False,
        )
        e.set_footer(text="⸻ Infernum Aeterna · Système ⸻")
        await poster(ch, e)
    except Exception as ex:
        log.warning("[LORE] Embed aptitudes résumé non posté : %s", ex)

    # ── 6. bestiaire-infernal — embeds ──────────────────────────────────────
    ch = find_ch("bestiaire") if doit("bestiaire") else None
    embeds_bestiaire = [
        {
            "titre": "倶舎那陀 Les Kushanāda",
            "desc": (
                "Créatures titanesques aux allures de magistrats cosmiques. "
                "Ils ne punissent pas : ils maintiennent. "
                "Leur seul but est d'empêcher quiconque de s'échapper des Strates."
            ),
            "fields": [
                ("Ce qu'on voit", "Des silhouettes de juges aux yeux vides, portant des masses "
                                  "rituelles. Leur taille varie selon la Strate : plus on descend, "
                                  "plus ils sont imposants."),
                ("Ce qu'on observe", "Ils restent passifs tant que personne ne tente de fuir. "
                                     "Dès qu'une âme approche des limites, la réaction est instantanée."),
                ("Ce qui a changé", "Depuis l'ouverture de la Fissure, certains Kushanāda semblent hésiter, "
                                    "comme si leurs instructions entraient en conflit avec quelque chose de nouveau."),
            ],
            "couleur": "gris_acier"
        },
        {
            "titre": "地獄の燐気 Le Jigoku no Rinki",
            "desc": (
                "Des sphères noires de Reishi corrompu suintent des murs de l'Enfer "
                "depuis la Fissure. Un contact prolongé dissout progressivement "
                "l'identité spirituelle de celui qui s'en approche."
            ),
            "fields": [
                ("Les premiers signes", "La mémoire se fragmente. La puissance devient instable. "
                                        "Des réminiscences involontaires d'avant la mort remontent à la surface."),
                ("Le point de non-retour", "Au stade avancé, le processus est irréversible. "
                                           "L'âme se fond dans la matière infernale, absorbée par l'Enfer lui-même."),
                ("Ceux qui osent", "Certains Togabito anciens ont appris à canaliser le Rinki. "
                                   "Le risque est extrême, mais le pouvoir qu'ils en tirent dépasse l'entendement."),
            ],
            "couleur": "pourpre_infernal"
        },
        {
            "titre": "虚 Les Hollow Infernaux",
            "desc": (
                "Des Hollow ayant sombré en Enfer plutôt que d'être purifiés. "
                "Le Reishi infernal les a profondément altérés, les rendant "
                "plus dangereux et moins prévisibles que leurs semblables."
            ),
            "fields": [
                ("Ce qui les distingue", "Leur masque est partiellement dissous. Leur Cero tire vers le noir. "
                                         "L'instinct brut a cédé la place à une logique primitive, plus inquiétante."),
                ("Leur comportement", "Ils ne sont ni sauvages ni organisés, mais quelque chose entre les deux. "
                                      "Ils semblent reconnaître une hiérarchie qui n'a jamais été formalisée."),
                ("L'énigme", "Certains semblent reconnaître les Togabito anciens "
                             "et ne pas les attaquer. Personne ne sait pourquoi."),
            ],
            "couleur": "noir_abyssal"
        },
        {
            "titre": "虚 Les Hollow · Évolution naturelle",
            "desc": (
                "Toute âme humaine qui ne trouve pas le chemin de Soul Society "
                "finit par se consumer de l'intérieur. Le cœur se creuse, le masque "
                "apparaît, et ce qui reste n'est plus qu'instinct et faim."
            ),
            "fields": [
                ("Gillian (メノスグランデ)", "La première forme d'évolution collective. Des centaines de "
                                             "Hollow fusionnent en un colosse aveugle, lent et massif. "
                                             "Une conscience dominante peut émerger du magma d'âmes, "
                                             "mais la plupart errent sans direction."),
                ("Adjuchas (中級大虚)", "L'Adjuchas a conservé sa volonté individuelle. Plus petit, "
                                        "plus rapide, plus vicieux que le Gillian. Il doit dévorer "
                                        "sans relâche pour maintenir sa forme. S'il cesse, la "
                                        "régression est définitive."),
                ("Vasto Lorde (最上大虚)", "Le sommet de l'évolution Hollow. Un corps proche de l'humain, "
                                           "une puissance qui rivalise avec celle d'un Capitaine. Ils sont "
                                           "si rares que leur apparition change l'équilibre de Hueco Mundo."),
            ],
            "couleur": "gris_sable"
        },
        {
            "titre": "未知の存在 L'Entité Inconnue",
            "desc": (
                "Quelque chose frappe aux Portes de l'Enfer depuis l'extérieur des "
                "Trois Mondes. Ce n'est ni un Hollow, ni un Shinigami, ni un être "
                "d'aucune catégorie répertoriée."
            ),
            "fields": [
                ("Ce qu'on perçoit", "Les Kushanāda réagissent à sa présence par des comportements "
                                     "inédits. Les Quincy captent ses vibrations dans le Reishi ambiant. "
                                     "Le cristal du Reiō tremble à intervalles de plus en plus rapprochés."),
                ("Ce qu'on ignore", "Sa nature, son origine, ses intentions. Personne ne sait "
                                    "depuis quand elle frappe. L'Entité n'a pas de nom parce que "
                                    "nommer quelque chose suppose de le comprendre."),
                ("Ce qu'on craint", "Que la Fissure ne soit pas une conséquence du Konsō Reisai "
                                    "ou de la disparition des Deux Piliers, mais un effet secondaire "
                                    "de ce qui se passe de l'autre côté des Portes."),
            ],
            "couleur": "pourpre_infernal"
        },
    ]
    for data in embeds_bestiaire:
        e = discord.Embed(title=data["titre"], description=data["desc"], color=COULEURS[data["couleur"]])
        for nom, val in data["fields"]:
            e.add_field(name=nom, value=val, inline=False)
        e.set_footer(text="⸻ Infernum Aeterna · Bestiaire ⸻")
        await poster(ch, e)

    # ── 7. pacte-des-ames — 3 embeds + bouton Prêter Serment ─────────────────
    ch = find_ch("pacte") if doit("pacte") else None

    # Embed 1 — Introduction narrative
    e_intro = discord.Embed(
        title="⚖️ Le Pacte des Âmes · 魂の誓約",
        description=(
            "Le Pacte des Âmes n'est pas un règlement. C'est un accord entre "
            "ceux qui choisissent d'écrire ensemble un récit plus grand "
            "qu'eux-mêmes.\n\n"
            "Lisez ce qui suit. C'est la fondation sur laquelle repose chaque "
            "scène, chaque combat, chaque mot échangé sur ce serveur."
        ),
        color=COULEURS["or_ancien"]
    )
    e_intro.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
    await poster(ch, e_intro)

    # Embed 2 — Les Dix Serments (partie 1 : 5 premiers)
    e_serments1 = discord.Embed(
        title="Les Dix Serments · I",
        color=COULEURS["or_ancien"]
    )
    e_serments1.add_field(
        name="𝐈 · Le Souffle d'Autrui",
        value="Je respecte le fil narratif de chaque joueur. Je n'interromps ni ne détourne une scène sans l'accord de ses auteurs.",
        inline=False
    )
    e_serments1.add_field(
        name="𝐈𝐈 · La Main Retenue",
        value="Je n'impose aucune action, blessure ou conséquence au personnage d'un autre joueur sans son consentement explicite.",
        inline=False
    )
    e_serments1.add_field(
        name="𝐈𝐈𝐈 · Le Voile du Savoir",
        value="Ce que je sais et ce que mon personnage sait sont deux vérités distinctes. Le méta-gaming n'a pas sa place entre ces murs.",
        inline=False
    )
    e_serments1.add_field(
        name="𝐈𝐕 · La Parole du Canon",
        value="Je reste en accord avec le lore du serveur. En cas de doute, je consulte le staff avant d'agir.",
        inline=False
    )
    e_serments1.add_field(
        name="𝐕 · L'Espace Partagé",
        value="Je ne monopolise ni les zones narratives importantes, ni les événements en cours. Chaque âme mérite sa place dans le récit.",
        inline=False
    )
    e_serments1.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
    await poster(ch, e_serments1)

    # Embed 3 — Les Dix Serments (partie 2 : 5 derniers)
    e_serments2 = discord.Embed(
        title="Les Dix Serments · II",
        color=COULEURS["or_ancien"]
    )
    e_serments2.add_field(
        name="𝐕𝐈 · Le Seuil de la Mort",
        value="J'informe le staff avant toute mort narrative, séquence sensible ou événement irréversible.",
        inline=False
    )
    e_serments2.add_field(
        name="𝐕𝐈𝐈 · La Justice Silencieuse",
        value="Face à un manquement, je signale plutôt que de rendre justice seul. Aucune modération ne m'appartient.",
        inline=False
    )
    e_serments2.add_field(
        name="𝐕𝐈𝐈𝐈 · La Colère Contenue",
        value="J'accepte les décisions du staff, quitte à en débattre ensuite par écrit — jamais dans la colère du moment.",
        inline=False
    )
    e_serments2.add_field(
        name="𝐈𝐗 · Le Seuil Ouvert",
        value="J'accueille les nouveaux avec la patience qu'on m'a accordée. Chaque âme qui traverse la Fissure mérite un guide.",
        inline=False
    )
    e_serments2.add_field(
        name="𝐗 · La Fondation",
        value=(
            "Je contribue à faire de ce serveur une expérience qui mérite "
            "d'être racontée — par mes écrits, mon respect, et ma présence.\n\n"
            "*「 Ces serments ne sont pas des règles. Ils sont la fondation. 」*"
        ),
        inline=False
    )
    e_serments2.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
    await poster(ch, e_serments2)

    # Embed 3 — Confirmation + bouton
    e_confirm = discord.Embed(
        description=(
            "Pressez le sceau ci-dessous pour accepter le Pacte et accéder "
            "au reste du serveur.\n\n"
            "*「 Tout commencement est un serment. 」*"
        ),
        color=COULEURS["or_ancien"]
    )
    e_confirm.set_footer(text="⸻ Infernum Aeterna · Le Pacte ⸻")
    if ch:
        view = BoutonPacte()
        msg = await ch.send(embed=e_confirm, view=view)
        try:
            await msg.pin()
        except Exception:
            pass
        await asyncio.sleep(0.3)

    # ── 8. modele-de-fiche — 2 embeds ────────────────────────────────────────
    ch = find_ch("modele-de-fiche") if doit("modele-de-fiche") else None

    modele = (
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
        "APTITUDES (selon votre budget Reiryoku) :\n"
        "Voir le détail sur la page Aptitudes du site web.\n"
        "1.\n"
        "2.\n"
        "3.\n\n"
        "OBJECTIF NARRATIF :\n"
        "[Ce que votre personnage cherche dans le contexte de la Fissure]\n"
        "═══════════════════════════════\n"
        "```"
    )
    e1 = discord.Embed(
        title="📋 Forger son Identité · 魂の形",
        description=(
            "Votre fiche est le premier souffle de votre personnage. "
            "C'est ici qu'il cesse d'être une idée et commence à vivre.\n\n"
            "Copiez le modèle ci-dessous, prenez le temps de le remplir, "
            "puis soumettez-le. Le staff lira chaque mot.\n\u200b"
        ),
        color=COULEURS["blanc_seireitei"]
    )
    e1.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e1)

    e_modele = discord.Embed(description=modele, color=COULEURS["blanc_seireitei"])
    e_modele.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e_modele)

    e2 = discord.Embed(title="📥 Le Chemin vers la Validation", color=COULEURS["or_pale"])
    e2.add_field(
        name="Préparer",
        value="Copiez le modèle ci-dessus. L'Histoire demande **300 mots** minimum.",
        inline=False
    )
    e2.add_field(
        name="Soumettre",
        value="Dans `📥・soumission-de-fiche`, tapez `/fiche-soumettre` pour ouvrir le formulaire.",
        inline=False
    )
    e2.add_field(
        name="Attendre",
        value="Le staff répond sous **48 heures**. Vous recevrez un MP à la validation.",
        inline=False
    )
    e2.add_field(
        name="Entrer dans le récit",
        value=(
            "Après validation, vos rôles et l'accès aux zones RP sont attribués "
            "automatiquement.\n\n"
            f"📜 [Guide de création complet]({LORE_WEB_URL}#creation)\n"
            f"🔮 [Détail des aptitudes par faction]({APTITUDES_WEB_URL})"
        ),
        inline=False
    )
    e2.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e2)

    # ── 9. figures-de-legende — personnages originaux du lore ───────────────
    ch = find_ch("figures-de-legende") if doit("figures-de-legende") else None
    figures = [
        {
            "titre": "👑 Kōshin Jūrōmaru · 光信樹郎丸",
            "desc": (
                "Fondateur du Gotei 13. Son Zanpakutō de type feu était l'aîné et le "
                "plus puissant de sa catégorie. Il réunit treize guerriers d'une efficacité "
                "terrifiante et imposa l'ordre à Soul Society par la force, district par "
                "district.\n\n"
                "Il mourut de vieillesse après des millénaires, ce qui était presque sans "
                "précédent pour un être de sa puissance. Son corps fut honoré par le Konsō "
                "Reisai. Personne, à l'époque, ne savait ce que ce rituel impliquait "
                "véritablement."
            ),
            "couleur": "or_ancien"
        },
        {
            "titre": "⚔️ Tōka Shibari · 灯華柴張",
            "desc": (
                "La première à porter le titre non officiel de Kenpachi. Son Zanpakutō "
                "existait en état de libération permanente, tant le lien entre elle et "
                "l'esprit de sa lame était total. La séparation n'avait jamais eu lieu.\n\n"
                "Elle tomba au combat. C'était la seule sortie qu'elle aurait acceptée. "
                "Les chroniques la décrivent comme une force aussi impitoyable que le "
                "Capitaine-Commandant lui-même, portée par une fureur plus intime."
            ),
            "couleur": "rouge_chaine"
        },
        {
            "titre": "🔮 Renjō Mikazuchi · 蓮生三日国",
            "desc": (
                "Le plus mystérieux des trois Capitaines fondateurs. Il abritait quelque "
                "chose en lui, une entité spirituelle d'une nature inconnue que même ses "
                "pairs ne comprenaient pas.\n\n"
                "Il mourut dans un état de paix sereine qui contrastait avec toute la "
                "violence de l'époque. Son sourire, disent les chroniques, ne s'est "
                "jamais effacé. Comme s'il avait compris quelque chose que les autres "
                "ne verraient que des millénaires plus tard."
            ),
            "couleur": "pourpre_infernal"
        },
        {
            "titre": "🥨 Kenpachi Dorian · ケンパチ・ドリアン",
            "desc": (
                "Premier et dernier Shinigami d'origine européenne à avoir intégré "
                "le Gotei 13. Les archives de la Douzième Division — pourtant "
                "habituées à l'invraisemblable — consacrent à son cas un dossier "
                "entier classé sous la mention « inexplicable et probablement faux ».\n\n"
                "Dorian aurait maîtrisé le Zanjutsu, le Hakuda, le Hohō, le Kidō, le "
                "contrôle du Reiatsu et le Senryaku de manière simultanée et absolue. "
                "À sa sortie de l'Académie. Le jour même de son entrée, si l'on en croit "
                "certains témoignages. Les examinateurs auraient tenté de le recaler par "
                "principe, mais son Reiatsu aurait fait fondre les formulaires.\n\n"
                "Sa puissance spirituelle, scellée sous sept couches de Kidō, trois "
                "Bakudō expérimentaux et un cadenas acheté au Rukongai, dépassait "
                "paraît-il celle de l'ensemble du Gotei 13 réuni. Des Capitaines "
                "auraient perdu connaissance en le croisant dans un couloir. Le Reio "
                "lui-même — selon des sources invérifiables et franchement suspectes "
                "— aurait esquissé un froncement de sourcil, ce qui constituerait "
                "la seule émotion jamais attribuée au Roi des Âmes.\n\n"
                "Son Bankai, nommé « Tout Ce Qui Existe, N'Existe Pas, Et N'Existera "
                "Jamais Sauf Le Mardi », possédait la capacité simultanée de contrôler "
                "le temps, l'espace, la gravité, les émotions, les souvenirs, la météo, "
                "les courants marins du Dangai et les prix du marché au Rukongai. Son "
                "Shikai seul suffisait à réécrire les lois de la physique dans un "
                "rayon de douze kilomètres. Personne ne l'a vu, mais tout le monde "
                "en est absolument certain.\n\n"
                "Il mourut à l'âge de vingt-trois ans, étouffé par un bretzel.\n\n"
                "Le rapport officiel mentionne un pique-nique au pied du Sōkyoku, un "
                "bretzel artisanal offert par un membre de la Quatrième Division, et un "
                "silence gêné de quatorze minutes avant que quiconque ne songe à "
                "intervenir. Sa puissance spirituelle, capable selon les témoins "
                "d'ébranler les fondations du Seireitei et de faire pleurer les "
                "Kushanāda, s'avéra rigoureusement inapte à déloger un morceau de "
                "pâte salée de sa trachée.\n\n"
                "Les treize Divisions observèrent une minute de silence.\n"
                "Puis reprirent leurs activités, légèrement soulagées."
            ),
            "couleur": "gris_sable"
        },
    ]
    for fig in figures:
        e = discord.Embed(
            title=fig["titre"],
            description=fig["desc"],
            color=COULEURS[fig["couleur"]]
        )
        e.set_footer(text="⸻ Infernum Aeterna · Légendes ⸻")
        await poster(ch, e)

    # ── 10. etat-de-la-fissure — embed initial ──────────────────────────────
    ch = find_ch("etat-de-la-fissure") if doit("etat-de-la-fissure") else None
    e = discord.Embed(
        title="⛓️ État de la Fissure · 裂け目の状態",
        description=(
            "La Fissure est actuellement **stable**.\n\n"
            "Ce canal se met à jour après chaque événement majeur. "
            "L'état de la Fissure influence toutes les zones de RP."
        ),
        color=COULEURS["pourpre_infernal"]
    )
    e.add_field(name="Niveau actuel", value="🟢 **1 · Stable**", inline=True)
    e.add_field(name="Dernier changement", value="Initialisation du serveur", inline=True)
    e.set_footer(text="⸻ Infernum Aeterna · Fissure ⸻")
    await poster(ch, e)

    # ── 11. tableau-des-missions — embed initial ────────────────────────────
    ch = find_ch("tableau-des-missions") if doit("tableau-des-missions") else None
    e = discord.Embed(
        title="📌 Tableau des Missions · 任務表",
        description=(
            "Les missions actives du staff s'affichent ici. Difficulté, "
            "factions concernées, récompenses narratives. Revenez souvent."
        ),
        color=COULEURS["blanc_seireitei"]
    )
    e.add_field(name="Aucune mission active", value="*Le calme précède toujours la tempête.*", inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Missions ⸻")
    await poster(ch, e)

    # ── 12. hierarchie-des-espada — lore + classement ────────────────────────
    ch = find_ch("hierarchie-des-espada") if doit("hierarchie-des-espada") else None
    e = discord.Embed(
        title="💠 Hiérarchie de Las Noches · 十刃",
        description=(
            "Las Noches fonctionne selon une loi unique : la puissance "
            "détermine la place. Pas de politique, pas de vote, pas de "
            "discours. L'ordre est maintenu parce que chacun sait ce que "
            "l'autre peut faire."
        ),
        color=COULEURS["gris_sable"]
    )
    e.add_field(
        name="💠 Espada (十刃)",
        value=(
            "Les dix plus puissants Arrancar. Numérotés de 0 à 9, le "
            "chiffre gravé dans leur chair marquant leur rang. Chacun "
            "règne sur un secteur de Las Noches et commande ses propres "
            "subordonnés. Leur Resurrección peut renverser l'issue d'un "
            "conflit à elle seule."
        ),
        inline=False,
    )
    e.add_field(
        name="◇ Fracción",
        value=(
            "L'entourage direct d'un Espada. Un mélange de lieutenants, "
            "de gardes et de serviteurs loyaux. La Fracción doit sa "
            "position à la confiance de son Espada, et cette confiance "
            "peut être retirée à tout moment."
        ),
        inline=False,
    )
    e.add_field(
        name="○ Números",
        value=(
            "Les Arrancar numérotés au-delà des dix premiers. Soldats "
            "et combattants ordinaires de Las Noches. Certains sont "
            "ambitieux, d'autres résignés, tous savent que leur numéro "
            "peut changer par la force."
        ),
        inline=False,
    )
    e.add_field(
        name="◈ Privaron Espada",
        value=(
            "D'anciens Espada déchus, remplacés par un adversaire plus "
            "puissant. Ils conservent leur force mais ont perdu leur "
            "place et le respect qui va avec. Certains attendent leur "
            "revanche. D'autres ont cessé d'attendre."
        ),
        inline=False,
    )
    e.add_field(
        name="👑 Rey",
        value=(
            "Le souverain de Hueco Mundo. Celui qui s'assoit au sommet de "
            "Las Noches et dont la puissance ne laisse de doute à personne. "
            "Le titre se prend par la force ou ne se prend pas."
        ),
        inline=False,
    )
    e.set_footer(text="⸻ Infernum Aeterna · Hueco Mundo ⸻")
    await poster(ch, e)

    e = discord.Embed(
        title="📊 Classement actuel des Espada",
        description="*Le trône attend ses prétendants.*",
        color=COULEURS["gris_sable"]
    )
    e.add_field(name="Aucun Espada enregistré", value="Les positions se rempliront au fil du RP.", inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Hueco Mundo ⸻")
    await poster(ch, e)

    # ── 13. veille-de-la-fissure (Quincy) — embed initial ──────────────────
    ch = find_ch("veille-de-la-fissure") if doit("veille-de-la-fissure") else None
    e = discord.Embed(
        title="📌 Veille de la Fissure · 裂け目の監視",
        description=(
            "Les Quincy surveillent la contamination depuis leur refuge. "
            "Anomalies de Reishi, mouvements suspects, alertes de la chaîne "
            "de commandement survivante : tout est consigné ici."
        ),
        color=COULEURS["bleu_abyssal"]
    )
    e.add_field(name="Statut actuel", value="🔵 Surveillance passive. Aucune anomalie signalée.", inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Quincy ⸻")
    await poster(ch, e)

    # ── 14. etat-de-la-frontiere — embed initial ────────────────────────────
    ch = find_ch("etat-de-la-frontiere") if doit("etat-de-la-frontiere") else None
    e = discord.Embed(
        title="📌 État de la Frontière · 境界の状態",
        description=(
            "La Frontière. Un territoire mouvant entre les mondes, né de la "
            "Fissure. Des fragments arrachés aux mondes adjacents y dérivent "
            "dans un vide gris parcouru de courants de Reishi brut. Le Jigoku "
            "no Rinki y est plus dense qu'ailleurs.\n\n"
            "Aucune faction ne la contrôle. Elle grandit."
        ),
        color=COULEURS["gris_acier"]
    )
    e.add_field(
        name="Statut actuel",
        value="⚪ Frontière instable. Passages détectés.",
        inline=False
    )
    e.set_footer(text="⸻ Infernum Aeterna · Frontière ⸻")
    await poster(ch, e)

    # ── 15. incidents-repertories — embed initial ───────────────────────────
    ch = find_ch("incidents-repertories") if doit("incidents-repertories") else None
    e = discord.Embed(
        title="📌 Incidents Répertoriés · 事件記録",
        description=(
            "Anomalies spirituelles dans le Monde des Vivants. Portails "
            "instables, apparitions de Hollow, fluctuations de Reishi. "
            "Chaque incident est consigné ici."
        ),
        color=COULEURS["gris_acier"]
    )
    e.add_field(name="Aucun incident actif", value="*Le monde des vivants dort encore. Pour combien de temps ?*", inline=False)
    e.set_footer(text="⸻ Infernum Aeterna · Monde des Vivants ⸻")
    await poster(ch, e)

    # ── 16. progression — embed explicatif ──────────────────────────────────
    ch = find_ch("progression") if doit("progression") else None
    e = discord.Embed(
        title="📈 Progression · 成長の道",
        description=(
            "Montées de rang, gains de points, aptitudes débloquées : tout "
            "est consigné ici automatiquement après validation par le staff.\n\n"
            "Commande `/classement` pour le tableau complet."
        ),
        color=COULEURS["or_pale"]
    )
    e.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e)

    # ── 17. objectifs-narratifs — embed explicatif ──────────────────────────
    ch = find_ch("objectifs-narratifs") if doit("objectifs-narratifs") else None
    e = discord.Embed(
        title="🎯 Objectifs Narratifs · 物語の目標",
        description=(
            "Après validation de votre fiche, le staff publie vos objectifs "
            "ici. Ce sont les conditions pour débloquer les aptitudes de "
            "Transcendance et les montées de rang exceptionnelles.\n\n"
            "Accomplissez-les en RP, signalez votre progression au staff."
        ),
        color=COULEURS["or_pale"]
    )
    e.add_field(
        name="Le parcours",
        value=(
            "Fiche validée → objectifs publiés → RP à votre rythme → "
            "signal au staff → validation → montée de rang ou aptitude "
            "débloquée."
        ),
        inline=False
    )
    e.set_footer(text="⸻ Infernum Aeterna · Administration ⸻")
    await poster(ch, e)

    # ── 18. esprits-perdus (FAQ) — embed d'accueil ─────────────────────────
    ch = find_ch("esprits-perdus") if doit("esprits-perdus") else None
    e = discord.Embed(
        title="❓ Esprits Perdus · 迷える魂",
        description=(
            "Vous êtes perdus ? Posez vos questions ici. Le staff ou la "
            "communauté répondra. Les réponses fréquentes seront épinglées."
        ),
        color=COULEURS["bleu_abyssal"]
    )
    e.add_field(
        name="Premiers repères",
        value=(
            "**Créer un personnage** → `📋・modele-de-fiche`\n"
            "**Découvrir les factions** → `🎭・choisir-son-destin`\n"
            "**Lire le lore** → `📖・infernum-aeterna` ou la page web\n"
            "**Lancer un combat** → bouton ⚔️ dans les salles dédiées"
        ),
        inline=False
    )
    e.set_footer(text="⸻ Infernum Aeterna · Portail ⸻")
    await poster(ch, e)



# ══════════════════════════════════════════════════════════════════════════════
#  VUES (boutons persistants + menus interactifs)
# ══════════════════════════════════════════════════════════════════════════════

class SelectLoreView(discord.ui.View):
    """Menu déroulant multi-sélection pour choisir les channels lore à actualiser."""

    def __init__(self, bot, guild, channels_trouves: list[tuple[str, discord.TextChannel]]):
        super().__init__(timeout=120)
        self.bot = bot
        self.guild = guild
        self.channels_trouves = channels_trouves

        # Construire les options du Select (max 25, on en a ≤19)
        options = [
            discord.SelectOption(
                label="✦ Tout sélectionner",
                value="__tous__",
                description=f"Actualise les {len(channels_trouves)} channels d'un coup",
            )
        ]
        for cle, ch in channels_trouves:
            options.append(discord.SelectOption(
                label=LABELS_LORE.get(cle, cle),
                value=cle,
                description=f"#{ch.name}",
            ))

        select = discord.ui.Select(
            placeholder=f"Choisir les channels à actualiser ({len(channels_trouves)} disponibles)…",
            min_values=1,
            max_values=len(options),
            options=options,
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction):
        selected = interaction.data["values"]

        # "Tout sélectionner" → toutes les clés
        if "__tous__" in selected:
            cles = [cle for cle, _ in self.channels_trouves]
        else:
            cles = [v for v in selected if v != "__tous__"]

        n = len(cles)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⏳ Actualisation en cours…",
                description=f"Nettoyage puis réécriture de **{n}** channel(s).\nCela peut prendre quelques minutes.",
                color=COULEURS["or_ancien"],
            ),
            view=None,
        )

        # Phase 1 — nettoyage (supprimer les anciens messages du bot)
        nettoyees = 0
        for cle in cles:
            ch = trouver_channel(self.guild, cle)
            if ch:
                nettoyees += await _nettoyer_channel_bot(ch, self.bot.user)

        # Phase 2 — repeupler uniquement les channels sélectionnés
        await _peupler_channels_lore(self.guild, cles_cibles=cles)

        # Rapport final
        labels = [LABELS_LORE.get(c, c) for c in cles]
        liste_txt = "\n".join(f"• {l}" for l in labels)
        embed = discord.Embed(
            title="✅ Lore actualisé",
            description=(
                f"**{nettoyees}** ancien(s) message(s) supprimé(s)\n"
                f"**{n}** channel(s) repeuplé(s) :\n\n{liste_txt}"
            ),
            color=COULEURS["or_ancien"],
        )
        embed.set_footer(text="⸻ Infernum Aeterna ⸻")
        await interaction.edit_original_response(embed=embed)


class BoutonPacte(discord.ui.View):
    """Bouton persistant 'Prêter Serment' — assigne le rôle voyageur."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚖️ Prêter Serment", style=discord.ButtonStyle.success, custom_id="pacte_serment")
    async def preter_serment(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles_ids = charger_roles()
        guild = interaction.guild
        member = interaction.user

        role_id = roles_ids.get("voyageur")
        if not role_id:
            await interaction.response.send_message("❌ Rôle introuvable. Contactez le staff.", ephemeral=True)
            return
        role = guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ Rôle introuvable sur ce serveur.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.response.send_message(
                "*Vous avez déjà prêté serment. Les Portes vous sont ouvertes.*",
                ephemeral=True
            )
            return

        await member.add_roles(role, reason="Pacte des Âmes accepté")
        await interaction.response.send_message(
            "**Le Pacte est scellé.**\n\n"
            "*Les Portes s'entrouvrent. De nouveaux channels apparaissent devant vous.*\n\n"
            "Découvrez les factions dans `🎭・choisir-son-destin`, puis forgez "
            "votre personnage dans `📋・modele-de-fiche`.\n\n"
            "「 Tout commencement est un serment. 」",
            ephemeral=True
        )


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
    # Retirer emojis et séparateur ・
    cleaned = re.sub(r"[^\w\s-]", "", nom).strip().lstrip("・").strip()
    # Prendre la partie après le dernier espace ou ・ si c'est un emoji suivi de texte
    parts = nom.split("・", 1)
    if len(parts) == 2:
        cleaned = parts[1].strip()
    return cleaned.lower().replace(" ", "-")


async def setup(bot):
    await bot.add_cog(Construction(bot))
