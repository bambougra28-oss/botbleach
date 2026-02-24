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
    "reishi":         ("霊子", "Les particules dont toute matière spirituelle est faite. Plus le Reishi d'une âme est dense, plus elle frappe fort, résiste longtemps et pèse lourd sur le monde qui l'entoure."),
    "reiatsu":        ("霊圧", "La pression que le Reishi d'un être exerce autour de lui. Invisible pour les faibles, écrasante pour les puissants. Quand un Capitaine libère le sien, l'air se tord et les genoux plient."),
    "zanpakuto":      ("斬魄刀", "L'épée des Shinigami, forgée à partir de leur propre âme. Chaque lame porte un nom, celui d'une entité intérieure qui ne parle qu'à ceux qu'elle juge dignes. On ne choisit pas son Zanpakutō : c'est lui qui vous trouve."),
    "shikai":         ("始解", "La première libération. On prononce le nom de la lame et quelque chose se déverrouille, un pacte murmuré entre le porteur et l'esprit qui vit dans l'acier."),
    "bankai":         ("卍解", "La seconde et dernière libération. Dix ans de maîtrise au minimum. La puissance se multiplie d'un facteur que les manuels n'osent pas chiffrer, et le prix à payer est à la mesure du gain."),
    "hollow":         ("虚", "Une âme humaine qui n'a pas trouvé le chemin de Soul Society. La peur et la faim ont dévoré son cœur. Un trou béant s'ouvre dans sa poitrine, là où la personne se trouvait autrefois. Le masque apparaît, et ce qui reste n'est plus qu'instinct."),
    "resurreccion":   ("帰刃", "L'Arrancar brise le sceau de son Zanpakutō et retrouve sa forme Hollow d'origine. Un dépouillement volontaire : redevenir la bête pour en libérer toute la puissance."),
    "jigokusari":     ("地獄鎖", "Les chaînes de l'Enfer. Elles naissent de la chair même des Strates, s'enroulent autour des damnés, les tuent, les ressuscitent et recommencent. On ne les brise pas : on apprend à les porter."),
    "kushanada":      ("倶舎那陀", "Les gardiens colossaux de l'Enfer. Des silhouettes de juges aux yeux vides, portant des masses rituelles. Personne ne sait qui les a créés. Ils ne parlent pas, ne dorment pas, ne ralentissent jamais."),
    "jigoku_no_rinki":("地獄の燐気", "Des sphères noires et phosphorescentes qui suintent des murs de l'Enfer depuis la Fissure. Un contact prolongé fragmente la mémoire, déstabilise la puissance, dissout lentement l'identité spirituelle."),
    "konso":          ("魂葬", "Le rite par lequel un Shinigami frappe du manche de son Zanpakutō le front d'une âme errante pour l'envoyer à Soul Society. Un geste appris dès l'Académie, répété sans question depuis des millénaires."),
    "konso_reisai":   ("魂葬霊祭", "Le rituel secret. Douze ans après la mort d'un Capitaine, un Hollow est sacrifié devant sa tombe et son Reishi est canalisé vers l'Enfer. On enseigne aux subordonnés que c'est un passage vers le repos. Ce n'en est pas un."),
    "reio":           ("霊王", "Le Roi des Âmes. Capturé par les Cinq Ancêtres, mutilé, scellé dans un cristal. Ni vivant ni mort. Il est le verrou qui maintient les Trois Mondes séparés, et ce verrou commence à céder."),
    "bras_droit_reio":("耳禿", "Le Bras Droit du Reiō, arraché lors de la mutilation originelle. Devenu divinité à part entière, il incarne la Stagnation — l'un des Deux Piliers dont la disparition a fait basculer l'équilibre vers la Fissure."),
    "togabito":       ("咎人", "Littéralement « personne fautive ». Pas une espèce : une condition. Des âmes envoyées en Enfer par le péché, par la purification d'un Hollow trop coupable, ou par le Konsō Reisai."),
    "mer_primordiale":("原初の海", "L'état du monde avant les mondes. Une existence indivisée où la vie et la mort ne se distinguaient pas, où les âmes existaient sans naître et disparaissaient sans mourir. L'obscurité la rongea de l'intérieur."),
    "lichtreich":     ("光帝国", "L'Empire de Lumière des Quincy, à l'époque où ils pouvaient regarder le Gotei 13 dans les yeux. Ses guerriers portaient les Schrift. Ses ruines vivent dans la mémoire de ceux qui ont survécu."),
    "wandenreich":    ("見えざる帝国", "L'Empire Invisible. Les survivants Quincy, cachés depuis des siècles dans les ombres du Seireitei, se nourrissant du Reishi de l'ennemi en attendant leur heure."),
    "oken":           ("王鍵", "La Clé Royale. Gravée dans les os des membres de la Division Zéro, elle ouvre le passage vers le Palais du Reiō. Un privilège et une prison."),
    "gotei_13":       ("護廷十三隊", "Les Treize Divisions de la Cour. Fondées par des tueurs, devenues gardiennes d'un ordre bâti sur un mensonge vieux de plusieurs millions d'années."),
    "hueco_mundo":    ("虚圏", "Le Monde Creux. Un désert blanc infini sous une lune qui ne bouge pas, où les Hollow se dévorent entre eux depuis la nuit des temps. Structures de quartz, cristaux de Reishi pétrifiés, silence."),
    "seireitei":      ("瀞霊廷", "La Cour des Âmes Pures. Forteresse au cœur de Soul Society, tout en murs blancs et en silence. Les Shinigami y résident, y commandent, et y gardent des secrets que personne n'a demandé à connaître."),
    "schrift":        ("聖文字", "Une lettre sacrée, gravée dans l'âme d'un Quincy par l'Empereur lui-même. Elle transforme un don individuel en puissance absolue. Ceux qui la portent n'ont pas tous compris ce qu'ils ont accepté."),
    "las_noches":     ("虚夜宮", "Le Palais de la Nuit Creuse. Forteresse de Hueco Mundo bâtie couche après couche sur des générations, chaque conquérant y ajoutant sa strate. Des couloirs dont la logique n'appartient qu'à ceux qui les ont creusés."),
    "blut":           ("血装", "La fortification du sang, technique propre aux Quincy. Le Blut Vene rend le corps presque imperméable aux coups ; le Blut Arterie décuple la force de frappe. On ne peut activer les deux à la fois."),
    "kyokai":         ("境界", "La Frontière. Avant la Fissure, c'était un vide entre les mondes, un couloir que tout le monde traversait sans lever les yeux. Maintenant c'est un territoire. Des fragments de mondes y dérivent, les lois spirituelles s'y contredisent, et les quatre races s'y croisent sans qu'aucune ne puisse revendiquer quoi que ce soit. Chaque semaine, elle s'élargit un peu plus."),
    "entite_inconnue":("未知の存在", "Quelque chose frappe aux Portes de l'Enfer depuis l'extérieur des Trois Mondes. Personne ne sait ce que c'est. Personne ne sait depuis quand ça dure. Les Kushanāda réagissent à sa présence, les Quincy perçoivent ses vibrations dans le Reishi, et le Reiō scellé dans son cristal n'a jamais tremblé autant. L'Entité n'a pas de nom parce que nommer quelque chose suppose de le comprendre."),
}


# ══════════════════════════════════════════════════════════════════════════════
#  FICHES FACTION — style narratif immersif
# ══════════════════════════════════════════════════════════════════════════════

FICHES_FACTION = {
    "shinigami": {
        "titre":   "死神 Shinigami · Gardiens de Soul Society",
        "couleur": COULEURS["blanc_seireitei"],
        "web_fragment": "shinigami",
        "sections": [
            ("Origine",
             "Le mot Shinigami désignait autrefois n'importe quelle âme dont le Reishi était "
             "assez dense pour la distinguer du commun du Rukongai. Il n'y avait pas d'organisation, "
             "pas de hiérarchie : seulement des êtres trop puissants pour vivre parmi les autres. "
             "Puis un guerrier au Zanpakutō de feu réunit treize lames et fonda ce qui deviendrait "
             "le Gotei 13. Pas une assemblée de protecteurs. Une bande de tueurs qui avait compris "
             "que l'ordre ne viendrait que par la force. La respectabilité, elle, viendrait plus tard."),
            ("Puissance",
             "Chaque Shinigami porte un Zanpakutō dont la voix intérieure ne se révèle qu'aux "
             "dignes. Prononcer son nom déclenche le Shikai, première libération, premier pacte "
             "entre le guerrier et l'esprit de la lame. Le Bankai est l'aboutissement : dix ans "
             "d'entraînement au bas mot, une puissance multipliée d'un facteur que personne ne "
             "chiffre à voix haute. Autour de cette lame gravitent quatre disciplines : Kidō, "
             "Hohō, Zanjutsu, Hakuda. Leur combinaison dessine un style de combat propre à chacun."),
            ("Le Secret",
             "Depuis la fondation du Gotei, les Capitaines morts sont envoyés en Enfer par le "
             "Konsō Reisai. Leur Reishi est trop dense pour être réabsorbé par Soul Society, "
             "alors on le canalise vers les Strates, douze ans après la mort, lors d'une "
             "cérémonie où un Hollow est sacrifié devant la tombe. Les subordonnés pensent que "
             "c'est un passage vers le repos. Des générations entières de Capitaines ont été "
             "pleurées puis précipitées dans l'abîme à l'insu de tous. La dette accumulée "
             "se compte en millénaires."),
            ("Face à la Fissure",
             "Les Capitaines savent maintenant. La vérité leur est tombée dessus quand il était "
             "devenu impossible de la taire. Ce savoir fissure le haut commandement autant que "
             "la Fissure fissure le monde. Car la question va bien au-delà de la stratégie "
             "militaire : les anciens Capitaines qu'on retrouve en Enfer, ceux qui y ont survécu "
             "et qui en émergent par la brèche, sont-ils des ennemis à combattre ou des victimes "
             "à qui l'on doit des comptes ?"),
        ]
    },
    "togabito": {
        "titre":   "咎人 Togabito · Les Forgés par l'Enfer",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "togabito",
        "sections": [
            ("La Damnation",
             "Togabito signifie « personne fautive », mais le mot est trompeur. Tous ne sont "
             "pas coupables. Trois routes mènent aux Strates : le péché commis de son vivant, "
             "les crimes humains qu'un Hollow purifié emporte avec lui dans la mort, et le "
             "Konsō Reisai qui expédie les Capitaines défunts sous terre sans leur demander "
             "leur avis. Damnés par sentence, damnés par accident, damnés par nécessité "
             "cosmique. L'Enfer ne fait pas la différence."),
            ("La Transformation",
             "Mourir et ressusciter en boucle pendant des siècles transforme une âme. La "
             "plupart sombrent dans l'oubli de ce qu'elles furent. D'autres durcissent au point "
             "de ne plus rien sentir. Les rares qui traversent cette épreuve en sortent changées. "
             "Elles apprennent à manier les Jigokusari comme une arme plutôt qu'un fardeau, et "
             "la puissance qu'elles développent ne ressemble à rien de connu. C'est une force "
             "alchimique, née de l'absence prolongée de tout espoir."),
            ("Factions internes",
             "Les plus récents forment la Faction Évasion : ils veulent sortir, c'est tout. "
             "Les plus anciens, ceux qui ont eu le temps de réfléchir, forment la Faction "
             "Compréhension : ils veulent comprendre la cause avant d'agir. Et puis il y a la "
             "Faction Signal, la plus silencieuse. Ceux-là pensent que la Fissure n'est pas un "
             "accident mais une transformation, et que cette transformation dépasse de loin la "
             "question de s'échapper."),
            ("La Fissure vue d'en bas",
             "En des millions d'années d'existence, rien n'était jamais arrivé en Enfer qui ne "
             "soit une punition. La Fissure est la première exception. Les Jigokusari se "
             "desserrent par endroits. Les Kushanāda montrent des hésitations inédites. Le "
             "Jigoku no Rinki flotte en permanence dans certaines strates. Quelque chose a bougé "
             "dans une architecture que tout le monde croyait figée pour l'éternité. Les murs "
             "tiennent encore, mais ils tremblent."),
        ]
    },
    "arrancar": {
        "titre":   "破面 Arrancar · Les Briseurs de Masque",
        "couleur": COULEURS["gris_sable"],
        "web_fragment": "arrancar",
        "sections": [
            ("La Tragédie Hollow",
             "Tout Hollow fut une personne. Quand la Chaîne du Destin se ronge jusqu'au bout, "
             "un trou s'ouvre là où le cœur se trouvait, et ce qui restait d'humain se dissout "
             "dans la faim. Le masque apparaît, l'instinct prend le relais. C'est la tragédie "
             "la plus cruelle de cet univers : les monstres que les Shinigami pourchassent à "
             "travers les mondes sont les victimes d'un système qui les a laissés pourrir."),
            ("Devenir Arrancar",
             "Briser son propre masque, c'est arracher la croûte de la bête pour retrouver "
             "quelque chose d'humain en dessous. L'Arrancar gagne des capacités proches de "
             "celles d'un Shinigami tout en gardant sa puissance Hollow d'origine. Le fragment "
             "de masque qui subsiste sur le visage ou le corps est la cicatrice de ce qu'il "
             "était. Le trou dans la poitrine, lui, ne se referme pas. Leur Zanpakutō scelle "
             "leur puissance ; la Resurrección la déchaîne."),
            ("Hueco Mundo",
             "Un désert blanc qui n'en finit pas, sous une lune qui ne bouge jamais. Las Noches "
             "se dresse au milieu, forteresse empilée sur des générations de conquérants, chacun "
             "y ajoutant ses murs et ses couloirs. La hiérarchie est simple : Espada, Fracción, "
             "Números. Le plus fort commande. Pas de philosophie, pas de discours. La loi du "
             "plus puissant, assumée sans fard."),
            ("Résonance infernale",
             "Le trou dans la poitrine résonne avec l'énergie qui filtre de la Fissure. Les "
             "Shinigami ne le sentent pas, les Quincy ne le sentent pas, mais les Arrancar, eux, "
             "perçoivent quelque chose. Ceux qui ont été contaminés par le Jigoku no Rinki "
             "décrivent une sensation de complétude partielle, comme si le vide se remplissait "
             "un peu. Le lien entre le trou Hollow et ce qui existait avant les Trois Mondes "
             "n'avait jamais été envisagé sérieusement. La Fissure force la question."),
        ]
    },
    "quincy": {
        "titre":   "滅却師 Quincy · Les Survivants de Lumière",
        "couleur": COULEURS["bleu_abyssal"],
        "web_fragment": "quincy",
        "sections": [
            ("Héritiers du Reiō",
             "Des humains vivants, nés avec une sensibilité spirituelle héritée du Reiō "
             "lui-même. Le fils du Roi des Âmes porta cette puissance à son paroxysme, et son "
             "sang coule encore dans chaque lignée Quincy. Là où un Shinigami doit forger un "
             "lien avec son Zanpakutō, un Quincy naît connecté au Reishi ambiant. Il le lit "
             "comme on lit un tissu, fil par fil, capable d'en anticiper chaque tension et "
             "chaque rupture."),
            ("Pourquoi ils détruisent",
             "Le Reishi d'un Hollow empoisonne l'âme d'un Quincy. Pas de purification possible, "
             "pas de demi-mesure : c'est détruire ou mourir. Les Shinigami les accusent de "
             "briser l'équilibre des âmes. Les Quincy entendent cette accusation comme une "
             "hypocrisie insupportable. On leur reproche de ne pas se laisser tuer."),
            ("Du Lichtreich au Wandenreich",
             "Il fut un temps où les Quincy avaient un empire. Le Lichtreich, l'Empire de "
             "Lumière, tenait tête au Gotei 13 par la seule force de ses guerriers et de leurs "
             "Schrift, lettres de puissance gravées dans l'âme par l'Empereur. La chute ne prit "
             "pas la forme d'une défaite glorieuse sur un champ de bataille. Ce fut une "
             "extermination méthodique, famille par famille, village par village. Les survivants "
             "se cachèrent dans les ombres du Seireitei et fondèrent le Wandenreich, l'Empire "
             "Invisible, nourri par le Reishi de ceux qui avaient massacré les leurs.\n\n"
             "Aujourd'hui, le Schrift subsiste mais l'Empereur qui les gravait a disparu. "
             "Certains Quincy héritent d'un fragment de cette puissance par le sang, d'autres "
             "la forgent par un entraînement qui frôle le sacrifice. Obtenir un Schrift "
             "en jeu nécessite d'atteindre le rang de Sternritter et de remplir une condition "
             "RP validée par le staff."),
            ("Ce qu'ils voient",
             "Leur perception du Reishi leur montre quelque chose depuis la Fissure. L'énergie "
             "infernale qui se répand dans les Trois Mondes ne se disperse pas au hasard. Elle "
             "suit un tracé, progresse dans une direction, comme si elle cherchait quelque chose "
             "ou quelqu'un. Les Quincy survivants en débattent en secret, et le consensus "
             "n'existe pas. Partager cette vision avec les Shinigami, ceux-là mêmes qui ont "
             "tenté de les exterminer, est un choix que personne ne veut prendre à la légère."),
        ]
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  STRATES DE L'ENFER
# ══════════════════════════════════════════════════════════════════════════════

STRATES = [
    {
        "nom":    "Prātus · Première Strate",
        "emoji":  "🔴",
        "couleur": COULEURS["rouge_chaine"],
        "desc":   ("Le Vestibule des Damnés. Une chaleur à fondre les os, un sol de "
                   "cendres qui colle aux pieds, des hurlements qui ne cessent jamais. "
                   "Les nouveaux arrivants gardent encore leur ancien visage, certains "
                   "appellent un nom qu'ils finiront par oublier. La plupart ne "
                   "descendent pas plus bas. Ils sombrent ici."),
    },
    {
        "nom":    "Carnale · Deuxième Strate",
        "emoji":  "🟠",
        "couleur": COULEURS["brun_cendre"],
        "desc":   ("Les Plaines Brûlantes. Des rivières de soufre, des corps qui brûlent "
                   "et se reconstituent en boucle sans fin. La violence ici est mécanique, "
                   "gratuite, infligée sans raison lisible. Ceux qui traversent n'en "
                   "ressortent pas plus forts. Ils en ressortent éteints. Ce qu'ils ont "
                   "perdu là-bas ne reviendra pas."),
    },
    {
        "nom":    "Sulfura · Troisième Strate",
        "emoji":  "🟡",
        "couleur": COULEURS["or_soufre"],
        "desc":   ("Les Geysers de Soufre. Vapeurs toxiques, visibilité nulle, un terrain "
                   "qui se reconfigure à chaque heure sans logique apparente. Seuls les "
                   "instincts aiguisés par des siècles de souffrance permettent de s'orienter. "
                   "Les autres tournent en rond jusqu'à ce que l'Enfer les broie encore."),
    },
    {
        "nom":    "Profundus · Quatrième Strate",
        "emoji":  "🔵",
        "couleur": COULEURS["violet_profond"],
        "desc":   ("L'Obscurité Profonde. La pression spirituelle y est si dense qu'elle "
                   "écrase tout être dont le Reishi ne peut la soutenir. Les Kushanāda "
                   "rôdent en permanence. Très peu d'âmes y descendent. Celles qui "
                   "remontent ont quelque chose de changé dans le regard que les mots "
                   "ne savent pas nommer."),
    },
    {
        "nom":    "Saiōbu · Cinquième Strate",
        "emoji":  "⚫",
        "couleur": COULEURS["noir_absolu"],
        "desc":   ("L'Abyssal. Le silence est total, percé seulement par des vibrations "
                   "que nulle oreille n'était faite pour capter. Les lois des Trois Mondes "
                   "ne s'appliquent plus ici. Ce qui existe à cette profondeur est antérieur "
                   "à la création elle-même. Réservé aux événements narratifs majeurs."),
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
            "Il n'y avait pas de monde. Pas encore. Les rares êtres capables d'en parler "
            "nomment ce qui existait alors la **Mer Primordiale** (原初の海, Gensho no Umi). "
            "Pas un océan d'eau : un état. Une existence indivise où le vivant et le mort ne "
            "se distinguaient pas, où les âmes existaient sans naître et disparaissaient sans "
            "mourir.\n\n"
            "C'était silencieux, mais ce n'était pas paisible. Quelque chose rongeait ce monde "
            "de l'intérieur, une faim sans nom qui dévorait les âmes une par une, sans que "
            "personne ne s'y oppose. Un être finit par émerger pour lui faire face. On le "
            "nommerait plus tard **Reiō**, le Roi des Âmes.\n\n"
            "Cinq êtres puissants l'observèrent. Les ancêtres des cinq Grandes Maisons "
            "Nobles. Cinq motivations différentes, une seule décision. Ils le capturèrent, "
            "lui arrachèrent les bras, les jambes, le cœur, et le scellèrent dans un cristal. "
            "Le Reiō ne résista pas. Pas un geste."
        ),
        "fields": [
            ("La Création",
             "De sa puissance mutilée, les cinq ancêtres séparèrent la vie et la mort. "
             "Soul Society, le Monde des Vivants, Hueco Mundo : trois mondes distincts, "
             "un cycle d'âmes pour les relier. Une ère nouvelle commençait."),
            ("L'Enfer · antérieur à tout",
             "L'Enfer n'a pas été créé. Il existait déjà, bien avant la Mer Primordiale "
             "elle-même. Le Monde des Vivants fut en partie érigé pour lui servir de "
             "couvercle. Ce couvercle repose sur un équilibre fragile : si le Reiatsu "
             "infernal dépasse celui des Trois Mondes réunis, il peut être soulevé "
             "de l'intérieur."),
            ("Le Reiō aujourd'hui",
             "Scellé dans son cristal, mutilé de toutes parts. Ni vivant ni mort. "
             "Verrou cosmique dont dépend la séparation des mondes. Ses membres "
             "arrachés ont acquis leur propre conscience. Sa chair sacrifiée est la "
             "source de toute puissance spirituelle connue. Et le plus troublant : "
             "il a choisi de ne pas résister."),
        ],
    },
    "fissure": {
        "titre":  "🩸 La Fissure · Cause et Conséquences",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "prologue",
        "description": (
            "Personne ne l'a vue venir. Une déchirure dans le tissu qui sépare l'Enfer des "
            "Trois Mondes, sans cause identifiée, sans précédent dans les archives du Gotei. "
            "La théorie la plus crédible met en cause les **Deux Piliers Maudits** : Mimihagi "
            "(Stagnation) et son pendant (Progression), fragments du Reiō qui maintenaient "
            "sans le savoir un contrepoids à l'énergie infernale accumulée. Les deux ont "
            "disparu presque en même temps. Le contrepoids s'est effondré. La Fissure s'est "
            "ouverte."
        ),
        "fields": [
            ("Manifestation",
             "Des déchirures visibles dans le tissu spirituel, comme des lézardes dans "
             "un mur. Les sphères noires du Jigoku no Rinki débordent dans les Trois "
             "Mondes. Des Hollow anormaux apparaissent en nombre dans le Monde des "
             "Vivants. Les frontières entre les Strates de l'Enfer vacillent."),
            ("Impact sur chaque faction",
             "Chez les **Shinigami**, la révélation du Konsō Reisai ébranle les certitudes "
             "du haut commandement. Les **Togabito** sentent leurs chaînes se desserrer pour "
             "la première fois, tiraillés entre l'espoir et la méfiance. Les **Arrancar** "
             "perçoivent une résonance physique entre la Fissure et le vide qu'ils portent "
             "en eux. Les **Quincy** lisent dans la contamination une direction que personne "
             "d'autre ne distingue."),
            ("La question",
             "L'énergie infernale ne se disperse pas au hasard. Elle progresse selon une "
             "logique, suit un tracé, se dirige vers quelque chose. Ou vers quelqu'un."),
        ],
    },
    "reio": {
        "titre":  "👁️ Le Reiō · Le Roi Mutilé",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "prologue",
        "description": (
            "Le **Reiō** (霊王, Roi des Âmes) émergea de la Mer Primordiale pour combattre "
            "l'obscurité qui la dévorait. Sa puissance dépassait tout ce que ce monde avait "
            "produit : à la fois Quincy et Shinigami, porteur d'innombrables capacités, il "
            "fut le premier à se dresser contre le chaos.\n\n"
            "Les Cinq Ancêtres le capturèrent. Ils lui arrachèrent les membres, le scellèrent "
            "dans un cristal. Il ne résista pas. Peut-être avait-il vu ce qui allait arriver. "
            "Peut-être avait-il compris que sa mutilation était le prix à payer pour qu'un "
            "monde capable de durer puisse exister."
        ),
        "fields": [
            ("Les fragments dispersés",
             "Ses membres arrachés vivent encore, dotés de leur propre conscience. "
             "Le bras droit, devenu divinité à part entière, incarne la Stagnation. "
             "Le bras gauche incarne la Progression. D'autres fragments existent "
             "sous des formes que personne n'a encore identifiées. Son fils hérita "
             "d'un don prophétique : voir le futur et l'altérer."),
            ("Le Verrou",
             "Tant que le Reiō existe, les Trois Mondes restent séparés. Sa mort "
             "provoquerait leur effondrement immédiat. La Fissure est peut-être le "
             "signe que le verrou commence à céder."),
            ("Ce que personne ne dit",
             "Il n'a pas été contraint. Il a accepté. Le Reiō a choisi de devenir "
             "un outil pour que les mondes puissent exister. Ce que cela implique "
             "sur la légitimité de Soul Society et de ses institutions est une "
             "question que personne ne formule à voix haute. Pas encore."),
        ],
    },
    "division_zero": {
        "titre":  "零 La Division Zéro · Garde Royale",
        "couleur": COULEURS["or_pale"],
        "web_fragment": "division-zero",
        "description": (
            "La Division Zéro ne rend de comptes ni au Gotei 13, ni au Conseil Central 46. "
            "Elle répond aux descendants des cinq Grandes Maisons Nobles, héritiers de ceux "
            "qui commirent le Péché Originel. Ses membres sont d'anciens Capitaines, promus "
            "pour avoir apporté quelque chose de fondamental à Soul Society. Leur puissance "
            "combinée dépasse celle de l'ensemble du Gotei."
        ),
        "fields": [
            ("Le Palais du Reiō",
             "Une dimension flottante au-dessus de Soul Society. On n'y accède "
             "que par l'Ōken, une clé spirituelle gravée à même les os de ceux "
             "qui la portent. Tant que le Palais tient et qu'un membre de la "
             "Garde survit, les morts peuvent être ramenés."),
            ("Le silence gardé",
             "Ils connaissent la vérité. Le Péché Originel, le Konsō Reisai, "
             "l'antériorité de l'Enfer : ils savent tout et se taisent depuis "
             "des millions d'années. Leur silence passe pour un accord tacite "
             "avec l'ordre établi."),
            ("Face à la Fissure",
             "Intervenir, c'est révéler des millénaires de mensonge. Ne pas "
             "intervenir, c'est regarder l'Enfer se déverser. Les membres "
             "actuels sont divisés. Et la disparition simultanée des Deux "
             "Piliers pourrait être une catastrophe naturelle comme un acte "
             "délibéré. La Division Zéro est probablement la seule à pouvoir "
             "trancher."),
        ],
    },
    "konso_reisai": {
        "titre":  "⚰️ Le Konsō Reisai · Le Secret des Capitaines",
        "couleur": COULEURS["rouge_chaine"],
        "web_fragment": "shinigami",
        "description": (
            "Le rituel existe depuis la fondation du Gotei 13. Quand un Capitaine meurt, son "
            "Reishi est trop dense pour que le sol de Soul Society le réabsorbe : il faut "
            "l'envoyer ailleurs. Douze ans après la mort, une cérémonie est organisée en "
            "secret. Un Hollow est sacrifié devant la tombe et le Reishi du défunt est "
            "canalisé vers l'Enfer.\n\n"
            "Les subordonnés pensent assister à un rite de passage vers le repos éternel. "
            "Personne ne leur a dit la vérité. Des générations entières de Capitaines ont "
            "été honorées, pleurées et précipitées dans les Strates à l'insu de tous."
        ),
        "fields": [
            ("La Révélation",
             "Le secret a sauté après la Grande Guerre contre les Quincy "
             "survivants. Les Capitaines en fonction savent désormais. "
             "Les Vice-Capitaines commencent à l'apprendre, par bribes, "
             "à demi-mot. Les rangs inférieurs n'ont pas été informés."),
            ("Les Implications",
             "Des centaines de Capitaines envoyés en Enfer sur des "
             "millénaires. Certains y ont survécu, évolué, et atteint "
             "une puissance que rien dans les Trois Mondes n'égale. Ils "
             "sont les damnés les plus redoutables qui existent."),
            ("La Question",
             "Le rituel servait-il à renforcer les barrières de l'Enfer, "
             "ou à s'assurer que ces Capitaines trop puissants ne "
             "reviendraient jamais ? Et si certains le savaient avant "
             "de mourir, et qu'ils ont accepté quand même ?"),
        ],
    },
    "systeme": {
        "titre":  "⚔️ Système de Progression",
        "couleur": COULEURS["gris_acier"],
        "web_fragment": "",
        "description": (
            "La progression dans Infernum Aeterna suit le parcours narratif de votre "
            "personnage. Écrire des scènes, traverser des arcs, combattre, accomplir "
            "des missions : tout compte. Les points ne récompensent pas seulement la "
            "victoire, ils récompensent la présence."
        ),
        "fields": [
            ("Comment progresser",
             "Le staff attribue des **points de progression** pour le RP actif. "
             "Scènes, combats, arcs narratifs, missions, journal personnel : chaque "
             "contribution compte. Quand vos points franchissent un seuil de rang, la "
             "montée se déclenche : nouveaux rôles, narration dans le Journal de "
             "l'Enfer, budget de Reiryoku augmenté."),
            ("Rangs et puissance par faction",
             "**Shinigami** : Gakusei (500 pts, 250 PS) → Shinigami (1 200, 1 440) → "
             "Yonseki (2 500, 6 250) → Sanseki (4 000, 16 000) → "
             "Fukutaichō (6 500, 42 250) → Taichō (8 500, 72 250) → Sōtaichō (10 000, 100 000)\n\n"
             "**Togabito** : Zainin (500, 250) → Togabito (2 000, 4 000) → "
             "Tan-Togabito (4 500, 20 250) → Kō-Togabito (7 500, 56 250) → Gokuō (10 000, 100 000)\n\n"
             "**Arrancar** : Horō (500, 250) → Gillian (1 000, 1 000) → Adjuchas (2 000, 4 000) → "
             "Vasto Lorde (3 500, 12 250) → Números (5 000, 25 000) → Fracción (6 500, 42 250) → "
             "Privaron Espada (8 000, 64 000) → Espada (9 000, 81 000) → Rey (10 000, 100 000)\n\n"
             "**Quincy** : Minarai (500, 250) → Quincy (1 500, 2 250) → "
             "Jagdarmee (3 000, 9 000) → Sternritter (6 000, 36 000) → "
             "Schutzstaffel (8 500, 72 250) → Seitei (10 000, 100 000)"),
            ("Aptitudes et Reiryoku (霊力)",
             "Chaque rang accorde un budget de **Reiryoku** (de 3 à 26 points) "
             "à répartir entre les quatre **Voies** de votre faction. Trois paliers "
             "d'aptitudes : **Éveil** (1 霊力), **Maîtrise** (2 霊力), "
             "**Transcendance** (3 霊力). Le palier ultime est verrouillé derrière "
             "un rang élevé et une condition RP validée par le staff."),
            ("Puissance Spirituelle (PS)",
             "Calculée par **PS = Points² ÷ 1 000** (minimum 1). L'échelle est "
             "quadratique : un étudiant à 500 pts pèse 250 PS, un Capitaine à "
             "8 500 pts en affiche 72 250, un Commandant à 10 000 pts culmine "
             "à 100 000.\n\n"
             "En combat, l'écart de PS fixe un **palier narratif** :\n"
             "均衡 **Équilibre** (0–2 000) · toutes les aptitudes fonctionnent\n"
             "優勢 **Ascendant** (2 001–8 000) · les techniques de base faiblissent\n"
             "制圧 **Domination** (8 001–25 000) · seules les Maîtrises portent\n"
             "圧倒 **Écrasement** (25 001–55 000) · seule la Transcendance compte\n"
             "深淵 **Abîme** (55 001+) · rien ne comble le gouffre"),
            ("Mort narrative",
             "Un personnage peut mourir si les joueurs concernés donnent leur "
             "accord et que le staff valide. Après la mort, le personnage peut "
             "renaître dans un nouveau contexte ou repartir de zéro. Les acquis "
             "narratifs ne sont jamais perdus."),
        ],
    },
    "gotei": {
        "titre":  "🏯 Le Gotei 13 · Des Tueurs aux Gardiens",
        "couleur": COULEURS["blanc_seireitei"],
        "web_fragment": "shinigami",
        "description": (
            "Le Gotei 13 des origines n'avait rien d'une institution noble. C'était une "
            "bande de tueurs réunis par un guerrier au Zanpakutō de feu, le premier "
            "Capitaine-Commandant, un être d'une brutalité froide qui n'hésitait pas à "
            "sacrifier les siens si la situation l'exigeait.\n\n"
            "Ils imposèrent un ordre à Soul Society par la force brute, district par "
            "district. Parmi les premiers Capitaines, trois figures ont marqué les "
            "chroniques : Kōshin Jūrōmaru et son Zanpakutō de feu, l'aîné et le plus "
            "puissant de sa catégorie ; Tōka Shibari dont la lame existait en état de "
            "libération permanente ; Renjō Mikazuchi, le plus mystérieux, qui abritait "
            "en lui une entité d'une nature que personne ne comprit jamais."
        ),
        "fields": [
            ("L'adoucissement",
             "Après avoir vaincu le Lichtreich, le Gotei changea de visage. "
             "L'Académie fut fondée, le Konsō codifié, la brutalité remplacée par "
             "le protocole. L'Empereur Quincy estimait que cette organisation était "
             "morte il y a mille ans, remplacée par quelque chose de plus noble "
             "et de plus fragile."),
            ("Aujourd'hui",
             "Plusieurs millénaires d'existence. Le poids de tous ces secrets "
             "accumulés. La question la plus urgente n'est pas de savoir comment "
             "colmater la Fissure. C'est de savoir ce que le Gotei doit à toutes "
             "les âmes qu'il a envoyées en Enfer."),
        ],
    },
    "strates_lore": {
        "titre":  "⛓️ Les Cinq Strates de l'Enfer",
        "couleur": COULEURS["pourpre_infernal"],
        "web_fragment": "togabito",
        "description": (
            "L'Enfer descend en cinq niveaux. Chaque strate est plus violente que la "
            "précédente, plus dense en énergie infernale. Les premiers Togabito y arrivèrent "
            "sans guide, sans repère, sans explication. Juste les Kushanāda qui dévorent, les "
            "Jigokusari qui enchaînent, et cinq étages dont la logique ne se révèle qu'à ceux "
            "qui ont tenu assez longtemps pour la deviner.\n\n"
            "Depuis la Fissure, les frontières entre Strates sont devenues instables. Les "
            "passages prévisibles depuis des éternités ne le sont plus. Pour la première fois, "
            "l'architecture de l'Enfer tremble."
        ),
        "fields": [
            ("🔴 Prātus — Première Strate",
             "Le Vestibule des Damnés. Chaleur à fondre les os, cendres, hurlements "
             "permanents. Les nouveaux y gardent encore leur ancien visage."),
            ("🟠 Carnale — Deuxième Strate",
             "Les Plaines Brûlantes. Soufre, corps consumés et régénérés en "
             "boucle. Ceux qui traversent y perdent quelque chose qui ne revient pas."),
            ("🟡 Sulfura — Troisième Strate",
             "Les Geysers de Soufre. Visibilité nulle, terrain qui se reconfigure "
             "sans cesse. Seul l'instinct forgé par des siècles permet de s'orienter."),
            ("🔵 Profundus — Quatrième Strate",
             "L'Obscurité Profonde. Pression spirituelle écrasante, Kushanāda en "
             "permanence. Très peu y descendent. Ceux qui remontent ne sont plus les mêmes."),
            ("⚫ Saiōbu — Cinquième Strate",
             "L'Abyssal. Silence total. Les lois des Trois Mondes ne s'appliquent "
             "plus. Ce qui existe ici est antérieur à la création."),
        ],
    },
    "tensions": {
        "titre":  "⚡ Tensions Inter-Factions",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "creation",
        "description": (
            "Les quatre races n'ont pas attendu la Fissure pour se méfier les unes des "
            "autres, mais la brèche a réorganisé toutes les alliances et toutes les rancœurs. "
            "Chaque relation entre factions porte une question narrative à laquelle le RP seul "
            "peut répondre."
        ),
        "fields": [
            ("Shinigami ↔ Togabito",
             "Le Konsō Reisai a été révélé. Les Togabito regardent les Shinigami "
             "et leur posent une seule question : *vous saviez ?* Les Shinigami "
             "qui tombent sur d'anciens Capitaines en Enfer se posent la même, "
             "dans l'autre sens."),
            ("Arrancar ↔ Togabito",
             "Le vide Hollow résonne avec l'énergie infernale. Les Arrancar "
             "veulent comprendre ce qu'ils ressentent, les Togabito anciens "
             "connaissent l'Enfer de l'intérieur. Il y a des choses à "
             "s'apprendre, et autant de raisons de ne pas se faire confiance."),
            ("Quincy ↔ Shinigami",
             "Un millénaire de génocide. La plaie ne s'est jamais refermée. "
             "Mais la Fissure pose un problème que ni les uns ni les autres ne "
             "peuvent résoudre seuls. S'allier avec ceux qui ont massacré les "
             "vôtres, ou périr séparément."),
            ("Quincy ↔ Togabito",
             "Les Quincy lisent une direction dans l'énergie infernale. Les "
             "Togabito anciens savent ce que cette direction signifie vu d'en "
             "bas. Aucun des deux camps ne possède le tableau complet seul."),
        ],
    },
    "frontiere": {
        "titre":  "🌀 La Frontière · 境界 Kyōkai",
        "couleur": COULEURS["gris_acier"],
        "web_fragment": "prologue",
        "description": (
            "Avant la Fissure, personne ne s'arrêtait dans l'espace entre les mondes. Les "
            "Shinigami le traversaient par le Senkaimon, les Quincy le perçaient par l'ombre, "
            "les Hollow le déchiraient par leurs Garganta. Un couloir, rien de plus.\n\n"
            "Quand les Portes de l'Enfer se sont fissurées, le couloir s'est élargi. Les "
            "murs se sont éloignés, puis effacés. Ce vide est devenu un lieu, vaste, mouvant, "
            "respirable. Les archives les plus anciennes de la Garde Royale avaient un mot "
            "pour le désigner : Kyōkai (境界). La Frontière.\n\n"
            "Elle n'a pas été créée. Elle a été révélée."
        ),
        "fields": [
            ("Ce qu'on y voit",
             "Pas de ciel. Un vide gris traversé de veines lumineuses qui pulsent selon "
             "des marées que personne ne comprend. Le sol est fait de morceaux volés aux "
             "mondes adjacents : dalles blanches du Seireitei, sable de quartz de Hueco "
             "Mundo, roche calcinée des Strates, asphalte fissuré du Monde des Vivants. "
             "Ces fragments dérivent, se heurtent, fusionnent. La topographie change d'une "
             "semaine à l'autre. Ceux qui essaient de cartographier la Frontière finissent "
             "par comprendre que c'est elle qui les cartographie."),
            ("Ce qui y tue",
             "Des courants de Reishi brut, des torrents d'énergie qui traversent sans "
             "prévenir et désintègrent tout corps spirituel trop faible. Des poches de "
             "vide absolu où un Shinigami perd son Shikai, où un Quincy ne sent plus un "
             "seul fil de Reishi sous ses doigts. Et partout, en nuages noirs et "
             "phosphorescents, le Jigoku no Rinki. Plus dense ici qu'ailleurs, plus "
             "proche de sa source."),
            ("Ceux qui s'y croisent",
             "Les patrouilles Shinigami débarquent par le Dangai, tendues, sur-armées. "
             "Les Togabito y émergent par la Fissure et c'est leur premier souffle hors "
             "de l'Enfer : certains restent à genoux des heures, incapables de croire "
             "que la douleur a cessé. Les Arrancar s'y aventurent de leur plein gré, "
             "attirés par une résonance que leur vide intérieur reconnaît. Les Quincy "
             "y lisent les flux contaminés et tracent des cartes que personne d'autre "
             "ne sait déchiffrer. Aucune faction ne contrôle cet endroit."),
            ("Ce qui inquiète",
             "Elle grandit. Chaque semaine, les fragments qui y dérivent sont plus "
             "nombreux, arrachés plus profondément aux mondes adjacents. Ce qui inquiète "
             "les esprits les plus lucides, ce n'est pas la taille de la Fissure. C'est "
             "que la Frontière remplace peu à peu les mondes eux-mêmes, que l'espace "
             "entre les choses devienne la seule chose qui subsiste. Les Togabito les "
             "plus anciens, ceux qui ont vu ce qui existe sous la Cinquième Strate, "
             "disent que la Frontière leur rappelle quelque chose. Quelque chose d'avant "
             "les mondes. Quelque chose qui ressemble à la Mer Primordiale."),
        ],
    },
    "chronologie": {
        "titre":  "📜 Chronologie · Les Sept Ères",
        "couleur": COULEURS["or_ancien"],
        "web_fragment": "prologue",
        "description": (
            "Le temps ne s'écoule pas de la même façon dans les Trois Mondes. Soul Society "
            "ne compte pas les années comme le Monde des Vivants, et l'Enfer ne compte rien "
            "du tout. Ce qui suit n'est pas une chronologie au sens propre. C'est une liste "
            "de ruptures. Chacune a changé la nature de ce qui existait avant. Aucune n'a "
            "été réparée."
        ),
        "fields": [
            ("Ère I · La Mer Primordiale",
             "Avant les mondes. Un état indivisé où vie et mort ne se distinguent "
             "pas. L'obscurité ronge les âmes de l'intérieur. Un être émerge pour "
             "la combattre. Cinq êtres puissants le capturent, le mutilent, le "
             "scellent dans un cristal. Il ne résiste pas. De sa puissance, ils "
             "créent Soul Society, le Monde des Vivants, Hueco Mundo. L'Enfer "
             "existait déjà."),
            ("Ère II · Le Chaos Originel",
             "Des millions d'années sans loi. Soul Society gouvernée par la force "
             "brute, les Hollow décimant le Monde des Vivants sans régulation. "
             "Dans les Strates, les premières âmes damnées découvrent les "
             "Kushanāda et les Jigokusari sans personne pour leur expliquer. "
             "À Hueco Mundo, la chaîne alimentaire Hollow prend forme : Gillian, "
             "Adjuchas, Vasto Lorde. Les plus rares brisent leur masque. Las "
             "Noches commence à s'élever."),
            ("Ère III · La Fondation du Gotei",
             "Un guerrier au Zanpakutō de feu réunit treize lames et impose "
             "l'ordre à Soul Society par la force. Ce ne sont pas des gardiens "
             "mais des tueurs qui ont compris que le chaos ne céderait qu'à "
             "l'organisation. Parmi eux, Tōka Shibari et sa lame en libération "
             "permanente, Renjō Mikazuchi et son mystère. Le Konsō Reisai est "
             "formalisé dans les premières générations. La dette commence à "
             "s'accumuler."),
            ("Ère IV · La Guerre de Lumière (~1 000 ans avant)",
             "Le Lichtreich, Empire de Lumière des Quincy, défie le Gotei. Leur "
             "Empereur, fils du Reiō, porte une puissance prophétique que personne "
             "ne comprend encore. La guerre est totale. L'Empereur tombe. Après la "
             "victoire, le Gotei change de visage : l'Académie est fondée, la "
             "brutalité cède la place à l'institution. Plus noble. Plus fragile."),
            ("Ère V · Les Siècles de Silence",
             "L'extermination des Quincy. Discrète, méthodique, famille par "
             "famille. Les survivants fondent le Wandenreich dans les ombres "
             "du Seireitei. Pendant ce temps, les Capitaines continuent de "
             "mourir et d'être expédiés en Enfer. Certains y ont évolué en "
             "entités d'une puissance inégalée dans les Trois Mondes."),
            ("Ère VI · La Grande Guerre et la Révélation",
             "Le Wandenreich frappe Soul Society. La guerre bouleverse tout. "
             "Les Deux Piliers Maudits, fragments du Reiō qui maintenaient "
             "sans le savoir l'équilibre entre l'Enfer et les Trois Mondes, "
             "disparaissent presque simultanément. Après le silence des armes, "
             "la vérité du Konsō Reisai est révélée aux Capitaines. Elle "
             "divise le haut commandement en profondeur."),
            ("Ère VII · La Fissure (maintenant)",
             "Sans les Deux Piliers, la balance s'est rompue. Les Portes de "
             "l'Enfer se sont fissurées. Le Jigoku no Rinki déborde dans les "
             "Trois Mondes. Les Jigokusari se desserrent. Les Kushanāda "
             "hésitent. Et entre les mondes, le vide que personne ne regardait "
             "s'est élargi jusqu'à devenir un territoire. La Frontière. Quatre "
             "races s'y croisent sans se comprendre, et elle grandit chaque "
             "semaine. Quelque chose se déplace dans l'énergie infernale, "
             "avec une direction et une logique."),
        ],
    },
    "creation": {
        "titre":  "📝 Guide de Création de Personnage",
        "couleur": COULEURS["gris_acier"],
        "web_fragment": "creation",
        "description": (
            "Tout ce lore est une fondation pour vos personnages. Chaque faction ouvre des "
            "angles narratifs différents, et la Fissure donne à chacun une raison d'exister "
            "qui dépasse sa propre histoire. Voici la question centrale de chaque camp."
        ),
        "fields": [
            ("死神 Shinigami",
             "Depuis combien de temps sert-on une institution fondée sur un "
             "mensonge ? Et que fait-on le jour où on l'apprend ? Chaque rang "
             "offre un angle différent. L'élève ignore tout. Le Capitaine "
             "porte le poids de la vérité sur ses épaules."),
            ("咎人 Togabito",
             "Des siècles de souffrance ont forgé une âme qui avait appris "
             "à tuer l'espoir en elle pour survivre. Et voilà que la Fissure "
             "s'ouvre, et que l'espoir revient. La diversité des origines "
             "rend chaque Togabito unique."),
            ("破面 Arrancar",
             "Le vide dans la poitrine pourrait se remplir un peu. La "
             "résonance infernale offre quelque chose d'inédit à ceux qui "
             "ont toujours porté l'absence. Reste à savoir quel prix "
             "ils sont prêts à payer."),
            ("滅却師 Quincy",
             "Ils voient ce que les autres ne voient pas. L'énergie "
             "infernale dessine une carte lisible pour eux seuls. La "
             "question : faut-il la partager avec les Shinigami, ceux "
             "qui ont tenté de les exterminer ?"),
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
        app_commands.Choice(name="La Fissure · Cause et Conséquences",      value="fissure"),
        app_commands.Choice(name="Le Reiō · Le Roi Mutilé",               value="reio"),
        app_commands.Choice(name="La Division Zéro",                       value="division_zero"),
        app_commands.Choice(name="Le Konsō Reisai · Le Secret",           value="konso_reisai"),
        app_commands.Choice(name="Le Gotei 13 · Des Tueurs aux Gardiens", value="gotei"),
        app_commands.Choice(name="Les Cinq Strates de l'Enfer",            value="strates_lore"),
        app_commands.Choice(name="La Frontière · 境界 Kyōkai",             value="frontiere"),
        app_commands.Choice(name="Chronologie · Les Sept Ères",            value="chronologie"),
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
        app_commands.Choice(name=f"{v[0]} · {k.replace('_', ' ').capitalize()}", value=k)
        for k, v in list(GLOSSAIRE.items())[:25]  # Discord limite à 25 choices
    ])
    async def glossaire(self, interaction: discord.Interaction, terme: str):
        if terme not in GLOSSAIRE:
            await interaction.response.send_message("❌ Terme introuvable.", ephemeral=True)
            return
        kanji, definition = GLOSSAIRE[terme]
        embed = discord.Embed(
            title=f"📜 {kanji} · {terme.replace('_', ' ').capitalize()}",
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
                "Cinq niveaux. Chacun plus violent que le précédent, chacun plus dense "
                "en énergie infernale. Plus on descend, plus la puissance requise pour "
                "survivre est grande. Depuis la Fissure, les frontières entre Strates "
                "vacillent. L'Enfer tremble pour la première fois."
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
