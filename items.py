# items.py — Livros, itens negativos e itens especiais

import pygame
import random
import math
from config import *


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ── Renderizador de sprites procedurais ─────────────────────────────────────

def draw_book_sprite(color: tuple, label: str, width=46, height=60, golden=False) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Sombra
    shadow = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 60), (4, 4, width - 4, height - 4), border_radius=6)
    surf.blit(shadow, (0, 0))

    # Corpo do livro
    body_color = color
    pygame.draw.rect(surf, body_color, (0, 0, width - 4, height), border_radius=6)

    # Lombada
    spine_color = tuple(max(0, c - 40) for c in color)
    pygame.draw.rect(surf, spine_color, (0, 0, 10, height), border_radius=4)

    # Linhas de páginas
    page_color = (240, 240, 240, 200)
    for i in range(3):
        y = 12 + i * 14
        pygame.draw.line(surf, page_color, (13, y), (width - 8, y), 1)

    # Brilho dourado
    if golden:
        for _ in range(6):
            gx = random.randint(5, width - 5)
            gy = random.randint(5, height - 5)
            pygame.draw.circle(surf, (255, 255, 150, 180), (gx, gy), random.randint(2, 4))

    # Label da matéria
    try:
        font = pygame.font.SysFont("arial", 9, bold=True)
    except Exception:
        font = pygame.font.Font(None, 11)
    txt = font.render(label[:8], True, WHITE)
    txt_x = (width - 4) // 2 - txt.get_width() // 2
    surf.blit(txt, (txt_x, height // 2 - txt.get_height() // 2))

    return surf


def draw_phone_sprite(width=40, height=56) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, (50, 50, 50), (0, 0, width, height), border_radius=8)
    pygame.draw.rect(surf, (80, 180, 255), (4, 8, width - 8, height - 20), border_radius=4)
    pygame.draw.circle(surf, (150, 150, 150), (width // 2, height - 7), 4)
    try:
        font = pygame.font.SysFont("arial", 14, bold=True)
    except Exception:
        font = pygame.font.Font(None, 16)
    txt = font.render("📱", True, WHITE)
    surf.blit(txt, (width // 2 - txt.get_width() // 2, height // 2 - txt.get_height() // 2))
    return surf


def draw_cigarette_sprite(width=40, height=50) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    # corpo
    pygame.draw.rect(surf, (220, 220, 200), (10, 10, 12, 35), border_radius=3)
    # filtro
    pygame.draw.rect(surf, (200, 130, 80), (10, 38, 12, 8), border_radius=2)
    # brasa
    pygame.draw.circle(surf, (255, 80, 20), (16, 10), 5)
    # fumaça
    pygame.draw.arc(surf, (180, 180, 180, 120), (5, 0, 10, 12), 0, math.pi, 2)
    return surf


def draw_clock_sprite(width=50, height=50) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy, r = width // 2, height // 2, width // 2 - 2
    pygame.draw.circle(surf, (255, 220, 50), (cx, cy), r)
    pygame.draw.circle(surf, (200, 160, 0), (cx, cy), r, 2)
    pygame.draw.line(surf, (50, 50, 50), (cx, cy), (cx, cy - r + 6), 3)
    pygame.draw.line(surf, (50, 50, 50), (cx, cy), (cx + r - 8, cy), 2)
    return surf


def draw_shield_sprite(width=50, height=50) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pts = [(25, 2), (48, 14), (48, 30), (25, 48), (2, 30), (2, 14)]
    pygame.draw.polygon(surf, (70, 130, 220), pts)
    pygame.draw.polygon(surf, (150, 200, 255), pts, 2)
    try:
        font = pygame.font.SysFont("arial", 22, bold=True)
    except Exception:
        font = pygame.font.Font(None, 26)
    txt = font.render("🛡", True, WHITE)
    surf.blit(txt, (25 - txt.get_width() // 2, 22 - txt.get_height() // 2))
    return surf


def draw_magnet_sprite(width=50, height=50) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.arc(surf, (220, 50, 50), (5, 5, 40, 40), 0, math.pi, 10)
    pygame.draw.rect(surf, (220, 50, 50), (5, 20, 10, 20))
    pygame.draw.rect(surf, (220, 50, 50), (35, 20, 10, 20))
    pygame.draw.rect(surf, (200, 200, 50), (5, 38, 10, 6))
    pygame.draw.rect(surf, (70, 70, 220), (35, 38, 10, 6))
    return surf


# ── Classes de itens ──────────────────────────────────────────────────────────

class FallingItem:
    """Base de todos os itens que caem."""

    ITEM_TYPE = "base"

    def __init__(self, x, y, speed, sprite):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.sprite = sprite
        self.w = sprite.get_width()
        self.h = sprite.get_height()
        self.alive = True
        self.rotation = 0
        self.rot_speed = random.uniform(-2, 2)
        # oscilação horizontal leve
        self.osc_amp   = random.uniform(0, 30)
        self.osc_speed = random.uniform(0.03, 0.07)
        self.osc_t     = random.uniform(0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - self.w // 2,
                           int(self.y) - self.h // 2,
                           self.w, self.h)

    def update(self):
        self.y += self.speed
        self.osc_t += self.osc_speed
        self.x += math.sin(self.osc_t) * self.osc_amp * 0.05
        self.x = max(self.w // 2, min(SCREEN_W - self.w // 2, self.x))
        self.rotation = (self.rotation + self.rot_speed) % 360
        if self.y > SCREEN_H + self.h:
            self.alive = False

    def draw(self, surf):
        rotated = pygame.transform.rotate(self.sprite, self.rotation)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, r)

    def on_catch(self, game_state: dict) -> dict:
        """Retorna delta dict com efeitos."""
        return {}


class BookItem(FallingItem):
    ITEM_TYPE = "book"

    def __init__(self, x, speed, subject, points, color_hex):
        self.subject = subject
        self.points = points
        self.color = hex_to_rgb(color_hex)
        sprite = draw_book_sprite(self.color, subject)
        super().__init__(x, 0, speed, sprite)

    def on_catch(self, gs):
        return {"points": self.points, "combo": True, "color": self.color, "label": self.subject}


class GoldenBook(FallingItem):
    ITEM_TYPE = "golden"

    def __init__(self, x, speed):
        self.color = GOLD
        sprite = draw_book_sprite(GOLD, "OURO", golden=True)
        super().__init__(x, -80, speed, sprite)   # começa acima da tela
        self.y = -80
        self.life_timer = GOLDEN_DURATION * FPS
        self.pulse_t = 0

    def update(self):
        self.y += self.speed
        self.osc_t += self.osc_speed
        self.x += math.sin(self.osc_t) * self.osc_amp * 0.05
        self.x = max(self.w // 2, min(SCREEN_W - self.w // 2, self.x))
        self.rotation = (self.rotation + self.rot_speed) % 360
        self.life_timer -= 1
        self.pulse_t += 0.1
        if self.life_timer <= 0 or self.y > SCREEN_H + self.h:
            self.alive = False

    def draw(self, surf):
        # Aura pulsante
        radius = int(35 + 8 * math.sin(self.pulse_t))
        aura = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = int(60 + 40 * math.sin(self.pulse_t))
        pygame.draw.circle(aura, (*GOLD, alpha), (radius, radius), radius)
        surf.blit(aura, (int(self.x) - radius, int(self.y) - radius))
        super().draw(surf)

    def on_catch(self, gs):
        return {"points": GOLDEN_POINTS, "combo": False, "color": GOLD, "golden": True}


class PhoneItem(FallingItem):
    ITEM_TYPE = "phone"

    def __init__(self, x, speed):
        super().__init__(x, 0, speed, draw_phone_sprite())

    def on_catch(self, gs):
        return {"points": -PHONE_PENALTY, "combo_break": True, "shake": True, "color": RED}


class CigaretteItem(FallingItem):
    ITEM_TYPE = "cigarette"

    def __init__(self, x, speed):
        super().__init__(x, 0, speed, draw_cigarette_sprite())

    def on_catch(self, gs):
        return {"zero_score": True, "combo_break": True, "shake": True, "color": RED}


class ClockItem(FallingItem):
    ITEM_TYPE = "clock"

    def __init__(self, x, speed):
        super().__init__(x, 0, speed, draw_clock_sprite())

    def on_catch(self, gs):
        return {"time_bonus": CLOCK_BONUS, "color": YELLOW, "combo": False}


class ShieldItem(FallingItem):
    ITEM_TYPE = "shield"

    def __init__(self, x, speed):
        super().__init__(x, 0, speed, draw_shield_sprite())

    def on_catch(self, gs):
        return {"shield": True, "color": BLUE, "combo": False}


class MagnetItem(FallingItem):
    ITEM_TYPE = "magnet"

    def __init__(self, x, speed):
        super().__init__(x, 0, speed, draw_magnet_sprite())

    def on_catch(self, gs):
        return {"magnet": True, "color": (220, 50, 50), "combo": False}


# ── Factory ───────────────────────────────────────────────────────────────────

def spawn_item(speed: float) -> FallingItem:
    """Cria um item aleatório com a velocidade fornecida."""
    x = random.randint(50, SCREEN_W - 50)
    roll = random.random()

    if roll < 0.55:   # 55% livros comuns
        subj, pts, color = random.choice(BOOKS)
        return BookItem(x, speed, subj, pts, color)
    elif roll < 0.65: # 10% celular
        return PhoneItem(x, speed)
    elif roll < 0.70: # 5% cigarro
        return CigaretteItem(x, speed)
    elif roll < 0.77: # 7% relógio
        return ClockItem(x, speed)
    elif roll < 0.84: # 7% escudo
        return ShieldItem(x, speed)
    elif roll < 0.91: # 7% ímã
        return MagnetItem(x, speed)
    else:             # 9% livros (peso igual a todos)
        subj, pts, color = random.choice(BOOKS)
        return BookItem(x, speed, subj, pts, color)
