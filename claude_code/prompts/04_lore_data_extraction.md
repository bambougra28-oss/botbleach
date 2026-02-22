# TÂCHE 04 — Enrichir LORE_DATA dans lore.py

**Priorité : MOYENNE**  
**Fichier à modifier : `cogs/lore.py`**

---

## Problème

`LORE_DATA` est actuellement défini **inline** dans la commande `/lore` (environ ligne 216).  
Cela signifie que le dictionnaire est recréé à chaque appel de la commande.  
Et surtout, il est inaccessible depuis `construction.py` pour la tâche 01.

De plus, le contenu de certaines sections est partiel ou trop court pour un vrai serveur RP.

---

## Objectif

1. **Extraire `LORE_DATA` au niveau du module** (hors de la fonction) pour qu'il soit importable
2. **Enrichir chaque section** avec un contenu narratif complet
3. **Mettre à jour la commande `/lore`** pour utiliser le dictionnaire extrait

---

## Nouvelle structure de LORE_DATA

`LORE_DATA` doit être défini **avant la classe `Lore`**, au même niveau que `GLOSSAIRE` et `FICHES_FACTION`.

### Format attendu pour chaque entrée

```python
LORE_DATA = {
    "origine": {
        "titre":       "🌊 La Mer Primordiale & le Péché Originel",
        "couleur_cle": "or_ancien",   # clé dans config.COULEURS
        "description": "Texte principal (max 800 chars)",
        "fields": [
            ("Nom du champ", "Contenu du champ (max 800 chars)"),
            ...
        ],
    },
    "fissure":      { ... },
    "reio":         { ... },
    "division_zero":{ ... },
    "konso_reisai": { ... },
    "systeme":      { ... },
}
```

---

## Contenu enrichi à rédiger pour chaque section

### origine — La Mer Primordiale & le Péché Originel

```
Description :
Avant les Trois Mondes, il n'y avait que la Mer Primordiale — un chaos de Reishi brut,
informe, intemporel. Nulle loi. Nulle structure. Une puissance pure sans direction.

Le Péché Originel est l'acte fondateur : un être issu de ce chaos a voulu donner
une forme au néant. En structurant la Mer Primordiale, il a créé l'ordre — et par
contraste, a inventé le désordre. Soul Society, Hueco Mundo, le Monde des Vivants :
trois fragments d'un tout qui ne devait jamais être divisé.

Fields :
  La Mer Primordiale | Réservoir infini de Reishi dont tous les êtres spirituels
                       sont issus. Accessible uniquement en Enfer, aux Strates profondes.
                       Certains Togabito anciens rapportent l'avoir perçue.

  Le Premier Crime | L'acte de structuration a laissé un résidu — une "cassure"
                     dans la logique cosmique. L'Enfer en est la conséquence directe :
                     le dépôt de ce qui ne peut pas être intégré dans l'ordre.

  Conséquences actuelles | La Fissure suggère que la cassure s'élargit.
                           Le Péché Originel n'était peut-être pas un acte — mais un état permanent.
```

### fissure — La Fissure

```
Description :
Une anomalie spatiale d'origine inconnue qui relie l'Enfer aux Trois Mondes.
Apparue sans prévenir. Sans cause identifiée. Sans précédent dans les archives du Gotei.

Fields :
  Manifestation | Fissures visibles dans le tissu spirituel, sphères noires
                  de Jigoku no Rinki qui débordent. Augmentation des apparitions
                  de Hollow anormaux dans le Monde des Vivants.

  Théories | Effondrement naturel du verrou que représente le Reiō depuis sa mutilation.
             Acte délibéré d'une entité inconnue. Conséquence de la mort de Yhwach.
             Les avis divergent — le Gotei 13 n'a pas de consensus.

  Impact sur les factions | Shinigami : déstabilisation doctrinale. Togabito : espoir
                             d'évasion ou de transformation. Arrancar : résonance
                             physique avec leur trou identitaire. Quincy : lecture
                             de la contamination comme un signal dirigé.

  Niveau actuel | Variable. Consulter #📌・etat-de-la-fissure pour l'état en temps réel.
```

### reio — Le Reiō

```
Description :
Le Roi des Âmes. Verrou cosmique maintenant les Trois Mondes séparés.
Mutilé et scellé dans un cristal au Palais Royal par les Cinq Grandes Maisons.
Sa mutilation n'est pas un accident — c'est le fondement de l'ordre actuel.

Fields :
  La Mutilation | Ses membres ont été prélevés et sont devenus des entités indépendantes :
                  Mimihagi (bras droit), Pernida (bras gauche), et d'autres non identifiés.
                  Chaque membre séparé porte une fraction de sa conscience.

  Le Verrou | Tant que le Reiō existe, les Trois Mondes restent distincts.
              Sa mort provoque leur effondrement — Yhwach l'a prouvé temporairement.
              La Fissure suggère que le verrou fonctionne de moins en moins bien.

  Ce que personne ne dit | La mutilation a été choisie. Pas subie. Le Reiō a accepté
                            de devenir un outil. Pourquoi ? Les archives royales sont scellées.
```

### division_zero — La Division Zéro

```
Description :
Garde Royale du Palais Royal. Cinq Shinigami d'une puissance dépassant les Capitaines.
Chacun a apporté une contribution fondamentale à Soul Society — une chose qui définit
désormais la vie de tous les Shinigami sans exception.

Fields :
  Membres connus | Ichibē Hyōsube (les noms et leurs pouvoirs), Ōetsu Nimaiya (les Zanpakutō),
                   Kirio Hikifune (la nourriture spirituelle), Senjumaru Shutara (les vêtements),
                   Tenjirō Kirinji (les bains de guérison).

  Rôle actuel | En théorie : protéger le Reiō. En pratique : observer la Fissure
                depuis le Palais Royal et décider si une intervention est nécessaire.
                Aucune intervention annoncée à ce jour.

  Rapport à l'Enfer | La Division Zéro sait que le Konsō Reisai envoie des Capitaines en Enfer.
                       Leur silence sur ce sujet est interprété comme un accord tacite.
                       Certains pensent qu'ils y contribuent activement.
```

### konso_reisai — Le Konsō Reisai

```
Description :
Rituel secret transmis depuis la fondation du Gotei 13. À la mort d'un Capitaine,
son âme est envoyée en Enfer plutôt qu'à Soul Society — officiellement "pour renforcer
les barrières infernales". La vérité est connue du seul Capitaine-Commandant.

Fields :
  La Révélation | Le secret a éclaté lors de la dernière confrontation à l'Enfer.
                  Les Capitaines actuels savent. Les Vice-Capitaines commencent à apprendre.
                  Les rangs inférieurs n'ont pas encore été informés officiellement.

  Les implications | Des centaines de Capitaines décédés depuis des millénaires
                     se trouvent dans les Strates. Certains y ont évolué en entités
                     d'une puissance équivalente aux Togabito les plus anciens.

  La question | Étaient-ils envoyés pour "renforcer les barrières" ou pour être
                 emprisonnés ? Y a-t-il une différence ? Et si certains le savaient
                 avant de mourir — et ont accepté ?
```

### systeme — Système de Combat & Points

```
Description :
Le système de progression d'Infernum Aeterna reflète l'évolution narrative
de votre personnage — pas seulement ses victoires en combat.

Fields :
  Obtenir des points | Participation active au RP (scènes écrites, arcs narratifs),
                        victoires en combat (/clore-combat), contributions lore validées
                        par le staff, événements serveur. Points attribués par le staff via
                        /points-ajouter.

  Montée en rang | Automatique à chaque seuil franchi. Le staff est notifié.
                    Déclenche une narration épique dans #journal-de-l-enfer.
                    Nouveaux rôles et accès aux zones plus profondes débloqués.

  Aptitudes | À chaque rang, vous pouvez décrire de nouvelles aptitudes dans votre fiche.
               Le nombre maximum dépend du rang. Toute aptitude hors-norme doit être
               validée par le staff avant usage en RP.

  Mort narrative | Possible avec accord des deux joueurs + validation staff.
                    Le personnage peut "mourir" narrativement et renaître avec un nouveau
                    contexte, ou rejouer depuis le début avec ses acquis lore.
```

---

## Mise à jour de la commande /lore

Après extraction de `LORE_DATA` au niveau module, la commande `/lore` doit utiliser :

```python
@app_commands.command(name="lore", description="Résumé d'une faction, zone ou concept du lore.")
async def lore_cmd(self, interaction: discord.Interaction, sujet: str):
    data = LORE_DATA.get(sujet, LORE_DATA["origine"])
    couleur = COULEURS.get(data["couleur_cle"], COULEURS["or_ancien"])
    embed = discord.Embed(
        title=data["titre"],
        description=data["description"],
        color=couleur
    )
    for nom_champ, valeur_champ in data.get("fields", []):
        embed.add_field(name=nom_champ, value=valeur_champ, inline=False)
    embed.set_footer(text="⸻ Infernum Aeterna · Chroniques ⸻")
    await interaction.response.send_message(embed=embed)
```

---

## Validation

- [ ] `LORE_DATA` défini au niveau module (importable depuis construction.py)
- [ ] 6 sections présentes : origine, fissure, reio, division_zero, konso_reisai, systeme
- [ ] `/lore` fonctionne toujours pour chaque valeur
- [ ] Aucune section > 4096 chars au total (description + fields)
- [ ] `from cogs.lore import LORE_DATA` fonctionne sans erreur
