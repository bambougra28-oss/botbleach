"""
INFERNUM AETERNA — Aptitudes Arrancar
Les Quatre Instincts : Cero, Hierro, Sonído, Resurrección
"""

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 1 — CERO (虚閃) L'Éclair du Vide
# ══════════════════════════════════════════════════════════════════════════════

CERO = {
    "id": "arr_cero",
    "nom": "Cero",
    "kanji": "虚閃",
    "sous_titre": "L'Éclair du Vide",
    "faction": "arrancar",
    "couleur": 0xCC0000,
    "description": (
        "Le Cero est la voix du Hollow — un cri de puissance concentré en lumière "
        "destructrice. Chaque Arrancar le porte en lui depuis sa première faim. "
        "L'apprendre n'est pas une question de technique mais de contrôle : "
        "canaliser la rage sans se consumer."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_cer_p1a",
            "nom": "Cero",
            "kanji": "虚閃",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le rayon de destruction fondamental. Une décharge de Reishi concentré "
                "tirée depuis la paume, la bouche ou le bout des doigts. La couleur "
                "varie selon l'individu — rouge sang, violet profond, blanc éclatant. "
                "Chaque Cero porte l'empreinte de l'âme qui le projette."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_cer_p1b",
            "nom": "Bala",
            "kanji": "虚弾",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Balle du Vide. Un projectile de Reishi comprimé tiré à vingt fois "
                "la vitesse d'un Cero standard, au prix d'une puissance réduite d'un tiers. "
                "Ce que le Bala perd en dévastation, il le gagne en cadence — une pluie "
                "de tirs que même le Shunpo peine à esquiver."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_cer_p1c",
            "nom": "Cero Preparado",
            "kanji": "虚閃備",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Cero Préparé. L'Arrancar apprend à charger un Cero et à le retenir "
                "— la sphère de destruction concentrée reste suspendue au bout des doigts, "
                "prête à être libérée au moment optimal. Une bombe à retardement vivante "
                "qui transforme chaque geste en menace. Les adversaires les plus expérimentés "
                "savent que le Cero le plus dangereux est celui qui n'a pas encore été tiré."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_cer_p2a",
            "nom": "Gran Rey Cero",
            "kanji": "王虚の閃光",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_cer_p1a"],
            "rang_min": None,
            "description": (
                "L'Éclair Royal du Vide. Le Cero est mêlé au sang de l'Arrancar — "
                "littéralement. L'utilisateur entaille sa propre chair et mélange son "
                "essence au rayon. Le résultat est une spirale de destruction dont la "
                "puissance distord l'espace lui-même. Interdit à Las Noches sous peine "
                "de faire s'effondrer le dôme."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_cer_p2b",
            "nom": "Cero Oscuras",
            "kanji": "黒虚閃",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_cer_p1b"],
            "rang_min": None,
            "description": (
                "Le Cero des Ténèbres. Un faisceau noir qui absorbe la lumière autour "
                "de lui avant de frapper. Sa puissance est telle que même les barrières "
                "de Kidō de haut niveau vacillent à son contact. Seuls les Arrancar "
                "ayant atteint un seuil de puissance considérable peuvent le manifester."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_cer_p2c",
            "nom": "Cero Doble",
            "kanji": "虚閃二重",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_cer_p1a", "arr_cer_p1c"],
            "rang_min": None,
            "description": (
                "Le Cero Double. L'Arrancar absorbe le Cero adverse dans sa propre paume "
                "et le fusionne avec le sien avant de le renvoyer — doublé. La maîtrise "
                "requise est terrifiante : un instant de trop et l'énergie dévore la main. "
                "Un instant de moins et le Cero ennemi frappe de plein fouet. Les rares "
                "qui maîtrisent cette technique transforment chaque attaque adverse en "
                "munition gratuite."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_cer_p3a",
            "nom": "Cero Metralleta",
            "kanji": "無限虚閃",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_cer_p2a", "arr_cer_p2b"],
            "rang_min": "privaron_espada",
            "description": (
                "La Mitrailleuse du Vide. Des centaines de Cero tirés simultanément, "
                "chacun aussi puissant qu'un tir individuel. Le ciel se remplit de lumière "
                "destructrice et le sol se transforme en cratère. Le coût en Reishi est "
                "colossal — seuls les Arrancar dont les réserves frôlent l'infini peuvent "
                "soutenir ce barrage sans s'effondrer."
            ),
            "condition_rp": "Démonstration de puissance Cero validée en combat RP.",
        },
        {
            "id": "arr_cer_p3b",
            "nom": "Cero Sincrético",
            "kanji": "虚閃融合",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_cer_p2a", "arr_cer_p2c"],
            "rang_min": "espada",
            "description": (
                "Le Cero Syncrétique. La fusion de tous les types de Cero maîtrisés en "
                "un seul tir — Gran Rey, Oscuras, Doble, les propriétés de chacun tissées "
                "dans un rayon unique. Le résultat est une abomination de lumière et de "
                "ténèbres qui ne ressemble à rien de connu, un faisceau qui adapte sa "
                "nature à la cible pour maximiser la destruction. Chaque Cero Sincrético "
                "est unique — et dévastateur."
            ),
            "condition_rp": "Arc RP de transcendance de la nature Cero, fusion des variants.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 2 — HIERRO (鋼皮) La Peau d'Acier
# ══════════════════════════════════════════════════════════════════════════════

HIERRO = {
    "id": "arr_hierro",
    "nom": "Hierro",
    "kanji": "鋼皮",
    "sous_titre": "La Peau d'Acier",
    "faction": "arrancar",
    "couleur": 0x808080,
    "description": (
        "La peau d'un Arrancar n'est pas de la peau — c'est du Reishi condensé jusqu'à "
        "la densité du métal. Le Hierro est l'instinct de survie cristallisé, la preuve "
        "qu'un Hollow a survécu assez longtemps pour que son corps devienne une armure."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_hie_p1a",
            "nom": "Hierro",
            "kanji": "鋼皮",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Peau d'Acier. Le Reishi se condense autour du corps en une couche "
                "invisible qui repousse les attaques physiques et spirituelles de faible "
                "intensité. Les lames ordinaires glissent sur la peau sans laisser de marque. "
                "Ce n'est pas une technique activée — c'est un état permanent."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_hie_p1b",
            "nom": "Pesquisa",
            "kanji": "探査回路",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Circuit de Détection. Un sonar spirituel qui cartographie les sources "
                "de Reishi dans un large périmètre. L'Arrancar ferme les yeux et perçoit "
                "chaque présence comme une pulsation distincte — puissance, distance, "
                "intention. Impossible de se cacher d'un Pesquisa affûté."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_hie_p1c",
            "nom": "Hierro Garra",
            "kanji": "鋼爪",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les Griffes d'Acier. Le Reishi qui durcit la peau se concentre aux "
                "extrémités — les doigts deviennent des lames, les ongles des dagues. "
                "L'Arrancar retrouve les armes les plus primitives du Hollow : celles "
                "qui poussent de sa propre chair. Aucun désarmement possible contre "
                "des griffes qui font partie du corps."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_hie_p2a",
            "nom": "Hierro Kyōka",
            "kanji": "鋼皮強化",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_hie_p1a"],
            "rang_min": None,
            "description": (
                "Le Hierro Renforcé. La concentration de Reishi dans la peau atteint un "
                "seuil où même les lames de Capitaine laissent à peine une éraflure. "
                "L'Arrancar peut choisir de concentrer davantage la protection sur une zone "
                "spécifique — un bras levé pour bloquer, un torse bombé pour encaisser."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_hie_p2b",
            "nom": "Negación",
            "kanji": "否定",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_hie_p1b"],
            "rang_min": None,
            "description": (
                "Le Champ de Négation. Un pilier de lumière jaune descend du ciel et "
                "enveloppe l'Arrancar ou un allié, créant un espace inviolable que rien "
                "ne peut pénétrer ni quitter. Un pouvoir de protection absolue — "
                "le prix étant l'immobilité totale pendant sa durée."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_hie_p2c",
            "nom": "Hierro Kaeshi",
            "kanji": "鋼皮返し",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_hie_p1a", "arr_hie_p1c"],
            "rang_min": None,
            "description": (
                "Le Renvoi du Hierro. Le Reishi condensé dans la peau ne se contente plus "
                "d'absorber l'impact — il le restitue. L'énergie cinétique de l'attaque "
                "est capturée par le Hierro et renvoyée vers l'assaillant comme un ricochet "
                "spirituel. Plus le coup est puissant, plus le retour est dévastateur. "
                "Frapper cet Arrancar revient à se frapper soi-même."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_hie_p3a",
            "nom": "Kōsoku Saisei",
            "kanji": "高速再生",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_hie_p2a", "arr_hie_p2b"],
            "rang_min": "privaron_espada",
            "description": (
                "La Régénération Ultra-Rapide. La capacité que la plupart des Arrancar "
                "sacrifient en arrachant leur masque — retrouvée, maîtrisée, transcendée. "
                "Les membres sectionnés repoussent en secondes, les organes se reconstituent. "
                "Le coût est un appétit de Reishi dévorant — le corps consomme l'énergie "
                "environnante pour se reconstruire, laissant un vide spirituel autour du "
                "régénérant."
            ),
            "condition_rp": "Arc RP de reconnexion avec l'instinct Hollow originel.",
        },
        {
            "id": "arr_hie_p3b",
            "nom": "Hierro Tenshi",
            "kanji": "鋼皮天至",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_hie_p2a", "arr_hie_p2c"],
            "rang_min": "espada",
            "description": (
                "Le Hierro Absolu. La densité du Reishi dans la peau atteint un niveau "
                "que la théorie jugeait impossible — les lames ne rayent plus, les sorts "
                "se dissipent au contact, même les techniques de haut rang glissent sans "
                "mordre. L'Arrancar devient une forteresse vivante. Le revers : cette "
                "concentration permanente draine les réserves de Reishi et rend chaque "
                "mouvement légèrement plus lourd, comme si le corps payait le prix de "
                "son invulnérabilité."
            ),
            "condition_rp": "Arc RP de transcendance défensive validé.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 3 — SONÍDO (響転) Le Pas Résonnant
# ══════════════════════════════════════════════════════════════════════════════

SONIDO = {
    "id": "arr_sonido",
    "nom": "Sonído",
    "kanji": "響転",
    "sous_titre": "Le Pas Résonnant",
    "faction": "arrancar",
    "couleur": 0x4169E1,
    "description": (
        "Là où le Shunpo des Shinigami est silence et précision, le Sonído est tonnerre "
        "et instinct. L'Arrancar ne calcule pas sa trajectoire — il la ressent. Le son "
        "qui accompagne chaque déplacement est le battement de cœur d'un prédateur "
        "qui fond sur sa proie."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_son_p1a",
            "nom": "Sonído",
            "kanji": "響転",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Pas Résonnant. L'équivalent Arrancar du Shunpo — un déplacement "
                "instantané accompagné d'un bruit sourd caractéristique, comme un "
                "battement de tambour étouffé. Moins gracieux que le Shunpo mais tout "
                "aussi efficace, et certains affirment qu'il est plus rapide en ligne droite."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_son_p1b",
            "nom": "Garganta",
            "kanji": "黒腔",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Gorge Noire. L'Arrancar déchire le tissu de la réalité pour ouvrir "
                "un passage entre les mondes. Le corridor qui s'ouvre est un néant absolu "
                "où le voyageur doit créer son propre chemin en solidifiant le Reishi "
                "sous ses pieds. Un faux pas signifie l'errance éternelle entre les dimensions."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_son_p1c",
            "nom": "Yobigoe",
            "kanji": "呼声",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Cri d'Appel. Un rugissement chargé de Reishi qui déstabilise les "
                "sens spirituels de l'adversaire — le Pesquisa se brouille, le Shunpo "
                "dérape, la concentration vacille. Ce n'est pas une attaque mais un "
                "prélude, le grondement du tonnerre avant la foudre. L'instinct du "
                "prédateur qui annonce qu'il chasse."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_son_p2a",
            "nom": "Gemelos Sonído",
            "kanji": "双児響転",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_son_p1a"],
            "rang_min": None,
            "description": (
                "Le Sonído Jumeau. La vitesse atteint un seuil où l'Arrancar laisse "
                "derrière lui non pas une image rémanente mais un véritable clone — "
                "une copie de Reishi assez solide pour frapper, bloquer, distraire. "
                "Pendant une fraction de seconde, il existe réellement en deux endroits."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_son_p2b",
            "nom": "Gonzui",
            "kanji": "魂吸",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_son_p1b"],
            "rang_min": None,
            "description": (
                "L'Aspiration des Âmes. L'Arrancar ouvre la bouche et inhale — non pas "
                "de l'air, mais le Reishi ambiant, les âmes faibles, les résidus spirituels. "
                "Un acte de prédation pure qui restaure les réserves d'énergie et affaiblit "
                "tout ce qui se trouve dans le périmètre. Primitif, efficace, terrifiant."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_son_p2c",
            "nom": "Chokkaku Sonído",
            "kanji": "直覚響転",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_son_p1a", "arr_son_p1c"],
            "rang_min": None,
            "description": (
                "Le Sonído Instinctif. Le déplacement cesse d'être une décision consciente "
                "— le corps bouge avant la pensée, guidé par l'instinct de prédateur hérité "
                "du Hollow originel. L'Arrancar ne sait pas où il va aller jusqu'à ce qu'il "
                "y soit déjà. Contre-intuitif mais d'une efficacité terrifiante : aucune "
                "anticipation ne peut prédire un mouvement que l'auteur lui-même n'a pas planifié."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_son_p3a",
            "nom": "Gran Caída",
            "kanji": "大落下",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_son_p2a", "arr_son_p2b"],
            "rang_min": "privaron_espada",
            "description": (
                "La Grande Chute. L'Arrancar concentre la totalité de son Reishi dans une "
                "descente verticale d'une vitesse et d'une puissance apocalyptiques. "
                "Le point d'impact génère une onde de choc qui ravage tout dans un rayon "
                "considérable. C'est la gravité elle-même weaponisée — un météore vivant "
                "qui choisit où il frappe."
            ),
            "condition_rp": "Arc RP de transcendance de ses limites physiques.",
        },
        {
            "id": "arr_son_p3b",
            "nom": "Depredador",
            "kanji": "捕食踏破",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_son_p2a", "arr_son_p2c"],
            "rang_min": "espada",
            "description": (
                "Le Prédateur. L'Arrancar verrouille une proie et la chasse à travers les "
                "dimensions — Sonído après Sonído, inlassable, implacable. La vitesse "
                "augmente avec chaque pas, l'instinct affine chaque trajectoire. Fuir est "
                "futile : la Garganta s'ouvre et se ferme dans le sillage du chasseur. "
                "Nulle distance, nul mur, nulle dimension ne peut protéger la proie d'un "
                "Depredador lancé à pleine vitesse."
            ),
            "condition_rp": "Arc RP de chasse transcendant les limites dimensionnelles.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 4 — RESURRECCIÓN (帰刃) Le Retour de la Lame
# ══════════════════════════════════════════════════════════════════════════════

RESURRECCION = {
    "id": "arr_resurreccion",
    "nom": "Resurrección",
    "kanji": "帰刃",
    "sous_titre": "Le Retour de la Lame",
    "faction": "arrancar",
    "couleur": 0x2F4F4F,
    "description": (
        "Le Zanpakutō d'un Arrancar n'est pas un compagnon — c'est un sceau. Il contient "
        "la puissance Hollow originelle, comprimée et domestiquée. La Resurrección brise "
        "ce sceau. Ce qui en sort n'est pas un monstre — c'est la vérité."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_res_p1a",
            "nom": "Fūin Jōtai",
            "kanji": "封印状態",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": "numeros",
            "description": (
                "L'État Scellé. L'Arrancar apprend à maintenir consciemment le sceau "
                "de son Zanpakutō, canalisant un filet de puissance Hollow sans le briser. "
                "Cette maîtrise permet d'accéder à des capacités mineures en forme scellée "
                "— griffes plus dures, sens aiguisés, instinct de prédateur affiné."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_res_p1b",
            "nom": "Instinto",
            "kanji": "本能",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": "numeros",
            "description": (
                "L'Instinct. Le souvenir du Hollow affleure à la surface — pas assez pour "
                "transformer, juste assez pour réagir. Les réflexes deviennent surhumains, "
                "le corps esquive avant que l'esprit ne perçoive le danger. C'est la mémoire "
                "du prédateur qui survit sous la forme humanisée."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_res_p1c",
            "nom": "Zanpakutō Kyōmei",
            "kanji": "斬魄共鳴",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": "numeros",
            "description": (
                "La Résonance du Zanpakutō. L'Arrancar cesse de voir son arme comme un "
                "objet étranger et commence à sentir le Hollow scellé à l'intérieur — ses "
                "pulsations, ses humeurs, ses désirs. La lame vibre en réponse à la volonté "
                "de son porteur, et le porteur perçoit les murmures de la bête enfermée. "
                "Un dialogue silencieux entre deux facettes de la même âme."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_res_p2a",
            "nom": "Tokusei",
            "kanji": "帰刃特性",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_res_p1b"],
            "rang_min": "numeros",
            "description": (
                "La Propriété Unique. Chaque Resurrección possède un aspect qui lui est "
                "propre — une capacité spéciale qui reflète la nature profonde du Hollow. "
                "Poison, vitesse, dureté, illusion — la forme libérée révèle l'essence "
                "de la bête, et cette essence est toujours terrifiante."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_res_p2b",
            "nom": "Kaihō no Kehai",
            "kanji": "解放の気配",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_res_p1a", "arr_res_p1c"],
            "rang_min": "numeros",
            "description": (
                "Le Signe de la Libération. Le pouvoir de la Resurrección commence à "
                "suinter à travers le sceau — une manifestation partielle qui altère "
                "l'apparence et les capacités de l'Arrancar sans briser complètement "
                "le Zanpakutō. Les yeux changent de couleur, des fragments de masque "
                "apparaissent, le Reishi s'épaissit. Un avant-goût de la véritable forme "
                "qui suffit à faire reculer les âmes faibles."
            ),
            "condition_rp": None,
        },
        {
            "id": "arr_res_p2c",
            "nom": "Honnō Kakusei",
            "kanji": "本能覚醒",
            "palier": 2,
            "cout": 2,
            "prereqs": ["arr_res_p1b", "arr_res_p1c"],
            "rang_min": "numeros",
            "description": (
                "L'Éveil Instinctif. Le dialogue avec le Hollow intérieur atteint un "
                "seuil de profondeur où les réflexes transcendent l'entraînement — le "
                "corps puise directement dans la mémoire de l'espèce Hollow, des millions "
                "d'années de prédation cristallisées en instinct pur. L'Arrancar se bat "
                "comme s'il avait combattu mille fois chaque adversaire."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "arr_res_p3a",
            "nom": "Resurrección",
            "kanji": "帰刃",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_res_p2a", "arr_res_p2b"],
            "rang_min": "privaron_espada",
            "description": (
                "La commande est prononcée. Le Zanpakutō se brise — non pas se casser, "
                "mais se dissoudre, se fondre dans la chair de l'Arrancar comme un souvenir "
                "qui refait surface. Le masque se complète partiellement. Le trou dans la "
                "poitrine pulse. Ce qui émerge n'est pas un monstre — c'est ce que le Hollow "
                "était depuis toujours, enfin débarrassé de tout ce qui n'était pas essentiel."
            ),
            "condition_rp": "Scène RP de libération émotionnelle intense.",
        },
        {
            "id": "arr_res_p3b",
            "nom": "Segunda Etapa",
            "kanji": "刃帰二段",
            "palier": 3,
            "cout": 3,
            "prereqs": ["arr_res_p3a", "arr_res_p2c"],
            "rang_min": "espada",
            "description": (
                "La Seconde Phase. Au-delà de la Resurrección, un stade que nul ne croyait "
                "possible — une libération de la libération. Le masque disparaît entièrement. "
                "Le trou se referme. L'Arrancar transcende la frontière entre Hollow et "
                "Shinigami et devient quelque chose d'entièrement nouveau. La puissance "
                "qui s'en dégage fait trembler les fondations de Las Noches."
            ),
            "condition_rp": "Arc RP de transcendance intérieure validé par le staff.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════════════════════════════

VOIES_ARRANCAR = [CERO, HIERRO, SONIDO, RESURRECCION]
