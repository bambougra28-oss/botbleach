"""
INFERNUM AETERNA — Aptitudes Quincy
Les Quatre Héritages : Reishi Sōsa, Blut, Hirenkyaku, Seikei
"""

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 1 — REISHI SŌSA (霊子操作) La Manipulation des Particules
# ══════════════════════════════════════════════════════════════════════════════

REISHI_SOSA = {
    "id": "quin_reishi",
    "nom": "Reishi Sōsa",
    "kanji": "霊子操作",
    "sous_titre": "La Manipulation des Particules",
    "faction": "quincy",
    "couleur": 0x4169E1,
    "description": (
        "Là où les Shinigami canalisent leur propre Reishi et les Hollow le dévorent, "
        "les Quincy le commandent. Ils absorbent les particules spirituelles de "
        "l'environnement et les reconfigurent selon leur volonté — un art qui "
        "fait d'eux les architectes du champ de bataille."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_rei_p1a",
            "nom": "Reishi Shūshū",
            "kanji": "霊子収集",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Collecte du Reishi. Le Quincy apprend à tirer les particules "
                "spirituelles de l'air, du sol, de la matière environnante. Dans un "
                "monde saturé de Reishi comme Soul Society, cette capacité transforme "
                "le territoire ennemi en arsenal personnel. Dans le Monde des Vivants, "
                "le flux est plus ténu mais jamais absent."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_rei_p1b",
            "nom": "Heilig Pfeil",
            "kanji": "神聖滅矢",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Flèche Sacrée. Le Reishi collecté est comprimé en un projectile de "
                "lumière bleue tiré depuis l'arc spirituel du Quincy. Chaque flèche est "
                "forgée en une fraction de seconde, sa puissance proportionnelle au "
                "Reishi disponible. Précise, rapide, et surtout — destructrice pour "
                "les Hollow d'une manière que les Zanpakutō ne peuvent imiter."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_rei_p1c",
            "nom": "Reishi Kōchiku",
            "kanji": "霊子構築",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Construction de Reishi. Au-delà de la collecte, le Quincy apprend à "
                "donner forme aux particules — des plateformes sous les pieds, des marches "
                "dans le vide, des structures simples mais solides. La base de tout l'art "
                "Quincy : si vous maîtrisez les particules, le monde entier est votre atelier."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_rei_p2a",
            "nom": "Reishi Busō",
            "kanji": "霊子武装",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_rei_p1a", "quin_rei_p1c"],
            "rang_min": None,
            "description": (
                "L'Armement de Reishi. Au-delà de l'arc, le Quincy façonne le Reishi "
                "en armes de toute forme — épées, boucliers, plateformes, pièges. "
                "L'imagination est la seule limite, tant que la concentration tient. "
                "Les constructions sont solides comme l'acier mais se dissipent dès "
                "que l'attention vacille."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_rei_p2b",
            "nom": "Gintō Kiso",
            "kanji": "銀筒基礎",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_rei_p1b"],
            "rang_min": None,
            "description": (
                "Les Fondamentaux du Gintō. Les tubes d'argent emplis de Reishi liquéfié "
                "— Heizen, Gritz, Wolke — les trois techniques de base qui transforment "
                "de petits conteneurs en armes dévastatrices. L'art de la préparation : "
                "le Quincy qui entre en combat avec ses tubes chargés a déjà gagné "
                "la moitié de la bataille."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_rei_p2c",
            "nom": "Gintō Senryaku",
            "kanji": "銀筒戦略",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_rei_p2b"],
            "rang_min": None,
            "description": (
                "Le Gintō Stratégique. Au-delà des techniques fondamentales, le Quincy "
                "apprend à combiner les tubes — superposer un Gritz sur un Heizen pour "
                "piéger puis détruire, chaîner les Wolke pour créer un réseau de défenses. "
                "Le champ de bataille devient un échiquier de tubes prépositionnés, chaque "
                "pièce prête à exploser au signal."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_rei_p3a",
            "nom": "Ransōtengai",
            "kanji": "乱装天傀",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_rei_p2a", "quin_rei_p2b"],
            "rang_min": "sternritter",
            "description": (
                "La Marionnette Céleste Désordonnée. Des fils de Reishi invisibles "
                "s'attachent aux membres du Quincy et les animent indépendamment du "
                "corps — même paralysé, même les os brisés, le combattant continue "
                "de se mouvoir. Une technique née du refus absolu de tomber, transmise "
                "par ceux qui ont préféré se battre jusqu'à la mort plutôt que de "
                "s'agenouiller."
            ),
            "condition_rp": "Arc RP de dépassement physique face à une adversité écrasante.",
        },
        {
            "id": "quin_rei_p3b",
            "nom": "Gintō Meister",
            "kanji": "銀筒極意",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_rei_p2c", "quin_rei_p2a"],
            "rang_min": "sternritter",
            "description": (
                "La Maîtrise Absolue du Gintō. Le Quincy transcende les techniques nommées "
                "et crée les siennes — des constructions de Reishi liquéfié d'une complexité "
                "et d'une puissance inédites. Les tubes deviennent des pinceaux et le champ "
                "de bataille une toile. Seuls les plus grands stratèges Quincy atteignent "
                "ce niveau où la préparation et l'improvisation ne font plus qu'un."
            ),
            "condition_rp": "Arc RP de maîtrise stratégique du Gintō validé.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 2 — BLUT (血装) La Fortification du Sang
# ══════════════════════════════════════════════════════════════════════════════

BLUT = {
    "id": "quin_blut",
    "nom": "Blut",
    "kanji": "血装",
    "sous_titre": "La Fortification du Sang",
    "faction": "quincy",
    "couleur": 0x8B0000,
    "description": (
        "Le Reishi coule dans les veines des Quincy comme un second sang. Le Blut est "
        "l'art de canaliser ce flux pour renforcer le corps — en défense ou en attaque, "
        "jamais les deux en même temps. Le choix entre survivre et frapper est la "
        "décision la plus fondamentale du combattant Quincy."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_blu_p1a",
            "nom": "Blut Vene",
            "kanji": "静血装",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Veine Statique. Le Reishi se concentre dans les vaisseaux pour "
                "durcir le corps de l'intérieur. La peau se marque de motifs lumineux "
                "sous l'effort — des veines bleues qui trahissent le flux de puissance. "
                "Le résultat est une résistance qui rivalise avec le Hierro des Arrancar."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_blu_p1b",
            "nom": "Blut Arterie",
            "kanji": "動血装",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "L'Artère Dynamique. Le flux de Reishi inverse sa priorité — au lieu "
                "de protéger, il amplifie. Les coups portés gagnent une puissance "
                "disproportionnée, les flèches percent ce qu'elles ne pouvaient "
                "qu'égratigner. Le prix : une vulnérabilité totale pendant l'activation."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_blu_p1c",
            "nom": "Blut Konro",
            "kanji": "血装根路",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Voie Radiculaire du Sang. Le Quincy apprend à percevoir et contrôler "
                "les flux de Reishi dans son propre système sanguin — chaque veine, chaque "
                "artère, chaque capillaire devient un circuit conscient. Cette connaissance "
                "intime de son propre corps est la fondation sur laquelle reposent toutes "
                "les techniques de Blut avancées."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_blu_p2a",
            "nom": "Blut Anhaben",
            "kanji": "血装外殻",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_blu_p1a"],
            "rang_min": None,
            "description": (
                "La Coque de Sang. Le Blut Vene s'étend au-delà du corps et enveloppe "
                "le Quincy dans une bulle de protection qui consume tout ce qu'elle "
                "touche — vêtements, sol, adversaire trop proche. Une défense absolue "
                "dont le coût est la destruction de tout ce qui n'est pas le protégé."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_blu_p2b",
            "nom": "Blut Wechsel",
            "kanji": "血装転換",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_blu_p1b", "quin_blu_p1c"],
            "rang_min": None,
            "description": (
                "La Conversion du Sang. La transition entre Vene et Arterie devient "
                "instantanée — un battement de cœur suffit pour passer de la défense "
                "absolue à l'attaque dévastatrice. Ce qui était un choix douloureux "
                "devient un outil tactique, un rythme de combat unique aux Quincy "
                "d'élite."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_blu_p2c",
            "nom": "Blut Erweiterung",
            "kanji": "血装拡張",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_blu_p1a", "quin_blu_p1c"],
            "rang_min": None,
            "description": (
                "L'Extension du Blut. Le flux de Reishi sanguin ne se limite plus au "
                "corps du Quincy — il s'étend aux alliés proches par contact physique "
                "ou aux armes tenues en main. Le Blut Vene peut protéger un camarade, "
                "le Blut Arterie peut charger une lame. Le prix est un drainage accru "
                "des réserves personnelles."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_blu_p3a",
            "nom": "Blut Vereint",
            "kanji": "血装統一",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_blu_p2a", "quin_blu_p2b"],
            "rang_min": "sternritter",
            "description": (
                "Le Sang Unifié. L'impossible devient réalité — Vene et Arterie coexistent "
                "dans le même flux. Le Quincy frappe avec une puissance maximale tout en "
                "maintenant une défense impénétrable. La contradiction est résolue par "
                "une maîtrise du Reishi qui défie la compréhension. Ceux qui l'atteignent "
                "cessent d'être des combattants — ils deviennent des forces de la nature."
            ),
            "condition_rp": "Arc RP de maîtrise absolue du Blut validé.",
        },
        {
            "id": "quin_blu_p3b",
            "nom": "Blut Allerhöchst",
            "kanji": "血装至高",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_blu_p3a", "quin_blu_p2c"],
            "rang_min": "schutzstaffel",
            "description": (
                "Le Blut Suprême. Le Reishi sanguin atteint une densité et une pureté "
                "sans précédent — chaque cellule du corps est saturée de puissance. "
                "Le Quincy transcende les limites biologiques : les blessures se referment "
                "instantanément, la force dépasse les barèmes connus, et même les attaques "
                "qui devraient être fatales sont réduites à des égratignures. L'héritage "
                "sanguin du Quincy dans sa forme la plus absolue."
            ),
            "condition_rp": "Arc RP de transcendance de l'héritage sanguin Quincy.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 3 — HIRENKYAKU (飛廉脚) Le Pas du Dieu du Vent
# ══════════════════════════════════════════════════════════════════════════════

HIRENKYAKU = {
    "id": "quin_hirenkyaku",
    "nom": "Hirenkyaku",
    "kanji": "飛廉脚",
    "sous_titre": "Le Pas du Dieu du Vent",
    "faction": "quincy",
    "couleur": 0x87CEEB,
    "description": (
        "Les Quincy ne marchent pas — ils glissent sur des courants de Reishi "
        "qu'ils créent sous leurs pieds. Le Hirenkyaku est la mobilité élevée "
        "au rang d'art, une danse de lumière et de vitesse qui transforme "
        "le champ de bataille en échiquier."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_hir_p1a",
            "nom": "Hirenkyaku",
            "kanji": "飛廉脚",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le déplacement à haute vitesse des Quincy. Le praticien crée une "
                "plateforme de Reishi sous ses pieds et surfe dessus, atteignant des "
                "vitesses comparables au Shunpo. Moins explosif en accélération, "
                "mais plus fluide en mouvement continu — le Quincy ne s'arrête pas "
                "entre deux points, il trace un arc."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_hir_p1b",
            "nom": "Schatten",
            "kanji": "影",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "L'Ombre. Le Quincy se dissout dans les ombres environnantes et "
                "réapparaît à un autre point d'ombre dans un rayon limité. Ce n'est "
                "pas un déplacement — c'est une transition par un espace intermédiaire "
                "que les Quincy appellent le Schatten Bereich, le Domaine des Ombres."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_hir_p1c",
            "nom": "Reishi Ashiba",
            "kanji": "霊子足場",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les Plateformes de Reishi. Le Quincy crée des points d'appui solides "
                "dans le vide — des marches invisibles qui permettent le combat aérien, "
                "la course verticale, les changements de direction impossibles. Là où "
                "les Shinigami se tiennent sur le Reishi ambiant par instinct, les Quincy "
                "construisent délibérément leurs propres routes dans le ciel."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_hir_p2a",
            "nom": "Kirchenlied",
            "kanji": "聖唱",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_hir_p1a"],
            "rang_min": None,
            "description": (
                "Le Chant de l'Église. Une technique de déplacement offensif — le Quincy "
                "trace un pentacle de Reishi au sol puis s'en sert comme tremplin pour "
                "une attaque aérienne dévastatrice. Le pentacle explose après utilisation, "
                "ajoutant une onde de choc au point de départ."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_hir_p2b",
            "nom": "Sprenger",
            "kanji": "爆散",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_hir_p1b"],
            "rang_min": None,
            "description": (
                "L'Explosion. Cinq Seele Schneider plantés au sol forment un pentacle "
                "qui, alimenté par un Gintō, génère une explosion de Reishi concentré. "
                "La zone piégée devient un enfer de lumière bleue qui désintègre tout "
                "ce qui s'y trouve. Lent à préparer, impossible à survivre."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_hir_p2c",
            "nom": "Licht Spur",
            "kanji": "光の軌跡",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_hir_p1a", "quin_hir_p1c"],
            "rang_min": None,
            "description": (
                "La Traînée de Lumière. Le Hirenkyaku laisse derrière lui un sillage de "
                "Reishi solidifié — un mur, un fil, une barrière que l'adversaire doit "
                "contourner ou traverser à ses risques. Le Quincy dessine des pièges en "
                "se déplaçant, transformant sa fuite en offensive et sa course en "
                "architecture de combat."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_hir_p3a",
            "nom": "Licht Regen",
            "kanji": "光の雨",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_hir_p2a", "quin_hir_p2b"],
            "rang_min": "sternritter",
            "description": (
                "La Pluie de Lumière. Le ciel se remplit de milliers de flèches de "
                "Reishi qui s'abattent simultanément sur une zone entière. Chaque "
                "projectile est guidé par la volonté du tireur — pas un seul ne manque "
                "sa cible. L'effet visuel est celui d'un déluge de lumière bleue si "
                "dense qu'il transforme la nuit en jour. Il n'y a nulle part où se cacher."
            ),
            "condition_rp": "Maîtrise RP démontrée du tir en volume validée.",
        },
        {
            "id": "quin_hir_p3b",
            "nom": "Raumverschiebung",
            "kanji": "空間転移",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_hir_p2b", "quin_hir_p2c"],
            "rang_min": "sternritter",
            "description": (
                "Le Déplacement Spatial. Le Quincy transcende la vitesse — au lieu de se "
                "déplacer rapidement, il réécrit sa position dans l'espace. Un pas, et il "
                "est ailleurs — pas entre-temps, pas de trajectoire, pas de traînée. La "
                "téléportation pure par manipulation du Reishi environnemental. Le coût "
                "est un drainage massif de Reishi et un temps de récupération entre "
                "chaque saut."
            ),
            "condition_rp": "Arc RP de transcendance spatiale du Hirenkyaku.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 4 — SEIKEI (聖体) Le Corps Sacré
# ══════════════════════════════════════════════════════════════════════════════

SEIKEI = {
    "id": "quin_seikei",
    "nom": "Seikei",
    "kanji": "聖体",
    "sous_titre": "Le Corps Sacré",
    "faction": "quincy",
    "couleur": 0xFFD700,
    "description": (
        "Le corps du Quincy est un temple — un réceptacle forgé par des générations "
        "d'héritage spirituel. Le Seikei est la voie qui exploite ce potentiel jusqu'à "
        "ses limites absolues, transformant l'héritier en incarnation de la volonté "
        "de son lignage."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_sei_p1a",
            "nom": "Quincy Kreuz",
            "kanji": "滅却十字",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Croix de la Destruction. L'artefact fondamental de tout Quincy — "
                "le médium à travers lequel le Reishi est canalisé pour former l'arc "
                "spirituel. Sa forme varie selon le lignage et l'individu : pendentif, "
                "bracelet, gant. Perdre sa Croix, c'est perdre une partie de soi."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_sei_p1b",
            "nom": "Seele Schneider",
            "kanji": "魂切",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Trancheur d'Âmes. La seule arme de mêlée des Quincy — une lame "
                "de Reishi vibrant à une fréquence si élevée qu'elle ne coupe pas "
                "la matière mais relâche les liens entre les particules spirituelles. "
                "Ce qu'elle touche ne se brise pas — il se désagrège."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_sei_p1c",
            "nom": "Reishi Keitai",
            "kanji": "霊子形態",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Forme du Reishi. Le Quincy apprend à altérer la forme de son arme "
                "spirituelle — l'arc peut devenir une arbalète, une épée de lumière, un "
                "bouclier, selon les besoins. Cette flexibilité fondamentale est le signe "
                "d'un Quincy qui ne se contente pas de tirer des flèches mais qui comprend "
                "que le Reishi est un matériau, pas un outil."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_sei_p2a",
            "nom": "Sklaverei",
            "kanji": "聖隷",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_sei_p1a"],
            "rang_min": None,
            "description": (
                "L'Esclavage Sacré. Le Quincy arrache le Reishi des structures "
                "environnantes — bâtiments, arbres, sol — et l'absorbe de force. "
                "Les constructions s'effritent, le terrain se désagrège. Dans un "
                "monde fait de Reishi, cette capacité est la terreur incarnée : "
                "le Quincy dévore littéralement la réalité pour se renforcer."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_sei_p2b",
            "nom": "Seishi Kyōka",
            "kanji": "聖矢強化",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_sei_p1b", "quin_sei_p1c"],
            "rang_min": None,
            "description": (
                "Le Renforcement des Flèches Sacrées. Les projectiles cessent d'être "
                "de simples traits de lumière — chaque flèche peut se multiplier en vol, "
                "changer de trajectoire, exploser en fragments. Le Quincy tire une flèche "
                "et elle devient dix. Les dix deviennent cent. La précision ne souffre pas "
                "de la multiplication — au contraire, elle s'affine."
            ),
            "condition_rp": None,
        },
        {
            "id": "quin_sei_p2c",
            "nom": "Seirei Kaihō",
            "kanji": "聖霊解放",
            "palier": 2,
            "cout": 2,
            "prereqs": ["quin_sei_p1a", "quin_sei_p1c"],
            "rang_min": None,
            "description": (
                "La Libération de l'Esprit Sacré. Le Quincy commence à manifester les "
                "prémices du Corps Sacré — des fragments d'ailes lumineux, un halo partiel, "
                "une aura de Reishi condensé. Ce n'est pas encore la transformation complète "
                "mais un aperçu de la puissance qui dort dans le sang. Suffisant pour "
                "inspirer la terreur chez ceux qui savent ce que cela annonce."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "quin_sei_p3a",
            "nom": "Vollständig",
            "kanji": "完聖体",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_sei_p2a", "quin_sei_p2c"],
            "rang_min": "sternritter",
            "description": (
                "Le Corps Sacré Complet. Des ailes de lumière jaillissent du dos du "
                "Quincy, un halo se forme au-dessus de sa tête. Le Reishi environnant "
                "afflue vers lui comme attiré par un aimant divin. Dans cet état, "
                "le Quincy transcende les limites humaines — il est, pendant un bref "
                "instant, ce que les anciens auraient appelé un ange."
            ),
            "condition_rp": "Épreuve RP démontrant la foi et la détermination du Quincy.",
        },
        {
            "id": "quin_sei_p3b",
            "nom": "Schrift",
            "kanji": "聖文字",
            "palier": 3,
            "cout": 3,
            "prereqs": ["quin_sei_p3a", "quin_sei_p2b"],
            "rang_min": "sternritter",
            "description": (
                "La Lettre Sacrée. Une capacité unique gravée dans l'âme du Quincy — "
                "non pas apprise mais révélée, comme si elle avait toujours été là, "
                "attendant d'être nommée. Chaque Schrift est différent, chacun est "
                "absolu dans son domaine. La lettre définit le porteur autant que le "
                "porteur définit la lettre. On ne choisit pas son Schrift — on le "
                "découvre, et après, rien n'est plus pareil."
            ),
            "condition_rp": "Arc RP de révélation de la Lettre Sacrée validé par le staff.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════════════════════════════

VOIES_QUINCY = [REISHI_SOSA, BLUT, HIRENKYAKU, SEIKEI]
