"""
INFERNUM AETERNA — Cog Lore
Consultation rapide du lore directement depuis Discord.

Commandes :
  /lore           — résumé d'une faction, zone, ou concept
  /glossaire      — définition d'un terme en japonais
  /fiche-faction  — fiche complète d'une faction jouable
  /strates        — carte narrative des strates de l'Enfer
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from config import COULEURS


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

LORE_WEB_URL = "https://bambougra28-oss.github.io/botbleach/web/"


def _ajouter_lien_web(embed, fragment=""):
    """Ajoute un lien vers la page web complète en dernier field."""
    url = f"{LORE_WEB_URL}#{fragment}" if fragment else LORE_WEB_URL
    embed.add_field(name="\u200b", value=f"📜 [Lire le texte intégral]({url})", inline=False)


# ══════════════════════════════════════════════════════════════════════════════
#  GLOSSAIRE — 25 entrées (limite Discord)
# ══════════════════════════════════════════════════════════════════════════════

GLOSSAIRE = {
    "reishi":         ("霊子", "Particules spirituelles constitutives de toute matière dans les Trois Mondes. La densité de Reishi détermine la puissance d'une âme."),
    "reiatsu":        ("霊圧", "Pression spirituelle émise par le Reishi concentré d'un être. Mesure visible de la puissance — quand un Capitaine libère son Reiatsu, l'air lui-même plie."),
    "zanpakuto":      ("斬魄刀", "Épée spirituelle des Shinigami. Contient et canalise leur puissance. Son nom est celui d'une entité intérieure dont la voix ne se révèle qu'à ceux qui méritent de l'entendre."),
    "shikai":         ("始解", "Première libération d'un Zanpakutō. Le nom est prononcé pour activer sa forme initiale — un pacte entre le porteur et l'esprit de la lame."),
    "bankai":         ("卍解", "Seconde et ultime libération. Requiert dix ans de maîtrise minimum. Multiplie la puissance par un facteur considérable — rares sont ceux qui y survivent."),
    "hollow":         ("虚", "Âme ayant raté le passage vers Soul Society. Son cœur est dévoré par la peur et la faim. Un trou béant dans la poitrine marque l'absence de ce qui faisait d'elle une personne."),
    "resurreccion":   ("帰刃", "Libération de la puissance Hollow d'un Arrancar. Retrouve temporairement sa forme Hollow originelle — un acte de dépouillement autant que de déchaînement."),
    "jigokusari":     ("地獄鎖", "Chaînes spirituelles de l'Enfer. Issues de la chair même de ce monde, elles s'enroulent autour des âmes damnées et les contraignent dans un cycle de mort et de résurrection."),
    "kushanada":      ("倶舎那陀", "Gardiens massifs de l'Enfer. Créatures colossales à quatre membres dont la seule fonction apparente est de dévorer et de punir, sans relâche, sans fatigue."),
    "jigoku_no_rinki":("地獄の淋気", "Sphères noires phosphorescentes apparues depuis la Fissure. Marqueur visible du déséquilibre infernal qui s'infiltre dans les Trois Mondes."),
    "konso":          ("魂葬", "Rite des Shinigami pour guider les âmes humaines vers Soul Society en frappant leur front du manche du Zanpakutō. Un geste simple dont nul ne questionne la portée."),
    "konso_reisai":   ("魂葬霊祭", "Cérémonie secrète : douze ans après la mort d'un Capitaine, son Reishi est canalisé vers l'Enfer. Un mensonge bienveillant qui a duré des millénaires."),
    "reio":           ("霊王", "Roi des Âmes. Mutilé et scellé dans un cristal par les Cinq Grandes Maisons. Verrou cosmique maintenant les Trois Mondes — ni vivant, ni mort, simplement nécessaire."),
    "mimihagi":       ("耳禿", "Bras droit arraché du Reiō. Divinité de la Stagnation. L'un des Deux Piliers Maudits dont la disparition causa la Fissure."),
    "togabito":       ("咎人", "Littéralement « personne fautive ». Âmes damnées de l'Enfer — par péché, par purification, ou par le rituel secret du Konsō Reisai. Condition, non espèce."),
    "mer_primordiale":("原初の海", "État indivisé précédant les Trois Mondes. Vie et mort n'étaient pas distincts. Source de toute puissance spirituelle — et de l'obscurité qui la rongea."),
    "lichtreich":     ("光帝国", "Empire de Lumière. Civilisation Quincy à son apogée, capable de regarder le Gotei 13 en face. Ses ruines persistent dans la mémoire et dans les ombres."),
    "wandenreich":    ("見えざる帝国", "Empire Invisible. Organisation secrète des survivants Quincy, cachée dans les ombres du Seireitei depuis des siècles, nourrie par le Reishi de l'ennemi."),
    "oken":           ("王鍵", "Clé Royale. Gravée dans les os des membres de la Division Zéro. Permet l'accès au Palais du Reiō — un privilège qui est aussi une prison."),
    "gotei_13":       ("護廷十三隊", "Les Treize Divisions de la Cour. Institution militaire de Soul Society fondée par des tueurs, devenue gardienne d'un ordre bâti sur un secret inavouable."),
    "hueco_mundo":    ("虚圏", "Le Monde Creux. Désert blanc infini sous une lune immobile, domaine des Hollow. Structures de quartz et cristaux de Reishi pétrifiés par des millénaires d'accumulation."),
    "seireitei":      ("瀞霊廷", "La Cour des Âmes Pures. Cœur fortifié de Soul Society où résident les Shinigami. Ses murs blancs cachent des siècles de vérités tues."),
    "schrift":        ("聖文字", "Lettre sacrée gravée dans l'âme d'un Quincy par l'Empereur. Transforme une capacité individuelle en puissance incommensurable — un don et une chaîne."),
    "las_noches":     ("虚夜宮", "Le Palais de la Nuit Creuse. Forteresse de Hueco Mundo bâtie couche après couche par des générations d'Arrancar, chaque époque y laissant sa marque."),
    "blut":           ("血装", "Fortification spirituelle du sang, technique défensive Quincy. Le Blut Vene rend le corps quasi imperméable aux blessures ; le Blut Arterie décuple la puissance offensive."),
}


# ══════════════════════════════════════════════════════════════════════════════
#  FICHES FACTION — style narratif immersif
# ══════════════════════════════════════════════════════════════════════════════

FICHES_FACTION = {
    "shinigami": {
        "titre":   "死神 Shinigami — Gardiens de Soul Society",
        "couleur": COULEURS["blanc_seireitei"],
        "web_fragment": "shinigami",
        "sections": [
            ("Origine",
             "Avant que le Gotei ne porte ce nom, il n'y avait que des âmes — des êtres "
             "nés dans la lumière blanche de Soul Society ou arrivés du Monde des Vivants "
             "porteurs d'un Reishi d'une densité que nul ne savait encore mesurer. On les "
             "appelait Shinigami parce que leur puissance les séparait du Rukongai, mais le "
             "terme ne désignait aucune organisation. Le Gotei des origines fut fondé par des "
             "tueurs redoutables, pas des gardiens — la noblesse vint après la victoire."),
            ("Puissance",
             "Le Zanpakutō est l'extension d'une entité intérieure dont la voix ne se révèle "
             "qu'à ceux qui méritent de l'entendre. Shikai, première libération — un pacte "
             "murmuré. Bankai, seconde et ultime — dix ans de maîtrise, un facteur de puissance "
             "qui change la nature même du combat. Kidō, Hohō, Zanjutsu, Hakuda : quatre "
             "disciplines qui dessinent l'identité de chaque guerrier."),
            ("Le Secret",
             "Le Konsō Reisai envoie les Capitaines défunts en Enfer depuis des éons. Douze ans "
             "après leur mort, un Hollow est sacrifié devant la tombe, et le Reishi trop dense "
             "est canalisé vers l'abîme. On enseigne aux rangs inférieurs que c'est un passage "
             "vers le repos. C'est un mensonge bienveillant qui a duré des millénaires. La dette "
             "s'est accumulée pendant très, très longtemps."),
            ("Face à la Fissure",
             "Les Capitaines connaissent maintenant la vérité. Elle leur a été révélée quand il "
             "n'était plus possible de la cacher. Ce qu'ils font de cette vérité divise "
             "profondément le haut commandement. La question n'est pas seulement : que faire de "
             "la Fissure ? Elle est aussi : ceux que nous avons envoyés en Enfer pendant des "
             "millénaires — sont-ils nos ennemis, nos victimes, ou les deux à la fois ?"),
        ]
    },
    "togabito": {
        "titre":   "咎人 Togabito — Les Forgés par l'Enfer",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "togabito",
        "sections": [
            ("La Damnation",
             "Un Togabito n'est pas une espèce. C'est une condition — la condition de ceux que "
             "l'Enfer a réclamés. Trois voies mènent à la damnation : les péchés commis de son "
             "vivant, les crimes humains d'un Hollow purifié que la purification n'efface pas, "
             "et le Konsō Reisai qui précipite les Capitaines défunts dans les Strates. Des "
             "damnés par jugement, des damnés par accident, des damnés par nécessité cosmique."),
            ("La Transformation",
             "Des siècles de mort et de résurrection font quelque chose à une âme. Certains "
             "sombrent. D'autres durcissent. D'autres encore — les plus rares — traversent. "
             "Ils apprennent à tenir leurs Jigokusari non plus comme un fardeau mais comme une "
             "extension de leur volonté. La puissance qu'un Togabito ancien développe ne "
             "ressemble à rien de ce que les Trois Mondes connaissent — alchimique, née de "
             "l'absence prolongée de tout espoir."),
            ("Factions internes",
             "Faction Évasion : les plus récents, les plus désespérés, ceux qui veulent sortir. "
             "Faction Compréhension : les plus anciens, les plus stratèges, ceux qui veulent "
             "d'abord comprendre la cause avant d'agir. Faction Signal : les plus silencieux, "
             "ceux qui pensent que la Fissure est une transformation d'une importance bien "
             "supérieure à la simple question de s'échapper."),
            ("La Fissure vue d'en bas",
             "La Fissure est la première chose arrivée en Enfer depuis des millions d'années "
             "qui ne soit pas une punition. Les Jigokusari se relâchent légèrement. Les "
             "Kushanāda montrent des irrégularités. Le Jigoku no Rinki flotte en permanence "
             "dans certaines zones. Quelque chose a bougé dans une architecture que tout le "
             "monde croyait immuable. Les murs n'ont pas cédé — mais ils tremblent."),
        ]
    },
    "arrancar": {
        "titre":   "破面 Arrancar — Les Briseurs de Masque",
        "couleur": COULEURS["gris_sable"],
        "web_fragment": "arrancar",
        "sections": [
            ("La Tragédie Hollow",
             "Un Hollow n'est pas un monstre. C'était une personne. Quand la Chaîne du Destin "
             "se ronge entièrement, un trou s'ouvre là où le cœur était autrefois, et ce qui "
             "restait de la personne se dissout. Le masque apparaît. La faim remplace tout. "
             "C'est peut-être la tragédie la plus profonde de cette cosmologie : les monstres "
             "que les Shinigami chassent sont les victimes d'un système qui les a abandonnés."),
            ("Devenir Arrancar",
             "Un Arrancar est un Hollow qui a brisé son masque. Cet acte libère des capacités "
             "propres aux Shinigami tout en conservant la puissance d'origine. Ils retrouvent "
             "une apparence humaine. Le fragment de masque qui demeure est la cicatrice "
             "permanente de ce qu'ils étaient. Le trou dans la poitrine reste — visible, béant, "
             "sans réponse. Leur Zanpakutō contient leur puissance ; la Resurrección la libère."),
            ("Hueco Mundo",
             "Désert blanc infini sous une lune immobile. Las Noches, forteresse bâtie couche "
             "après couche par des générations d'Arrancar. Espada, Fracción, Números — une "
             "hiérarchie directe où le plus puissant commande, sans philosophie, par simple "
             "constatation. Chaque époque y a laissé sa marque architecturale, des couloirs "
             "dont la logique n'est compréhensible que par ceux qui les ont construits."),
            ("Résonance infernale",
             "Le trou dans la poitrine résonne avec l'énergie infernale d'une façon que ni les "
             "Shinigami ni les Quincy ne perçoivent. Depuis la Fissure, certains Arrancar "
             "contaminés par le Jigoku no Rinki décrivent une légère complétude — comme si le "
             "vide se remplissait partiellement. La connexion entre le trou Hollow et l'abîme "
             "qui précède les Trois Mondes n'a jamais été théorisée sérieusement. Jusqu'ici."),
        ]
    },
    "quincy": {
        "titre":   "滅却師 Quincy — Les Survivants de Lumière",
        "couleur": COULEURS["bleu_abyssal"],
        "web_fragment": "quincy",
        "sections": [
            ("Héritiers du Reiō",
             "Humains vivants portant depuis leur naissance une sensibilité spirituelle "
             "exceptionnelle, héritée du Reiō lui-même. Son fils — l'Empereur Quincy — porta "
             "cette puissance à son niveau absolu, et son sang coule dans toutes les lignées. "
             "Chaque Quincy porte un fragment de cette hérédité divine. Ils ne voient pas le "
             "Reishi comme une extension de soi, mais comme un tissu vivant dont on peut lire "
             "chaque fil et anticiper chaque rupture."),
            ("Pourquoi ils détruisent",
             "Le Reishi d'un Hollow est un poison pour un Quincy — il détruit leur âme sans "
             "rémission. Les Quincy ne détruisent pas les Hollow par jugement moral. Ils les "
             "détruisent parce qu'ils n'ont pas le luxe de les purifier. L'accusation Shinigami "
             "— *vous détruisez l'équilibre* — est pour eux une hypocrisie douloureuse : on "
             "leur reproche de survivre."),
            ("Du Lichtreich au Wandenreich",
             "L'Empire de Lumière fut une civilisation capable de regarder le Gotei en face. "
             "Ses guerriers d'élite portaient les Schrift — lettres de puissance gravées dans "
             "l'âme par l'Empereur. Après la défaite, le génocide ne s'accomplit pas dans la "
             "violence spectaculaire d'une bataille — il se déroula dans la discrétion "
             "méthodique d'une extermination organisée. La cicatrice ne se referma jamais. Le "
             "Wandenreich naquit dans les ombres du Seireitei."),
            ("Ce qu'ils voient",
             "Depuis la Fissure, la perception Quincy du Reishi leur révèle quelque chose que "
             "les autres races ne perçoivent pas : la progression infernale n'est pas aléatoire. "
             "Elle suit une logique. Elle a une direction. Quelque chose dans l'énergie qui "
             "filtre des zones de rupture semble se mouvoir vers quelque chose — ou chercher "
             "quelqu'un. Les Quincy survivants débattent en secret de ce qu'ils doivent en "
             "faire. Le temps presse."),
        ]
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  STRATES DE L'ENFER
# ══════════════════════════════════════════════════════════════════════════════

STRATES = [
    {
        "nom":    "Prātus — Première Strate",
        "emoji":  "🔴",
        "couleur": COULEURS["rouge_chaine"],
        "desc":   ("Le Vestibule des Damnés. Chaleur écrasante, sol de cendres, hurlements "
                   "permanents. Les Togabito récents y arrivent encore proches de leur ancienne "
                   "identité — certains appellent un nom qu'ils n'oublieront que plus tard. "
                   "La plupart sombrent ici, dans l'oubli de ce qu'ils furent."),
    },
    {
        "nom":    "Carnale — Deuxième Strate",
        "emoji":  "🟠",
        "couleur": 0x8B2500,
        "desc":   ("Les Plaines Brûlantes. Rivières de soufre, corps consumés et régénérés "
                   "en boucle sans répit ni raison. Violence permanente, gratuite, mécaniquement "
                   "infligée. Ceux qui traversent acquièrent une résistance à la douleur qui "
                   "n'est plus de la force — c'est l'extinction de quelque chose en eux."),
    },
    {
        "nom":    "Sulfura — Troisième Strate",
        "emoji":  "🟡",
        "couleur": 0xB8860B,
        "desc":   ("Les Geysers de Soufre. Vapeurs toxiques, visibilité nulle, terrain "
                   "imprévisible qui se reconfigure sans logique apparente. Seuls ceux dont "
                   "l'instinct est aiguisé par des siècles de souffrance s'y orientent. Les "
                   "autres errent jusqu'à ce que l'Enfer les broie une fois de plus."),
    },
    {
        "nom":    "Profundus — Quatrième Strate",
        "emoji":  "🔵",
        "couleur": 0x1A0030,
        "desc":   ("L'Obscurité Profonde. Pression spirituelle accablante qui écrase tout "
                   "être dont le Reishi ne peut la soutenir. Présence constante des Kushanāda. "
                   "Très peu y descendent. Ceux qui le font reviennent changés d'une façon "
                   "que les mots ne savent pas décrire — ou ne reviennent pas."),
    },
    {
        "nom":    "Saiōbu — Cinquième Strate",
        "emoji":  "⚫",
        "couleur": 0x050505,
        "desc":   ("L'Abyssal. Silence total rompu par des vibrations cosmiques que nulle "
                   "oreille n'était censée percevoir. Là où les lois des Trois Mondes ne "
                   "s'appliquent plus. Ce qui existe ici précède la création elle-même. "
                   "Réservé aux événements narratifs majeurs du staff."),
    },
]


# ══════════════════════════════════════════════════════════════════════════════
#  LORE_DATA — 10 sujets
# ══════════════════════════════════════════════════════════════════════════════

LORE_DATA = {
    "origine": {
        "titre":  "🌊 La Mer Primordiale & le Péché Originel",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "prologue",
        "description": (
            "Avant que le monde soit ce qu'il est, il n'y avait pas de monde. Il y avait "
            "autre chose — quelque chose que les rares êtres capables d'en parler appellent "
            "la **Mer Primordiale** (原初の海, Gensho no Umi). Pas un océan d'eau, mais un "
            "état : une existence indivise dans laquelle le vivant et le mort n'étaient pas "
            "distincts, dans laquelle chaque âme existait sans naître et disparaissait sans "
            "mourir.\n\n"
            "Ce monde était silencieux. Mais il n'était pas en paix. Une obscurité le rongea "
            "de l'intérieur — une faim sans nom, une corruption qui dévorait les âmes sans "
            "qu'il y ait de gardien pour y mettre fin. Un être en émergea pour lui faire "
            "face : celui qui serait plus tard nommé **Reiō**, le Roi des Âmes.\n\n"
            "Cinq êtres puissants l'observèrent — les ancêtres des cinq Grandes Maisons "
            "Nobles. Cinq raisons différentes, une seule décision. Ils capturèrent le Reiō, "
            "lui arrachèrent les bras, les jambes, le cœur, le scellèrent dans un cristal. "
            "Et le Reiō, tout au long de ce supplice, ne résista pas."
        ),
        "fields": [
            ("La Création",
             "Utilisant sa puissance comme clé de voûte, les ancêtres créèrent Soul "
             "Society, le Monde des Vivants, Hueco Mundo. La vie et la mort furent "
             "séparées. Le cycle des âmes inaugura une ère nouvelle."),
            ("L'Enfer — antérieur à tout",
             "L'Enfer ne fut pas créé. Il existait déjà. Le Monde des Vivants fut "
             "partiellement érigé pour lui servir de couvercle. Ce couvercle repose "
             "sur un équilibre fragile : si le Reiatsu infernal dépasse celui des "
             "Trois Mondes réunis, il peut être soulevé de l'intérieur."),
            ("Le Reiō aujourd'hui",
             "Scellé dans son cristal, mutilé de toutes parts, ni vivant ni mort — "
             "verrou cosmique. Ses membres arrachés ont acquis une conscience propre. "
             "Sa chair sacrifiée est la source de toute puissance spirituelle. Tout "
             "découle du sacrifice d'un être qui choisit de ne pas résister."),
        ],
    },
    "fissure": {
        "titre":  "🩸 La Fissure — Cause et Conséquences",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "prologue",
        "description": (
            "Une anomalie spatiale qui relie l'Enfer aux Trois Mondes. Apparue sans "
            "prévenir, sans cause identifiée, sans précédent dans les archives du Gotei. "
            "La théorie des **Deux Piliers Maudits** offre l'explication la plus crédible : "
            "deux entités — Mimihagi (Stagnation) et son pendant (Progression) — maintenaient "
            "involontairement un contrepoids à l'accumulation infernale. Leur disparition "
            "simultanée a rompu la balance. La Fissure a suivi."
        ),
        "fields": [
            ("Manifestation",
             "Fissures visibles dans le tissu spirituel. Sphères noires de Jigoku no "
             "Rinki qui débordent dans les Trois Mondes. Augmentation des Hollow "
             "anormaux dans le Monde des Vivants. Les frontières entre Strates vacillent."),
            ("Impact sur chaque faction",
             "Shinigami : déstabilisation doctrinale, révélation du Konsō Reisai. "
             "Togabito : relâchement des chaînes, espoir ou signal. "
             "Arrancar : résonance physique avec leur trou identitaire. "
             "Quincy : lecture dirigée de la contamination."),
            ("La question",
             "La progression de l'énergie infernale n'est pas aléatoire. Elle suit "
             "une logique. Elle a une direction. Quelque chose cherche quelque chose "
             "— ou quelqu'un. Le temps presse."),
        ],
    },
    "reio": {
        "titre":  "👁️ Le Reiō — Le Roi Mutilé",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "prologue",
        "description": (
            "Le **Reiō** (霊王, Roi des Âmes, nom véritable Adnyeus) émergea de la Mer "
            "Primordiale pour combattre l'obscurité qui la rongeait. Il portait une puissance "
            "qui dépassait tout ce que ce monde avait produit — à la fois Quincy et Shinigami "
            "et simple personne portant d'innombrables capacités. Le symbole de l'espoir "
            "qui gouvernait le monde chaotique.\n\n"
            "Capturé par les Cinq Ancêtres, mutilé, scellé dans un cristal pour l'éternité. "
            "Et il ne résista pas. Il avait vu ce qui allait arriver. Il avait peut-être même "
            "choisi de laisser faire — comprenant que sa mutilation était le prix de la "
            "création d'un monde capable de durer."
        ),
        "fields": [
            ("Les fragments dispersés",
             "Ses membres arrachés ont acquis une conscience propre : Mimihagi "
             "(bras droit, Stagnation), Pernida (bras gauche, Progression), et "
             "d'autres sous des formes encore non identifiées. Son fils hérita "
             "de l'Almighty — le don prophétique de voir et d'altérer le futur."),
            ("Le Verrou",
             "Tant que le Reiō existe, les Trois Mondes restent distincts. "
             "Sa mort provoque leur effondrement. La Fissure suggère que le "
             "verrou fonctionne de moins en moins bien."),
            ("Ce que personne ne dit",
             "La mutilation a été choisie. Pas subie. Le Reiō a accepté de "
             "devenir un outil. Ce que cela révèle sur la légitimité des "
             "institutions de Soul Society — c'est une question que personne "
             "ne pose à voix haute. Pas encore."),
        ],
    },
    "division_zero": {
        "titre":  "零 La Division Zéro — Garde Royale",
        "couleur": COULEURS["or_pale"],
        "web_fragment": "division-zero",
        "description": (
            "La Division Zéro n'obéit pas au Gotei 13. Elle n'obéit pas au Conseil Central "
            "46. Elle obéit à la volonté des ancêtres des cinq Grandes Maisons Nobles — "
            "ceux-là mêmes qui commirent le Péché Originel. Ses membres sont d'anciens "
            "Capitaines promus après avoir apporté quelque chose de fondamental à Soul "
            "Society. Leur puissance combinée dépasse celle du Gotei tout entier."
        ),
        "fields": [
            ("Le Palais du Reiō",
             "Dimension flottante au-dessus de Soul Society. Accessible "
             "uniquement par ceux qui portent l'Ōken, clé spirituelle gravée "
             "dans leurs propres os. Tant que le Palais existe et qu'un "
             "membre de la Garde survit, les tombés peuvent être ressuscités."),
            ("Le silence gardé",
             "La Division Zéro sait la vérité du Péché Originel, du Konsō "
             "Reisai, de l'antériorité de l'Enfer. Elle choisit depuis des "
             "millions d'années de ne rien dire. Son silence est interprété "
             "comme un accord tacite avec l'ordre établi."),
            ("Face à la Fissure",
             "Intervenir signifie révéler des siècles de mensonge. Ne pas "
             "intervenir signifie laisser l'Enfer se déverser. Les membres "
             "actuels ne sont pas unanimes. La disparition simultanée des "
             "Deux Piliers est soit une catastrophe, soit un acte délibéré "
             "— et la Division Zéro est la seule qui pourrait le savoir."),
        ],
    },
    "konso_reisai": {
        "titre":  "⚰️ Le Konsō Reisai — Le Secret des Capitaines",
        "couleur": COULEURS["rouge_chaine"],
        "web_fragment": "shinigami",
        "description": (
            "Rituel secret transmis depuis la fondation du Gotei 13. À la mort d'un Capitaine, "
            "son âme est envoyée en Enfer plutôt qu'à Soul Society. La raison est cosmique : "
            "un Shinigami de rang Capitaine possède une densité de Reishi si élevée que son "
            "âme ne peut être réabsorbée par le sol de Soul Society. Si elle flotte librement, "
            "elle déséquilibre l'environnement spirituel de façon irréversible.\n\n"
            "Douze ans après la mort, une cérémonie est organisée. Un Hollow est sacrifié "
            "devant la tombe. Le Reishi du défunt est canalisé vers l'Enfer. On enseigne aux "
            "rangs inférieurs que c'est un passage vers le repos. Des générations de Capitaines "
            "ont été pleurées par leurs subordonnés et précipitées en Enfer à leur insu."
        ),
        "fields": [
            ("La Révélation",
             "Le secret a éclaté après la Grande Guerre contre les Quincy "
             "survivants. Les Capitaines actuels savent. Les Vice-Capitaines "
             "commencent à apprendre. Les rangs inférieurs n'ont pas encore "
             "été informés officiellement."),
            ("Les Implications",
             "Des centaines de Capitaines décédés depuis des millénaires "
             "se trouvent dans les Strates. Certains y ont évolué en entités "
             "d'une puissance qui dépasse tout ce que les Trois Mondes ont "
             "produit. Ils sont les damnés les plus puissants de l'Enfer."),
            ("La Question",
             "Étaient-ils envoyés pour renforcer les barrières, ou pour "
             "être emprisonnés ? Y a-t-il une différence ? Et si certains "
             "le savaient avant de mourir — et ont accepté ?"),
        ],
    },
    "systeme": {
        "titre":  "⚔️ Système de Combat & Points",
        "couleur": COULEURS["gris_acier"],
        "web_fragment": "",
        "description": (
            "Le système de progression d'Infernum Aeterna reflète l'évolution narrative "
            "de votre personnage — pas seulement ses victoires en combat."
        ),
        "fields": [
            ("Obtenir des points",
             "Participation active au RP (scènes écrites, arcs narratifs), "
             "victoires en combat (`/clore-combat`), contributions lore validées "
             "par le staff, événements serveur. Points attribués par le staff via "
             "`/points-ajouter`."),
            ("Montée en rang",
             "Automatique à chaque seuil franchi. Le staff est notifié. "
             "Déclenche une narration épique dans `#journal-de-l-enfer`. "
             "Nouveaux rôles et accès aux zones plus profondes débloqués."),
            ("Aptitudes",
             "À chaque rang, vous pouvez décrire de nouvelles aptitudes dans votre fiche. "
             "Le nombre maximum dépend du rang. Toute aptitude hors-norme doit être "
             "validée par le staff avant usage en RP."),
            ("Mort narrative",
             "Possible avec accord des deux joueurs + validation staff. "
             "Le personnage peut « mourir » narrativement et renaître avec un nouveau "
             "contexte, ou rejouer depuis le début avec ses acquis lore."),
        ],
    },
    "gotei": {
        "titre":  "🏯 Le Gotei 13 — Des Tueurs aux Gardiens",
        "couleur": COULEURS["blanc_seireitei"],
        "web_fragment": "shinigami",
        "description": (
            "La première génération du Gotei 13 n'était pas des défenseurs au sens noble du "
            "terme — c'était une bande de tueurs redoutables pour lesquels le mot « défense » "
            "n'était qu'une étiquette. Son fondateur, le premier Capitaine-Commandant, était "
            "un être d'une brutalité froide qui n'avait aucun scrupule à sacrifier ses propres "
            "subordonnés si les circonstances l'exigeaient.\n\n"
            "Ce Gotei des origines imposa un ordre à Soul Society non par la persuasion mais "
            "par la force, district après district. Parmi les premiers Capitaines, trois figures "
            "méritent d'être mentionnées : Kōshin Jūrōmaru portait un Zanpakutō de type feu — "
            "l'aîné et le plus puissant ; Tōka Shibari possédait un Zanpakutō en libération "
            "permanente ; Renjō Mikazuchi abritait une entité spirituelle d'une nature inconnue."
        ),
        "fields": [
            ("L'adoucissement",
             "Après la victoire contre le Lichtreich, le Gotei se transforma. "
             "La Shin'ō Academy fut fondée. Le Konsō devint une pratique codifiée. "
             "Mais selon l'Empereur Quincy, cette organisation mourut il y a mille "
             "ans — remplacée par quelque chose de plus noble mais plus vulnérable."),
            ("Aujourd'hui",
             "Une institution de plusieurs millénaires portant le poids de toute "
             "cette histoire. La question la plus urgente n'est pas la Fissure — "
             "c'est ce que le Gotei doit aux âmes qu'il a précipitées en Enfer."),
        ],
    },
    "strates_lore": {
        "titre":  "⛓️ Les Cinq Strates de l'Enfer",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "togabito",
        "description": (
            "L'Enfer est structuré en cinq niveaux de violence et de densité d'énergie "
            "infernale croissantes. Les tout premiers Togabito arrivèrent dans un "
            "environnement dont personne ne connaissait les règles — pas de guide, pas "
            "de structure, seulement les Kushanāda qui dévorent et punissent, les "
            "Jigokusari qui contraignent, et cinq strates dont la logique interne ne "
            "se révèle qu'à ceux qui ont survécu assez longtemps pour la percevoir.\n\n"
            "Depuis la Fissure, les frontières entre Strates vacillent. Les passages "
            "qui étaient prévisibles depuis des éternités ne le sont plus. L'architecture "
            "immuable de l'Enfer tremble pour la première fois."
        ),
        "fields": [
            ("🔴 Prātus — Première Strate",
             "Le Vestibule des Damnés. Chaleur écrasante, cendres, hurlements. "
             "Les récents y arrivent proches de leur ancienne identité."),
            ("🟠 Carnale — Deuxième Strate",
             "Les Plaines Brûlantes. Soufre, régénération en boucle, violence "
             "gratuite. Ceux qui traversent y perdent quelque chose."),
            ("🟡 Sulfura — Troisième Strate",
             "Les Geysers de Soufre. Visibilité nulle, terrain imprévisible. "
             "Seul l'instinct aiguisé par des siècles permet de s'orienter."),
            ("🔵 Profundus — Quatrième Strate",
             "L'Obscurité Profonde. Pression spirituelle accablante, Kushanāda "
             "constants. Très peu y descendent. Retour improbable."),
            ("⚫ Saiōbu — Cinquième Strate",
             "L'Abyssal. Silence total. Lois cosmiques suspendues. Ce qui "
             "existe ici précède la création elle-même."),
        ],
    },
    "tensions": {
        "titre":  "⚡ Tensions Inter-Factions",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "creation",
        "description": (
            "Le lore d'Infernum Aeterna crée naturellement des dynamiques entre les quatre "
            "races que les joueurs peuvent explorer en RP. Chaque relation inter-faction porte "
            "une question narrative différente, et aucune n'a de réponse simple."
        ),
        "fields": [
            ("Shinigami ↔ Togabito",
             "La révélation du Konsō Reisai. Les Togabito portent la question : "
             "*vous saviez ?* Les Shinigami qui rencontrent d'anciens confrères "
             "en Enfer portent la même question, inversée."),
            ("Arrancar ↔ Togabito",
             "La résonance entre le vide des Hollow et l'énergie infernale. Les "
             "Arrancar cherchent à comprendre ce qu'ils ressentent. Les Togabito "
             "anciens connaissent l'Enfer de l'intérieur. Choses à s'apprendre "
             "mutuellement — et raisons de se méfier."),
            ("Quincy ↔ Shinigami",
             "La vieille blessure. Un millénaire de génocide ne s'oublie pas. "
             "Mais la Fissure crée une menace commune qui oblige à choisir : "
             "continuer à se haïr ou s'allier pour survivre."),
            ("Quincy ↔ Togabito",
             "Les Quincy voient la direction que prend l'énergie infernale. Les "
             "Togabito anciens connaissent ce que cette direction signifie de "
             "l'intérieur. Aucun des deux camps n'a le tableau complet seul."),
        ],
    },
    "creation": {
        "titre":  "📝 Guide de Création de Personnage",
        "couleur": COULEURS["gris_acier"],
        "web_fragment": "creation",
        "description": (
            "Ce lore est une fondation pour des personnages originaux. Chaque faction offre "
            "des angles narratifs uniques, et la Fissure donne à chacun une raison d'exister "
            "au-delà de sa propre histoire. Voici les questions centrales par faction."
        ),
        "fields": [
            ("死神 Shinigami",
             "Depuis combien de temps sert-on une institution fondée sur un "
             "mensonge ? Qu'est-ce qu'on fait quand on l'apprend ? Chaque "
             "rang offre un angle différent — de l'élève naïf au Capitaine "
             "portant le poids de la vérité."),
            ("咎人 Togabito",
             "Comment un être forgé par des siècles de souffrance réagit-il "
             "à un sentiment — l'espoir — qu'il avait appris à tuer en "
             "lui-même pour survivre ? La diversité des origines rend chaque "
             "Togabito unique."),
            ("破面 Arrancar",
             "Si quelque chose peut légèrement remplir le vide dans la "
             "poitrine, à quel prix est-on prêt à le chercher ? La "
             "résonance infernale pose une question existentielle sans "
             "précédent pour ceux qui ont toujours porté l'absence."),
            ("滅却師 Quincy",
             "Ils voient ce que les autres ne voient pas. La contamination "
             "infernale est pour eux une carte lisible. Faut-il partager "
             "cette vision avec les Shinigami — ceux qui ont tenté de les "
             "exterminer — pour survivre ensemble ?"),
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════════════════

class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /lore ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="lore", description="Résumé d'une faction, zone ou concept du lore.")
    @app_commands.describe(sujet="Faction, zone ou concept à consulter")
    @app_commands.choices(sujet=[
        app_commands.Choice(name="La Mer Primordiale & le Péché Originel", value="origine"),
        app_commands.Choice(name="La Fissure — Cause et Conséquences",     value="fissure"),
        app_commands.Choice(name="Le Reiō — Le Roi Mutilé",                value="reio"),
        app_commands.Choice(name="La Division Zéro",                       value="division_zero"),
        app_commands.Choice(name="Le Konsō Reisai — Le Secret",            value="konso_reisai"),
        app_commands.Choice(name="Le Gotei 13 — Des Tueurs aux Gardiens",  value="gotei"),
        app_commands.Choice(name="Les Cinq Strates de l'Enfer",            value="strates_lore"),
        app_commands.Choice(name="Tensions Inter-Factions",                value="tensions"),
        app_commands.Choice(name="Guide de Création de Personnage",        value="creation"),
        app_commands.Choice(name="Système de Combat & Points",             value="systeme"),
    ])
    async def lore(self, interaction: discord.Interaction, sujet: str):
        embed = _construire_lore(sujet)
        await interaction.response.send_message(embed=embed)

    # ── /glossaire ────────────────────────────────────────────────────────────
    @app_commands.command(name="glossaire", description="Définition d'un terme japonais du lore.")
    @app_commands.describe(terme="Terme à définir")
    @app_commands.choices(terme=[
        app_commands.Choice(name=f"{v[0]} — {k.replace('_', ' ').capitalize()}", value=k)
        for k, v in list(GLOSSAIRE.items())[:25]  # Discord limite à 25 choices
    ])
    async def glossaire(self, interaction: discord.Interaction, terme: str):
        if terme not in GLOSSAIRE:
            await interaction.response.send_message("❌ Terme introuvable.", ephemeral=True)
            return
        kanji, definition = GLOSSAIRE[terme]
        embed = discord.Embed(
            title=f"📜 {kanji} — {terme.replace('_', ' ').capitalize()}",
            description=definition,
            color=COULEURS["or_ancien"]
        )
        embed.set_footer(text="⸻ Infernum Aeterna · Glossaire ⸻")
        _ajouter_lien_web(embed)
        await interaction.response.send_message(embed=embed)

    # ── /fiche-faction ────────────────────────────────────────────────────────
    @app_commands.command(name="fiche-faction", description="Fiche complète d'une faction jouable.")
    @app_commands.choices(faction=[
        app_commands.Choice(name="死神 Shinigami", value="shinigami"),
        app_commands.Choice(name="咎人 Togabito",  value="togabito"),
        app_commands.Choice(name="破面 Arrancar",  value="arrancar"),
        app_commands.Choice(name="滅却師 Quincy",  value="quincy"),
    ])
    async def fiche_faction(self, interaction: discord.Interaction, faction: str):
        if faction not in FICHES_FACTION:
            await interaction.response.send_message("❌ Faction inconnue.", ephemeral=True)
            return
        fiche = FICHES_FACTION[faction]
        embed = discord.Embed(title=fiche["titre"], color=fiche["couleur"])
        for nom_section, texte in fiche["sections"]:
            embed.add_field(name=nom_section, value=texte, inline=False)
        embed.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")
        _ajouter_lien_web(embed, fiche.get("web_fragment", ""))
        await interaction.response.send_message(embed=embed)

    # ── /strates ──────────────────────────────────────────────────────────────
    @app_commands.command(name="strates", description="Carte narrative des cinq Strates de l'Enfer.")
    async def strates(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⛓️ Les Cinq Strates de l'Enfer",
            description=(
                "L'Enfer est structuré en cinq niveaux de violence croissante. "
                "Plus une âme descend, plus la puissance requise pour y survivre est grande. "
                "Depuis la Fissure, les frontières entre Strates vacillent — l'architecture "
                "immuable de l'Enfer tremble pour la première fois."
            ),
            color=COULEURS["pourpre_infernal"]
        )
        for strate in STRATES:
            embed.add_field(
                name=f"{strate['emoji']} {strate['nom']}",
                value=strate["desc"],
                inline=False
            )
        embed.set_footer(text="⸻ Infernum Aeterna · Géographie de l'Enfer ⸻")
        _ajouter_lien_web(embed, "togabito")
        await interaction.response.send_message(embed=embed)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS LORE
# ══════════════════════════════════════════════════════════════════════════════

def _construire_lore(sujet: str) -> discord.Embed:
    data = LORE_DATA.get(sujet, LORE_DATA["origine"])
    embed = discord.Embed(title=data["titre"], description=data["description"], color=data["couleur"])
    for nom_champ, valeur_champ in data.get("fields", []):
        embed.add_field(name=nom_champ, value=valeur_champ, inline=False)
    embed.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")
    _ajouter_lien_web(embed, data.get("web_fragment", ""))
    return embed


async def setup(bot):
    await bot.add_cog(Lore(bot))
