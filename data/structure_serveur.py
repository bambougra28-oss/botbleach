"""
INFERNUM AETERNA — Structure complète du serveur Discord
Toute la topologie : rôles, catégories, channels, permissions.
"""

import discord

# ══════════════════════════════════════════════════════════════════════════════
#  RÔLES — définition (nom, couleur, mentionnable, hoisted)
# ══════════════════════════════════════════════════════════════════════════════

ROLES = [
    # ── Administration ────────────────────────────────────────────────────────
    {"cle": "architecte",         "nom": "⛩️ Architecte",            "couleur": 0xC9A84C, "hoist": True,  "mentionable": False, "position": 90},
    {"cle": "gardien_des_portes", "nom": "🔱 Gardien des Portes",    "couleur": 0x6B1FA8, "hoist": True,  "mentionable": False, "position": 85},
    {"cle": "emissaire",          "nom": "⚜️ Émissaire",             "couleur": 0xE8E8F0, "hoist": True,  "mentionable": False, "position": 80},
    {"cle": "chroniqueur",        "nom": "📜 Chroniqueur",           "couleur": 0xD4AF37, "hoist": False, "mentionable": False, "position": 70},

    # ── Factions (base) ───────────────────────────────────────────────────────
    {"cle": "shinigami",          "nom": "死神 Shinigami",            "couleur": 0xE8E8F0, "hoist": True,  "mentionable": True,  "position": 60},
    {"cle": "togabito",           "nom": "咎人 Togabito",             "couleur": 0x6B1FA8, "hoist": True,  "mentionable": True,  "position": 59},
    {"cle": "arrancar",           "nom": "破面 Arrancar",             "couleur": 0x8A8A7A, "hoist": True,  "mentionable": True,  "position": 58},
    {"cle": "quincy",             "nom": "滅却師 Quincy",             "couleur": 0x1A3A6B, "hoist": True,  "mentionable": True,  "position": 57},

    # ── Rangs Shinigami ───────────────────────────────────────────────────────
    {"cle": "sotaicho",           "nom": "👑 総隊長 Sōtaichō",        "couleur": 0xFFD700, "hoist": False, "mentionable": True,  "position": 56},
    {"cle": "taicho",             "nom": "⭐ 隊長 Taichō",            "couleur": 0xF5F5F5, "hoist": False, "mentionable": True,  "position": 55},
    {"cle": "fukutaicho",         "nom": "🎖️ 副隊長 Fukutaichō",      "couleur": 0xDDDDDD, "hoist": False, "mentionable": True,  "position": 54},
    {"cle": "sanseki",            "nom": "⚔️ 三席 Sanseki",           "couleur": 0xBBBBBB, "hoist": False, "mentionable": True,  "position": 53},
    {"cle": "yonseki",            "nom": "🗡️ 四席 Yonseki",           "couleur": 0xAAAAAA, "hoist": False, "mentionable": True,  "position": 52},
    {"cle": "shinigami_asserm",   "nom": "☯️ 死神 Shinigami",         "couleur": 0x999999, "hoist": False, "mentionable": True,  "position": 51},
    {"cle": "gakusei",            "nom": "🎓 学生 Gakusei",           "couleur": 0x777777, "hoist": False, "mentionable": True,  "position": 50},

    # ── Rangs Togabito ────────────────────────────────────────────────────────
    {"cle": "gokuo",              "nom": "👑 獄王 Gokuō",             "couleur": 0xBB30FF, "hoist": False, "mentionable": True,  "position": 48},
    {"cle": "ko_togabito",        "nom": "⛓️ 古咎人 Ko-Togabito",     "couleur": 0x9B30FF, "hoist": False, "mentionable": True,  "position": 47},
    {"cle": "tan_togabito",       "nom": "🔗 鍛咎人 Tan-Togabito",    "couleur": 0x7B20DF, "hoist": False, "mentionable": True,  "position": 46},
    {"cle": "togabito_damne",     "nom": "🩸 咎人 Togabito",          "couleur": 0x5B10BF, "hoist": False, "mentionable": True,  "position": 45},
    {"cle": "zainin",             "nom": "💀 罪人 Zainin",            "couleur": 0x4B009F, "hoist": False, "mentionable": True,  "position": 44},

    # ── Rangs Arrancar / Hollow ───────────────────────────────────────────────
    {"cle": "rey",                "nom": "👑 王 Rey",                 "couleur": 0xE8D8C0, "hoist": False, "mentionable": True,  "position": 43},
    {"cle": "espada",             "nom": "💠 十刃 Espada",            "couleur": 0xC8C8C0, "hoist": False, "mentionable": True,  "position": 42},
    {"cle": "privaron_espada",    "nom": "◈ 十刃落ち Privaron Espada","couleur": 0xA8A8A0, "hoist": False, "mentionable": True,  "position": 41},
    {"cle": "fraccion",           "nom": "◇ 従属官 Fracción",        "couleur": 0x8A8A82, "hoist": False, "mentionable": True,  "position": 40},
    {"cle": "numeros",            "nom": "○ 数字持ち Números",        "couleur": 0x6A6A62, "hoist": False, "mentionable": True,  "position": 39},
    {"cle": "vasto_lorde",        "nom": "🟣 最上大虚 Vasto Lorde",   "couleur": 0x6B3FA0, "hoist": False, "mentionable": True,  "position": 38},
    {"cle": "adjuchas",           "nom": "🔵 中級大虚 Adjuchas",      "couleur": 0x2D4F7F, "hoist": False, "mentionable": True,  "position": 37},
    {"cle": "gillian",            "nom": "🟢 最下大虚 Gillian",       "couleur": 0x2D5F2D, "hoist": False, "mentionable": True,  "position": 36},
    {"cle": "horo",               "nom": "◽ 虚 Horō",               "couleur": 0x4A4A42, "hoist": False, "mentionable": True,  "position": 35},

    # ── Rangs Quincy ──────────────────────────────────────────────────────────
    {"cle": "seitei",             "nom": "👑 聖帝 Seitei",            "couleur": 0x5A7FCC, "hoist": False, "mentionable": True,  "position": 33},
    {"cle": "schutzstaffel",      "nom": "✦ 親衛隊 Schutzstaffel",   "couleur": 0x4A6FBB, "hoist": False, "mentionable": True,  "position": 32},
    {"cle": "sternritter",        "nom": "✧ 星十字騎士団 Sternritter","couleur": 0x3A5FAB, "hoist": False, "mentionable": True,  "position": 31},
    {"cle": "jagdarmee",          "nom": "⊕ 狩猟部隊 Jagdarmee",     "couleur": 0x2F4F9B, "hoist": False, "mentionable": True,  "position": 30},
    {"cle": "quincy_confirme",    "nom": "∗ 滅却師 Quincy",          "couleur": 0x2A4F9B, "hoist": False, "mentionable": True,  "position": 29},
    {"cle": "minarai",            "nom": "∘ 見習い Minarai",         "couleur": 0x1A3F8B, "hoist": False, "mentionable": True,  "position": 28},

    # ── Rôles fonctionnels ────────────────────────────────────────────────────
    {"cle": "personnage_valide",  "nom": "✅ Personnage Validé",     "couleur": 0x57F287, "hoist": False, "mentionable": False, "position": 20},
    {"cle": "en_attente",         "nom": "⏳ En Attente",            "couleur": 0xFEE75C, "hoist": False, "mentionable": False, "position": 19},
    {"cle": "voyageur",            "nom": "🌀 Voyageur",              "couleur": 0x7B7D8A, "hoist": False, "mentionable": False, "position": 19},
    {"cle": "observateur",        "nom": "👁️ Observateur",           "couleur": 0x5865F2, "hoist": False, "mentionable": False, "position": 18},
    {"cle": "evenement_actif",    "nom": "🎲 Événement Actif",       "couleur": 0xEB459E, "hoist": False, "mentionable": True,  "position": 17},
    {"cle": "abonne_annonces",    "nom": "📣 Annonces",              "couleur": 0x5865F2, "hoist": False, "mentionable": True,  "position": 16},
    {"cle": "rp_ouvert",          "nom": "🎭 RP Ouvert",             "couleur": 0xED4245, "hoist": False, "mentionable": True,  "position": 15},
    {"cle": "narrateur_ping",     "nom": "🔔 Narrateur Ping",        "couleur": 0xC9A84C, "hoist": False, "mentionable": True,  "position": 14},
]


# ══════════════════════════════════════════════════════════════════════════════
#  STRUCTURE DES CATÉGORIES ET CHANNELS
#  Format :
#    "permissions_base" : qui peut voir / écrire par défaut
#    "channels" : liste de channels avec leurs overrides
# ══════════════════════════════════════════════════════════════════════════════

def _lecture_seule(everyone=True):
    """Shorthand : tout le monde voit, personne n'écrit."""
    return {"everyone_view": True, "everyone_send": False}

def _staff_only():
    """Shorthand : invisible pour tout le monde, visible pour le staff."""
    return {"everyone_view": False, "everyone_send": False}

# ── Tags prédéfinis pour les forums RP ────────────────────────────────────────
FORUM_TAGS_RP = [
    {"nom": "🟢 En cours",  "emoji": "🟢"},
    {"nom": "🔴 Terminé",   "emoji": "🔴"},
    {"nom": "⚔️ Combat",    "emoji": "⚔️"},
    {"nom": "👤 Solo",       "emoji": "👤"},
    {"nom": "🔓 Ouvert",    "emoji": "🔓"},
    {"nom": "🔒 Fermé",     "emoji": "🔒"},
]


CATEGORIES = [
    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⸰ PORTAIL ⸰ 〕",
        "permissions": _lecture_seule(),
        "channels": [
            {"nom": "🩸・fissure-du-monde",    "type": "text", "sujet": "Bienvenue dans Infernum Aeterna.", "lecture_seule": True},
            {"nom": "⚖️・pacte-des-âmes",      "type": "text", "sujet": "Règles du serveur rédigées sous forme de serments.", "lecture_seule": True},
            {"nom": "📣・voix-du-seireitei",   "type": "text", "sujet": "Annonces officielles du staff.", "lecture_seule": True, "visible_a": "voyageur"},
            {"nom": "🎭・choisir-son-destin",  "type": "text", "sujet": "Sélection de faction via boutons.", "lecture_seule": True, "boutons_faction": True, "visible_a": "voyageur"},
            {"nom": "🔔・abonnements",         "type": "text", "sujet": "Gestion des rôles de notification.", "lecture_seule": False, "abonnements": True, "visible_a": "voyageur"},
            {"nom": "❓・esprits-perdus",      "type": "text", "sujet": "Foire aux questions — réponses en fils épinglés.", "lecture_seule": False, "visible_a": "voyageur", "ecriture_gate": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⸰ CHRONIQUES ⸰ 〕",
        "permissions": _lecture_seule(),
        "visible_a": "voyageur",
        "channels": [
            {"nom": "📖・infernum-aeterna",    "type": "text", "sujet": "Lore fondateur — la Mer Primordiale, le Péché Originel, la Fissure.", "lecture_seule": True},
            {"nom": "⚜️・les-quatre-factions", "type": "text", "sujet": "Histoire et philosophie de chaque faction.", "lecture_seule": True},
            {"nom": "👑・figures-de-legende",  "type": "text", "sujet": "Les grandes figures de l'Enfer.", "lecture_seule": True},
            {"nom": "🗺️・geographie-des-mondes","type": "text", "sujet": "Carte narrative des zones de RP.", "lecture_seule": True},
            {"nom": "⚔️・systeme-et-competences","type": "text", "sujet": "Système de points et d'aptitudes.", "lecture_seule": True},
            {"nom": "🦴・bestiaire-infernal",  "type": "text", "sujet": "Kushanāda, Jigoku no Rinki et créatures de l'Enfer.", "lecture_seule": True},
            {"nom": "📜・glossaire",           "type": "text", "sujet": "Termes japonais et leur signification.", "lecture_seule": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⸰ ADMINISTRATION ⸰ 〕",
        "permissions": _lecture_seule(),
        "visible_a": "voyageur",
        "channels": [
            {"nom": "📋・modele-de-fiche",     "type": "text", "sujet": "Modèle de fiche personnage avec bouton de soumission.", "lecture_seule": True},
            {"nom": "✅・fiches-validees",     "type": "text", "sujet": "Archives publiques — un fil par personnage validé.", "lecture_seule": True},
            {"nom": "📈・progression",         "type": "text", "sujet": "Suivi public des points, rangs et aptitudes.", "lecture_seule": True},
            {"nom": "🎯・objectifs-narratifs", "type": "text", "sujet": "Conditions pour débloquer aptitudes spéciales.", "lecture_seule": True},
            {"nom": "📥・soumission-de-fiche", "type": "text", "sujet": "Déposez votre fiche ici pour validation.", "lecture_seule": False, "valide_perso": True, "ecriture_gate": True},

        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⸰ COMMUNAUTÉ ⸰ 〕",
        "permissions": {"everyone_view": True, "everyone_send": True},
        "visible_a": "voyageur",
        "channels": [
            {"nom": "💬・entre-deux-mondes",   "type": "text", "sujet": "Discussion générale hors-RP."},
            {"nom": "🌸・présentations",       "type": "text", "sujet": "Présentez-vous à la communauté."},
            {"nom": "🎨・galerie-des-âmes",    "type": "text", "sujet": "Illustrations et art lié au serveur."},
            {"nom": "🎵・résonance",           "type": "text", "sujet": "Partages musicaux et ambiances sonores."},
            {"nom": "💡・murmures-du-staff",   "type": "forum", "sujet": "Suggestions et retours — forum avec tags."},
            {"nom": "⚔️・theorycraft",         "type": "text", "sujet": "Discussions sur les aptitudes et stratégies."},
            {"nom": "🔎・recrutement-rp",      "type": "text", "sujet": "Chercher des partenaires de RP."},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 死神 SOUL SOCIETY 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・tableau-des-missions",  "type": "text", "sujet": "Missions actives — mis à jour par le staff.", "lecture_seule": True},
            {"nom": "🏛️・le-seireitei",         "type": "forum", "sujet": "Cœur de Soul Society — créez vos scènes RP ici.", "faction_write": "shinigami", "scene_launcher": True, "forum_tags": True},
            {"nom": "⚔️・salles-de-combat",     "type": "text", "sujet": "Bouton de création de fil de combat.", "combat": True, "faction_write": "shinigami"},
            {"nom": "🗼・grandes-divisions",     "type": "forum", "sujet": "Salle inter-divisions — scènes et interactions.", "faction_write": "shinigami", "scene_launcher": True, "forum_tags": True},
            {"nom": "🔒・salle-du-conseil",     "type": "text", "sujet": "Accès Capitaines et Vice-Capitaines uniquement.", "rank_write": ["sotaicho", "taicho", "fukutaicho"], "faction_view": "shinigami"},
            {"nom": "📚・archives-de-division", "type": "forum", "sujet": "Historique et traditions des divisions.", "faction_write": "shinigami"},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 破面 HUECO MUNDO 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・hierarchie-des-espada",   "type": "text", "sujet": "Roster Espada actuel.", "lecture_seule": True},
            {"nom": "🌙・las-noches-salle-du-trone","type": "text", "sujet": "Salle du trône — accès Espada.", "rank_write": ["rey", "espada"], "faction_view": "arrancar"},
            {"nom": "🏜️・desert-de-las-noches",    "type": "forum", "sujet": "Grand désert — scènes RP Arrancar.", "faction_write": "arrancar", "scene_launcher": True, "forum_tags": True},
            {"nom": "💠・salles-de-combat",        "type": "text", "sujet": "Bouton de création de fil de combat.", "combat": True, "faction_write": "arrancar"},
            {"nom": "⚠️・zones-de-contamination",  "type": "forum", "sujet": "Scènes de contamination au Jigoku no Rinki.", "faction_write": "arrancar", "forum_tags": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⛓️ LES STRATES — L'ENFER 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・etat-de-la-fissure",      "type": "text", "sujet": "État actuel de la Fissure — mis à jour après événements majeurs.", "lecture_seule": True},
            {"nom": "🔴・pratus-premier-niveau",   "type": "forum", "sujet": "Première Strate — le Vestibule des Damnés.", "faction_write": "togabito", "scene_launcher": True, "forum_tags": True},
            {"nom": "🟠・carnale-deuxieme-niveau",  "type": "forum", "sujet": "Deuxième Strate — les Plaines Brûlantes.", "faction_write": "togabito", "scene_launcher": True, "forum_tags": True},
            {"nom": "🟡・sulfura-troisieme-niveau", "type": "forum", "sujet": "Troisième Strate — les Geysers de Soufre.", "faction_write": "togabito", "scene_launcher": True, "forum_tags": True},
            {"nom": "🔵・profundus-quatrieme-niveau","type": "forum", "sujet": "Quatrième Strate — validation staff requise.", "rank_write": ["gokuo", "ko_togabito", "tan_togabito"], "forum_tags": True},
            {"nom": "⚫・saiobu-abyssal",          "type": "text", "sujet": "Cinquième Strate — réservé aux événements majeurs.", "evenement": True},
            {"nom": "⚔️・combats-en-enfer",        "type": "text", "sujet": "Bouton de création de fil de combat infernal.", "combat": True, "faction_write": "togabito"},
            {"nom": "🧠・les-chaines-philosophie", "type": "forum", "sujet": "Monologues intérieurs et développement de personnage Togabito.", "faction_write": "togabito", "forum_tags": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 滅却師 SURVIVANTS QUINCY 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・veille-de-la-fissure",   "type": "text", "sujet": "Surveillance de la contamination — vision unique des Quincy.", "lecture_seule": True},
            {"nom": "🏚️・le-refuge",              "type": "forum", "sujet": "Repaire clandestin des survivants — scènes RP.", "faction_write": "quincy", "scene_launcher": True, "forum_tags": True},
            {"nom": "🏹・salles-de-combat",       "type": "text", "sujet": "Bouton de création de fil de combat.", "combat": True, "faction_write": "quincy"},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 🌍 MONDE DES VIVANTS 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・incidents-repertories",  "type": "text", "sujet": "Liste des anomalies actives signalées.", "lecture_seule": True},
            {"nom": "🏙️・ville-principale",       "type": "forum", "sujet": "Zone urbaine — scènes RP toutes factions.", "cross_faction": True, "scene_launcher": True, "forum_tags": True},
            {"nom": "🌲・zones-isolees",          "type": "forum", "sujet": "Zones naturelles isolées — scènes RP.", "cross_faction": True, "scene_launcher": True, "forum_tags": True},
            {"nom": "🕳️・portails-actifs",        "type": "text", "sujet": "[ÉVÉNEMENT] Actif uniquement lors d'ouvertures de portail.", "evenement": True},
            {"nom": "⚔️・confrontations",         "type": "text", "sujet": "Conflits inter-factions dans le Monde des Vivants.", "combat": True, "cross_faction": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 ⚔️ LA FRONTIÈRE 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📌・etat-de-la-frontiere",    "type": "text", "sujet": "Situation mise à jour après chaque événement majeur.", "lecture_seule": True},
            {"nom": "🌑・no-mans-land",            "type": "forum", "sujet": "Territoire entre les mondes — scènes RP toutes factions.", "cross_faction": True, "scene_launcher": True, "forum_tags": True},
            {"nom": "🔴・la-fissure-principale",   "type": "forum", "sujet": "L'épicentre — scènes RP les plus intenses du serveur.", "cross_faction": True, "scene_launcher": True, "forum_tags": True},
            {"nom": "⚔️・combats-de-frontiere",   "type": "text", "sujet": "Affrontements aux abords de la Fissure.", "combat": True, "cross_faction": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 📔 JOURNAUX DES ÂMES 〕",
        "permissions": {"everyone_view": False, "everyone_send": False},
        "visible_a": "personnage_valide",
        "channels": [
            {"nom": "📔・journaux-des-ames",      "type": "forum", "sujet": "Journal personnel de chaque personnage — monologues, réflexions, événements clés.", "cross_faction": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 📣 CHRONIQUES VIVANTES 〕",
        "permissions": _lecture_seule(),
        "visible_a": "voyageur",
        "channels": [
            {"nom": "✍️・journal-de-l-enfer",     "type": "text", "sujet": "Narrations épiques des événements majeurs — bot uniquement.", "lecture_seule": True, "narrateur": True},
            {"nom": "⚡・flash-evenements",       "type": "text", "sujet": "Alertes courtes d'événements — bot uniquement.", "lecture_seule": True, "narrateur": True},
            {"nom": "🏆・hall-des-legendes",      "type": "text", "sujet": "Exploits notables des personnages.", "lecture_seule": True, "narrateur": True},
            {"nom": "📅・calendrier-des-arcs",    "type": "text", "sujet": "Calendrier narratif des arcs en cours.", "lecture_seule": True},
            {"nom": "🗂️・archives-des-arcs",      "type": "text", "sujet": "Résumés des arcs terminés.", "lecture_seule": True},
        ]
    },

    # ──────────────────────────────────────────────────────────────────────────
    {
        "nom": "〔 🔒 STAFF — INVISIBLE 〕",
        "permissions": _staff_only(),
        "channels": [
            {"nom": "💬・discussions-staff",      "type": "text", "sujet": "Canal de communication interne."},
            {"nom": "✅・validations",            "type": "text", "sujet": "Fiches en attente de validation."},
            {"nom": "⚙️・configuration-bot",     "type": "text", "sujet": "Commandes de configuration du bot."},
            {"nom": "📊・logs-bot",              "type": "text", "sujet": "Journaux automatiques du bot."},
            {"nom": "🗺️・planification",         "type": "text", "sujet": "Planning des arcs et événements."},
            {"nom": "🎭・gestion-evenements",     "type": "text", "sujet": "Organisation des événements narratifs."},
            {"nom": "🐛・signalement-bugs",       "type": "text", "sujet": "Rapport de bugs et anomalies du bot."},
        ]
    },
]
