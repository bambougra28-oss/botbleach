"""
INFERNUM AETERNA — Aptitudes Shinigami
Les Quatre Disciplines : Zanjutsu, Kidō, Hohō, Hakuda
"""

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 1 — ZANJUTSU (斬術) L'Art du Sabre
# ══════════════════════════════════════════════════════════════════════════════

ZANJUTSU = {
    "id": "shin_zanjutsu",
    "nom": "Zanjutsu",
    "kanji": "斬術",
    "sous_titre": "L'Art du Sabre",
    "faction": "shinigami",
    "couleur": 0xC0C0D0,
    "description": (
        "La lame n'est pas une arme — c'est un miroir. Chaque coup porté révèle autant "
        "le porteur que la cible. Le Zanjutsu est la voie la plus ancienne des Shinigami, "
        "celle qui exige de regarder l'esprit de son Zanpakutō dans les yeux et d'accepter "
        "ce qu'il montre."
    ),
    "aptitudes": [
        # ── P1 — Éveil ──────────────────────────────────────────────────────
        {
            "id": "shin_zan_p1a",
            "nom": "Jinzen",
            "kanji": "刃禅",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Assis en silence, la lame posée sur les genoux, le Shinigami ferme les yeux "
                "et plonge dans l'espace intérieur où réside l'esprit du Zanpakutō. La méditation "
                "peut durer des heures, des jours. La plupart n'entendent rien. Ceux qui reviennent "
                "avec un nom sur les lèvres ne sont plus jamais les mêmes."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_zan_p1b",
            "nom": "Kendō",
            "kanji": "剣道",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Avant de communier avec l'esprit, il faut maîtriser la chair. Le Kendō enseigne "
                "la posture, la coupe, le rythme — les fondements sur lesquels toute technique "
                "repose. Une lame mal tenue ne tranchera jamais rien, peu importe la puissance "
                "spirituelle qu'on y injecte."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_zan_p1c",
            "nom": "Maai",
            "kanji": "間合い",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La distance juste. Le Maai est l'art de lire l'espace entre deux combattants "
                "— savoir quand l'adversaire est à portée, quand il ne l'est pas, quand un pas "
                "en avant tranchera et quand un pas en arrière sauvera. Ceux qui maîtrisent le "
                "Maai ne sont jamais là où l'ennemi les attend."
            ),
            "condition_rp": None,
        },
        # ── P2 — Maîtrise ───────────────────────────────────────────────────
        {
            "id": "shin_zan_p2a",
            "nom": "Shikai",
            "kanji": "始解",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_zan_p1a"],
            "rang_min": None,
            "description": (
                "Le Zanpakutō répond enfin à l'appel. La commande de libération est prononcée "
                "— un mot, une phrase, un ordre qui résonne dans les deux mondes à la fois. "
                "La lame change de forme, révélant une fraction de sa véritable nature. Ce n'est "
                "pas un pouvoir accordé — c'est un pacte scellé entre deux volontés."
            ),
            "condition_rp": "Scène RP de méditation Jinzen validée par le staff.",
        },
        {
            "id": "shin_zan_p2b",
            "nom": "Isshin",
            "kanji": "一心",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_zan_p1b"],
            "rang_min": None,
            "description": (
                "L'unité parfaite entre le corps et la lame. Le Shinigami ne manie plus son "
                "Zanpakutō — il le prolonge. Chaque mouvement du bras s'achève naturellement "
                "dans l'acier, sans décalage, sans hésitation. Les témoins décrivent un "
                "combattant qui semble danser avec son ombre."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_zan_p2c",
            "nom": "Ryōdan",
            "kanji": "両断",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_zan_p1b", "shin_zan_p1c"],
            "rang_min": None,
            "description": (
                "La Coupe Dévastatrice. Toute la force du praticien converge en une unique "
                "frappe descendante — un arc vertical qui ne connaît ni hésitation ni retenue. "
                "Le Ryōdan ne cherche pas à blesser — il cherche à trancher en deux. L'air "
                "lui-même se fend sur le passage de la lame, laissant une traînée de vide "
                "que le Reishi met un instant à combler."
            ),
            "condition_rp": None,
        },
        # ── P3 — Transcendance ──────────────────────────────────────────────
        {
            "id": "shin_zan_p3a",
            "nom": "Bankai",
            "kanji": "卍解",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_zan_p2a", "shin_zan_p2b"],
            "rang_min": "fukutaicho",
            "description": (
                "La libération finale. Le Zanpakutō se matérialise dans sa forme absolue — "
                "une manifestation de puissance si considérable que l'air autour du porteur "
                "se distord. Maîtriser le Bankai requiert des années d'entraînement et un lien "
                "avec l'esprit de la lame qui transcende la simple communion. Ceux qui y "
                "parviennent sont comptés sur les doigts d'une main à chaque génération."
            ),
            "condition_rp": "Arc RP complet de matérialisation et combat contre l'esprit du Zanpakutō.",
        },
        {
            "id": "shin_zan_p3b",
            "nom": "Bankai Jukuren",
            "kanji": "卍解熟練",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_zan_p3a", "shin_zan_p2c"],
            "rang_min": "taicho",
            "description": (
                "Le Bankai Maîtrisé. Là où la plupart des porteurs peinent à maintenir leur "
                "libération finale, celui-ci l'habite comme une seconde peau. Le Reishi ne "
                "fuit plus — il obéit. La forme ultime du Zanpakutō répond à la pensée, "
                "pas à la volonté. La différence est celle entre crier un ordre et murmurer "
                "un souhait. Les légendes parlent de combattants qui maintenaient leur Bankai "
                "en dormant."
            ),
            "condition_rp": "Arc RP de maîtrise du Bankai démontrant un contrôle total en situation extrême.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 2 — KIDŌ (鬼道) Les Arts Démoniaques
# ══════════════════════════════════════════════════════════════════════════════

KIDO = {
    "id": "shin_kido",
    "nom": "Kidō",
    "kanji": "鬼道",
    "sous_titre": "Les Arts Démoniaques",
    "faction": "shinigami",
    "couleur": 0x7B68EE,
    "description": (
        "Les incantations ne sont pas des formules — ce sont des clés. Chaque mot prononcé "
        "ouvre une porte dans le tissu de la réalité spirituelle, et le Kidō est l'art de "
        "choisir laquelle. Destruction, entrave, guérison — trois chemins, une seule discipline."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_kid_p1a",
            "nom": "Hadō Kiso",
            "kanji": "破道基礎",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les sorts de destruction de base — Shakkahō, Byakurai, Sōkatsui. "
                "Chacun s'apprend dans l'ordre, incantation complète obligatoire. "
                "La puissance est modeste, mais la précision est ce qui sépare un apprenti "
                "d'un cadavre. Bien des Shinigami n'iront jamais au-delà."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_kid_p1b",
            "nom": "Bakudō Kiso",
            "kanji": "縛道基礎",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les sorts d'entrave fondamentaux — Sai, Hainawa, Sekienton. "
                "Là où le Hadō détruit, le Bakudō contraint. Immobiliser un adversaire "
                "sans le tuer est souvent plus difficile que de le réduire en cendres. "
                "La maîtrise du Bakudō trahit la patience et la précision d'un esprit formé."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_kid_p1c",
            "nom": "Kidō Riron",
            "kanji": "鬼道理論",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Théorie du Kidō. Avant la puissance, la compréhension. Le praticien étudie "
                "les flux de Reishi, les structures des incantations, les principes qui lient "
                "un mot à un effet. Cette connaissance théorique est la fondation invisible sur "
                "laquelle reposent les prouesses les plus spectaculaires — et la seule raison "
                "pour laquelle le lanceur ne se désintègre pas en lançant un sort de rang élevé."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_kid_p2a",
            "nom": "Eishōhaki",
            "kanji": "詠唱破棄",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_kid_p1a", "shin_kid_p1c"],
            "rang_min": None,
            "description": (
                "L'incantation est abandonnée. Le sort est lancé par la seule volonté, "
                "sans un mot — un luxe réservé à ceux dont la maîtrise du Reishi est "
                "suffisamment enracinée pour se passer de béquilles verbales. "
                "La puissance diminue, mais la vitesse d'exécution devient terrifiante."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_kid_p2b",
            "nom": "Kaidō",
            "kanji": "回道",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_kid_p1b"],
            "rang_min": None,
            "description": (
                "L'art de guérir par le Reishi. Le pratiquant pose ses mains sur la blessure "
                "et canalise son énergie spirituelle pour reconstituer les tissus endommagés. "
                "Cela demande une compréhension intime de l'anatomie spirituelle — savoir "
                "où chaque fibre de Reishi doit aller pour que le corps se souvienne de ce "
                "qu'il était avant la blessure."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_kid_p2c",
            "nom": "Hadō Chūkyū",
            "kanji": "破道中級",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_kid_p1a"],
            "rang_min": None,
            "description": (
                "Les sorts de destruction intermédiaires — Shakkahō renforcé, Sōren Sōkatsui, "
                "Haien. Les numéros 31 à 63, là où la frontière entre art et arme s'efface. "
                "L'incantation s'allonge, la concentration requise double, et les dégâts passent "
                "du « gênant » au « définitif ». Les apprentis qui brûlent les étapes perdent "
                "généralement un bras."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_kid_p2d",
            "nom": "Bakudō Chūkyū",
            "kanji": "縛道中級",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_kid_p1b"],
            "rang_min": None,
            "description": (
                "Les sorts d'entrave intermédiaires — Rikujōkōrō, Hyapporankan, Dankū. "
                "Les numéros 31 à 63, les barrières qui arrêtent les Cero et les prisons "
                "qui piègent même les esprits les plus puissants. Le Bakudō intermédiaire "
                "est l'outil favori de ceux qui préfèrent capturer plutôt que détruire — "
                "et de ceux qui savent que parfois, le meilleur mur est invisible."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_kid_p3a",
            "nom": "Nijū Eishō",
            "kanji": "二重詠唱",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_kid_p2a", "shin_kid_p2c", "shin_kid_p2d"],
            "rang_min": "fukutaicho",
            "description": (
                "Deux incantations entrelacées, deux sorts lancés simultanément — un Hadō "
                "et un Bakudō tissés dans le même souffle. La concentration requise est "
                "inhumaine. Le moindre déséquilibre entre les deux flux de Reishi provoque "
                "un retour de flamme capable de dévorer les bras du lanceur. Seuls les "
                "maîtres absolus du Kidō osent emprunter cette voie."
            ),
            "condition_rp": "Démonstration RP de maîtrise avancée du Kidō validée.",
        },
        {
            "id": "shin_kid_p3b",
            "nom": "Kaidō Kiseki",
            "kanji": "回道奇跡",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_kid_p2b", "shin_kid_p2d"],
            "rang_min": "fukutaicho",
            "description": (
                "Le Miracle du Kaidō. La guérison transcende ses limites naturelles — organes "
                "détruits, membres sectionnés, dommages à l'âme elle-même. Le praticien ne "
                "soigne plus le corps — il réécrit ce que la blessure a effacé. Le coût est "
                "une fatigue dévorante et le risque constant de prendre sur soi la souffrance "
                "du patient. Ceux qui marchent cette voie portent les cicatrices des autres."
            ),
            "condition_rp": "Arc RP de guérison d'une blessure considérée comme fatale.",
        },
        {
            "id": "shin_kid_p3c",
            "nom": "Kidō Jōi",
            "kanji": "鬼道上位",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_kid_p2c", "shin_kid_p2d"],
            "rang_min": "fukutaicho",
            "description": (
                "Les sorts de rang 64 et au-delà — Raikōhō, Sōkatsui Suprême, Hiryū Gekizoku "
                "Shinten Raihō. L'incantation devient un poème de guerre, chaque syllabe chargée "
                "d'assez de Reishi pour raser un quartier. À ce niveau, la frontière entre Kidō "
                "et catastrophe naturelle s'efface. Les praticiens qui atteignent cette maîtrise "
                "se comptent sur les doigts d'une main dans chaque génération."
            ),
            "condition_rp": "Démonstration RP de maîtrise avancée du Hadō et du Bakudō validée par le staff.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 3 — HOHŌ (歩法) L'Art du Déplacement
# ══════════════════════════════════════════════════════════════════════════════

HOHO = {
    "id": "shin_hoho",
    "nom": "Hohō",
    "kanji": "歩法",
    "sous_titre": "L'Art du Déplacement",
    "faction": "shinigami",
    "couleur": 0x87CEEB,
    "description": (
        "La vitesse n'est pas un attribut — c'est une philosophie. Le Hohō enseigne "
        "que la distance entre deux points n'est qu'une suggestion, et que celui qui "
        "maîtrise le pas peut réécrire la géographie du champ de bataille."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hoh_p1a",
            "nom": "Shunpo",
            "kanji": "瞬歩",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Pas Éclair. Le corps disparaît d'un point et réapparaît à un autre "
                "en un battement de cil. Ce n'est pas de la téléportation — c'est un "
                "déplacement si rapide que l'œil ne peut suivre. La base de toute mobilité "
                "avancée chez les Shinigami, et le premier signe qu'un guerrier mérite "
                "d'être pris au sérieux."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hoh_p1b",
            "nom": "Senka",
            "kanji": "閃花",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "L'Éclair Floral. Un mouvement qui combine le Shunpo avec une frappe "
                "chirurgicale dans le dos de l'adversaire, visant les points de liaison "
                "du Saketsu et du Hakusui. Quand l'exécution est parfaite, la cible ne "
                "sait pas qu'elle a été touchée avant que ses jambes ne cèdent."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hoh_p1c",
            "nom": "Hohō Hansha",
            "kanji": "歩法反射",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Réflexe du Hohō. Un micro-Shunpo instinctif déclenché par la perception "
                "d'un danger imminent — le corps s'écarte avant même que l'esprit n'ait "
                "analysé la menace. Ce n'est pas une esquive calculée mais une réaction "
                "gravée dans les muscles par des milliers d'heures d'entraînement. Les "
                "vétérans qui possèdent ce réflexe survivent à des frappes qu'ils n'ont "
                "jamais vues venir."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hoh_p2a",
            "nom": "Utsusemi",
            "kanji": "空蝉",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hoh_p1a"],
            "rang_min": None,
            "description": (
                "La Mue de la Cigale. Au moment précis de l'impact, le corps s'efface "
                "en laissant derrière lui un leurre — une image rémanente si convaincante "
                "que l'adversaire ne réalise sa méprise qu'après avoir frappé dans le vide. "
                "Un art de survie qui exige un timing irréprochable."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hoh_p2b",
            "nom": "Bunshin Sōkō",
            "kanji": "分身装甲",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hoh_p1b"],
            "rang_min": None,
            "description": (
                "Des images rémanentes persistantes, chacune assez dense en Reishi pour "
                "tromper même un Pesquisa. Le praticien se multiplie aux yeux de l'ennemi, "
                "brouillant toute tentative de localisation. Les clones se dissipent au "
                "contact mais le doute qu'ils sèment est, lui, bien réel."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hoh_p2c",
            "nom": "Shunpo Renzoku",
            "kanji": "瞬歩連続",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hoh_p1a", "shin_hoh_p1c"],
            "rang_min": None,
            "description": (
                "Le Shunpo Continu. Là où la plupart marquent une pause entre deux pas éclair "
                "— un battement de cœur pour se réorienter —, le praticien enchaîne sans "
                "rupture. Le résultat est une trajectoire fluide et imprévisible, un zigzag "
                "de présences fantômes qui rend le combattant impossible à anticiper. Le prix "
                "est une endurance qui fond comme neige au soleil."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hoh_p3a",
            "nom": "Kyōka Shunpo",
            "kanji": "響花極",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_hoh_p2a", "shin_hoh_p2b"],
            "rang_min": "fukutaicho",
            "description": (
                "Le Shunpo poussé au-delà de ses limites théoriques. Le praticien ne se "
                "déplace plus — il existe simultanément en plusieurs points de l'espace "
                "pendant une fraction de seconde, comme si la réalité hésitait sur sa "
                "position. À ce niveau, la vitesse cesse d'être une question physique "
                "et devient une distorsion spirituelle pure."
            ),
            "condition_rp": "Arc RP démontrant une maîtrise absolue du Hohō.",
        },
        {
            "id": "shin_hoh_p3b",
            "nom": "Shunpo Senkō",
            "kanji": "瞬歩閃光",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_hoh_p2c", "shin_hoh_p2a"],
            "rang_min": "taicho",
            "description": (
                "L'Éclair du Shunpo. Le déplacement atteint une vitesse qui dépasse la "
                "perception spirituelle — non seulement les yeux ne suivent plus, mais le "
                "Pesquisa, l'Analyse Reishi, les sens augmentés ne détectent rien. Le "
                "praticien laisse dans son sillage des ondes de choc qui ébranlent les "
                "structures environnantes. Se déplacer à cette vitesse est se transformer "
                "en projectile vivant."
            ),
            "condition_rp": "Arc RP de transcendance des limites de la vitesse.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 4 — HAKUDA (白打) L'Art du Combat à Mains Nues
# ══════════════════════════════════════════════════════════════════════════════

HAKUDA = {
    "id": "shin_hakuda",
    "nom": "Hakuda",
    "kanji": "白打",
    "sous_titre": "L'Art du Combat à Mains Nues",
    "faction": "shinigami",
    "couleur": 0xCD853F,
    "description": (
        "Quand la lame est brisée, quand le Kidō est épuisé, quand le Shunpo ne suffit "
        "plus à fuir — il reste le corps. Le Hakuda est la discipline de ceux qui ont "
        "compris que la plus ancienne arme est aussi la plus fiable."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hak_p1a",
            "nom": "Bukei",
            "kanji": "武形",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les formes martiales de base — postures, enchaînements, blocages. "
                "Le fondement de toute technique de corps à corps. Chaque mouvement "
                "est économe, précis, répété des milliers de fois jusqu'à devenir "
                "instinct. Sans le Bukei, tout le reste n'est que gesticulation."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hak_p1b",
            "nom": "Tekken",
            "kanji": "鉄拳",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Poing de Fer. La concentration du Reishi dans les articulations "
                "transforme un coup de poing ordinaire en impact dévastateur. "
                "L'os ne casse pas — il transmet l'énergie spirituelle comme un "
                "conducteur. Les murs de pierre sont les premières victimes de "
                "ceux qui maîtrisent cette technique."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hak_p1c",
            "nom": "Tai Sabaki",
            "kanji": "体捌き",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Mouvement du Corps. L'art d'esquiver sans reculer — pivoter, glisser, "
                "rediriger la force de l'adversaire contre lui-même. Le Tai Sabaki transforme "
                "chaque attaque reçue en opportunité de contre. Le praticien ne fuit pas le "
                "danger, il le laisse passer à travers l'espace qu'il vient de quitter."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hak_p2a",
            "nom": "Ikkotsu",
            "kanji": "一骨",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hak_p1b"],
            "rang_min": None,
            "description": (
                "Un seul os. Un seul coup. La totalité du Reishi du praticien converge "
                "dans le poing au moment de l'impact. Le résultat n'est pas une frappe "
                "— c'est une détonation localisée qui pulvérise tout ce qu'elle touche. "
                "L'utilisateur ressent le contrecoup dans chaque fibre de son bras."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hak_p2b",
            "nom": "Kazaguruma",
            "kanji": "風車",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hak_p1a"],
            "rang_min": None,
            "description": (
                "Le Moulin à Vent. Le corps entier devient l'arme — une rotation "
                "aérienne qui transforme les jambes en faux. Le praticien s'élève, "
                "tourne et frappe dans un mouvement fluide qui couvre un arc de "
                "trois cent soixante degrés. Impossible à bloquer sans reculer."
            ),
            "condition_rp": None,
        },
        {
            "id": "shin_hak_p2c",
            "nom": "Tesshō",
            "kanji": "鉄掌",
            "palier": 2,
            "cout": 2,
            "prereqs": ["shin_hak_p1b", "shin_hak_p1c"],
            "rang_min": None,
            "description": (
                "La Paume de Fer. Le Reishi se concentre non pas dans le poing fermé mais "
                "dans la paume ouverte — et la frappe projette une onde de choc qui traverse "
                "les défenses physiques. Le Tesshō ne fracture pas les os — il fait vibrer "
                "le Reishi de la cible si violemment que les organes internes se disloquent. "
                "Une technique silencieuse et chirurgicale."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "shin_hak_p3a",
            "nom": "Sōkotsu",
            "kanji": "双骨",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_hak_p2a", "shin_hak_p2b"],
            "rang_min": "fukutaicho",
            "description": (
                "Deux os. Les deux poings frappent simultanément avec une puissance "
                "qui fait trembler l'air lui-même. Le Sōkotsu n'est pas simplement "
                "un Ikkotsu doublé — c'est une technique qui exige une synchronisation "
                "parfaite des deux flux de Reishi, un exploit que même les maîtres du "
                "Hakuda mettent des décennies à accomplir. L'impact est terminal."
            ),
            "condition_rp": "Victoire RP en combat rapproché contre un adversaire de rang égal ou supérieur.",
        },
        {
            "id": "shin_hak_p3b",
            "nom": "Shunkō",
            "kanji": "瞬閧",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_hak_p2a", "shin_hak_p2c", "shin_kid_p2a"],
            "rang_min": "taicho",
            "description": (
                "La Clameur Éclair. L'union interdite du Hakuda et du Kidō — le Reishi "
                "concentré par l'Eishōhaki est redirigé à travers les membres au lieu "
                "d'être projeté en sort. Le résultat est une aura de puissance brute "
                "qui enveloppe le corps du combattant, annihilant tout vêtement sur le "
                "dos et les épaules. Chaque frappe porte la force combinée du poing et "
                "du Kidō. Technique légendaire que seuls les plus grands maîtres du "
                "double art ont su manifester."
            ),
            "condition_rp": "Arc RP démontrant la fusion du Hakuda et du Kidō en combat.",
        },
        {
            "id": "shin_hak_p3c",
            "nom": "Oni Dekopin",
            "kanji": "鬼デコピン",
            "palier": 3,
            "cout": 3,
            "prereqs": ["shin_hak_p2a", "shin_hak_p2c"],
            "rang_min": "fukutaicho",
            "description": (
                "La Pichenette du Démon. L'absurdité de la technique ne fait que souligner "
                "sa terreur — un simple mouvement de doigt, une pichenette qui projette "
                "l'adversaire à travers des murs. La concentration de Reishi dans un point "
                "de contact minuscule produit une pression monstrueuse. Ceux qui en sont "
                "victimes décrivent l'impact d'un boulet de canon. Ceux qui la maîtrisent "
                "sourient."
            ),
            "condition_rp": "Démonstration RP de puissance Hakuda disproportionnée.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════════════════════════════

VOIES_SHINIGAMI = [ZANJUTSU, KIDO, HOHO, HAKUDA]
