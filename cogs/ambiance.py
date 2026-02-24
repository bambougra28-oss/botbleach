"""
INFERNUM AETERNA — Cog Ambiance
Publie automatiquement des messages atmosphériques dans les zones RP
à intervalles réguliers. Chaque message est généré par Claude
et adapté à la zone et à l'état actuel de la Fissure.

Commandes :
  /ambiance-activer   — active les messages dans un channel
  /ambiance-desactiver
  /ambiance-forcer    — déclenche immédiatement un message
  /ambiance-statut    — liste les channels actifs
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import anthropic
import asyncio
import random
import logging
from datetime import datetime, timezone

from config import COULEURS, ANTHROPIC_KEY, CLAUDE_MODEL, NARRATEUR_SYSTEM
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

AMBIANCE_FILE = "data/ambiance.json"

# ── Intervalles disponibles ────────────────────────────────────────────────────
INTERVALLES = {
    "30min":  30,
    "1h":     60,
    "2h":     120,
    "4h":     240,
    "6h":     360,
}

# ── Profils d'ambiance par zone ────────────────────────────────────────────────
# Chaque profil guide Claude pour écrire dans l'atmosphère de la zone
PROFILS_ZONE = {
    # Enfer
    "pratus":    "Première Strate de l'Enfer. Chaleur écrasante, sol de cendres, hurlements lointains. Togabito récents et désespérés.",
    "carnale":   "Deuxième Strate. Plaines brûlantes, rivières de soufre, odeur de chair consumée. Violence permanente.",
    "sulfura":   "Troisième Strate. Geysers de soufre, vapeurs toxiques, visibilité nulle. Terrain imprévisible.",
    "profundus": "Quatrième Strate. Obscurité quasi-totale, pression spirituelle accablante, présence des Kushanāda.",
    "saiobu":    "Cinquième Strate. Abyssal. Silence total rompu par des vibrations cosmiques. Peu y survivent.",
    "fissure":   "La Fissure principale. Épicentre de l'événement. Reishi infernal s'échappe en volutes violettes. Instabilité maximale.",
    "frontiere": "Frontière entre les mondes. Espace entre deux réalités. Lois physiques instables. Tout peut surgir.",
    # Soul Society
    "seireitei": "Le Seireitei. Murs de Sekkiseki blanc, patrouilles de Shinigami, tension palpable depuis la Fissure.",
    "academie":  "La Shin'ō Academy. Étudiants qui s'entraînent, apprentissage du Zanjutsu, murmures sur l'Enfer.",
    # Hueco Mundo
    "desert":    "Le désert de Las Noches. Sable blanc sous lune immobile, silence absolu, présence de Hollows.",
    "las_noches":"Las Noches. Architecture massive de pierre blanche, corridors sans fin, hiérarchie des Espada.",
    # Monde des vivants
    "ville":     "Une ville humaine. Vivants inconscients du chaos spirituel. Présences spectrales croissantes.",
    "refuge":    "Le refuge Quincy. Caché dans les ombres du Seireitei. Tension, préparation, méfiance.",
    # Générique
    "defaut":    "Zone indéterminée des Trois Mondes. Reishi perturbé par la Fissure. Atmosphère lourde.",
}

# ── Détection de la zone depuis le nom du channel ─────────────────────────────
DETECTION_ZONE = {
    "pratus":       "pratus",
    "carnale":      "carnale",
    "sulfura":      "sulfura",
    "profundus":    "profundus",
    "saiobu":       "saiobu",
    "fissure":      "fissure",
    "frontiere":    "frontiere",
    "no-mans":      "frontiere",
    "seireitei":    "seireitei",
    "divisions":    "seireitei",
    "academie":     "academie",
    "las-noches":   "las_noches",
    "desert":       "desert",
    "ville":        "ville",
    "refuge":       "refuge",
    "zones-isolees":"ville",
}


def _detecter_zone(channel_name: str) -> str:
    nom = channel_name.lower()
    for mot_cle, zone in DETECTION_ZONE.items():
        if mot_cle in nom:
            return zone
    return "defaut"



# ══════════════════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════════════════

class Ambiance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._store = JsonStore(AMBIANCE_FILE)
        self.channels_actifs = self._store.data
        self._client = None
        if ANTHROPIC_KEY:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=30.0)
        else:
            log.warning("ANTHROPIC_KEY absente — ambiance IA désactivée")
        self._semaphore = asyncio.Semaphore(3)
        self.boucle_ambiance.start()

    def cog_unload(self):
        self.boucle_ambiance.cancel()

    # ── Génération d'un message d'ambiance ────────────────────────────────────
    async def _generer_message(self, zone: str, channel_name: str) -> str:
        if not self._client:
            return "「 Le silence règne. 」"

        profil = PROFILS_ZONE.get(zone, PROFILS_ZONE["defaut"])
        prompt = (
            f"Tu dois écrire un court message d'ambiance pour une zone de RP sur le serveur Infernum Aeterna.\n\n"
            f"Zone : {channel_name}\n"
            f"Atmosphère : {profil}\n\n"
            "Écris UN SEUL paragraphe court (3-5 lignes) à la troisième personne ou en description narrative. "
            "Décris ce que des personnages ANONYMES présents percevraient en ce moment précis : "
            "sons, sensations, mouvements imperceptibles, Reishi dans l'air, présences. "
            "Varie chaque fois (ne répète pas les mêmes formules). "
            "Termine toujours par une courte phrase d'atmosphère en italique entre guillemets japonais 「 」.\n\n"
            "INTERDIT :\n"
            "- Aucun dialogue.\n"
            "- Aucun personnage nommé (ni OC, ni canon de Bleach).\n"
            "- Aucune mention de personnages canon (Yamamoto, Aizen, Ichigo, Yoruichi, etc.).\n"
            "- Aucune action attribuée à un personnage spécifique.\n"
            "- Aucune invention d'événement narratif (combat, explosion, mort, etc.).\n"
            "- Uniquement de la description sensorielle et atmosphérique."
        )
        async with self._semaphore:
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=300,
                        system=NARRATEUR_SYSTEM,
                        messages=[{"role": "user", "content": prompt}]
                    )
                ),
                timeout=35.0
            )
        return response.content[0].text.strip()

    async def _publier_ambiance(self, channel_id: int, config: dict):
        channel = self.bot.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            # Nettoyage : supprimer les channels morts de la config
            ch_id_str = str(channel_id)
            if ch_id_str in self.channels_actifs:
                del self.channels_actifs[ch_id_str]
                await self._store.save()
                log.info("Ambiance: channel %s supprimé (introuvable)", channel_id)
            return
        zone = config.get("zone", _detecter_zone(channel.name))
        try:
            texte = await self._generer_message(zone, channel.name)
        except Exception as e:
            log.error("Ambiance: erreur génération pour %s : %s", channel.name, e)
            return

        # Embed minimal et discret — ne doit pas écraser le RP
        couleurs_zone = {
            "pratus":    COULEURS["rouge_chaine"],
            "carnale":   0x8B2500,
            "sulfura":   0xB8860B,
            "profundus": 0x1A0030,
            "saiobu":    0x050505,
            "fissure":   COULEURS["pourpre_infernal"],
            "frontiere": 0x1A1A2E,
            "seireitei": COULEURS["blanc_seireitei"],
            "academie":  COULEURS["blanc_casse"],
            "las_noches":COULEURS["gris_sable"],
            "desert":    0x3D3526,
            "ville":     0x2C3E50,
            "refuge":    COULEURS["bleu_abyssal"],
            "defaut":    COULEURS["noir_abyssal"],
        }
        embed = discord.Embed(
            description=texte,
            color=couleurs_zone.get(zone, COULEURS["noir_abyssal"])
        )
        embed.set_footer(text="⸰ ambiance ⸰")
        await channel.send(embed=embed)
        config["dernier_envoi"] = datetime.now(timezone.utc).isoformat()
        await self._store.save()

    # ── Boucle toutes les 10 minutes — vérifie quels channels ont besoin ───────
    @tasks.loop(minutes=10)
    async def boucle_ambiance(self):
        if not self.channels_actifs:
            return
        maintenant = datetime.now(timezone.utc)
        for ch_id_str, config in list(self.channels_actifs.items()):
            if not config.get("actif", False):
                continue
            intervalle_min = config.get("intervalle_minutes", 60)
            dernier = config.get("dernier_envoi")
            if dernier:
                depuis = (maintenant - datetime.fromisoformat(dernier)).total_seconds() / 60
                if depuis < intervalle_min:
                    continue
            # Ajouter un léger décalage aléatoire (±5 min) pour ne pas être trop mécanique
            await asyncio.sleep(random.randint(0, 300))
            await self._publier_ambiance(int(ch_id_str), config)

    @boucle_ambiance.before_loop
    async def before_boucle(self):
        await self.bot.wait_until_ready()

    # ══════════════════════════════════════════════════════════════════════════
    #  COMMANDES
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="ambiance-activer", description="[STAFF] Active les messages d'ambiance dans ce channel.")
    @app_commands.describe(
        intervalle="Fréquence des messages",
        zone="Profil d'atmosphère (détecté automatiquement si non précisé)",
    )
    @app_commands.choices(intervalle=[
        app_commands.Choice(name=k, value=v) for k, v in INTERVALLES.items()
    ])
    @app_commands.choices(zone=[
        app_commands.Choice(name=k.replace("_", " ").capitalize(), value=k)
        for k in PROFILS_ZONE.keys()
    ])
    @app_commands.default_permissions(manage_channels=True)
    async def ambiance_activer(
        self,
        interaction: discord.Interaction,
        intervalle: int = 60,
        zone: Optional[str] = None,
    ):
        ch = interaction.channel
        zone_finale = zone or _detecter_zone(ch.name)
        ch_id = str(ch.id)
        self.channels_actifs[ch_id] = {
            "actif": True,
            "channel_nom": ch.name,
            "zone": zone_finale,
            "intervalle_minutes": intervalle,
            "dernier_envoi": None,
        }
        await self._store.save()
        await interaction.response.send_message(
            f"✅ Ambiance activée dans {ch.mention}\n"
            f"Zone : **{zone_finale}** · Intervalle : **{intervalle} min**",
            ephemeral=True
        )

    @app_commands.command(name="ambiance-desactiver", description="[STAFF] Désactive les messages d'ambiance dans ce channel.")
    @app_commands.default_permissions(manage_channels=True)
    async def ambiance_desactiver(self, interaction: discord.Interaction):
        ch_id = str(interaction.channel.id)
        if ch_id in self.channels_actifs:
            self.channels_actifs[ch_id]["actif"] = False
            await self._store.save()
        await interaction.response.send_message("✅ Ambiance désactivée.", ephemeral=True)

    @app_commands.command(name="ambiance-forcer", description="[STAFF] Déclenche immédiatement un message d'ambiance.")
    @app_commands.default_permissions(manage_channels=True)
    async def ambiance_forcer(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ch = interaction.channel
        ch_id = str(ch.id)
        config = self.channels_actifs.get(ch_id, {"zone": _detecter_zone(ch.name), "actif": True})
        await self._publier_ambiance(ch.id, config)
        await interaction.followup.send("✅ Message d'ambiance déclenché.", ephemeral=True)

    @app_commands.command(name="ambiance-statut", description="[STAFF] Liste les channels avec ambiance active.")
    @app_commands.default_permissions(manage_channels=True)
    async def ambiance_statut(self, interaction: discord.Interaction):
        actifs = {k: v for k, v in self.channels_actifs.items() if v.get("actif")}
        if not actifs:
            await interaction.response.send_message("Aucune ambiance active.", ephemeral=True)
            return
        embed = discord.Embed(title="🌫️ Channels avec Ambiance Active", color=COULEURS["pourpre_infernal"])
        for ch_id, cfg in actifs.items():
            embed.add_field(
                name=f"#{cfg.get('channel_nom', ch_id)}",
                value=f"Zone : {cfg.get('zone', '?')} · {cfg.get('intervalle_minutes', '?')} min",
                inline=True
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ambiance(bot))
