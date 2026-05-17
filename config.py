# config.py — Configurações globais do Missão Biblioteca

import os

# ── Janela ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
TITLE = "Missão Biblioteca"

# ── Tempo ────────────────────────────────────────────────────────────────────
GAME_DURATION = 60          # segundos por partida
DIFFICULTY_INTERVAL = 15    # a cada N segundos aumenta dificuldade

# ── Personagem ───────────────────────────────────────────────────────────────
PLAYER_SPEED = 6
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 80

# ── Objetos ──────────────────────────────────────────────────────────────────
ITEM_BASE_SPEED   = 3
ITEM_SPEED_INC    = 0.5     # incremento a cada fase
ITEM_BASE_RATE    = 90      # frames entre spawns
ITEM_RATE_DEC     = 5       # redução de frames entre spawns por fase
ITEM_MIN_RATE     = 30

# ── Livros (matéria, pontos, cor_hex) ────────────────────────────────────────
BOOKS = [
    ("Português",       10, "#E74C3C"),
    ("Matemática",      20, "#3498DB"),
    ("Biologia",        15, "#2ECC71"),
    ("Geografia",       12, "#F39C12"),
    ("História",        12, "#8E44AD"),
    ("Inglês",          18, "#1ABC9C"),
    ("Artes",            8, "#E91E63"),
    ("Ed. Física",       5, "#FF5722"),
]

# ── Itens negativos ──────────────────────────────────────────────────────────
PHONE_PENALTY   = 50        # remove pontos
CIGARETTE_ZERO  = True      # zera tudo

# ── Livro dourado ─────────────────────────────────────────────────────────────
GOLDEN_POINTS   = 100
GOLDEN_DURATION = 3         # segundos na tela
GOLDEN_CHANCE   = 0.003     # chance por frame de spawnar

# ── Combo ────────────────────────────────────────────────────────────────────
COMBO_3_BONUS   = 20
COMBO_5_BONUS   = 50
COMBO_FEVER_AT  = 10        # livros seguidos para MODO FEBRE

# ── Modo Febre ────────────────────────────────────────────────────────────────
FEVER_DURATION  = 5         # segundos
FEVER_MULTIPLIER = 2

# ── Itens especiais ──────────────────────────────────────────────────────────
CLOCK_BONUS     = 10        # segundos extras
SHIELD_USES     = 1
MAGNET_DURATION = 5         # segundos
MAGNET_RADIUS   = 200

# ── Ranking ──────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "ranking.db")
TOP_N   = 5

# ── Cores base ───────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
YELLOW  = (255, 215, 0)
RED     = (220, 50,  50)
GREEN   = (46,  204, 113)
BLUE    = (52,  152, 219)
PURPLE  = (142, 68,  173)
ORANGE  = (230, 126, 34)
CYAN    = (26,  188, 156)
PINK    = (233, 30,  99)
GOLD    = (255, 200, 0)
DARK    = (15,  15,  30)
DARKISH = (25,  25,  50)

# ── Caminhos de assets (gerados proceduralmente se não existirem) ─────────────
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR  = os.path.join(ASSETS_DIR, "fonts")
