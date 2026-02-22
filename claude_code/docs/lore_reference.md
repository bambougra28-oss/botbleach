# Données Lore — Référence Complète

## Contenu disponible dans cogs/lore.py

### GLOSSAIRE — 19 termes
Format : `"cle": ("kanji", "définition")`

| Clé | Kanji | Terme fr |
|---|---|---|
| reishi | 霊子 | Particule spirituelle |
| reiatsu | 霊圧 | Pression spirituelle |
| zanpakuto | 斬魄刀 | Épée de l'âme |
| shikai | 始解 | 1ère libération Zanpakutō |
| bankai | 卍解 | Libération finale |
| hollow | 虚 | Âme corrompue |
| resurreccion | 鬼道解放 | Libération Arrancar |
| jigokusari | 地獄鎖 | Chaînes de l'Enfer |
| kushanada | 倶舎那陀 | Gardiens de l'Enfer |
| jigoku_no_rinki | 地獄の淋気 | Énergie infernale |
| konso | 魂葬 | Enterrement de l'âme |
| konso_reisai | 魂葬霊祭 | Rituel secret Capitaines |
| reio | 霊王 | Roi des Âmes |
| mimihagi | 耳塞ぎ | Bras droit du Reiō |
| togabito | 咎人 | Les coupables |
| mer_primordiale | 原始海 | Avant les Trois Mondes |
| lichtreich | 光の帝国 | Empire de Lumière (Quincy) |
| wandenreich | 見えざる帝国 | Empire invisible |
| oken | 王鍵 | Clé du Roi |

### FICHES_FACTION — 4 factions
Chaque faction : titre, couleur (depuis COULEURS), sections (liste de tuples)

**Shinigami** — 4 sections : Origine, Pouvoir, Secret, Fissure  
**Togabito** — 4 sections : Origine, Pouvoir, Factions internes, Fissure  
**Arrancar** — 4 sections : Origine, Pouvoir, Hiérarchie, Fissure  
**Quincy** — 4 sections : Origine, Pouvoir, Traumatisme, Fissure

### STRATES — 5 niveaux
Chaque strate : nom, niveau (1-5), couleur hex, description narrative

| Niveau | Nom | Couleur |
|---|---|---|
| 1 | Prātus | Rougeâtre |
| 2 | Carnale | Orange sombre |
| 3 | Sulfura | Jaune soufre |
| 4 | Profundus | Bleu profond |
| 5 | Saiōbu | Noir absolu |

### LORE_DATA — 6 sections (défini inline dans /lore, à extraire — tâche 04)
- `origine` : La Mer Primordiale
- `fissure` : La Fissure  
- `reio` : Le Reiō
- `division_zero` : La Division Zéro
- `konso_reisai` : Le Konsō Reisai
- `systeme` : Système de combat

---

## Contenu disponible dans cogs/ambiance.py

### PROFILS_ZONE — descriptions atmosphériques par zone
Utilisable pour peupler les descriptions de canaux ou introductions de zones dynamiques.

```python
PROFILS_ZONE = {
    "enfer":         {"themes": [...], "tokens": [...], "couleur": ...},
    "soul_society":  {"themes": [...], "tokens": [...], "couleur": ...},
    "hueco_mundo":   {"themes": [...], "tokens": [...], "couleur": ...},
    "vivants":       {"themes": [...], "tokens": [...], "couleur": ...},
    "frontiere":     {"themes": [...], "tokens": [...], "couleur": ...},
}
```

---

## Rangs détaillés par faction

### Shinigami (7 rangs)
| Clé | Label | Points |
|---|---|---|
| academie | 🎓 Académie | 500 |
| etudiant_avance | 📗 Étudiant Avancé | 1 200 |
| shinigami_assermente | ☯️ Shinigami Assermenté | 2 500 |
| officier | 🗡️ Officier | 4 000 |
| officier_senior | ⚔️ Officier Senior | 6 000 |
| vice_capitaine | 🎖️ Vice-Capitaine | 8 000 |
| capitaine | 👑 Capitaine | 10 000 |

### Togabito (4 rangs)
| Clé | Label | Points |
|---|---|---|
| condamne_recent | 💀 Condamné Récent | 500 |
| damne_resilient | 🩸 Damné Résilient | 2 000 |
| damne_forge | 🔗 Damné Forgé | 5 000 |
| ancien_damne | ⛓️ Ancien Damné | 10 000 |

### Arrancar (5 rangs)
| Clé | Label | Points |
|---|---|---|
| arrancar_libre | ◽ Arrancar Libre | 800 |
| numeros | ○ Números | 2 000 |
| fraccion | ◇ Fracción | 4 000 |
| privaron_espada | ◈ Privaron Espada | 7 000 |
| espada | 💠 Espada | 10 000 |

### Quincy (4 rangs)
| Clé | Label | Points |
|---|---|---|
| quincy_initie | ∘ Quincy Initié | 500 |
| quincy_confirme | ∗ Quincy Confirmé | 2 500 |
| sternritter | ✧ Sternritter | 6 000 |
| quincy_pur | ✦ Quincy Pur | 10 000 |

---

## Niveaux Fissure (evenements.py)

| Niveau | Nom | Couleur | Description |
|---|---|---|---|
| 1 | Stable | Vert | Activité minimale |
| 2 | Instable | Or | Fluctuations détectées |
| 3 | Critique | Orange | Contamination active |
| 4 | Brisée | Rouge | Passages spontanés |
| 5 | Apocalypse | Noir | Effondrement imminent |

---

## Couleurs de config.py — référence complète

```python
COULEURS = {
    "or_ancien":         0xC9A84C,  # Or chaud — lore, histoire
    "or_pale":           0xF5E6A3,  # Or pâle — système, points
    "rouge_chaine":      0x8B1A1A,  # Rouge sombre — combat, danger
    "pourpre_infernal":  0x6B1FA8,  # Violet — Enfer, Togabito
    "blanc_seireitei":   0xF0F0F0,  # Blanc cassé — Soul Society
    "gris_acier":        0x5A5A6A,  # Gris — neutre, staff
    "gris_sable":        0x8A8A7A,  # Gris sable — Arrancar
    "bleu_abyssal":      0x1A3A6B,  # Bleu profond — Quincy
    "vert_sombre":       0x2D5A27,  # Vert — validation, succès
    "noir_absolu":       0x050505,  # Quasi-noir — Saiōbu, mort
}
```
