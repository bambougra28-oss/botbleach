"""
INFERNUM AETERNA — Aptitudes : Constantes
Budget Reiryoku par rang, restrictions P3, et règles du système.
"""

# ══════════════════════════════════════════════════════════════════════════════
#  BUDGET REIRYOKU (霊力) PAR RANG
# ══════════════════════════════════════════════════════════════════════════════

REIRYOKU_PAR_RANG = {
    # Shinigami (total arbre : 78 pts)
    "gakusei":          3,
    "shinigami_asserm": 7,
    "yonseki":          12,
    "sanseki":          18,
    "fukutaicho":       26,
    "taicho":           35,
    "sotaicho":         45,
    # Togabito (total arbre : 64 pts)
    "zainin":           3,
    "togabito_damne":   10,
    "tan_togabito":     20,
    "ko_togabito":      33,
    "gokuo":            45,
    # Arrancar (total arbre : 60 pts)
    "horo":             3,
    "gillian":          5,
    "adjuchas":         9,
    "vasto_lorde":      13,
    "numeros":          17,
    "fraccion":         22,
    "privaron_espada":  28,
    "espada":           36,
    "rey":              45,
    # Quincy (total arbre : 60 pts)
    "minarai":          3,
    "quincy_confirme":  8,
    "jagdarmee":        15,
    "sternritter":      25,
    "schutzstaffel":    35,
    "seitei":           45,
}

# ══════════════════════════════════════════════════════════════════════════════
#  RANGS MINIMUM POUR PALIER 3 (Transcendance)
# ══════════════════════════════════════════════════════════════════════════════

# Rangs à partir desquels P3 est accessible, par faction
RANGS_P3 = {
    "shinigami": {"fukutaicho", "taicho", "sotaicho"},
    "togabito":  {"ko_togabito", "gokuo"},
    "arrancar":  {"privaron_espada", "espada", "rey"},
    "quincy":    {"sternritter", "schutzstaffel", "seitei"},
}

# ══════════════════════════════════════════════════════════════════════════════
#  COÛTS PAR PALIER
# ══════════════════════════════════════════════════════════════════════════════

COUT_PALIER = {
    1: 1,
    2: 2,
    3: 3,
}

# ══════════════════════════════════════════════════════════════════════════════
#  COULEURS PAR FACTION (pour les embeds aptitudes)
# ══════════════════════════════════════════════════════════════════════════════

COULEURS_FACTION = {
    "shinigami": 0xE8E8F0,
    "togabito":  0x6B1FA8,
    "arrancar":  0x8A8A7A,
    "quincy":    0x1A3A6B,
}

# ══════════════════════════════════════════════════════════════════════════════
#  EMOJIS PAR FACTION
# ══════════════════════════════════════════════════════════════════════════════

EMOJI_FACTION = {
    "shinigami": "死神",
    "togabito":  "咎人",
    "arrancar":  "破面",
    "quincy":    "滅却師",
}

# ══════════════════════════════════════════════════════════════════════════════
#  EMOJIS PAR PALIER
# ══════════════════════════════════════════════════════════════════════════════

EMOJI_PALIER = {
    1: "◈",   # Éveil
    2: "◆",   # Maîtrise
    3: "✦",   # Transcendance
}

NOM_PALIER = {
    1: "Éveil",
    2: "Maîtrise",
    3: "Transcendance",
}
