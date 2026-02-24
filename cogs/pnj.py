"""
INFERNUM AETERNA — Cog PNJ (Personnages Non Joueurs)
- /pnj-invoquer [pnj] [contexte]  — Invoque un PNJ dans un thread dédié
- /pnj-parler [message]            — Parle au PNJ actif dans le thread courant
- /pnj-congedier                   — Met fin à la session PNJ
- /pnj-liste                       — Liste les PNJ disponibles et les sessions actives
"""

import discord
from discord.ext import commands
from discord import app_commands
import anthropic
import asyncio
import logging
from datetime import datetime, timezone

from config import COULEURS, ANTHROPIC_KEY, CLAUDE_MODEL, PNJ_SYSTEM
from utils.json_store import JsonStore

log = logging.getLogger("infernum")

# ─── Données persistantes ────────────────────────────────────────────────────
FICHIER_PNJ = "data/pnj.json"
DONNEES_DEFAUT = {
    "sessions": {},
    "quotas": {},
}

# ─── Limites ──────────────────────────────────────────────────────────────────
QUOTA_JOURNALIER = 3          # Invocations max par joueur par jour
MAX_ECHANGES = 10             # Échanges max par session avant départ du PNJ
MAX_HISTORIQUE = 20           # Messages conservés en mémoire pour l'IA
MAX_TOKENS_REPONSE = 500      # Tokens max par réponse IA
TIMEOUT_API = 35.0            # Timeout appel API en secondes

# PNJ_SYSTEM est importé depuis config.py

# ─── Catalogue des PNJ prédéfinis ─────────────────────────────────────────────
PNJ_CATALOGUE = {
    "kushanada": {
        "nom": "倶舎那陀 Kushanāda",
        "description": "Gardien titanesque des Strates. Parle peu. Quand il parle, c'est une sentence.",
        "personnalite": "Neutre, impersonnel, parle à la troisième personne. Voix de pierre.",
        "emoji": "🔴",
        "couleur": "gris_acier",
        "ps": 90,
    },
    "garde_seireitei": {
        "nom": "Garde du Seireitei",
        "description": "Shinigami de garde aux portes. Discipliné, légèrement nerveux à cause de la Fissure.",
        "personnalite": "Formel, respectueux des rangs, inquiet mais stoïque.",
        "emoji": "⚔️",
        "couleur": "blanc_seireitei",
        "ps": 20,
    },
    "marchand_rukongai": {
        "nom": "Marchand du Rukongai",
        "description": "Vieil homme qui vend des objets spirituels au marché noir du Rukongai.",
        "personnalite": "Rusé, bavard, parle en métaphores. Sait plus qu'il ne devrait.",
        "emoji": "🏪",
        "couleur": "or_pale",
        "ps": 3,
    },
    "hollow_errant": {
        "nom": "虚 Hollow Errant",
        "description": "Hollow partiellement conscient, rodant aux abords de la Fissure.",
        "personnalite": "Sauvage mais lucide par moments. Parle de manière fragmentée.",
        "emoji": "👹",
        "couleur": "noir_abyssal",
        "ps": 12,
    },
    "damne_ancien": {
        "nom": "Damné Ancien",
        "description": "Togabito millénaire enchaîné depuis si longtemps qu'il a oublié son crime.",
        "personnalite": "Philosophe, résigné, parle de la souffrance comme d'un art. Sagesse sombre.",
        "emoji": "⛓️",
        "couleur": "pourpre_infernal",
        "ps": 60,
    },
    "quincy_refugie": {
        "nom": "Quincy Réfugié",
        "description": "Survivant quincy caché dans le Monde des Vivants, traqué.",
        "personnalite": "Méfiant, pragmatique, loyal envers les siens. Parle à voix basse.",
        "emoji": "🏹",
        "couleur": "bleu_abyssal",
        "ps": 30,
    },
    "esprit_perdu": {
        "nom": "Esprit Perdu",
        "description": "Âme errante dans la Frontière, ni vivante ni morte.",
        "personnalite": "Confus, nostalgique, poétique. Ne sait plus qui il est.",
        "emoji": "👻",
        "couleur": "gris_sable",
        "ps": 2,
    },
    "personnalise": {
        "nom": "PNJ Personnalisé",
        "description": "Un PNJ défini par le staff.",
        "personnalite": "Défini par le contexte fourni.",
        "emoji": "🎭",
        "couleur": "or_ancien",
        "ps": 50,
    },
}

# Choix pour l'autocomplete de /pnj-invoquer
PNJ_CHOICES = [
    app_commands.Choice(name=f"{data['emoji']} {data['nom']}", value=cle)
    for cle, data in PNJ_CATALOGUE.items()
]


class PNJ(commands.Cog):
    """Cog de gestion des PNJ interactifs propulsés par IA."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._store = JsonStore(FICHIER_PNJ, default=DONNEES_DEFAUT)
        self.data = self._store.data
        # Initialiser les clés manquantes au cas où le fichier existe déjà partiellement
        self.data.setdefault("sessions", {})
        self.data.setdefault("quotas", {})
        # Client Anthropic
        self._client = None
        if ANTHROPIC_KEY:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_KEY, timeout=30.0)
        else:
            log.warning("ANTHROPIC_KEY absente — PNJ IA désactivés")
        self._semaphore = asyncio.Semaphore(2)

    async def _sauvegarder(self):
        """Sauvegarde les données PNJ sur disque."""
        self._store.data = self.data
        await self._store.save()

    # ── Vérification quota journalier ──────────────────────────────────────────

    def _verifier_quota(self, user_id: str) -> tuple[bool, int]:
        """Retourne (autorisé, nb_restant). Réinitialise si le jour a changé."""
        aujourd_hui = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        quota = self.data["quotas"].get(user_id)

        if quota is None or quota.get("date") != aujourd_hui:
            # Nouveau jour ou premier usage — réinitialiser
            self.data["quotas"][user_id] = {"date": aujourd_hui, "count": 0}
            quota = self.data["quotas"][user_id]

        restant = QUOTA_JOURNALIER - quota["count"]
        return restant > 0, max(restant, 0)

    def _incrementer_quota(self, user_id: str):
        """Incrémente le compteur de quota pour l'utilisateur."""
        aujourd_hui = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        quota = self.data["quotas"].setdefault(user_id, {"date": aujourd_hui, "count": 0})
        if quota["date"] != aujourd_hui:
            quota["date"] = aujourd_hui
            quota["count"] = 0
        quota["count"] += 1

    # ── Construction du prompt système complet ─────────────────────────────────

    def _construire_system_prompt(self, pnj_data: dict, contexte: str = "") -> str:
        """Construit le prompt système complet pour le PNJ."""
        prompt = PNJ_SYSTEM
        prompt += f"\nTu incarnes : {pnj_data['nom']}"
        prompt += f"\nDescription : {pnj_data['description']}"
        prompt += f"\nPersonnalité : {pnj_data['personnalite']}"
        ps = pnj_data.get("ps")
        if ps:
            prompt += f"\nTu as une Puissance Spirituelle de {ps} PS."
        if contexte:
            prompt += f"\nContexte de la scène : {contexte}"
        return prompt

    # ── Génération IA ──────────────────────────────────────────────────────────

    async def _generer_reponse(self, system_prompt: str, historique: list[dict]) -> str:
        """Appelle l'API Claude pour générer la réponse du PNJ."""
        if not self._client:
            return "*(Le PNJ reste silencieux... la connexion spirituelle est rompue.)*"

        # Tronquer l'historique aux N derniers messages pour éviter le dépassement de tokens
        messages_tronques = historique[-MAX_HISTORIQUE:] if len(historique) > MAX_HISTORIQUE else historique

        async with self._semaphore:
            loop = asyncio.get_running_loop()
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self._client.messages.create(
                            model=CLAUDE_MODEL,
                            max_tokens=MAX_TOKENS_REPONSE,
                            system=system_prompt,
                            messages=messages_tronques,
                        ),
                    ),
                    timeout=TIMEOUT_API,
                )
                return response.content[0].text
            except asyncio.TimeoutError:
                log.error("Timeout API lors de la génération PNJ")
                return "*(Le PNJ semble perdu dans ses pensées... l'énergie spirituelle fluctue.)*"
            except Exception as e:
                log.error("Erreur API PNJ : %s", e, exc_info=True)
                return "*(Une interférence spirituelle empêche le PNJ de répondre pour l'instant.)*"

    # ── Construction d'embed PNJ ───────────────────────────────────────────────

    def _construire_embed(self, pnj_data: dict, texte: str, titre_suffixe: str = "") -> discord.Embed:
        """Construit un embed aux couleurs du PNJ."""
        cle_couleur = pnj_data.get("couleur", "or_ancien")
        couleur = COULEURS.get(cle_couleur, COULEURS["or_ancien"])

        titre = f"{pnj_data['emoji']} {pnj_data['nom']}"
        if titre_suffixe:
            titre += f" — {titre_suffixe}"

        embed = discord.Embed(
            title=titre,
            description=texte,
            color=couleur,
        )
        embed.set_footer(text="⸻ Infernum Aeterna · PNJ ⸻")
        return embed

    def _construire_embed_erreur(self, message: str) -> discord.Embed:
        """Construit un embed d'erreur standardisé."""
        embed = discord.Embed(
            title="⚠️ Erreur PNJ",
            description=message,
            color=COULEURS["rouge_chaine"],
        )
        embed.set_footer(text="⸻ Infernum Aeterna · PNJ ⸻")
        return embed

    # ── Récupération de session par thread ─────────────────────────────────────

    def _get_session(self, thread_id: str) -> dict | None:
        """Retourne la session PNJ associée au thread, ou None."""
        return self.data["sessions"].get(thread_id)

    # ══════════════════════════════════════════════════════════════════════════
    #  /pnj-invoquer
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="pnj-invoquer",
        description="Invoque un PNJ pour une interaction RP dans un thread dédié.",
    )
    @app_commands.describe(
        pnj="Le PNJ à invoquer",
        contexte="Contexte de la scène (obligatoire pour PNJ Personnalisé, optionnel sinon)",
    )
    @app_commands.choices(pnj=PNJ_CHOICES)
    async def pnj_invoquer(
        self,
        interaction: discord.Interaction,
        pnj: str,
        contexte: str = "",
    ):
        await interaction.response.defer(ephemeral=True)

        # Vérifier que l'API est disponible
        if not self._client:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "La clé API Anthropic est absente. Les PNJ IA sont désactivés."
                ),
                ephemeral=True,
            )
            return

        # Vérifier que le PNJ existe dans le catalogue
        pnj_data = PNJ_CATALOGUE.get(pnj)
        if not pnj_data:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(f"PNJ inconnu : `{pnj}`"),
                ephemeral=True,
            )
            return

        # Le PNJ personnalisé nécessite un contexte
        if pnj == "personnalise" and not contexte:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Le PNJ Personnalisé nécessite un **contexte** décrivant le personnage et la scène."
                ),
                ephemeral=True,
            )
            return

        # Vérifier le quota journalier
        user_id = str(interaction.user.id)
        autorise, restant = self._verifier_quota(user_id)
        if not autorise:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    f"Vous avez atteint la limite de **{QUOTA_JOURNALIER} invocations par jour**.\n"
                    "Le quota se réinitialise à minuit UTC."
                ),
                ephemeral=True,
            )
            return

        # Vérifier que le channel supporte les threads
        channel = interaction.channel
        if not isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Les PNJ ne peuvent être invoqués que dans un salon textuel."
                ),
                ephemeral=True,
            )
            return

        # Créer le thread pour l'interaction PNJ
        nom_thread = f"{pnj_data['emoji']} {pnj_data['nom']} — {interaction.user.display_name}"
        # Tronquer le nom du thread à 100 caractères (limite Discord)
        if len(nom_thread) > 100:
            nom_thread = nom_thread[:97] + "..."

        try:
            thread = await channel.create_thread(
                name=nom_thread,
                type=discord.ChannelType.public_thread,
                auto_archive_duration=60,
                reason=f"Session PNJ invoquée par {interaction.user}",
            )
        except discord.HTTPException as e:
            log.error("Erreur création thread PNJ : %s", e)
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Impossible de créer le thread. Vérifiez les permissions du bot."
                ),
                ephemeral=True,
            )
            return

        # Construire le prompt système
        system_prompt = self._construire_system_prompt(pnj_data, contexte)

        # Générer l'introduction du PNJ
        intro_prompt = "Présente-toi brièvement en personnage. Décris ce que le joueur voit et ressent en ta présence. Termine par une ouverture pour l'interaction."
        if contexte:
            intro_prompt += f"\nContexte fourni par l'invocateur : {contexte}"

        historique_initial = [{"role": "user", "content": intro_prompt}]
        texte_intro = await self._generer_reponse(system_prompt, historique_initial)

        # Enregistrer la session
        thread_id = str(thread.id)
        self.data["sessions"][thread_id] = {
            "pnj_type": pnj,
            "pnj_nom": pnj_data["nom"],
            "invocateur_id": interaction.user.id,
            "channel_id": channel.id,
            "contexte": contexte,
            "historique": [
                {"role": "user", "content": intro_prompt},
                {"role": "assistant", "content": texte_intro},
            ],
            "date_creation": datetime.now(timezone.utc).isoformat(),
            "interactions": 0,
        }

        # Incrémenter le quota
        self._incrementer_quota(user_id)
        await self._sauvegarder()

        # Poster l'introduction dans le thread
        embed_intro = self._construire_embed(pnj_data, texte_intro, "Apparition")
        ps = pnj_data.get("ps")
        if ps:
            embed_intro.add_field(name="⚡ Puissance Spirituelle", value=f"**{ps}** PS", inline=True)
        embed_intro.add_field(
            name="Comment interagir",
            value=(
                "Utilisez `/pnj-parler` dans ce thread pour parler au PNJ.\n"
                f"**{MAX_ECHANGES} échanges** maximum par session.\n"
                "Utilisez `/pnj-congedier` pour mettre fin à la rencontre."
            ),
            inline=False,
        )
        await thread.send(embed=embed_intro)

        # Confirmer à l'invocateur
        restant_apres = restant - 1
        await interaction.followup.send(
            f"Le PNJ **{pnj_data['emoji']} {pnj_data['nom']}** a été invoqué dans {thread.mention}.\n"
            f"Invocations restantes aujourd'hui : **{restant_apres}/{QUOTA_JOURNALIER}**",
            ephemeral=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  /pnj-parler
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="pnj-parler",
        description="Parle au PNJ actif dans ce thread.",
    )
    @app_commands.describe(message="Ce que vous dites ou faites (en RP)")
    async def pnj_parler(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()

        # Vérifier que l'API est disponible
        if not self._client:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "La clé API Anthropic est absente. Les PNJ IA sont désactivés."
                ),
            )
            return

        # Vérifier qu'on est dans un thread avec une session PNJ active
        thread_id = str(interaction.channel_id)
        session = self._get_session(thread_id)
        if not session:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Aucune session PNJ active dans ce thread.\n"
                    "Utilisez `/pnj-invoquer` dans un salon textuel pour invoquer un PNJ."
                ),
            )
            return

        # Vérifier le nombre d'échanges
        if session["interactions"] >= MAX_ECHANGES:
            pnj_data = PNJ_CATALOGUE.get(session["pnj_type"], PNJ_CATALOGUE["personnalise"])
            embed_depart = self._construire_embed(
                pnj_data,
                (
                    "*(Le PNJ semble s'éloigner, comme rappelé par une force invisible. "
                    "La connexion spirituelle s'estompe... La session a atteint sa limite "
                    f"de **{MAX_ECHANGES} échanges**.)*"
                ),
                "Départ",
            )
            await interaction.followup.send(embed=embed_depart)
            # Nettoyer la session
            del self.data["sessions"][thread_id]
            await self._sauvegarder()
            return

        # Récupérer les données du PNJ
        pnj_data = PNJ_CATALOGUE.get(session["pnj_type"], PNJ_CATALOGUE["personnalise"])

        # Ajouter le message du joueur à l'historique
        # Préfixer le message du joueur avec son nom pour le contexte IA
        contenu_joueur = f"[{interaction.user.display_name}] : {message}"
        session["historique"].append({"role": "user", "content": contenu_joueur})

        # Construire le prompt système
        system_prompt = self._construire_system_prompt(pnj_data, session.get("contexte", ""))

        # Générer la réponse du PNJ
        texte_reponse = await self._generer_reponse(system_prompt, session["historique"])

        # Ajouter la réponse à l'historique
        session["historique"].append({"role": "assistant", "content": texte_reponse})
        session["interactions"] += 1
        await self._sauvegarder()

        # Poster la réponse du joueur en texte simple pour le contexte visuel
        await interaction.followup.send(
            f"**{interaction.user.display_name}** :\n> {message}"
        )

        # Poster la réponse du PNJ en embed
        echanges_restants = MAX_ECHANGES - session["interactions"]
        embed_reponse = self._construire_embed(pnj_data, texte_reponse)
        if echanges_restants <= 3:
            embed_reponse.add_field(
                name="⏳ Échanges restants",
                value=f"**{echanges_restants}** échange{'s' if echanges_restants > 1 else ''} avant le départ du PNJ.",
                inline=False,
            )
        await interaction.channel.send(embed=embed_reponse)

    # ══════════════════════════════════════════════════════════════════════════
    #  /pnj-congedier
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="pnj-congedier",
        description="Met fin à la session PNJ dans ce thread.",
    )
    async def pnj_congedier(self, interaction: discord.Interaction):
        await interaction.response.defer()

        thread_id = str(interaction.channel_id)
        session = self._get_session(thread_id)

        if not session:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Aucune session PNJ active dans ce thread."
                ),
            )
            return

        # Vérifier les permissions : seul l'invocateur ou le staff peut congédier
        est_invocateur = interaction.user.id == session["invocateur_id"]
        est_staff = interaction.user.guild_permissions.manage_messages
        if not est_invocateur and not est_staff:
            await interaction.followup.send(
                embed=self._construire_embed_erreur(
                    "Seul l'invocateur du PNJ ou un membre du staff peut le congédier."
                ),
            )
            return

        # Récupérer les données du PNJ pour l'embed de départ
        pnj_data = PNJ_CATALOGUE.get(session["pnj_type"], PNJ_CATALOGUE["personnalise"])

        # Générer un message d'adieu via l'IA
        system_prompt = self._construire_system_prompt(pnj_data, session.get("contexte", ""))
        historique_adieu = session["historique"].copy()
        historique_adieu.append({
            "role": "user",
            "content": "[Le joueur met fin à l'interaction. Fais tes adieux en personnage, brièvement.]",
        })
        texte_adieu = await self._generer_reponse(system_prompt, historique_adieu)

        # Poster l'embed d'adieu
        embed_adieu = self._construire_embed(pnj_data, texte_adieu, "Départ")
        embed_adieu.add_field(
            name="Session terminée",
            value=(
                f"**{session['interactions']}** échange{'s' if session['interactions'] != 1 else ''} "
                f"au total.\nThread archivé."
            ),
            inline=False,
        )
        await interaction.followup.send(embed=embed_adieu)

        # Supprimer la session
        del self.data["sessions"][thread_id]
        await self._sauvegarder()

        # Archiver le thread si possible
        channel = interaction.channel
        if isinstance(channel, discord.Thread):
            try:
                await channel.edit(archived=True, reason="Session PNJ terminée")
            except discord.HTTPException as e:
                log.warning("Impossible d'archiver le thread PNJ %s : %s", thread_id, e)

    # ══════════════════════════════════════════════════════════════════════════
    #  /pnj-liste
    # ══════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="pnj-liste",
        description="Liste les PNJ disponibles et les sessions actives.",
    )
    async def pnj_liste(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # ── Partie 1 : catalogue des PNJ ──
        lignes_catalogue = []
        for cle, data in PNJ_CATALOGUE.items():
            if cle == "personnalise":
                continue  # Affiché séparément
            lignes_catalogue.append(
                f"{data['emoji']} **{data['nom']}** · ⚡ {data.get('ps', '?')} PS\n"
                f"  *{data['description']}*"
            )

        texte_catalogue = "\n\n".join(lignes_catalogue)
        texte_catalogue += (
            f"\n\n🎭 **PNJ Personnalisé** · ⚡ 50 PS (défaut)\n"
            f"  *Un PNJ défini par vos soins via le paramètre `contexte`.*"
        )

        embed_catalogue = discord.Embed(
            title="📋 PNJ Disponibles",
            description=texte_catalogue,
            color=COULEURS["or_ancien"],
        )
        embed_catalogue.set_footer(text="⸻ Infernum Aeterna · PNJ ⸻")

        # ── Partie 2 : sessions actives ──
        sessions = self.data.get("sessions", {})
        sessions_valides = []
        sessions_a_nettoyer = []

        for tid, sess in sessions.items():
            # Vérifier que le thread existe encore
            thread = self.bot.get_channel(int(tid))
            if thread is None:
                sessions_a_nettoyer.append(tid)
                continue
            pnj_info = PNJ_CATALOGUE.get(sess["pnj_type"], PNJ_CATALOGUE["personnalise"])
            invocateur = self.bot.get_user(sess["invocateur_id"])
            nom_invocateur = invocateur.display_name if invocateur else f"ID {sess['invocateur_id']}"
            sessions_valides.append(
                f"{pnj_info['emoji']} **{sess['pnj_nom']}** — {thread.mention}\n"
                f"  Invoqué par *{nom_invocateur}* · "
                f"{sess['interactions']}/{MAX_ECHANGES} échanges"
            )

        # Nettoyer les sessions orphelines (threads supprimés)
        if sessions_a_nettoyer:
            for tid in sessions_a_nettoyer:
                del self.data["sessions"][tid]
            await self._sauvegarder()

        if sessions_valides:
            texte_sessions = "\n\n".join(sessions_valides)
        else:
            texte_sessions = "*Aucune session PNJ active actuellement.*"

        embed_sessions = discord.Embed(
            title="🔮 Sessions actives",
            description=texte_sessions,
            color=COULEURS["pourpre_infernal"],
        )
        embed_sessions.set_footer(text="⸻ Infernum Aeterna · PNJ ⸻")

        # ── Quota de l'utilisateur ──
        user_id = str(interaction.user.id)
        _, restant = self._verifier_quota(user_id)
        embed_sessions.add_field(
            name="Votre quota",
            value=f"**{restant}/{QUOTA_JOURNALIER}** invocations restantes aujourd'hui.",
            inline=False,
        )

        await interaction.followup.send(embeds=[embed_catalogue, embed_sessions], ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(PNJ(bot))
