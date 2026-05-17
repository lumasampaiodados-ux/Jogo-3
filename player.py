# player.py — Personagem do jogador

import pygame
import math
from config import *


AVATAR_COLORS = [
    (52,  152, 219),   # azul
    (46,  204, 113),   # verde
    (231, 76,  60),    # vermelho
    (155, 89,  182),   # roxo
    (241, 196, 15),    # amarelo
    (230, 126, 34),    # laranja
    (26,  188, 156),   # ciano
    (236, 72,  153),   # rosa
]


def build_player_sprite(color: tuple, state: str = "idle", frame: int = 0) -> pygame.Surface:
    """Desenha o sprite do aluno proceduralmente."""
    w, h = PLAYER_WIDTH, PLAYER_HEIGHT
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    dark = tuple(max(0, c - 50) for c in color)
    light = tuple(min(255, c + 60) for c in color)
    skin = (255, 213, 170)

    # ── Mochila ───────────────────────────────────────────────────────────
    bag_x = w // 2 - 8
    bag_y = h // 2 - 2
    pygame.draw.rect(surf, dark, (bag_x - 16, bag_y, 14, 22), border_radius=4)
    pygame.draw.rect(surf, color, (bag_x - 14, bag_y + 2, 10, 18), border_radius=3)

    # ── Corpo ─────────────────────────────────────────────────────────────
    body_y = h // 2 - 5
    pygame.draw.rect(surf, color, (w // 2 - 16, body_y, 32, 28), border_radius=6)
    # detalhe da camisa
    pygame.draw.rect(surf, light, (w // 2 - 6, body_y + 4, 12, 8), border_radius=3)

    # ── Pernas ────────────────────────────────────────────────────────────
    leg_y = body_y + 26
    bob = int(4 * math.sin(frame * 0.3)) if state == "walk" else 0
    pygame.draw.rect(surf, dark, (w // 2 - 14, leg_y, 12, 20 - bob), border_radius=4)
    pygame.draw.rect(surf, dark, (w // 2 + 2,  leg_y, 12, 20 + bob), border_radius=4)
    # sapatos
    pygame.draw.ellipse(surf, (50, 50, 50), (w // 2 - 16, leg_y + 18 - bob, 16, 8))
    pygame.draw.ellipse(surf, (50, 50, 50), (w // 2,      leg_y + 18 + bob, 16, 8))

    # ── Braços ───────────────────────────────────────────────────────────
    arm_bob = int(6 * math.sin(frame * 0.3)) if state == "walk" else 0
    pygame.draw.rect(surf, color, (w // 2 - 26, body_y + arm_bob, 10, 20), border_radius=4)
    pygame.draw.rect(surf, color, (w // 2 + 16, body_y - arm_bob, 10, 20), border_radius=4)
    # mãos
    pygame.draw.circle(surf, skin, (w // 2 - 21, body_y + 20 + arm_bob), 6)
    pygame.draw.circle(surf, skin, (w // 2 + 21, body_y + 20 - arm_bob), 6)

    # ── Cabeça ────────────────────────────────────────────────────────────
    head_y = h // 2 - 26
    pygame.draw.ellipse(surf, skin, (w // 2 - 14, head_y - 14, 28, 30))
    # cabelo
    pygame.draw.ellipse(surf, dark, (w // 2 - 14, head_y - 16, 28, 16))
    # olhos
    eye_open = state != "sad"
    if eye_open:
        pygame.draw.circle(surf, (50, 50, 50), (w // 2 - 5, head_y - 4), 3)
        pygame.draw.circle(surf, (50, 50, 50), (w // 2 + 5, head_y - 4), 3)
        pygame.draw.circle(surf, WHITE, (w // 2 - 4, head_y - 5), 1)
        pygame.draw.circle(surf, WHITE, (w // 2 + 6, head_y - 5), 1)
    else:
        pygame.draw.line(surf, (50, 50, 50), (w//2-7, head_y-4), (w//2-2, head_y-2), 2)
        pygame.draw.line(surf, (50, 50, 50), (w//2+3, head_y-4), (w//2+8, head_y-2), 2)
    # boca
    if state == "catch":
        pygame.draw.circle(surf, (200, 80, 80), (w // 2, head_y + 4), 4)
    elif state == "sad":
        pygame.draw.arc(surf, (150, 50, 50), (w//2-7, head_y+2, 14, 8), math.pi, 0, 2)
    else:
        pygame.draw.arc(surf, (200, 100, 100), (w//2-6, head_y, 12, 8), math.pi, 0, 2)

    # ── Efeito de pegar livro ─────────────────────────────────────────────
    if state == "catch":
        for i in range(5):
            angle = math.pi / 4 * i
            sx = w // 2 + int(math.cos(angle) * 28)
            sy = head_y + int(math.sin(angle) * 20)
            pygame.draw.circle(surf, (255, 230, 50, 180), (sx, sy), 3)

    return surf


class Player:
    def __init__(self, name: str = "Aluno", avatar: int = 0):
        self.name = name
        self.avatar_idx = avatar % len(AVATAR_COLORS)
        self.color = AVATAR_COLORS[self.avatar_idx]

        self.x = float(SCREEN_W // 2)
        self.y = float(SCREEN_H - PLAYER_HEIGHT // 2 - 10)
        self.speed = PLAYER_SPEED

        # animação
        self.frame = 0
        self.state = "idle"   # idle | walk | catch | sad
        self.state_timer = 0

        # sprites pré-renderizados para cada estado e 8 frames
        self._cache: dict[tuple, pygame.Surface] = {}

        # powerups
        self.shield = 0          # usos restantes
        self.magnet = 0.0        # segundos restantes
        self.magnet_active = False

    # ── Sprites ──────────────────────────────────────────────────────────────

    def _get_sprite(self) -> pygame.Surface:
        key = (self.state, self.frame % 16)
        if key not in self._cache:
            self._cache[key] = build_player_sprite(self.color, self.state, self.frame)
        return self._cache[key]

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, keys, dt_frames: float = 1.0):
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            moving = True

        # limites
        self.x = max(PLAYER_WIDTH // 2, min(SCREEN_W - PLAYER_WIDTH // 2, self.x))

        # estado
        if self.state_timer > 0:
            self.state_timer -= 1
        else:
            self.state = "walk" if moving else "idle"

        if moving:
            self.frame += 1
        else:
            self.frame = 0

        # magnet cooldown
        if self.magnet > 0:
            self.magnet -= dt_frames / FPS
            self.magnet_active = True
        else:
            self.magnet = 0
            self.magnet_active = False

    def move_toward(self, target_x: float):
        """Controle por toque."""
        diff = target_x - self.x
        if abs(diff) > self.speed:
            self.x += self.speed * (1 if diff > 0 else -1)
        else:
            self.x = target_x

    def set_state(self, state: str, duration: int = 20):
        self.state = state
        self.state_timer = duration

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x) - PLAYER_WIDTH // 2,
            int(self.y) - PLAYER_HEIGHT // 2,
            PLAYER_WIDTH, PLAYER_HEIGHT
        )

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface):
        sprite = self._get_sprite()
        blit_x = int(self.x) - sprite.get_width() // 2
        blit_y = int(self.y) - sprite.get_height() // 2
        surf.blit(sprite, (blit_x, blit_y))

        # Anel do ímã
        if self.magnet_active:
            import math
            t = pygame.time.get_ticks() / 300
            radius = int(MAGNET_RADIUS + 10 * math.sin(t))
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 50, 50, 40), (radius, radius), radius)
            pygame.draw.circle(s, (220, 50, 50, 100), (radius, radius), radius, 2)
            surf.blit(s, (int(self.x) - radius, int(self.y) - radius))

        # Ícone de escudo
        if self.shield > 0:
            sx, sy = int(self.x) + PLAYER_WIDTH // 2, int(self.y) - PLAYER_HEIGHT // 2
            pygame.draw.circle(surf, BLUE, (sx, sy), 10)
            try:
                font = pygame.font.SysFont("arial", 10, bold=True)
            except Exception:
                font = pygame.font.Font(None, 12)
            t = font.render(f"🛡{self.shield}", True, WHITE)
            surf.blit(t, (sx - t.get_width() // 2, sy - t.get_height() // 2))
