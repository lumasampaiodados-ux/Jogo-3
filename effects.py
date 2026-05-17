# effects.py — Partículas, textos flutuantes e efeitos visuais

import pygame
import random
import math
from config import *


class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, life=40, size=5):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-4, -1)
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15          # gravidade leve
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        radius = max(1, int(self.size * (self.life / self.max_life)))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
        surf.blit(s, (int(self.x) - radius, int(self.y) - radius))

    @property
    def alive(self):
        return self.life > 0


class FloatingText:
    def __init__(self, x, y, text, color=WHITE, font_size=28, life=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = life
        self.max_life = life
        self.vy = -1.5
        try:
            self.font = pygame.font.SysFont("arial", font_size, bold=True)
        except Exception:
            self.font = pygame.font.Font(None, font_size)

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        img = self.font.render(self.text, True, self.color)
        img.set_alpha(alpha)
        surf.blit(img, (int(self.x) - img.get_width() // 2, int(self.y)))

    @property
    def alive(self):
        return self.life > 0


class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0

    def trigger(self, duration=20, intensity=8):
        self.duration = duration
        self.intensity = intensity

    def update(self):
        if self.duration > 0:
            self.duration -= 1

    def offset(self):
        if self.duration > 0:
            return (
                random.randint(-self.intensity, self.intensity),
                random.randint(-self.intensity, self.intensity)
            )
        return (0, 0)


class FlashOverlay:
    """Overlay colorido que aparece e some."""
    def __init__(self):
        self.color = (255, 0, 0)
        self.alpha = 0
        self.decay = 10

    def trigger(self, color=(255, 0, 0), alpha=120, decay=8):
        self.color = color
        self.alpha = alpha
        self.decay = decay

    def update(self):
        self.alpha = max(0, self.alpha - self.decay)

    def draw(self, surf):
        if self.alpha > 0:
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            s.fill((*self.color, int(self.alpha)))
            surf.blit(s, (0, 0))


class StarBurst:
    """Explosão de estrelas ao pegar livro."""
    def __init__(self, x, y, color, n=12):
        self.particles = []
        for i in range(n):
            angle = (2 * math.pi / n) * i
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, color, vx, vy, life=35, size=4))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)

    @property
    def alive(self):
        return len(self.particles) > 0


class EffectsManager:
    def __init__(self):
        self.particles: list[Particle] = []
        self.texts: list[FloatingText] = []
        self.bursts: list[StarBurst] = []
        self.shake = ScreenShake()
        self.flash = FlashOverlay()

    # ── API pública ─────────────────────────────────────────────────────────

    def book_catch(self, x, y, points, color):
        self.bursts.append(StarBurst(x, y, color))
        sign = "+" if points >= 0 else ""
        self.texts.append(FloatingText(x, y - 20, f"{sign}{points}", color, font_size=30))
        self.flash.trigger((255, 255, 100), alpha=40, decay=10)

    def negative_hit(self, x, y, label="-50"):
        self.shake.trigger(18, 10)
        self.flash.trigger((220, 0, 0), alpha=140, decay=8)
        self.texts.append(FloatingText(x, y - 20, label, RED, font_size=32))
        for _ in range(20):
            self.particles.append(Particle(x, y, (220, 50, 50)))

    def golden_catch(self, x, y):
        self.bursts.append(StarBurst(x, y, GOLD, n=20))
        self.texts.append(FloatingText(x, y - 30, "+100 ✨", GOLD, font_size=36))
        self.flash.trigger(GOLD, alpha=80, decay=6)

    def combo_text(self, x, y, text, color=YELLOW):
        self.texts.append(FloatingText(x, y, text, color, font_size=34))

    def spawn_particles(self, x, y, color, n=10):
        for _ in range(n):
            self.particles.append(Particle(x, y, color))

    # ── Loop ─────────────────────────────────────────────────────────────────

    def update(self):
        self.shake.update()
        self.flash.update()
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]
        for t in self.texts:
            t.update()
        self.texts = [t for t in self.texts if t.alive]
        for b in self.bursts:
            b.update()
        self.bursts = [b for b in self.bursts if b.alive]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)
        for b in self.bursts:
            b.draw(surf)
        for t in self.texts:
            t.draw(surf)
        self.flash.draw(surf)
