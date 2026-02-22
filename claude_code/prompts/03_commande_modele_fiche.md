# TÂCHE 03 — Commande /modele-fiche

**Priorité : MOYENNE**  
**Fichier à modifier : `cogs/personnage.py`**

---

## Problème

La commande `/modele-fiche` est mentionnée dans le README comme "non implémentée".  
Un joueur qui arrive sur le serveur et cherche comment soumettre sa fiche n'a pas de raccourci.  
Le channel `📋・modele-de-fiche` contiendra le modèle (tâche 01), mais `/modele-fiche` permet  
d'envoyer le modèle en DM n'importe où, sans que le joueur ait à chercher le bon channel.

---

## Implémentation

Ajouter dans `cogs/personnage.py`, dans la classe `Personnage` :

```python
@app_commands.command(name="modele-fiche", description="Reçois le modèle de fiche personnage en DM.")
async def modele_fiche(self, interaction: discord.Interaction):
    """Envoie le modèle de fiche complet en DM au demandeur."""

    modele_texte = (
        "```\n"
        "═══════════════════════════════\n"
        "   FICHE PERSONNAGE — INFERNUM AETERNA\n"
        "═══════════════════════════════\n"
        "Nom du personnage :\n"
        "Faction : [Shinigami / Togabito / Arrancar / Quincy]\n"
        "Rang souhaité :\n"
        "Âge apparent :\n\n"
        "HISTOIRE (300 mots minimum) :\n"
        "[Votre texte]\n\n"
        "APPARENCE :\n"
        "[Description physique]\n\n"
        "APTITUDES (3 maximum selon rang) :\n"
        "1.\n"
        "2.\n"
        "3.\n\n"
        "OBJECTIF NARRATIF :\n"
        "[Ce que votre personnage cherche dans le contexte de la Fissure]\n"
        "═══════════════════════════════\n"
        "```"
    )

    embed_modele = discord.Embed(
        title="📋 Modèle de Fiche Personnage",
        description=modele_texte,
        color=COULEURS["blanc_seireitei"]
    )
    embed_modele.set_footer(text="⸻ Infernum Aeterna · Soumission via /fiche-soumettre ⸻")

    embed_instructions = discord.Embed(
        title="📥 Comment soumettre",
        color=COULEURS["or_pale"]
    )
    embed_instructions.add_field(
        name="Étape 1", value="Copiez le modèle et remplissez chaque section.", inline=False
    )
    embed_instructions.add_field(
        name="Étape 2", value="Histoire : minimum 300 mots. Soyez précis sur les aptitudes.", inline=False
    )
    embed_instructions.add_field(
        name="Étape 3",
        value="Allez dans `📥・soumission-de-fiche` et tapez `/fiche-soumettre`.",
        inline=False
    )
    embed_instructions.add_field(
        name="Délai", value="Validation staff sous 48h. Notification en DM.", inline=False
    )

    # Tentative d'envoi en DM
    try:
        await interaction.user.send(embed=embed_modele)
        await interaction.user.send(embed=embed_instructions)
        await interaction.response.send_message(
            "✅ Le modèle de fiche t'a été envoyé en DM !", ephemeral=True
        )
    except discord.Forbidden:
        # DM désactivés — envoyer en éphémère dans le channel
        await interaction.response.send_message(
            embeds=[embed_modele, embed_instructions], ephemeral=True
        )
```

---

## Validation

- [ ] `/modele-fiche` envoie le modèle en DM si les DM sont ouverts
- [ ] Si DM fermés → envoie en éphémère dans le channel
- [ ] Modèle et instructions correctement formatés
- [ ] Commande visible dans la liste des commandes Discord
