# TÂCHE 02 — Boutons persistants après redémarrage du bot

**Priorité : HAUTE**  
**Fichier à modifier : `cogs/construction.py`, `main.py`**

---

## Problème

Actuellement, `BoutonsFaction` et `BoutonsAbonnements` stockent `roles_map` (dictionnaire `{cle: discord.Role}`) en mémoire lors du `/setup`.

Après un redémarrage du bot, Discord affiche toujours les boutons (ils existent dans les messages), mais les callbacks ne sont plus enregistrés. Résultat : cliquer sur un bouton de faction ne fait rien ou retourne une erreur.

Le problème : `discord.Role` est un objet runtime qui n'existe pas entre les sessions.  
`roles_ids.json` contient les IDs mais pas les objets `discord.Role`.

---

## Solution

Refactoriser les trois Views pour qu'elles chargent leurs rôles **depuis `roles_ids.json` + guild** au moment du clic, plutôt qu'au moment de la création de la View.

### BoutonsFaction — nouveau pattern

```python
class BoutonsFaction(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ← plus de roles_map en paramètre
        factions = [
            ("死神 Shinigami", "shinigami", discord.ButtonStyle.secondary),
            ("咎人 Togabito",  "togabito",  discord.ButtonStyle.danger),
            ("破面 Arrancar",  "arrancar",  discord.ButtonStyle.secondary),
            ("滅却師 Quincy",  "quincy",    discord.ButtonStyle.primary),
        ]
        for label, cle, style in factions:
            btn = discord.ui.Button(label=label, style=style, custom_id=f"faction_{cle}")
            btn.callback = self._make_callback(cle)
            self.add_item(btn)

    def _make_callback(self, cle):
        async def callback(interaction: discord.Interaction):
            # Charger les rôles depuis le JSON + guild au moment du clic
            roles_ids = charger_roles()
            guild = interaction.guild
            role_id = roles_ids.get(cle)
            if not role_id:
                await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
                return
            role = guild.get_role(role_id)
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable sur ce serveur.", ephemeral=True)
                return

            member = interaction.user
            factions_cles = ["shinigami", "togabito", "arrancar", "quincy"]
            roles_a_retirer = [
                guild.get_role(roles_ids[c])
                for c in factions_cles
                if c in roles_ids and guild.get_role(roles_ids[c]) in member.roles
            ]
            roles_a_retirer = [r for r in roles_a_retirer if r]
            if roles_a_retirer:
                await member.remove_roles(*roles_a_retirer, reason="Changement de faction")
            await member.add_roles(role, reason=f"Faction choisie : {cle}")
            await interaction.response.send_message(
                f"⚔️ Vous avez rejoint la faction **{role.name}**.", ephemeral=True
            )
        return callback
```

### BoutonsAbonnements — nouveau pattern

```python
class BoutonsAbonnements(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ← plus de roles_map en paramètre
        abonnements = [
            ("📣 Annonces",   "abonne_annonces"),
            ("🎲 Événements", "evenement_actif"),
            ("🎭 RP Ouvert",  "rp_ouvert"),
            ("🔔 Narrateur",  "narrateur_ping"),
        ]
        for label, cle in abonnements:
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, custom_id=f"abo_{cle}")
            btn.callback = self._make_callback(cle)
            self.add_item(btn)

    def _make_callback(self, cle):
        async def callback(interaction: discord.Interaction):
            roles_ids = charger_roles()
            guild = interaction.guild
            role_id = roles_ids.get(cle)
            if not role_id:
                await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
                return
            role = guild.get_role(role_id)
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable sur ce serveur.", ephemeral=True)
                return
            member = interaction.user
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(f"🔕 Désabonné de **{role.name}**.", ephemeral=True)
            else:
                await member.add_roles(role)
                await interaction.response.send_message(f"🔔 Abonné à **{role.name}**.", ephemeral=True)
        return callback
```

### Appels à mettre à jour dans construction.py

```python
# Avant (passait roles_map)
view = BoutonsFaction(roles_map)
view = BoutonsAbonnements(roles_map)

# Après (plus d'argument)
view = BoutonsFaction()
view = BoutonsAbonnements()
```

### Enregistrement dans main.py — CRITIQUE

Pour que les boutons survivent au redémarrage, il faut enregistrer les Views **dans `setup_hook`** avec `bot.add_view()` :

```python
async def setup_hook(self):
    # ... chargement des cogs ...

    # Enregistrer les Views persistantes (APRÈS chargement des cogs)
    from cogs.construction import BoutonsFaction, BoutonCombat, BoutonsAbonnements
    self.add_view(BoutonsFaction())
    self.add_view(BoutonCombat("tous"))
    self.add_view(BoutonsAbonnements())
```

`bot.add_view()` indique à discord.py que ces Views peuvent traiter des interactions  
sur des messages déjà envoyés, même si le bot vient de redémarrer.

---

## Points d'attention

- `BoutonCombat` n'a pas ce problème (son callback délègue au cog Combat par `client.cogs.get`)  
  mais doit quand même être enregistré via `add_view` pour survivre au restart
- Les `custom_id` doivent rester identiques (`faction_shinigami`, `abo_annonces`…)  
  — ils servent de clé de correspondance entre le message Discord et la View Python
- Tester en redémarrant le bot et en cliquant un bouton sans refaire `/setup`

---

## Validation

- [ ] Cliquer sur un bouton faction après redémarrage → rôle attribué correctement
- [ ] Cliquer sur un bouton abonnement après redémarrage → toggle rôle correct
- [ ] Cliquer sur bouton combat après redémarrage → modal s'ouvre
- [ ] Aucune erreur `Unknown Interaction` dans les logs
