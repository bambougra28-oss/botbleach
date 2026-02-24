/**
 * INFERNUM AETERNA — Simulateur de Build : Donnees
 * Transcription directe des fichiers Python data/aptitudes/*.py
 * Source de verite : constants.py + shinigami.py + togabito.py + arrancar.py + quincy.py
 */

// ══════════════════════════════════════════════════════════════════════════════
//  RANGS PAR FACTION
// ══════════════════════════════════════════════════════════════════════════════

var SIM_RANGS = {
  shinigami: [
    {cle:"gakusei",       nom:"Gakusei",          emoji:"\uD83C\uDF93", budget:3,  p3:false},
    {cle:"shinigami_asserm",nom:"Shinigami",       emoji:"\u262F\uFE0F", budget:6,  p3:false},
    {cle:"yonseki",       nom:"Yonseki",           emoji:"\uD83D\uDDE1\uFE0F", budget:10, p3:false},
    {cle:"sanseki",       nom:"Sanseki",           emoji:"\u2694\uFE0F", budget:14, p3:false},
    {cle:"fukutaicho",    nom:"Fukutaich\u014D",   emoji:"\uD83C\uDF96\uFE0F", budget:18, p3:true},
    {cle:"taicho",        nom:"Taich\u014D",       emoji:"\u2B50",       budget:22, p3:true},
    {cle:"sotaicho",      nom:"S\u014Dtaich\u014D",emoji:"\uD83D\uDC51", budget:26, p3:true}
  ],
  togabito: [
    {cle:"zainin",        nom:"Zainin",            emoji:"\uD83D\uDC80", budget:3,  p3:false},
    {cle:"togabito_damne",nom:"Togabito",          emoji:"\uD83E\uDE78", budget:8,  p3:false},
    {cle:"tan_togabito",  nom:"Tan-Togabito",      emoji:"\uD83D\uDD17", budget:14, p3:false},
    {cle:"ko_togabito",   nom:"K\u014D-Togabito",  emoji:"\u26D3\uFE0F", budget:20, p3:true},
    {cle:"gokuo",         nom:"Goku\u014D",        emoji:"\uD83D\uDC51", budget:26, p3:true}
  ],
  arrancar: [
    {cle:"horo",          nom:"Hor\u014D",         emoji:"\u25FD",       budget:3,  p3:false},
    {cle:"gillian",       nom:"Gillian",           emoji:"\uD83D\uDFE2", budget:5,  p3:false},
    {cle:"adjuchas",      nom:"Adjuchas",          emoji:"\uD83D\uDD35", budget:8,  p3:false},
    {cle:"vasto_lorde",   nom:"Vasto Lorde",       emoji:"\uD83D\uDFE3", budget:11, p3:false},
    {cle:"numeros",       nom:"N\u00FAmeros",      emoji:"\u25CB",       budget:14, p3:false},
    {cle:"fraccion",      nom:"Fracci\u00F3n",     emoji:"\u25C7",       budget:17, p3:false},
    {cle:"privaron_espada",nom:"Privaron Espada",  emoji:"\u25C8",       budget:20, p3:true},
    {cle:"espada",        nom:"Espada",            emoji:"\uD83D\uDCA0", budget:23, p3:true},
    {cle:"rey",           nom:"Rey",               emoji:"\uD83D\uDC51", budget:26, p3:true}
  ],
  quincy: [
    {cle:"minarai",       nom:"Minarai",           emoji:"\u2218",       budget:3,  p3:false},
    {cle:"quincy_confirme",nom:"Quincy",           emoji:"\u2217",       budget:7,  p3:false},
    {cle:"jagdarmee",     nom:"Jagdarmee",         emoji:"\u2295",       budget:12, p3:false},
    {cle:"sternritter",   nom:"Sternritter",       emoji:"\u2727",       budget:18, p3:true},
    {cle:"schutzstaffel", nom:"Schutzstaffel",     emoji:"\u2726",       budget:22, p3:true},
    {cle:"seitei",        nom:"Seitei",            emoji:"\uD83D\uDC51", budget:26, p3:true}
  ]
};

// ══════════════════════════════════════════════════════════════════════════════
//  FACTIONS + VOIES + APTITUDES
// ══════════════════════════════════════════════════════════════════════════════

var SIM_FACTIONS = {

// ─────────────────────────────────────────────────────────────────────────────
//  SHINIGAMI
// ─────────────────────────────────────────────────────────────────────────────
shinigami: {
  nom:"Shinigami", kanji:"\u6B7B\u795E", couleur:"#E8E8F0",
  accroche:"Gardes de la mort, gardiens de l'\u00E9quilibre entre les mondes.",
  voies:[
  // ── Zanjutsu ──
  {id:"shin_zanjutsu",nom:"Zanjutsu",kanji:"\u65AC\u8853",sousTitre:"L'Art du Sabre",
   desc:"La lame n'est pas une arme \u2014 c'est un miroir. Chaque coup port\u00E9 r\u00E9v\u00E8le autant le porteur que la cible.",
   apt:[
    {id:"shin_zan_p1a",nom:"Jinzen",kanji:"\u5203\u7985",p:1,c:1,desc:"Assis en silence, la lame pos\u00E9e sur les genoux, le Shinigami ferme les yeux et plonge dans l'espace int\u00E9rieur o\u00F9 r\u00E9side l'esprit du Zanpakut\u014D. La m\u00E9ditation peut durer des heures, des jours. La plupart n'entendent rien. Ceux qui reviennent avec un nom sur les l\u00E8vres ne sont plus jamais les m\u00EAmes.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_zan_p1b",nom:"Kend\u014D",kanji:"\u5263\u9053",p:1,c:1,desc:"Avant de communier avec l'esprit, il faut ma\u00EEtriser la chair. Le Kend\u014D enseigne la posture, la coupe, le rythme \u2014 les fondements sur lesquels toute technique repose.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_zan_p1c",nom:"Maai",kanji:"\u9593\u5408\u3044",p:1,c:1,desc:"La distance juste. Le Maai est l'art de lire l'espace entre deux combattants \u2014 savoir quand l'adversaire est \u00E0 port\u00E9e, quand il ne l'est pas, quand un pas en avant tranchera.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_zan_p2a",nom:"Shikai",kanji:"\u59CB\u89E3",p:2,c:2,desc:"Le Zanpakut\u014D r\u00E9pond enfin \u00E0 l'appel. La commande de lib\u00E9ration est prononc\u00E9e \u2014 un mot, une phrase, un ordre qui r\u00E9sonne dans les deux mondes \u00E0 la fois. La lame change de forme, r\u00E9v\u00E9lant une fraction de sa v\u00E9ritable nature.",prereqIds:["shin_zan_p1a"],cond:"Sc\u00E8ne RP de m\u00E9ditation Jinzen valid\u00E9e par le staff.",rangMin:null},
    {id:"shin_zan_p2b",nom:"Isshin",kanji:"\u4E00\u5FC3",p:2,c:2,desc:"L'unit\u00E9 parfaite entre le corps et la lame. Le Shinigami ne manie plus son Zanpakut\u014D \u2014 il le prolonge. Chaque mouvement du bras s'ach\u00E8ve naturellement dans l'acier.",prereqIds:["shin_zan_p1b"],cond:null,rangMin:null},
    {id:"shin_zan_p2c",nom:"Ry\u014Ddan",kanji:"\u4E21\u65AD",p:2,c:2,desc:"La Coupe D\u00E9vastatrice. Toute la force du praticien converge en une unique frappe descendante \u2014 un arc vertical qui ne conna\u00EEt ni h\u00E9sitation ni retenue.",prereqIds:["shin_zan_p1b","shin_zan_p1c"],cond:null,rangMin:null},
    {id:"shin_zan_p3a",nom:"Bankai",kanji:"\u534D\u89E3",p:3,c:3,desc:"La lib\u00E9ration finale. Le Zanpakut\u014D se mat\u00E9rialise dans sa forme absolue \u2014 une manifestation de puissance si consid\u00E9rable que l'air autour du porteur se distord. Ma\u00EEtriser le Bankai requiert des ann\u00E9es d'entra\u00EEnement.",prereqIds:["shin_zan_p2a","shin_zan_p2b"],cond:"Arc RP complet de mat\u00E9rialisation et combat contre l'esprit du Zanpakut\u014D.",rangMin:"fukutaicho"},
    {id:"shin_zan_p3b",nom:"Bankai Jukuren",kanji:"\u534D\u89E3\u719F\u7DF4",p:3,c:3,desc:"Le Bankai Ma\u00EEtris\u00E9. L\u00E0 o\u00F9 la plupart des porteurs peinent \u00E0 maintenir leur lib\u00E9ration finale, celui-ci l'habite comme une seconde peau. Le Reishi ne fuit plus \u2014 il ob\u00E9it.",prereqIds:["shin_zan_p3a","shin_zan_p2c"],cond:"Arc RP de ma\u00EEtrise du Bankai d\u00E9montrant un contr\u00F4le total en situation extr\u00EAme.",rangMin:"taicho"}
  ]},
  // ── Kid\u014D ──
  {id:"shin_kido",nom:"Kid\u014D",kanji:"\u9B3C\u9053",sousTitre:"Les Arts D\u00E9moniaques",
   desc:"Les incantations ne sont pas des formules \u2014 ce sont des cl\u00E9s. Chaque mot prononc\u00E9 ouvre une porte dans le tissu de la r\u00E9alit\u00E9 spirituelle.",
   apt:[
    {id:"shin_kid_p1a",nom:"Had\u014D Kiso",kanji:"\u7834\u9053\u57FA\u790E",p:1,c:1,desc:"Les sorts de destruction de base \u2014 Shakkah\u014D, Byakurai, S\u014Dkatsui. Chacun s'apprend dans l'ordre, incantation compl\u00E8te obligatoire.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_kid_p1b",nom:"Bakud\u014D Kiso",kanji:"\u7E1B\u9053\u57FA\u790E",p:1,c:1,desc:"Les sorts d'entrave fondamentaux \u2014 Sai, Hainawa, Sekienton. L\u00E0 o\u00F9 le Had\u014D d\u00E9truit, le Bakud\u014D contraint.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_kid_p1c",nom:"Kid\u014D Riron",kanji:"\u9B3C\u9053\u7406\u8AD6",p:1,c:1,desc:"La Th\u00E9orie du Kid\u014D. Avant la puissance, la compr\u00E9hension. Le praticien \u00E9tudie les flux de Reishi, les structures des incantations.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_kid_p2a",nom:"Eish\u014Dhaki",kanji:"\u8A60\u5531\u7834\u68C4",p:2,c:2,desc:"L'incantation est abandonn\u00E9e. Le sort est lanc\u00E9 par la seule volont\u00E9, sans un mot. La puissance diminue, mais la vitesse d'ex\u00E9cution devient terrifiante.",prereqIds:["shin_kid_p1a","shin_kid_p1c"],cond:null,rangMin:null},
    {id:"shin_kid_p2b",nom:"Kaid\u014D",kanji:"\u56DE\u9053",p:2,c:2,desc:"L'art de gu\u00E9rir par le Reishi. Le pratiquant pose ses mains sur la blessure et canalise son \u00E9nergie spirituelle pour reconstituer les tissus endommag\u00E9s.",prereqIds:["shin_kid_p1b"],cond:null,rangMin:null},
    {id:"shin_kid_p2c",nom:"Had\u014D Ch\u016Bky\u016B",kanji:"\u7834\u9053\u4E2D\u7D1A",p:2,c:2,desc:"Les sorts de destruction interm\u00E9diaires \u2014 num\u00E9ros 31 \u00E0 63, l\u00E0 o\u00F9 la fronti\u00E8re entre art et arme s'efface.",prereqIds:["shin_kid_p1a"],cond:null,rangMin:null},
    {id:"shin_kid_p2d",nom:"Bakud\u014D Ch\u016Bky\u016B",kanji:"\u7E1B\u9053\u4E2D\u7D1A",p:2,c:2,desc:"Les sorts d'entrave interm\u00E9diaires \u2014 Rikuj\u014Dk\u014Dr\u014D, Hyapporankan, Dank\u016B. Les barri\u00E8res qui arr\u00EAtent les Cero.",prereqIds:["shin_kid_p1b"],cond:null,rangMin:null},
    {id:"shin_kid_p3a",nom:"Nij\u016B Eish\u014D",kanji:"\u4E8C\u91CD\u8A60\u5531",p:3,c:3,desc:"Deux incantations entrelac\u00E9es, deux sorts lanc\u00E9s simultan\u00E9ment \u2014 un Had\u014D et un Bakud\u014D tiss\u00E9s dans le m\u00EAme souffle.",prereqIds:["shin_kid_p2a","shin_kid_p2c","shin_kid_p2d"],cond:"D\u00E9monstration RP de ma\u00EEtrise avanc\u00E9e du Kid\u014D valid\u00E9e.",rangMin:"fukutaicho"},
    {id:"shin_kid_p3b",nom:"Kaid\u014D Kiseki",kanji:"\u56DE\u9053\u5947\u8DE1",p:3,c:3,desc:"Le Miracle du Kaid\u014D. La gu\u00E9rison transcende ses limites naturelles \u2014 organes d\u00E9truits, membres sectionn\u00E9s, dommages \u00E0 l'\u00E2me elle-m\u00EAme.",prereqIds:["shin_kid_p2b","shin_kid_p2d"],cond:"Arc RP de gu\u00E9rison d'une blessure consid\u00E9r\u00E9e comme fatale.",rangMin:"fukutaicho"},
    {id:"shin_kid_p3c",nom:"Kid\u014D J\u014Di",kanji:"\u9B3C\u9053\u4E0A\u4F4D",p:3,c:3,desc:"Les sorts de rang 64 et au-del\u00E0 \u2014 Raik\u014Dh\u014D, S\u014Dkatsui Supr\u00EAme. L'incantation devient un po\u00E8me de guerre.",prereqIds:["shin_kid_p2c","shin_kid_p2d"],cond:"D\u00E9monstration RP de ma\u00EEtrise avanc\u00E9e du Had\u014D et du Bakud\u014D valid\u00E9e par le staff.",rangMin:"fukutaicho"}
  ]},
  // ── Hoh\u014D ──
  {id:"shin_hoho",nom:"Hoh\u014D",kanji:"\u6B69\u6CD5",sousTitre:"L'Art du D\u00E9placement",
   desc:"La vitesse n'est pas un attribut \u2014 c'est une philosophie. Le Hoh\u014D enseigne que la distance entre deux points n'est qu'une suggestion.",
   apt:[
    {id:"shin_hoh_p1a",nom:"Shunpo",kanji:"\u77AC\u6B69",p:1,c:1,desc:"Le Pas \u00C9clair. Le corps dispara\u00EEt d'un point et r\u00E9appara\u00EEt \u00E0 un autre en un battement de cil.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hoh_p1b",nom:"Senka",kanji:"\u9583\u82B1",p:1,c:1,desc:"L'\u00C9clair Floral. Un mouvement qui combine le Shunpo avec une frappe chirurgicale dans le dos de l'adversaire.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hoh_p1c",nom:"Hoh\u014D Hansha",kanji:"\u6B69\u6CD5\u53CD\u5C04",p:1,c:1,desc:"Le R\u00E9flexe du Hoh\u014D. Un micro-Shunpo instinctif d\u00E9clench\u00E9 par la perception d'un danger imminent.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hoh_p2a",nom:"Utsusemi",kanji:"\u7A7A\u8749",p:2,c:2,desc:"La Mue de la Cigale. Au moment pr\u00E9cis de l'impact, le corps s'efface en laissant derri\u00E8re lui un leurre.",prereqIds:["shin_hoh_p1a"],cond:null,rangMin:null},
    {id:"shin_hoh_p2b",nom:"Bunshin S\u014Dk\u014D",kanji:"\u5206\u8EAB\u88C5\u7532",p:2,c:2,desc:"Des images r\u00E9manentes persistantes, chacune assez dense en Reishi pour tromper m\u00EAme un Pesquisa.",prereqIds:["shin_hoh_p1b"],cond:null,rangMin:null},
    {id:"shin_hoh_p2c",nom:"Shunpo Renzoku",kanji:"\u77AC\u6B69\u9023\u7D9A",p:2,c:2,desc:"Le Shunpo Continu. Le praticien encha\u00EEne sans rupture, cr\u00E9ant une trajectoire fluide et impr\u00E9visible.",prereqIds:["shin_hoh_p1a","shin_hoh_p1c"],cond:null,rangMin:null},
    {id:"shin_hoh_p3a",nom:"Ky\u014Dka Shunpo",kanji:"\u97FF\u82B1\u6975",p:3,c:3,desc:"Le Shunpo pouss\u00E9 au-del\u00E0 de ses limites th\u00E9oriques. Le praticien existe simultan\u00E9ment en plusieurs points de l'espace.",prereqIds:["shin_hoh_p2a","shin_hoh_p2b"],cond:"Arc RP d\u00E9montrant une ma\u00EEtrise absolue du Hoh\u014D.",rangMin:"fukutaicho"},
    {id:"shin_hoh_p3b",nom:"Shunpo Senk\u014D",kanji:"\u77AC\u6B69\u9583\u5149",p:3,c:3,desc:"L'\u00C9clair du Shunpo. Le d\u00E9placement atteint une vitesse qui d\u00E9passe la perception spirituelle.",prereqIds:["shin_hoh_p2c","shin_hoh_p2a"],cond:"Arc RP de transcendance des limites de la vitesse.",rangMin:"taicho"}
  ]},
  // ── Hakuda ──
  {id:"shin_hakuda",nom:"Hakuda",kanji:"\u767D\u6253",sousTitre:"L'Art du Combat \u00E0 Mains Nues",
   desc:"Quand la lame est bris\u00E9e, quand le Kid\u014D est \u00E9puis\u00E9, quand le Shunpo ne suffit plus \u00E0 fuir \u2014 il reste le corps.",
   apt:[
    {id:"shin_hak_p1a",nom:"Bukei",kanji:"\u6B66\u5F62",p:1,c:1,desc:"Les formes martiales de base \u2014 postures, encha\u00EEnements, blocages. Le fondement de toute technique de corps \u00E0 corps.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hak_p1b",nom:"Tekken",kanji:"\u9244\u62F3",p:1,c:1,desc:"Le Poing de Fer. La concentration du Reishi dans les articulations transforme un coup de poing ordinaire en impact d\u00E9vastateur.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hak_p1c",nom:"Tai Sabaki",kanji:"\u4F53\u6368\u304D",p:1,c:1,desc:"Le Mouvement du Corps. L'art d'esquiver sans reculer \u2014 pivoter, glisser, rediriger la force de l'adversaire contre lui-m\u00EAme.",prereqIds:[],cond:null,rangMin:null},
    {id:"shin_hak_p2a",nom:"Ikkotsu",kanji:"\u4E00\u9AA8",p:2,c:2,desc:"Un seul os. Un seul coup. La totalit\u00E9 du Reishi converge dans le poing au moment de l'impact.",prereqIds:["shin_hak_p1b"],cond:null,rangMin:null},
    {id:"shin_hak_p2b",nom:"Kazaguruma",kanji:"\u98A8\u8ECA",p:2,c:2,desc:"Le Moulin \u00E0 Vent. Le corps entier devient l'arme \u2014 une rotation a\u00E9rienne qui transforme les jambes en faux.",prereqIds:["shin_hak_p1a"],cond:null,rangMin:null},
    {id:"shin_hak_p2c",nom:"Tessh\u014D",kanji:"\u9244\u638C",p:2,c:2,desc:"La Paume de Fer. Le Reishi se concentre dans la paume ouverte \u2014 la frappe projette une onde de choc qui traverse les d\u00E9fenses.",prereqIds:["shin_hak_p1b","shin_hak_p1c"],cond:null,rangMin:null},
    {id:"shin_hak_p3a",nom:"S\u014Dkotsu",kanji:"\u53CC\u9AA8",p:3,c:3,desc:"Deux os. Les deux poings frappent simultan\u00E9ment avec une puissance qui fait trembler l'air lui-m\u00EAme.",prereqIds:["shin_hak_p2a","shin_hak_p2b"],cond:"Victoire RP en combat rapproch\u00E9 contre un adversaire de rang \u00E9gal ou sup\u00E9rieur.",rangMin:"fukutaicho"},
    {id:"shin_hak_p3b",nom:"Oni Dekopin",kanji:"\u9B3C\u30C7\u30B3\u30D4\u30F3",p:3,c:3,desc:"La Pichenette du D\u00E9mon. Un simple mouvement de doigt, une pichenette qui projette l'adversaire \u00E0 travers des murs.",prereqIds:["shin_hak_p2a","shin_hak_p2c"],cond:"D\u00E9monstration RP de puissance Hakuda disproportionn\u00E9e.",rangMin:"fukutaicho"}
  ]},
  // ── Shunk\u014D ──
  {id:"shin_shunko",nom:"Shunk\u014D",kanji:"\u77AC\u95A7",sousTitre:"La Clameur \u00C9clair",
   desc:"L'union interdite du Hakuda et du Kid\u014D. Le Reishi concentr\u00E9 par l'Eish\u014Dhaki est redirig\u00E9 \u00E0 travers les membres.",
   apt:[
    {id:"shin_shun_p1a",nom:"Shunk\u014D",kanji:"\u77AC\u95A7",p:1,c:1,desc:"L'union interdite du Hakuda et du Kid\u014D. Une aura de puissance brute enveloppe le corps. Technique instable \u2014 l'\u00E9l\u00E9ment se r\u00E9v\u00E8le lors de la premi\u00E8re activation : Foudre, Vent, Flamme ou Glace.",prereqIds:["shin_hak_p2a","shin_kid_p2a"],cond:"Manifestation spontan\u00E9e lors d'un combat alliant Hakuda et Kid\u014D.",rangMin:"fukutaicho"},
    {id:"shin_shun_p1b",nom:"Hanki",kanji:"\u53CD\u9B3C",p:1,c:1,desc:"Le Revers D\u00E9moniaque. En produisant une \u00E9nergie exactement inverse \u00E0 un sort adverse au moment de l'impact physique, le combattant le neutralise.",prereqIds:["shin_hak_p1a","shin_kid_p2a"],cond:"Neutralisation d'un sort adverse par instinct martial en combat.",rangMin:"fukutaicho"},
    {id:"shin_shun_p1c",nom:"Reishi Junkan",kanji:"\u970A\u5B50\u5FAA\u74B0",p:1,c:1,desc:"La Circulation Spirituelle. Le pratiquant apprend \u00E0 faire circuler le Reishi \u00E0 travers les m\u00E9ridiens de son corps plut\u00F4t que de le projeter.",prereqIds:["shin_kid_p1a","shin_kid_p1c"],cond:null,rangMin:null},
    {id:"shin_shun_p2a",nom:"Shunk\u014D Seigyo",kanji:"\u77AC\u95A7\u30FB\u5236\u5FA1",p:2,c:2,desc:"La Clameur Dompt\u00E9e. L'aura \u00E9l\u00E9mentaire se stabilise sans fluctuation. Des effets \u00E9l\u00E9mentaires secondaires se manifestent.",prereqIds:["shin_shun_p1a","shin_shun_p1c"],cond:"Maintien du Shunk\u014D sur au moins 3 \u00E9changes cons\u00E9cutifs.",rangMin:null},
    {id:"shin_shun_p2b",nom:"Shunk\u014D Senkei",kanji:"\u77AC\u95A7\u30FB\u6226\u5F62",p:2,c:2,desc:"La Forme de Guerre. L'\u00E9nergie \u00E9l\u00E9mentaire se concentre en une forme de combat pr\u00E9cise : lames d'air, griffes de foudre, poings de flamme.",prereqIds:["shin_shun_p1a","shin_shun_p1b"],cond:"Utilisation offensive de la forme \u00E9l\u00E9mentaire en combat r\u00E9el.",rangMin:null},
    {id:"shin_shun_p3a",nom:"Shunk\u014D Kanzen",kanji:"\u77AC\u95A7\u30FB\u5B8C\u5168",p:3,c:3,desc:"La Clameur Parfaite. Le Shunk\u014D se projette \u00E0 distance, transformant l'environnement sur une trentaine de m\u00E8tres.",prereqIds:["shin_shun_p2a","shin_shun_p2b"],cond:"Ma\u00EEtrise absolue d\u00E9montr\u00E9e sur 3 combats en Shunk\u014D.",rangMin:"taicho"},
    {id:"shin_shun_p3b",nom:"Muk\u016B Shunk\u014D",kanji:"\u7121\u7A7A\u77AC\u95A7",p:3,c:3,desc:"La Clameur du Vide. Au-del\u00E0 de l'\u00E9l\u00E9ment. Le Shunk\u014D transcende l'affinit\u00E9 \u00E9l\u00E9mentaire pour devenir pure \u00E9nergie, invisible et absolue.",prereqIds:["shin_shun_p3a"],cond:"Arc RP de d\u00E9passement int\u00E9rieur \u2014 transcendance de l'affinit\u00E9 \u00E9l\u00E9mentaire.",rangMin:"taicho"}
  ]}
]},

// ─────────────────────────────────────────────────────────────────────────────
//  TOGABITO
// ─────────────────────────────────────────────────────────────────────────────
togabito: {
  nom:"Togabito", kanji:"\u54CE\u4EBA", couleur:"#6B1FA8",
  accroche:"Les Damn\u00E9s portent les marques de l'Enfer \u2014 et parfois, l'Enfer les porte.",
  voies:[
  // ── Jigokusari ──
  {id:"toga_jigokusari",nom:"Jigokusari",kanji:"\u5730\u7344\u9396",sousTitre:"Les Cha\u00EEnes de l'Enfer",
   desc:"Les cha\u00EEnes ne sont pas une punition \u2014 elles sont une extension de l'Enfer lui-m\u00EAme.",
   apt:[
    {id:"toga_jig_p1a",nom:"Kusari S\u014Dj\u016B",kanji:"\u9396\u64CD",p:1,c:1,desc:"Manipuler les cha\u00EEnes plut\u00F4t que les subir. Le Togabito dirige les maillons comme des appendices et peut se tracter le long d'une cha\u00EEne ancr\u00E9e.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_jig_p1b",nom:"Kusari Tate",kanji:"\u9396\u76FE",p:1,c:1,desc:"Les cha\u00EEnes se tissent devant le corps en un bouclier improvis\u00E9. Le m\u00E9tal infernal absorbe les impacts.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_jig_p1c",nom:"Kusari Kankaku",kanji:"\u9396\u611F\u899A",p:1,c:1,desc:"La Perception par les Cha\u00EEnes. Chaque maillon transmet les vibrations du monde \u2014 le souffle d'un ennemi cach\u00E9, le fr\u00E9missement d'une attaque.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_jig_p2a",nom:"Kusari Sha",kanji:"\u9396\u5C04",p:2,c:2,desc:"Les cha\u00EEnes se d\u00E9tachent du corps et fusent vers la cible. Technique aussi utilis\u00E9e pour la propulsion rapide.",prereqIds:["toga_jig_p1a"],cond:null,rangMin:null},
    {id:"toga_jig_p2b",nom:"Kusari R\u014D",kanji:"\u9396\u7262",p:2,c:2,desc:"Une prison de cha\u00EEnes se referme autour de l'adversaire. Les maillons s'entrem\u00EAlent et se resserrent.",prereqIds:["toga_jig_p1b"],cond:null,rangMin:null},
    {id:"toga_jig_p2c",nom:"Kusari Ky\u016Bsh\u016B",kanji:"\u9396\u5438\u53CE",p:2,c:2,desc:"L'Absorption des Cha\u00EEnes. Les maillons drainent le Reishi de la cible au contact.",prereqIds:["toga_jig_p1a","toga_jig_p1c"],cond:null,rangMin:null},
    {id:"toga_jig_p2d",nom:"Kusari Katachi",kanji:"\u9396\u5F62",p:2,c:2,desc:"La Forme des Cha\u00EEnes. Les maillons se reconfigurent \u2014 lance, mur, griffe g\u00E9ante, ailes de m\u00E9tal.",prereqIds:["toga_jig_p1b","toga_jig_p1c"],cond:null,rangMin:null},
    {id:"toga_jig_p3a",nom:"Rensa Shin'i",kanji:"\u9023\u9396\u795E\u610F",p:3,c:3,desc:"Les cha\u00EEnes deviennent une volont\u00E9 autonome qui anticipe, r\u00E9agit, frappe et d\u00E9fend.",prereqIds:["toga_jig_p2a","toga_jig_p2b"],cond:"Survie \u00E0 un affrontement avec un Kushan\u0101da ou \u00E9preuve des Strates profondes.",rangMin:"ko_togabito"},
    {id:"toga_jig_p3b",nom:"Kusari Tengoku",kanji:"\u9396\u5929\u7344",p:3,c:3,desc:"La Prison C\u00E9leste des Cha\u00EEnes. Une cage tridimensionnelle qui capture le Reishi lui-m\u00EAme.",prereqIds:["toga_jig_p2c","toga_jig_p2d"],cond:"Arc RP de ma\u00EEtrise totale des Cha\u00EEnes.",rangMin:"gokuo"}
  ]},
  // ── G\u014Dka ──
  {id:"toga_goka",nom:"G\u014Dka",kanji:"\u696D\u706B",sousTitre:"Le Feu Karmique",
   desc:"Le feu de l'Enfer n'est pas une flamme \u2014 c'est un jugement. Il br\u00FBle ce qui m\u00E9rite de br\u00FBler.",
   apt:[
    {id:"toga_gok_p1a",nom:"Gokuen",kanji:"\u7344\u708E",p:1,c:1,desc:"La Flamme de la Prison. Une flamme noire bord\u00E9e de violet qui consume tout ce qu'elle touche.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_gok_p1b",nom:"Sh\u014Dnetsu Kaku",kanji:"\u7126\u71B1\u6BBB",p:1,c:1,desc:"La Carapace Ardente. Le corps \u00E9met une chaleur intense qui repousse les attaques physiques.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_gok_p1c",nom:"G\u014Dka no Ishi",kanji:"\u696D\u706B\u306E\u610F\u5FD7",p:1,c:1,desc:"La Volont\u00E9 du Feu Karmique. Le Togabito lit les p\u00E9ch\u00E9s dans le Reishi des autres.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_gok_p2a",nom:"G\u014Dka H\u014D",kanji:"\u696D\u706B\u7832",p:2,c:2,desc:"Le Canon Karmique. Une d\u00E9charge concentr\u00E9e de flamme infernale en un rayon d\u00E9vastateur.",prereqIds:["toga_gok_p1a"],cond:null,rangMin:null},
    {id:"toga_gok_p2b",nom:"Sh\u014Dkyaku Ya",kanji:"\u713C\u5374\u91CE",p:2,c:2,desc:"La Plaine Calcin\u00E9e. Le feu karmique se r\u00E9pand en cercle, d\u00E9vorant tout.",prereqIds:["toga_gok_p1b"],cond:null,rangMin:null},
    {id:"toga_gok_p2c",nom:"G\u014Dka Yaiba",kanji:"\u696D\u706B\u5203",p:2,c:2,desc:"La Lame de Feu Karmique. Le feu infernal infus\u00E9 dans une arme juge en m\u00EAme temps qu'il tranche.",prereqIds:["toga_gok_p1a","toga_gok_p1c"],cond:null,rangMin:null},
    {id:"toga_gok_p3a",nom:"Rengoku Enran",kanji:"\u7149\u7344\u708E\u5D50",p:3,c:3,desc:"La Temp\u00EAte du Purgatoire. Le Togabito se dissout en une temp\u00EAte de flammes karmiques.",prereqIds:["toga_gok_p2a","toga_gok_p2b"],cond:"Arc RP de communion avec les flammes de la Strate Sulfura.",rangMin:"ko_togabito"},
    {id:"toga_gok_p3b",nom:"G\u014Dka Saiban",kanji:"\u696D\u706B\u88C1\u5224",p:3,c:3,desc:"Le Tribunal de Feu. La flamme karmique br\u00FBle l'\u00E2me proportionnellement aux p\u00E9ch\u00E9s qu'elle porte.",prereqIds:["toga_gok_p2a","toga_gok_p2c"],cond:"Arc RP de confrontation avec la nature judiciaire de l'Enfer.",rangMin:"gokuo"}
  ]},
  // ── Saisei ──
  {id:"toga_saisei",nom:"Saisei",kanji:"\u518D\u751F",sousTitre:"La R\u00E9g\u00E9n\u00E9ration Maudite",
   desc:"En Enfer, la mort n'est pas une fin \u2014 c'est un recommencement.",
   apt:[
    {id:"toga_sai_p1a",nom:"Jigoku Saisei",kanji:"\u5730\u7344\u518D\u751F",p:1,c:1,desc:"La r\u00E9g\u00E9n\u00E9ration acc\u00E9l\u00E9r\u00E9e, nourrie par le Reishi infernal. Les blessures se referment en quelques minutes.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_sai_p1b",nom:"Tsumi no Kioku",kanji:"\u7F6A\u306E\u8A18\u61B6",p:1,c:1,desc:"La M\u00E9moire du P\u00E9ch\u00E9. Chaque mort laisse une empreinte que le Togabito apprend \u00E0 lire.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_sai_p1c",nom:"Saisei Ishiki",kanji:"\u518D\u751F\u610F\u8B58",p:1,c:1,desc:"La Conscience de la R\u00E9g\u00E9n\u00E9ration. Le Togabito dirige consciemment le processus de reconstruction.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_sai_p2a",nom:"Junkan Ky\u014Dka",kanji:"\u5FAA\u74B0\u5F37\u5316",p:2,c:2,desc:"Le Cycle Renforc\u00E9. Chaque blessure gu\u00E9rie laisse le corps plus r\u00E9sistant.",prereqIds:["toga_sai_p1a"],cond:null,rangMin:null},
    {id:"toga_sai_p2b",nom:"Ts\u016Bkaku D\u014Dka",kanji:"\u75DB\u899A\u540C\u5316",p:2,c:2,desc:"L'Assimilation de la Douleur. Chaque blessure re\u00E7ue accro\u00EEt la puissance.",prereqIds:["toga_sai_p1b"],cond:null,rangMin:null},
    {id:"toga_sai_p2c",nom:"Saisei Hoji",kanji:"\u518D\u751F\u4FDD\u6301",p:2,c:2,desc:"La R\u00E9tention de R\u00E9g\u00E9n\u00E9ration. L'\u00E9nergie stock\u00E9e est lib\u00E9r\u00E9e en d\u00E9charge explosive.",prereqIds:["toga_sai_p1a","toga_sai_p1c"],cond:null,rangMin:null},
    {id:"toga_sai_p2d",nom:"Kioku Fuyo",kanji:"\u8A18\u61B6\u4ED8\u4E0E",p:2,c:2,desc:"L'Imposition de M\u00E9moires. Le Togabito projette ses souvenirs de mort sur l'ennemi.",prereqIds:["toga_sai_p1b","toga_sai_p1c"],cond:null,rangMin:null},
    {id:"toga_sai_p3a",nom:"Fushi no Kusari",kanji:"\u4E0D\u6B7B\u9396",p:3,c:3,desc:"L'Immortalit\u00E9 Encha\u00EEn\u00E9e. Le corps devient un n\u0153ud dans le tissu de l'Enfer, un point fixe indestructible.",prereqIds:["toga_sai_p2a","toga_sai_p2b"],cond:"Mort et r\u00E9surrection RP en Enfer valid\u00E9e par le staff.",rangMin:"ko_togabito"},
    {id:"toga_sai_p3b",nom:"Rinsai Tensei",kanji:"\u8F2A\u969B\u8EE2\u751F",p:3,c:3,desc:"La Transmigration Ultime. Le Togabito meurt volontairement et rena\u00EEt transform\u00E9 quelques secondes plus tard.",prereqIds:["toga_sai_p2c","toga_sai_p2d"],cond:"Arc RP de confrontation avec la nature cyclique de l'Enfer.",rangMin:"gokuo"}
  ]},
  // ── Rinki ──
  {id:"toga_rinki",nom:"Rinki",kanji:"\u71D0\u6C17",sousTitre:"L'Aura Phosphorescente",
   desc:"Le Jigoku no Rinki est un poison pour la plupart. Les anciens Togabito l'ont domin\u00E9.",
   apt:[
    {id:"toga_rin_p1a",nom:"Rinki Kanchi",kanji:"\u71D0\u6C17\u611F\u77E5",p:1,c:1,desc:"Perception du Rinki. Un sixi\u00E8me sens d\u00E9tectant les concentrations de Reishi infernal.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_rin_p1b",nom:"Rinki Gaiheki",kanji:"\u71D0\u6C17\u5916\u58C1",p:1,c:1,desc:"Le Mur Phosphorescent. Une barri\u00E8re de Rinki repoussant les attaques spirituelles faibles.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_rin_p1c",nom:"Rinki Ky\u016Bsh\u016B",kanji:"\u71D0\u6C17\u5438\u53CE",p:1,c:1,desc:"L'Absorption du Rinki. Aspirer le Reishi infernal ambiant comme source de puissance.",prereqIds:[],cond:null,rangMin:null},
    {id:"toga_rin_p2a",nom:"Rinki H\u014Dsha",kanji:"\u71D0\u6C17\u653E\u5C04",p:2,c:2,desc:"La Radiation Phosphorescente. Des ondes concentriques corrompant le Reishi ambiant.",prereqIds:["toga_rin_p1a"],cond:null,rangMin:null},
    {id:"toga_rin_p2b",nom:"Rinki Osen",kanji:"\u71D0\u6C17\u6C5A\u67D3",p:2,c:2,desc:"La Contamination. Le Togabito injecte du Rinki dans le corps de la cible.",prereqIds:["toga_rin_p1b"],cond:null,rangMin:null},
    {id:"toga_rin_p2c",nom:"Rinki Yoroi",kanji:"\u71D0\u6C17\u93A7",p:2,c:2,desc:"L'Armure de Rinki. Le Reishi infernal cristallis\u00E9 en carapace corrosive.",prereqIds:["toga_rin_p1b","toga_rin_p1c"],cond:null,rangMin:null},
    {id:"toga_rin_p3a",nom:"Jigoku Kaih\u014D",kanji:"\u5730\u7344\u89E3\u653E",p:3,c:3,desc:"Le Togabito cesse de r\u00E9sister \u00E0 l'Enfer. Il l'invite. La chair se reconfigure.",prereqIds:["toga_rin_p2a","toga_rin_p2b"],cond:"Arc RP de confrontation avec les Strates profondes.",rangMin:"ko_togabito"},
    {id:"toga_rin_p3b",nom:"Jigoku Osen Kai",kanji:"\u5730\u7344\u6C5A\u67D3\u754C",p:3,c:3,desc:"Le Monde de Corruption Infernale. Tout le Reishi dans un vaste p\u00E9rim\u00E8tre se corrompt.",prereqIds:["toga_rin_p2a","toga_rin_p2c"],cond:"Arc RP de domination totale du Rinki.",rangMin:"gokuo"}
  ]}
]},

// ─────────────────────────────────────────────────────────────────────────────
//  ARRANCAR
// ─────────────────────────────────────────────────────────────────────────────
arrancar: {
  nom:"Arrancar", kanji:"\u7834\u9762", couleur:"#8A8A7A",
  accroche:"Mi-Hollow, mi-humain \u2014 les Arrancar ont arrach\u00E9 leurs masques pour toucher la puissance.",
  voies:[
  // ── Cero ──
  {id:"arr_cero",nom:"Cero",kanji:"\u865A\u9583",sousTitre:"L'\u00C9clair du Vide",
   desc:"Le Cero est la voix du Hollow \u2014 un cri de puissance concentr\u00E9 en lumi\u00E8re destructrice.",
   apt:[
    {id:"arr_cer_p1a",nom:"Cero",kanji:"\u865A\u9583",p:1,c:1,desc:"Le rayon de destruction fondamental. Une d\u00E9charge de Reishi concentr\u00E9 tir\u00E9e depuis la paume, la bouche ou les doigts.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_cer_p1b",nom:"Bala",kanji:"\u865A\u5F3E",p:1,c:1,desc:"La Balle du Vide. Un projectile \u00E0 vingt fois la vitesse d'un Cero, au prix d'une puissance r\u00E9duite.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_cer_p1c",nom:"Cero Preparado",kanji:"\u865A\u9583\u5099",p:1,c:1,desc:"Le Cero Pr\u00E9par\u00E9. L'Arrancar charge un Cero et le retient, pr\u00EAt \u00E0 \u00EAtre lib\u00E9r\u00E9 au moment optimal.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_cer_p2a",nom:"Gran Rey Cero",kanji:"\u738B\u865A\u306E\u9583\u5149",p:2,c:2,desc:"L'\u00C9clair Royal du Vide. Le Cero m\u00EAl\u00E9 au sang de l'Arrancar, une spirale de destruction.",prereqIds:["arr_cer_p1a"],cond:null,rangMin:null},
    {id:"arr_cer_p2b",nom:"Cero Oscuras",kanji:"\u9ED2\u865A\u9583",p:2,c:2,desc:"Le Cero des T\u00E9n\u00E8bres. Un faisceau noir d'une puissance capable d'\u00E9branler les barri\u00E8res de Kid\u014D.",prereqIds:["arr_cer_p1b"],cond:null,rangMin:null},
    {id:"arr_cer_p2c",nom:"Cero Doble",kanji:"\u865A\u9583\u4E8C\u91CD",p:2,c:2,desc:"Le Cero Double. Absorber le Cero adverse et le fusionner avec le sien avant de le renvoyer doubl\u00E9.",prereqIds:["arr_cer_p1a","arr_cer_p1c"],cond:null,rangMin:null},
    {id:"arr_cer_p3a",nom:"Cero Metralleta",kanji:"\u7121\u9650\u865A\u9583",p:3,c:3,desc:"La Mitrailleuse du Vide. Des centaines de Cero tir\u00E9s simultan\u00E9ment.",prereqIds:["arr_cer_p2a","arr_cer_p2b"],cond:"D\u00E9monstration de puissance Cero valid\u00E9e en combat RP.",rangMin:"privaron_espada"},
    {id:"arr_cer_p3b",nom:"Cero Sincr\u00E9tico",kanji:"\u865A\u9583\u878D\u5408",p:3,c:3,desc:"Le Cero Syncr\u00E9tique. Fusion de tous les types de Cero en un seul tir d\u00E9vastateur.",prereqIds:["arr_cer_p2a","arr_cer_p2c"],cond:"Arc RP de transcendance de la nature Cero.",rangMin:"espada"}
  ]},
  // ── Hierro ──
  {id:"arr_hierro",nom:"Hierro",kanji:"\u92FC\u76AE",sousTitre:"La Peau d'Acier",
   desc:"La peau d'un Arrancar n'est pas de la peau \u2014 c'est du Reishi condens\u00E9 jusqu'\u00E0 la densit\u00E9 du m\u00E9tal.",
   apt:[
    {id:"arr_hie_p1a",nom:"Hierro",kanji:"\u92FC\u76AE",p:1,c:1,desc:"La Peau d'Acier. Le Reishi se condense autour du corps en une couche invisible repoussant les attaques.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_hie_p1b",nom:"Pesquisa",kanji:"\u63A2\u67FB\u56DE\u8DEF",p:1,c:1,desc:"Le Circuit de D\u00E9tection. Un sonar spirituel cartographiant les sources de Reishi.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_hie_p1c",nom:"Hierro Garra",kanji:"\u92FC\u722A",p:1,c:1,desc:"Les Griffes d'Acier. Le Reishi se concentre aux extr\u00E9mit\u00E9s \u2014 les doigts deviennent des lames.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_hie_p2a",nom:"Hierro Ky\u014Dka",kanji:"\u92FC\u76AE\u5F37\u5316",p:2,c:2,desc:"Le Hierro Renforc\u00E9. M\u00EAme les lames de Capitaine laissent \u00E0 peine une \u00E9raflure.",prereqIds:["arr_hie_p1a"],cond:null,rangMin:null},
    {id:"arr_hie_p2b",nom:"Negaci\u00F3n",kanji:"\u5426\u5B9A",p:2,c:2,desc:"Le Champ de N\u00E9gation. Un pilier de lumi\u00E8re cr\u00E9ant un espace inviolable.",prereqIds:["arr_hie_p1b"],cond:null,rangMin:null},
    {id:"arr_hie_p2c",nom:"Hierro Kaeshi",kanji:"\u92FC\u76AE\u8FD4\u3057",p:2,c:2,desc:"Le Renvoi du Hierro. L'\u00E9nergie cin\u00E9tique de l'attaque est renvoy\u00E9e vers l'assaillant.",prereqIds:["arr_hie_p1a","arr_hie_p1c"],cond:null,rangMin:null},
    {id:"arr_hie_p3a",nom:"K\u014Dsoku Saisei",kanji:"\u9AD8\u901F\u518D\u751F",p:3,c:3,desc:"La R\u00E9g\u00E9n\u00E9ration Ultra-Rapide. Les membres sectionn\u00E9s repoussent en secondes.",prereqIds:["arr_hie_p2a","arr_hie_p2b"],cond:"Arc RP de reconnexion avec l'instinct Hollow originel.",rangMin:"privaron_espada"},
    {id:"arr_hie_p3b",nom:"Hierro Tenshi",kanji:"\u92FC\u76AE\u5929\u81F3",p:3,c:3,desc:"Le Hierro Absolu. La densit\u00E9 du Reishi dans la peau atteint un niveau impossible \u00E0 percer.",prereqIds:["arr_hie_p2a","arr_hie_p2c"],cond:"Arc RP de transcendance d\u00E9fensive valid\u00E9.",rangMin:"espada"}
  ]},
  // ── Son\u00EDdo ──
  {id:"arr_sonido",nom:"Son\u00EDdo",kanji:"\u97FF\u8EE2",sousTitre:"Le Pas R\u00E9sonnant",
   desc:"L\u00E0 o\u00F9 le Shunpo est silence et pr\u00E9cision, le Son\u00EDdo est tonnerre et instinct.",
   apt:[
    {id:"arr_son_p1a",nom:"Son\u00EDdo",kanji:"\u97FF\u8EE2",p:1,c:1,desc:"Le Pas R\u00E9sonnant. D\u00E9placement instantan\u00E9 accompagn\u00E9 d'un bruit sourd caract\u00E9ristique.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_son_p1b",nom:"Garganta",kanji:"\u9ED2\u8154",p:1,c:1,desc:"La Gorge Noire. D\u00E9chirer le tissu de la r\u00E9alit\u00E9 pour ouvrir un passage entre les mondes.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_son_p1c",nom:"Yobigoe",kanji:"\u547C\u58F0",p:1,c:1,desc:"Le Cri d'Appel. Un rugissement charg\u00E9 de Reishi d\u00E9stabilisant les sens de l'adversaire.",prereqIds:[],cond:null,rangMin:null},
    {id:"arr_son_p2a",nom:"Gemelos Son\u00EDdo",kanji:"\u53CC\u5150\u97FF\u8EE2",p:2,c:2,desc:"Le Son\u00EDdo Jumeau. La vitesse laisse derri\u00E8re lui un v\u00E9ritable clone de Reishi.",prereqIds:["arr_son_p1a"],cond:null,rangMin:null},
    {id:"arr_son_p2b",nom:"Gonzui",kanji:"\u9B42\u5438",p:2,c:2,desc:"L'Aspiration des \u00C2mes. Inhaler le Reishi ambiant et les \u00E2mes faibles pour se restaurer.",prereqIds:["arr_son_p1b"],cond:null,rangMin:null},
    {id:"arr_son_p2c",nom:"Chokkaku Son\u00EDdo",kanji:"\u76F4\u899A\u97FF\u8EE2",p:2,c:2,desc:"Le Son\u00EDdo Instinctif. Le corps bouge avant la pens\u00E9e, guid\u00E9 par l'instinct de pr\u00E9dateur.",prereqIds:["arr_son_p1a","arr_son_p1c"],cond:null,rangMin:null},
    {id:"arr_son_p3a",nom:"Gran Ca\u00EDda",kanji:"\u5927\u843D\u4E0B",p:3,c:3,desc:"La Grande Chute. Descente verticale d'une vitesse et puissance apocalyptiques.",prereqIds:["arr_son_p2a","arr_son_p2b"],cond:"Arc RP de transcendance de ses limites physiques.",rangMin:"privaron_espada"},
    {id:"arr_son_p3b",nom:"Depredador",kanji:"\u6355\u98DF\u8E0F\u7834",p:3,c:3,desc:"Le Pr\u00E9dateur. Chasse implacable \u00E0 travers les dimensions. Fuir est futile.",prereqIds:["arr_son_p2a","arr_son_p2c"],cond:"Arc RP de chasse transcendant les limites dimensionnelles.",rangMin:"espada"}
  ]},
  // ── Resurrecci\u00F3n ──
  {id:"arr_resurreccion",nom:"Resurrecci\u00F3n",kanji:"\u5E30\u5203",sousTitre:"Le Retour de la Lame",
   desc:"Le Zanpakut\u014D d'un Arrancar est un sceau. La Resurrecci\u00F3n brise ce sceau.",
   apt:[
    {id:"arr_res_p1a",nom:"F\u016Bin J\u014Dtai",kanji:"\u5C01\u5370\u72B6\u614B",p:1,c:1,desc:"L'\u00C9tat Scell\u00E9. Ma\u00EEtrise consciente du sceau du Zanpakut\u014D.",prereqIds:[],cond:null,rangMin:"numeros"},
    {id:"arr_res_p1b",nom:"Instinto",kanji:"\u672C\u80FD",p:1,c:1,desc:"L'Instinct. Le souvenir du Hollow affleure \u2014 r\u00E9flexes surhumains.",prereqIds:[],cond:null,rangMin:"numeros"},
    {id:"arr_res_p1c",nom:"Zanpakut\u014D Ky\u014Dmei",kanji:"\u65AC\u9B44\u5171\u9CF4",p:1,c:1,desc:"La R\u00E9sonance du Zanpakut\u014D. Dialogue silencieux avec le Hollow scell\u00E9.",prereqIds:[],cond:null,rangMin:"numeros"},
    {id:"arr_res_p2a",nom:"Tokusei",kanji:"\u5E30\u5203\u7279\u6027",p:2,c:2,desc:"La Propri\u00E9t\u00E9 Unique. Capacit\u00E9 sp\u00E9ciale de la Resurrecci\u00F3n du Hollow.",prereqIds:["arr_res_p1b"],cond:null,rangMin:"numeros"},
    {id:"arr_res_p2b",nom:"Kaih\u014D no Kehai",kanji:"\u89E3\u653E\u306E\u6C17\u914D",p:2,c:2,desc:"Le Signe de la Lib\u00E9ration. Manifestation partielle de la Resurrecci\u00F3n.",prereqIds:["arr_res_p1a","arr_res_p1c"],cond:null,rangMin:"numeros"},
    {id:"arr_res_p2c",nom:"Honn\u014D Kakusei",kanji:"\u672C\u80FD\u899A\u9192",p:2,c:2,desc:"L'\u00C9veil Instinctif. Le corps puise dans la m\u00E9moire de l'esp\u00E8ce Hollow.",prereqIds:["arr_res_p1b","arr_res_p1c"],cond:null,rangMin:"numeros"},
    {id:"arr_res_p3a",nom:"Resurrecci\u00F3n",kanji:"\u5E30\u5203",p:3,c:3,desc:"La commande est prononc\u00E9e. Le Zanpakut\u014D se dissout et fusionne avec l'Arrancar.",prereqIds:["arr_res_p2a","arr_res_p2b"],cond:"Sc\u00E8ne RP de lib\u00E9ration \u00E9motionnelle intense.",rangMin:"privaron_espada"},
    {id:"arr_res_p3b",nom:"Segunda Etapa",kanji:"\u5203\u5E30\u4E8C\u6BB5",p:3,c:3,desc:"La Seconde Phase. Au-del\u00E0 de la Resurrecci\u00F3n \u2014 une lib\u00E9ration de la lib\u00E9ration.",prereqIds:["arr_res_p3a","arr_res_p2c"],cond:"Arc RP de transcendance int\u00E9rieure valid\u00E9 par le staff.",rangMin:"espada"}
  ]}
]},

// ─────────────────────────────────────────────────────────────────────────────
//  QUINCY
// ─────────────────────────────────────────────────────────────────────────────
quincy: {
  nom:"Quincy", kanji:"\u6EC5\u5374\u5E2B", couleur:"#1A3A6B",
  accroche:"Les derniers h\u00E9ritiers d'un sang sacr\u00E9 \u2014 les Quincy ne canalisent pas le Reishi, ils le commandent.",
  voies:[
  // ── Reishi S\u014Dsa ──
  {id:"quin_reishi",nom:"Reishi S\u014Dsa",kanji:"\u970A\u5B50\u64CD\u4F5C",sousTitre:"La Manipulation des Particules",
   desc:"Les Quincy absorbent les particules spirituelles de l'environnement et les reconfigurent selon leur volont\u00E9.",
   apt:[
    {id:"quin_rei_p1a",nom:"Reishi Sh\u016Bsh\u016B",kanji:"\u970A\u5B50\u53CE\u96C6",p:1,c:1,desc:"La Collecte du Reishi. Tirer les particules spirituelles de l'environnement.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_rei_p1b",nom:"Heilig Pfeil",kanji:"\u795E\u8056\u6EC5\u77E2",p:1,c:1,desc:"La Fl\u00E8che Sacr\u00E9e. Un projectile de lumi\u00E8re bleue tir\u00E9 depuis l'arc spirituel.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_rei_p1c",nom:"Reishi K\u014Dchiku",kanji:"\u970A\u5B50\u69CB\u7BC9",p:1,c:1,desc:"La Construction de Reishi. Donner forme aux particules \u2014 plateformes, marches, structures.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_rei_p2a",nom:"Reishi Bus\u014D",kanji:"\u970A\u5B50\u6B66\u88C5",p:2,c:2,desc:"L'Armement de Reishi. Fa\u00E7onner le Reishi en armes de toute forme.",prereqIds:["quin_rei_p1a","quin_rei_p1c"],cond:null,rangMin:null},
    {id:"quin_rei_p2b",nom:"Gint\u014D Kiso",kanji:"\u9280\u7B52\u57FA\u790E",p:2,c:2,desc:"Les Fondamentaux du Gint\u014D. Heizen, Gritz, Wolke \u2014 les tubes d'argent emplis de Reishi.",prereqIds:["quin_rei_p1b"],cond:null,rangMin:null},
    {id:"quin_rei_p2c",nom:"Gint\u014D Senryaku",kanji:"\u9280\u7B52\u6226\u7565",p:2,c:2,desc:"Le Gint\u014D Strat\u00E9gique. Combiner les tubes en r\u00E9seaux tactiques.",prereqIds:["quin_rei_p2b"],cond:null,rangMin:null},
    {id:"quin_rei_p3a",nom:"Rans\u014Dtengai",kanji:"\u4E71\u88C5\u5929\u5080",p:3,c:3,desc:"La Marionnette C\u00E9leste. Des fils de Reishi animent les membres ind\u00E9pendamment du corps.",prereqIds:["quin_rei_p2a","quin_rei_p2b"],cond:"Arc RP de d\u00E9passement physique face \u00E0 une adversit\u00E9 \u00E9crasante.",rangMin:"sternritter"},
    {id:"quin_rei_p3b",nom:"Gint\u014D Meister",kanji:"\u9280\u7B52\u6975\u610F",p:3,c:3,desc:"La Ma\u00EEtrise Absolue du Gint\u014D. Cr\u00E9ations de Reishi liquide d'une complexit\u00E9 in\u00E9dite.",prereqIds:["quin_rei_p2c","quin_rei_p2a"],cond:"Arc RP de ma\u00EEtrise strat\u00E9gique du Gint\u014D valid\u00E9.",rangMin:"sternritter"}
  ]},
  // ── Blut ──
  {id:"quin_blut",nom:"Blut",kanji:"\u8840\u88C5",sousTitre:"La Fortification du Sang",
   desc:"Le Reishi coule dans les veines des Quincy comme un second sang. Le Blut renforce le corps \u2014 en d\u00E9fense ou en attaque.",
   apt:[
    {id:"quin_blu_p1a",nom:"Blut Vene",kanji:"\u9759\u8840\u88C5",p:1,c:1,desc:"La Veine Statique. Le Reishi durcit le corps de l'int\u00E9rieur, rivalisant avec le Hierro.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_blu_p1b",nom:"Blut Arterie",kanji:"\u52D5\u8840\u88C5",p:1,c:1,desc:"L'Art\u00E8re Dynamique. Le flux amplifie les coups port\u00E9s, au prix de la vuln\u00E9rabilit\u00E9.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_blu_p1c",nom:"Blut Konro",kanji:"\u8840\u88C5\u6839\u8DEF",p:1,c:1,desc:"La Voie Radiculaire. Contr\u00F4le des flux de Reishi dans le syst\u00E8me sanguin.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_blu_p2a",nom:"Blut Anhaben",kanji:"\u8840\u88C5\u5916\u6BBB",p:2,c:2,desc:"La Coque de Sang. Le Blut Vene s'\u00E9tend au-del\u00E0 du corps en bulle de protection.",prereqIds:["quin_blu_p1a"],cond:null,rangMin:null},
    {id:"quin_blu_p2b",nom:"Blut Wechsel",kanji:"\u8840\u88C5\u8EE2\u63DB",p:2,c:2,desc:"La Conversion instantan\u00E9e entre Vene et Arterie.",prereqIds:["quin_blu_p1b","quin_blu_p1c"],cond:null,rangMin:null},
    {id:"quin_blu_p2c",nom:"Blut Erweiterung",kanji:"\u8840\u88C5\u62E1\u5F35",p:2,c:2,desc:"L'Extension du Blut aux alli\u00E9s proches ou aux armes tenues.",prereqIds:["quin_blu_p1a","quin_blu_p1c"],cond:null,rangMin:null},
    {id:"quin_blu_p3a",nom:"Blut Vereint",kanji:"\u8840\u88C5\u7D71\u4E00",p:3,c:3,desc:"Le Sang Unifi\u00E9. Vene et Arterie coexistent \u2014 puissance et d\u00E9fense maximales simultan\u00E9ment.",prereqIds:["quin_blu_p2a","quin_blu_p2b"],cond:"Arc RP de ma\u00EEtrise absolue du Blut valid\u00E9.",rangMin:"sternritter"},
    {id:"quin_blu_p3b",nom:"Blut Allerh\u00F6chst",kanji:"\u8840\u88C5\u81F3\u9AD8",p:3,c:3,desc:"Le Blut Supr\u00EAme. Le Reishi sanguin transcende les limites biologiques.",prereqIds:["quin_blu_p3a","quin_blu_p2c"],cond:"Arc RP de transcendance de l'h\u00E9ritage sanguin Quincy.",rangMin:"schutzstaffel"}
  ]},
  // ── Hirenkyaku ──
  {id:"quin_hirenkyaku",nom:"Hirenkyaku",kanji:"\u98DB\u5EC9\u811A",sousTitre:"Le Pas du Dieu du Vent",
   desc:"Les Quincy glissent sur des courants de Reishi qu'ils cr\u00E9ent sous leurs pieds.",
   apt:[
    {id:"quin_hir_p1a",nom:"Hirenkyaku",kanji:"\u98DB\u5EC9\u811A",p:1,c:1,desc:"Le d\u00E9placement \u00E0 haute vitesse des Quincy. Surfant sur une plateforme de Reishi.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_hir_p1b",nom:"Schatten",kanji:"\u5F71",p:1,c:1,desc:"L'Ombre. Dissolution dans les ombres et r\u00E9apparition \u00E0 un autre point.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_hir_p1c",nom:"Reishi Ashiba",kanji:"\u970A\u5B50\u8DB3\u5834",p:1,c:1,desc:"Les Plateformes de Reishi. Points d'appui solides dans le vide.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_hir_p2a",nom:"Kirchenlied",kanji:"\u8056\u5531",p:2,c:2,desc:"Le Chant de l'\u00C9glise. D\u00E9placement offensif via un pentacle de Reishi.",prereqIds:["quin_hir_p1a"],cond:null,rangMin:null},
    {id:"quin_hir_p2b",nom:"Sprenger",kanji:"\u7206\u6563",p:2,c:2,desc:"L'Explosion. Cinq Seele Schneider formant un pentacle d\u00E9vastateur.",prereqIds:["quin_hir_p1b"],cond:null,rangMin:null},
    {id:"quin_hir_p2c",nom:"Licht Spur",kanji:"\u5149\u306E\u8ECC\u8DE1",p:2,c:2,desc:"La Tra\u00EEn\u00E9e de Lumi\u00E8re. Sillage de Reishi solidifi\u00E9 laiss\u00E9 derri\u00E8re soi.",prereqIds:["quin_hir_p1a","quin_hir_p1c"],cond:null,rangMin:null},
    {id:"quin_hir_p3a",nom:"Licht Regen",kanji:"\u5149\u306E\u96E8",p:3,c:3,desc:"La Pluie de Lumi\u00E8re. Des milliers de fl\u00E8ches s'abattant sur une zone enti\u00E8re.",prereqIds:["quin_hir_p2a","quin_hir_p2b"],cond:"Ma\u00EEtrise RP d\u00E9montr\u00E9e du tir en volume valid\u00E9e.",rangMin:"sternritter"},
    {id:"quin_hir_p3b",nom:"Raumverschiebung",kanji:"\u7A7A\u9593\u8EE2\u79FB",p:3,c:3,desc:"Le D\u00E9placement Spatial. T\u00E9l\u00E9portation pure par manipulation du Reishi.",prereqIds:["quin_hir_p2b","quin_hir_p2c"],cond:"Arc RP de transcendance spatiale du Hirenkyaku.",rangMin:"sternritter"}
  ]},
  // ── Seikei ──
  {id:"quin_seikei",nom:"Seikei",kanji:"\u8056\u4F53",sousTitre:"Le Corps Sacr\u00E9",
   desc:"Le corps du Quincy est un temple forg\u00E9 par des g\u00E9n\u00E9rations d'h\u00E9ritage spirituel.",
   apt:[
    {id:"quin_sei_p1a",nom:"Quincy Kreuz",kanji:"\u6EC5\u5374\u5341\u5B57",p:1,c:1,desc:"La Croix de la Destruction. L'artefact fondamental canalisant le Reishi.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_sei_p1b",nom:"Seele Schneider",kanji:"\u9B42\u5207",p:1,c:1,desc:"Le Trancheur d'\u00C2mes. Lame de Reishi vibrant \u00E0 haute fr\u00E9quence.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_sei_p1c",nom:"Reishi Keitai",kanji:"\u970A\u5B50\u5F62\u614B",p:1,c:1,desc:"La Forme du Reishi. Alt\u00E9rer la forme de l'arme spirituelle \u2014 arc, arbal\u00E8te, \u00E9p\u00E9e de lumi\u00E8re.",prereqIds:[],cond:null,rangMin:null},
    {id:"quin_sei_p2a",nom:"Sklaverei",kanji:"\u8056\u96B7",p:2,c:2,desc:"L'Esclavage Sacr\u00E9. Arracher le Reishi des structures environnantes.",prereqIds:["quin_sei_p1a"],cond:null,rangMin:null},
    {id:"quin_sei_p2b",nom:"Seishi Ky\u014Dka",kanji:"\u8056\u77E2\u5F37\u5316",p:2,c:2,desc:"Le Renforcement des Fl\u00E8ches Sacr\u00E9es. Multiplication et guidage des projectiles.",prereqIds:["quin_sei_p1b","quin_sei_p1c"],cond:null,rangMin:null},
    {id:"quin_sei_p2c",nom:"Seirei Kaih\u014D",kanji:"\u8056\u970A\u89E3\u653E",p:2,c:2,desc:"La Lib\u00E9ration de l'Esprit Sacr\u00E9. Pr\u00E9mices du Corps Sacr\u00E9 \u2014 ailes, halo, aura.",prereqIds:["quin_sei_p1a","quin_sei_p1c"],cond:null,rangMin:null},
    {id:"quin_sei_p3a",nom:"Vollst\u00E4ndig",kanji:"\u5B8C\u8056\u4F53",p:3,c:3,desc:"Le Corps Sacr\u00E9 Complet. Ailes de lumi\u00E8re, halo divin, le Quincy transcende les limites humaines.",prereqIds:["quin_sei_p2a","quin_sei_p2c"],cond:"\u00C9preuve RP d\u00E9montrant la foi et la d\u00E9termination du Quincy.",rangMin:"sternritter"},
    {id:"quin_sei_p3b",nom:"Schrift",kanji:"\u8056\u6587\u5B57",p:3,c:3,desc:"La Lettre Sacr\u00E9e. Une capacit\u00E9 unique grav\u00E9e dans l'\u00E2me du Quincy.",prereqIds:["quin_sei_p3a","quin_sei_p2b"],cond:"Arc RP de r\u00E9v\u00E9lation de la Lettre Sacr\u00E9e valid\u00E9 par le staff.",rangMin:"sternritter"}
  ]}
]}

};
