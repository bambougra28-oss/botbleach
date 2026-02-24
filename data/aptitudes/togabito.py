"""
INFERNUM AETERNA — Aptitudes Togabito
Les Quatre Souffrances : Jigokusari, Gōka, Saisei, Rinki
Contenu original — aucun équivalent canon.
"""

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 1 — JIGOKUSARI (地獄鎖) Les Chaînes de l'Enfer
# ══════════════════════════════════════════════════════════════════════════════

JIGOKUSARI = {
    "id": "toga_jigokusari",
    "nom": "Jigokusari",
    "kanji": "地獄鎖",
    "sous_titre": "Les Chaînes de l'Enfer",
    "faction": "togabito",
    "couleur": 0x4A0080,
    "description": (
        "Les chaînes ne sont pas une punition — elles sont une extension de l'Enfer "
        "lui-même, une excroissance de sa volonté qui s'enroule autour des âmes damnées. "
        "Ceux qui cessent de les combattre découvrent qu'elles peuvent servir."
    ),
    "aptitudes": [
        # ── P1 — Éveil ──────────────────────────────────────────────────────
        {
            "id": "toga_jig_p1a",
            "nom": "Kusari Sōjū",
            "kanji": "鎖操",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Manipuler les chaînes plutôt que les subir. Le Togabito apprend à diriger "
                "les maillons comme des appendices supplémentaires — lents d'abord, maladroits, "
                "mais répondant à la volonté plutôt qu'à la douleur. En ancrant une chaîne "
                "et en se tractant le long d'elle, le damné acquiert une mobilité rudimentaire "
                "mais efficace — un Hohō de fer et de souffrance. Le premier pas vers "
                "la maîtrise est d'accepter que ces chaînes sont désormais une partie de soi."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_jig_p1b",
            "nom": "Kusari Tate",
            "kanji": "鎖盾",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Les chaînes se tissent devant le corps en un bouclier improvisé. "
                "Le métal infernal absorbe les impacts avec une efficacité que l'acier "
                "des Trois Mondes ne peut égaler — chaque maillon est saturé du Reishi "
                "corrompu de l'Enfer, une matière que même le Zanpakutō peine à trancher."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_jig_p1c",
            "nom": "Kusari Kankaku",
            "kanji": "鎖感覚",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Perception par les Chaînes. Chaque maillon transmet les vibrations du "
                "monde — le souffle d'un ennemi caché, le frémissement d'une attaque en "
                "préparation, la pulsation d'un Reishi distant. Le Togabito cesse de "
                "percevoir les chaînes comme un poids et commence à les sentir comme des "
                "nerfs, des extensions de sa propre conscience."
            ),
            "condition_rp": None,
        },
        # ── P2 — Maîtrise ───────────────────────────────────────────────────
        {
            "id": "toga_jig_p2a",
            "nom": "Kusari Sha",
            "kanji": "鎖射",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_jig_p1a"],
            "rang_min": None,
            "description": (
                "Les chaînes se détachent du corps et fusent vers la cible à une vitesse "
                "qui défie la physique spirituelle. Le Togabito projette ses maillons comme "
                "des lances, chaque impact marqué par un écho de la souffrance qu'ils portent. "
                "Technique également utilisée pour la propulsion rapide : ancrer une chaîne "
                "à un point distant et s'y tracter en un instant — l'équivalent damné du "
                "Shunpo ou du Sonído. Les chaînes reviennent toujours — elles connaissent "
                "le chemin du retour."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_jig_p2b",
            "nom": "Kusari Rō",
            "kanji": "鎖牢",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_jig_p1b"],
            "rang_min": None,
            "description": (
                "Une prison de chaînes se referme autour de l'adversaire. Les maillons "
                "s'entremêlent, se resserrent, et chaque tentative de fuite ne fait que "
                "les rendre plus étroits. La cage n'est pas seulement physique — le Reishi "
                "infernal qui la compose érode lentement la volonté de celui qui y est pris."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_jig_p2c",
            "nom": "Kusari Kyūshū",
            "kanji": "鎖吸収",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_jig_p1a", "toga_jig_p1c"],
            "rang_min": None,
            "description": (
                "L'Absorption des Chaînes. Les maillons infernaux ne se contentent plus "
                "de frapper — ils drainent. Au contact, le Reishi de la cible est aspiré "
                "le long des chaînes comme du sang dans un siphon. La victime s'affaiblit "
                "tandis que le Togabito se restaure. Un vampire de métal et de souffrance."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_jig_p2d",
            "nom": "Kusari Katachi",
            "kanji": "鎖形",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_jig_p1b", "toga_jig_p1c"],
            "rang_min": None,
            "description": (
                "La Forme des Chaînes. Les maillons se reconfigurent — une lance, un mur, "
                "une griffe géante, un pont, des ailes de métal. Le Togabito ne manipule "
                "plus des chaînes mais une matière plastique qui prend la forme de sa "
                "volonté. Sous forme d'ailes ou de ressorts, les chaînes offrent un "
                "déplacement aérien rapide, compensant l'absence de techniques de vitesse "
                "conventionnelles. La seule limite est l'imagination et la quantité de "
                "Reishi infernal disponible. Les formes les plus complexes exigent une "
                "concentration absolue."
            ),
            "condition_rp": None,
        },
        # ── P3 — Transcendance ──────────────────────────────────────────────
        {
            "id": "toga_jig_p3a",
            "nom": "Rensa Shin'i",
            "kanji": "連鎖神意",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_jig_p2a", "toga_jig_p2b"],
            "rang_min": "ko_togabito",
            "description": (
                "Les chaînes cessent d'être des outils — elles deviennent une volonté. "
                "Le Togabito ne les contrôle plus consciemment : elles anticipent, réagissent, "
                "frappent et défendent comme une intelligence autonome reliée à l'instinct "
                "du porteur. L'Enfer lui-même semble obéir. Les Kushanāda se détournent "
                "sur le passage de celui qui a atteint la Volonté Enchaînée."
            ),
            "condition_rp": "Survie à un affrontement avec un Kushanāda ou épreuve des Strates profondes.",
        },
        {
            "id": "toga_jig_p3b",
            "nom": "Kusari Tengoku",
            "kanji": "鎖天獄",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_jig_p2c", "toga_jig_p2d"],
            "rang_min": "gokuo",
            "description": (
                "La Prison Céleste des Chaînes. L'espace se plie. Les maillons se déploient "
                "en une cage tridimensionnelle qui ne capture pas seulement le corps mais "
                "le Reishi lui-même — une poche d'Enfer miniature se forme autour de la cible. "
                "À l'intérieur, les lois de la physique sont celles de la Strate la plus "
                "profonde. Nul ne s'en échappe sans l'accord du geôlier."
            ),
            "condition_rp": "Arc RP de maîtrise totale des Chaînes, connexion avec les Strates profondes.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 2 — GŌKA (業火) Le Feu Karmique
# ══════════════════════════════════════════════════════════════════════════════

GOKA = {
    "id": "toga_goka",
    "nom": "Gōka",
    "kanji": "業火",
    "sous_titre": "Le Feu Karmique",
    "faction": "togabito",
    "couleur": 0x8B0000,
    "description": (
        "Le feu de l'Enfer n'est pas une flamme — c'est un jugement. Il brûle ce qui "
        "mérite de brûler et ignore le reste. Ceux qui apprennent à le canaliser ne "
        "deviennent pas des pyromanciens — ils deviennent des bourreaux."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_gok_p1a",
            "nom": "Gokuen",
            "kanji": "獄炎",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Flamme de la Prison. Le Togabito apprend à concentrer le Reishi infernal "
                "en une flamme noire bordée de violet qui consume tout ce qu'elle touche. "
                "Ce feu ne s'éteint pas avec l'eau — il s'éteint quand il a fini de juger."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_gok_p1b",
            "nom": "Shōnetsu Kaku",
            "kanji": "焦熱殻",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Carapace Ardente. Le corps du Togabito émet une chaleur intense qui "
                "repousse les attaques physiques. Quiconque le touche à mains nues "
                "se brûle — non pas la chair, mais le Reishi lui-même, cette substance "
                "qui compose l'âme des êtres spirituels."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_gok_p1c",
            "nom": "Gōka no Ishi",
            "kanji": "業火の意志",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Volonté du Feu Karmique. Le Togabito apprend à lire les péchés dans "
                "le Reishi des autres — chaque âme porte l'empreinte de ses actes, et le "
                "feu infernal la perçoit comme un combustible. Plus le péché est lourd, "
                "plus la flamme est avide. Cette perception est un fardeau autant qu'une "
                "arme — celui qui voit les péchés des autres ne peut plus ignorer les siens."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_gok_p2a",
            "nom": "Gōka Hō",
            "kanji": "業火砲",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_gok_p1a"],
            "rang_min": None,
            "description": (
                "Le Canon Karmique. Une décharge concentrée de flamme infernale projetée "
                "en un rayon dévastateur. Le Togabito compresse la chaleur entre ses paumes "
                "et la libère d'un coup — l'impact évapore la matière spirituelle sur plusieurs "
                "mètres. Le recul est violent, le coût en endurance considérable."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_gok_p2b",
            "nom": "Shōkyaku Ya",
            "kanji": "焼却野",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_gok_p1b"],
            "rang_min": None,
            "description": (
                "La Plaine Calcinée. Le Togabito relâche son contrôle et le feu karmique "
                "se répand autour de lui en cercle, dévorant tout dans un rayon de plusieurs "
                "dizaines de mètres. Le sol se vitrifie, l'air crépite, et même les ombres "
                "semblent fuir. Un acte de destruction indiscriminée."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_gok_p2c",
            "nom": "Gōka Yaiba",
            "kanji": "業火刃",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_gok_p1a", "toga_gok_p1c"],
            "rang_min": None,
            "description": (
                "La Lame de Feu Karmique. Le Togabito infuse le feu infernal dans une arme "
                "— chaîne, os, fragment d'acier des Strates. La flamme ne brûle pas "
                "l'objet mais l'habite, transformant chaque coup en sentence. La lame "
                "juge en même temps qu'elle tranche, et les blessures qu'elle inflige "
                "résistent à la guérison spirituelle conventionnelle."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_gok_p3a",
            "nom": "Rengoku Enran",
            "kanji": "煉獄炎嵐",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_gok_p2a", "toga_gok_p2b"],
            "rang_min": "ko_togabito",
            "description": (
                "La Tempête du Purgatoire. Le Togabito ne projette plus le feu — il le "
                "devient. Son corps se dissout temporairement en une tempête de flammes "
                "karmiques qui dévore tout dans un périmètre impossible à fuir. Ceux qui "
                "survivent décrivent un mur de feu noir qui semblait vivant, qui semblait "
                "choisir. À son passage, même la pierre de l'Enfer fond."
            ),
            "condition_rp": "Arc RP de communion avec les flammes de la Strate Sulfura.",
        },
        {
            "id": "toga_gok_p3b",
            "nom": "Gōka Saiban",
            "kanji": "業火裁判",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_gok_p2a", "toga_gok_p2c"],
            "rang_min": "gokuo",
            "description": (
                "Le Tribunal de Feu. La flamme karmique atteint sa forme la plus pure — "
                "un feu qui ne brûle plus la chair mais l'âme elle-même, proportionnellement "
                "aux péchés qu'elle porte. Un innocent ne sentirait rien. Un meurtrier "
                "brûlerait jusqu'aux os. Le Togabito qui invoque ce jugement devient, "
                "l'espace d'un instant, un instrument de l'Enfer dans sa fonction originelle : "
                "non pas torturer, mais juger."
            ),
            "condition_rp": "Arc RP de confrontation avec la nature judiciaire de l'Enfer.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 3 — SAISEI (再生) La Régénération Maudite
# ══════════════════════════════════════════════════════════════════════════════

SAISEI = {
    "id": "toga_saisei",
    "nom": "Saisei",
    "kanji": "再生",
    "sous_titre": "La Régénération Maudite",
    "faction": "togabito",
    "couleur": 0x2D1B4E,
    "description": (
        "En Enfer, la mort n'est pas une fin — c'est un recommencement. Les Togabito "
        "meurent et renaissent, encore et encore, chaque résurrection gravant un peu "
        "plus de souffrance dans leur essence. Certains ont appris à canaliser ce cycle "
        "comme une arme."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_sai_p1a",
            "nom": "Jigoku Saisei",
            "kanji": "地獄再生",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La régénération accélérée, nourrie par le Reishi infernal. Les blessures "
                "se referment en quelques minutes plutôt qu'en jours. Ce n'est pas de la "
                "guérison — c'est l'Enfer qui refuse de laisser partir son prisonnier. "
                "La chair repousse, marquée de veines sombres qui trahissent l'origine "
                "du pouvoir."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_sai_p1b",
            "nom": "Tsumi no Kioku",
            "kanji": "罪の記憶",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Mémoire du Péché. Chaque mort subie en Enfer laisse une empreinte, "
                "et le Togabito apprend à lire ces empreintes — les siennes comme celles "
                "des autres. La douleur devient information, la souffrance passée devient "
                "connaissance. Un avantage acquis au prix le plus cruel."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_sai_p1c",
            "nom": "Saisei Ishiki",
            "kanji": "再生意識",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "La Conscience de la Régénération. Là où la plupart subissent la régénération "
                "comme un automatisme brutal, le Togabito apprend à la sentir, à la diriger — "
                "choisir quel tissu se reforme en premier, quelle blessure est prioritaire. "
                "Le contrôle conscient d'un processus que l'Enfer voulait aveugle."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_sai_p2a",
            "nom": "Junkan Kyōka",
            "kanji": "循環強化",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_sai_p1a"],
            "rang_min": None,
            "description": (
                "Le Cycle Renforcé. La régénération ne se contente plus de refermer les "
                "plaies — elle améliore. Chaque blessure guérie laisse le corps plus "
                "résistant qu'avant. Les os deviennent plus denses, la chair plus dure. "
                "Le Togabito qui a survécu à mille morts porte mille armures invisibles."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_sai_p2b",
            "nom": "Tsūkaku Dōka",
            "kanji": "痛覚同化",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_sai_p1b"],
            "rang_min": None,
            "description": (
                "L'Assimilation de la Douleur. Le Togabito ne ressent plus la souffrance "
                "comme un obstacle — il l'assimile comme carburant. Chaque blessure reçue "
                "accroît sa puissance au lieu de la diminuer. Un ennemi qui croit l'affaiblir "
                "en le frappant ne fait que nourrir la bête."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_sai_p2c",
            "nom": "Saisei Hoji",
            "kanji": "再生保持",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_sai_p1a", "toga_sai_p1c"],
            "rang_min": None,
            "description": (
                "La Rétention de Régénération. Le Togabito suspend volontairement la "
                "régénération — l'énergie qui aurait recousu ses plaies est stockée, "
                "comprimée, accumulée. Et quand il la libère d'un coup, la décharge "
                "de Reishi infernal explose depuis ses blessures ouvertes comme un "
                "geyser de puissance brute. Se blesser soi-même devient une stratégie."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_sai_p2d",
            "nom": "Kioku Fuyo",
            "kanji": "記憶付与",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_sai_p1b", "toga_sai_p1c"],
            "rang_min": None,
            "description": (
                "L'Imposition de Mémoires. Le Togabito projette ses propres souvenirs de "
                "mort sur l'ennemi — par contact, par regard, par le Reishi infernal qui "
                "les lie. La cible revit les agonies du damné comme si elles étaient siennes. "
                "La douleur n'est pas physique mais le traumatisme est réel, suffisant pour "
                "paralyser un esprit faible et ébranler les plus solides."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_sai_p3a",
            "nom": "Fushi no Kusari",
            "kanji": "不死鎖",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_sai_p2a", "toga_sai_p2b"],
            "rang_min": "ko_togabito",
            "description": (
                "L'Immortalité Enchaînée. Le corps du Togabito cesse d'être un corps au "
                "sens conventionnel — il devient un nœud dans le tissu même de l'Enfer, "
                "un point fixe que la destruction ne peut effacer. Tranché, il se reforme. "
                "Brûlé, il renaît des cendres. La seule limite est la volonté — et la "
                "certitude croissante que ce qui revient après chaque mort est un peu moins "
                "humain que ce qui est parti."
            ),
            "condition_rp": "Mort et résurrection RP en Enfer validée par le staff.",
        },
        {
            "id": "toga_sai_p3b",
            "nom": "Rinsai Tensei",
            "kanji": "輪際転生",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_sai_p2c", "toga_sai_p2d"],
            "rang_min": "gokuo",
            "description": (
                "La Transmigration Ultime. Le Togabito maîtrise le cycle de mort et "
                "renaissance en combat — il meurt volontairement, laissant son corps "
                "exploser en une déflagration de Reishi infernal, puis renaît quelques "
                "secondes plus tard à un point de son choix, restauré, transformé. "
                "Chaque mort le change. Chaque résurrection le rend plus étranger "
                "à ce qu'il était. Mais en combat, cette capacité est sans prix."
            ),
            "condition_rp": "Arc RP de confrontation avec la nature cyclique de l'Enfer.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  VOIE 4 — RINKI (燐気) L'Aura Phosphorescente
# ══════════════════════════════════════════════════════════════════════════════

RINKI = {
    "id": "toga_rinki",
    "nom": "Rinki",
    "kanji": "燐気",
    "sous_titre": "L'Aura Phosphorescente",
    "faction": "togabito",
    "couleur": 0x1A0033,
    "description": (
        "Le Jigoku no Rinki — les sphères noires qui suintent des murs de l'Enfer — "
        "est un poison pour la plupart des êtres spirituels. Mais les Togabito les plus "
        "anciens ont appris à l'absorber, à le façonner, à le retourner contre ceux "
        "qui les condamnent."
    ),
    "aptitudes": [
        # ── P1 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_rin_p1a",
            "nom": "Rinki Kanchi",
            "kanji": "燐気感知",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Perception du Rinki. Le Togabito développe un sixième sens capable de "
                "détecter les concentrations de Reishi infernal dans son environnement — "
                "présences cachées, pièges spirituels, fissures dimensionnelles. "
                "L'Enfer parle à ceux qui savent écouter."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_rin_p1b",
            "nom": "Rinki Gaiheki",
            "kanji": "燐気外壁",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "Le Mur Phosphorescent. Une barrière de Rinki enveloppe le corps du Togabito, "
                "repoussant les attaques spirituelles de faible intensité. Le bouclier émet "
                "une lueur sombre qui fait reculer instinctivement les êtres non corrompus."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_rin_p1c",
            "nom": "Rinki Kyūshū",
            "kanji": "燐気吸収",
            "palier": 1,
            "cout": 1,
            "prereqs": [],
            "rang_min": None,
            "description": (
                "L'Absorption du Rinki. Le Togabito aspire activement le Reishi infernal "
                "ambiant — les sphères de Rinki qui flottent dans l'air, les résidus "
                "de souffrance cristallisés dans la pierre. En Enfer, cette capacité "
                "transforme chaque strate en source de puissance. Hors de l'Enfer, "
                "le Togabito cherche instinctivement les poches de Reishi corrompu "
                "comme un assoiffé cherche l'eau."
            ),
            "condition_rp": None,
        },
        # ── P2 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_rin_p2a",
            "nom": "Rinki Hōsha",
            "kanji": "燐気放射",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_rin_p1a"],
            "rang_min": None,
            "description": (
                "La Radiation Phosphorescente. Le Togabito projette le Rinki en ondes "
                "concentriques qui corrompent le Reishi ambiant. Les sorts de Kidō "
                "s'effilochent, les techniques spirituelles perdent en cohésion. "
                "Un champ d'interférence que seuls les esprits les plus puissants "
                "peuvent traverser sans dommage."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_rin_p2b",
            "nom": "Rinki Osen",
            "kanji": "燐気汚染",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_rin_p1b"],
            "rang_min": None,
            "description": (
                "La Contamination. Le Togabito injecte du Rinki directement dans le corps "
                "de sa cible — par contact, par blessure ouverte, ou par simple proximité "
                "prolongée. Le Reishi de la victime se corrompt lentement, fragmentant "
                "sa concentration et brouillant ses sens spirituels."
            ),
            "condition_rp": None,
        },
        {
            "id": "toga_rin_p2c",
            "nom": "Rinki Yoroi",
            "kanji": "燐気鎧",
            "palier": 2,
            "cout": 2,
            "prereqs": ["toga_rin_p1b", "toga_rin_p1c"],
            "rang_min": None,
            "description": (
                "L'Armure de Rinki. Le Reishi infernal se cristallise autour du corps "
                "du Togabito en une carapace sombre et translucide. Quiconque frappe "
                "l'armure subit un contrecoup corrosif — le Rinki s'infiltre dans "
                "l'arme de l'attaquant, dans ses mains, dans son Reishi. Porter l'armure "
                "est un avertissement : me toucher, c'est se condamner."
            ),
            "condition_rp": None,
        },
        # ── P3 ───────────────────────────────────────────────────────────────
        {
            "id": "toga_rin_p3a",
            "nom": "Jigoku Kaihō",
            "kanji": "地獄解放",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_rin_p2a", "toga_rin_p2b"],
            "rang_min": "ko_togabito",
            "description": (
                "Le Togabito cesse de résister à l'Enfer. Il l'invite. Le Jigoku no Rinki "
                "ne s'infiltre plus à travers ses défenses — il est ses défenses. La chair "
                "se reconfigure selon une logique qui n'appartient ni aux vivants ni aux morts. "
                "Ce qui se tient debout après la Libération n'a plus de nom dans les langues "
                "des Trois Mondes. Les Kushanāda, pour la première fois depuis des millions "
                "d'années, reculent."
            ),
            "condition_rp": "Arc RP de confrontation avec les Strates profondes de l'Enfer.",
        },
        {
            "id": "toga_rin_p3b",
            "nom": "Jigoku Osen Kai",
            "kanji": "地獄汚染界",
            "palier": 3,
            "cout": 3,
            "prereqs": ["toga_rin_p2a", "toga_rin_p2c"],
            "rang_min": "gokuo",
            "description": (
                "Le Monde de Corruption Infernale. Le Togabito irradie un Rinki si dense "
                "et si pur que tout le Reishi dans un vaste périmètre se corrompt — les "
                "sorts se retournent, les techniques se désagrègent, les armes spirituelles "
                "se fissurent. Tout Reishi dans la zone devient du Rinki, et seul le "
                "Togabito sait naviguer dans ce chaos. Le champ de bataille lui appartient "
                "littéralement."
            ),
            "condition_rp": "Arc RP de domination totale du Rinki, maîtrise des Strates supérieures.",
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════════════════════════════

VOIES_TOGABITO = [JIGOKUSARI, GOKA, SAISEI, RINKI]
