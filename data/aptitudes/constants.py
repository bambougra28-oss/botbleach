"""
INFERNUM AETERNA — Aptitudes : Constantes
Budget Reiryoku par rang, restrictions P3, et règles du système.
"""

# ══════════════════════════════════════════════════════════════════════════════
#  BUDGET REIRYOKU (霊力) PAR RANG
# ══════════════════════════════════════════════════════════════════════════════

REIRYOKU_PAR_RANG = {
    # Shinigami
    "gakusei":          3,
    "shinigami_asserm": 6,
    "yonseki":          10,
    "sanseki":          14,
    "fukutaicho":       18,
    "taicho":           22,
    "sotaicho":         26,
    # Togabito
    "zainin":           3,
    "togabito_damne":   8,
    "tan_togabito":     14,
    "ko_togabito":      20,
    "gokuo":            26,
    # Arrancar
    "horo":             3,
    "gillian":          5,
    "adjuchas":         8,
    "vasto_lorde":      11,
    "numeros":          14,
    "fraccion":         17,
    "privaron_espada":  20,
    "espada":           23,
    "rey":              26,
    # Quincy
    "minarai":          3,
    "quincy_confirme":  7,
    "jagdarmee":        12,
    "sternritter":      18,
    "schutzstaffel":    22,
    "seitei":           26,
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
