#!/usr/bin/env python3
# main.py — Missão Biblioteca | Loop principal

import sys
import math
import random
import pygame

from config import *
from database import init_db
from ranking import RankingManager
from player import Player
from items import spawn_item, GoldenBook, FallingItem, MAGNET_RADIUS
from effects import EffectsManager
from ui import (Background, HUD, MainMenu, RankingScreen,
                HowToPlay, GameOverScreen, LoadingScreen)


# ─────────────────────────────────────────────────────────────────────────────
# Geração de sons procedural (sem arquivos externos)
# ─────────────────────────────────────────────────────────────────────────────

def make_beep(freq=440, duration_ms=80, volume=0.4,
              wave="sine", sample_rate=22050) -> pygame.mixer.Sound:
    import array, math
    n = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")
    amp = int(32767 * volume)
    fade = max(1, n // 8)
    for i in range(n):
        t = i / sample_rate
        if wave == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            v = 1 if math.sin(2 * math.pi * freq * t) >= 0 else -1
        else:
            v = 2 * (t * freq - math.floor(t * freq + 0.5))
        env = min(1.0, i / fade, (n - i) / fade)
        buf.append(int(amp * v * env))
    snd = pygame.sndarray.make_sound(
        pygame.sndarray.make_surface_array(buf, sample_rate)
        if hasattr(pygame.sndarray, "make_surface_array")
        else _buf_to_sound(buf, sample_rate)
    )
    return snd


def _buf_to_sound(buf, sample_rate=22050) -> pygame.mixer.Sound:
    import array
    # Fallback: mono 16-bit signed
    stereo = array.array("h")
    for v in buf:
        stereo.append(v)
        stereo.append(v)
    return pygame.sndarray.make_sound(
        pygame.surfarray.map_array(
            pygame.Surface((len(buf), 1)), None
        )
    ) if False else pygame.mixer.Sound(buffer=stereo)


def build_sounds() -> dict:
    """Cria dicionário de sons procedurais."""
    sounds = {}
    try:
        sounds["book"]     = make_beep(660,  60,  0.35, "sine")
        sounds["combo"]    = make_beep(880,  80,  0.40, "sine")
        sounds["golden"]   = make_beep(1200, 120, 0.45, "sine")
        sounds["negative"] = make_beep(200,  150, 0.50, "square")
        sounds["cigarette"]= make_beep(150,  200, 0.55, "square")
        sounds["fever"]    = make_beep(1000, 80,  0.40, "sine")
    except Exception:
        pass
    return sounds


# ─────────────────────────────────────────────────────────────────────────────
# Estado do jogo
# ─────────────────────────────────────────────────────────────────────────────

class GameState:
    def __init__(self, player: Player):
        self.player = player
        self.score      = 0
        self.time_left  = float(GAME_DURATION)
        self.items: list[FallingItem] = []
        self.combo      = 0
        self.fever      = False
        self.fever_timer = 0
        self.paused     = False
        self.muted      = False
        self.phase      = 0             # índice de dificuldade atual
        self.phase_timer = DIFFICULTY_INTERVAL * FPS
        self.spawn_timer = ITEM_BASE_RATE
        self.spawn_countdown = ITEM_BASE_RATE
        self.current_speed = ITEM_BASE_SPEED
        self.golden_cooldown = 0
        self.effects = EffectsManager()

    def current_speed_value(self):
        return ITEM_BASE_SPEED + self.phase * ITEM_SPEED_INC

    def current_rate(self):
        return max(ITEM_MIN_RATE, ITEM_BASE_RATE - self.phase * ITEM_RATE_DEC)

    def add_score(self, pts: int):
        mult = FEVER_MULTIPLIER if self.fever else 1
        self.score = max(0, self.score + pts * mult)

    def break_combo(self):
        self.combo = 0
        self.fever = False
        self.fever_timer = 0


# ─────────────────────────────────────────────────────────────────────────────
# Game loop
# ─────────────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)

        self.clock   = pygame.time.Clock()
        self.ranking = RankingManager()
        self.sounds  = build_sounds()
        self.muted   = False
        self.bg      = Background()
        self.hud     = HUD()
        self.hud.record_val = self.ranking.best_score

        self.scene   = "loading"
        self.loading = LoadingScreen()
        self.menu    = MainMenu()
        self.gs      = None
        self.touch_target = None  # para controle touch

    # ── Som ───────────────────────────────────────────────────────────────────

    def play(self, key: str):
        if self.muted:
            return
        snd = self.sounds.get(key)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    # ── Spawn ─────────────────────────────────────────────────────────────────

    def try_spawn(self):
        gs = self.gs
        gs.spawn_countdown -= 1
        if gs.spawn_countdown <= 0:
            gs.spawn_countdown = gs.current_rate()
            gs.items.append(spawn_item(gs.current_speed_value()))

        # Livro dourado
        gs.golden_cooldown -= 1
        if gs.golden_cooldown <= 0 and random.random() < GOLDEN_CHANCE:
            gs.items.append(GoldenBook(
                random.randint(60, SCREEN_W - 60),
                gs.current_speed_value()
            ))
            gs.golden_cooldown = FPS * 10  # cooldown mínimo entre dourados

    # ── Colisões ──────────────────────────────────────────────────────────────

    def check_collisions(self):
        gs = self.gs
        p  = gs.player
        p_rect = p.rect

        # Ímã: puxa livros para o jogador
        if p.magnet > 0:
            for item in gs.items:
                if item.ITEM_TYPE in ("book", "golden"):
                    dx = p.x - item.x
                    dy = p.y - item.y
                    dist = math.hypot(dx, dy)
                    if dist < MAGNET_RADIUS and dist > 0:
                        item.x += dx / dist * 4
                        item.y += dy / dist * 4

        to_remove = []
        for item in gs.items:
            if not item.alive:
                to_remove.append(item)
                continue
            if p_rect.colliderect(item.rect):
                delta = item.on_catch({})
                self._apply_delta(delta, item)
                to_remove.append(item)

        for item in to_remove:
            if item in gs.items:
                gs.items.remove(item)

    def _apply_delta(self, delta: dict, item: FallingItem):
        gs = self.gs
        p  = gs.player
        cx, cy = item.rect.centerx, item.rect.centery
        color  = delta.get("color", WHITE)

        # ── Escudo bloqueia negativos ─────────────────────────────────────
        is_negative = delta.get("zero_score") or (delta.get("points", 0) < 0)
        if is_negative and p.shield > 0:
            p.shield -= 1
            gs.effects.combo_text(cx, cy - 40, "🛡 BLOQUEADO!", BLUE)
            return

        # ── Pontos ───────────────────────────────────────────────────────
        pts = delta.get("points", 0)

        if delta.get("zero_score"):
            gs.score = 0
            gs.break_combo()
            gs.effects.negative_hit(cx, cy, "💀 ZEROU!")
            p.set_state("sad", 40)
            self.play("cigarette")
            return

        if pts != 0:
            if pts > 0:
                gs.add_score(pts)
            else:
                gs.add_score(pts)  # já aplica multiplier (mas negativo)

        if delta.get("combo"):
            gs.combo += 1
            self._check_combo(cx, cy)
            p.set_state("catch", 12)
            if delta.get("golden"):
                gs.effects.golden_catch(cx, cy)
                self.play("golden")
            else:
                gs.effects.book_catch(cx, cy, pts, color)
                self.play("book")

        if delta.get("combo_break"):
            gs.break_combo()
            gs.effects.negative_hit(cx, cy, f"-{abs(pts)}" if pts else "-50")
            p.set_state("sad", 30)
            self.play("negative")

        if delta.get("shake"):
            gs.effects.shake.trigger()

        if delta.get("time_bonus"):
            gs.time_left = min(gs.time_left + CLOCK_BONUS, GAME_DURATION + 30)
            gs.effects.combo_text(cx, cy - 30, f"+{CLOCK_BONUS}s ⏰", YELLOW)

        if delta.get("shield"):
            p.shield += SHIELD_USES
            gs.effects.combo_text(cx, cy - 30, "🛡 ESCUDO!", BLUE)

        if delta.get("magnet"):
            p.magnet = MAGNET_DURATION
            gs.effects.combo_text(cx, cy - 30, "🧲 ÍMAM!", RED)

    def _check_combo(self, cx, cy):
        gs = self.gs
        c = gs.combo
        if c == 3:
            gs.score += COMBO_3_BONUS
            gs.effects.combo_text(cx, cy - 55, f"COMBO x3! +{COMBO_3_BONUS}", ORANGE)
            self.play("combo")
        elif c == 5:
            gs.score += COMBO_5_BONUS
            gs.effects.combo_text(cx, cy - 55, f"COMBO x5! +{COMBO_5_BONUS}", ORANGE)
            self.play("combo")
        elif c >= COMBO_FEVER_AT and not gs.fever:
            gs.fever = True
            gs.fever_timer = FEVER_DURATION * FPS
            gs.effects.combo_text(SCREEN_W // 2, 110, "🔥 MODO FEBRE! 🔥", GOLD)
            self.play("fever")

        if gs.fever:
            gs.fever_timer -= 0
            # timer atualizado no update principal

    # ── Update do jogo ────────────────────────────────────────────────────────

    def update_game(self, dt: float):
        gs = self.gs
        if gs.paused:
            return

        # Tempo
        gs.time_left -= dt
        if gs.time_left <= 0:
            gs.time_left = 0
            self._end_game()
            return

        # Dificuldade
        gs.phase_timer -= 1
        if gs.phase_timer <= 0:
            gs.phase += 1
            gs.phase_timer = DIFFICULTY_INTERVAL * FPS

        # Febre
        if gs.fever:
            gs.fever_timer -= 1
            if gs.fever_timer <= 0:
                gs.fever = False

        # Input
        keys = pygame.key.get_pressed()
        gs.player.update(keys)

        # Touch target
        if self.touch_target is not None:
            gs.player.move_toward(self.touch_target)

        # Spawn
        self.try_spawn()

        # Itens
        for item in gs.items:
            item.update()
        gs.items = [i for i in gs.items if i.alive]

        # Colisões
        self.check_collisions()

        # Efeitos
        gs.effects.update()
        self.bg.update()

    # ── Fim de partida ────────────────────────────────────────────────────────

    def _end_game(self):
        gs = self.gs
        name = gs.player.name
        self.ranking.submit(name, gs.score, gs.player.avatar_idx)
        self.game_over_screen = GameOverScreen()
        self.scene = "gameover"

    # ── Desenho do jogo ───────────────────────────────────────────────────────

    def draw_game(self):
        gs = self.gs
        surf = self.screen

        # Shake offset
        ox, oy = gs.effects.shake.offset()
        game_surf = pygame.Surface((SCREEN_W, SCREEN_H))

        self.bg.draw(game_surf, fever=gs.fever)

        for item in gs.items:
            item.draw(game_surf)

        gs.player.draw(game_surf)
        gs.effects.draw(game_surf)

        # Linha do chão
        pygame.draw.line(game_surf, (60, 40, 15),
                         (0, SCREEN_H - 15), (SCREEN_W, SCREEN_H - 15), 2)

        surf.blit(game_surf, (ox, oy))

        self.hud.draw(
            surf,
            gs.player.name,
            gs.score,
            gs.time_left,
            gs.combo,
            self.ranking.best_score,
            gs.fever,
            gs.fever_timer,
            gs.player.shield > 0,
            gs.player.magnet > 0,
            gs.paused
        )

        # Botões touch (sempre visíveis)
        self._draw_touch_buttons(surf)

        # Botão mute
        mute_label = "🔇" if self.muted else "🔊"
        mute_font = pygame.font.SysFont("arial", 20)
        mt = mute_font.render(mute_label, True, (200, 200, 200))
        surf.blit(mt, (SCREEN_W - 36, 65))

    def _draw_touch_buttons(self, surf):
        btn_size = 64
        margin = 14
        y = SCREEN_H - btn_size - margin

        # Esquerda
        self._touch_left_rect = pygame.Rect(margin, y, btn_size, btn_size)
        # Direita
        self._touch_right_rect = pygame.Rect(margin * 2 + btn_size, y, btn_size, btn_size)

        for rect, label in [(self._touch_left_rect, "◀"), (self._touch_right_rect, "▶")]:
            s = pygame.Surface((btn_size, btn_size), pygame.SRCALPHA)
            s.fill((255, 255, 255, 40))
            pygame.draw.rect(s, (255, 255, 255, 80), (0, 0, btn_size, btn_size), 2, border_radius=10)
            surf.blit(s, rect.topleft)
            font = pygame.font.SysFont("arial", 28, bold=True)
            t = font.render(label, True, WHITE)
            surf.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))

    # ── Iniciar nova partida ──────────────────────────────────────────────────

    def start_game(self):
        name   = self.menu.name_input.strip() or "Aluno"
        avatar = self.menu.avatar_idx
        player = Player(name, avatar)
        self.gs = GameState(player)
        self.touch_target = None
        self.scene = "game"

    # ── Evento de toque / mouse ───────────────────────────────────────────────

    def handle_touch(self, event):
        if self.scene != "game" or self.gs is None or self.gs.paused:
            return
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = event.pos if hasattr(event, "pos") else (
                int(event.x * SCREEN_W), int(event.y * SCREEN_H)
            )
            if hasattr(self, "_touch_left_rect") and self._touch_left_rect.collidepoint(pos):
                self.touch_target = 0
            elif hasattr(self, "_touch_right_rect") and self._touch_right_rect.collidepoint(pos):
                self.touch_target = SCREEN_W
            else:
                self.touch_target = None
        if event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            self.touch_target = None

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        rank_screen  = None
        how_screen   = None
        go_screen    = None

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Teclas globais
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_m:
                        self.muted = not self.muted
                    if self.scene == "game" and self.gs:
                        if ev.key == pygame.K_p:
                            self.gs.paused = not self.gs.paused
                        if ev.key == pygame.K_ESCAPE:
                            self.scene = "menu"

                self.handle_touch(ev)

            # ── Cenas ──────────────────────────────────────────────────────
            if self.scene == "loading":
                self.loading.draw(self.screen)
                if self.loading.done:
                    self.scene = "menu"

            elif self.scene == "menu":
                action = self.menu.handle(events)
                self.menu.draw(self.screen, self.bg)
                if action == "play":
                    self.start_game()
                elif action == "rank":
                    rank_screen = RankingScreen()
                    self.scene = "ranking"
                elif action == "how":
                    how_screen = HowToPlay()
                    self.scene = "how"
                elif action == "quit":
                    pygame.quit()
                    sys.exit()

            elif self.scene == "ranking":
                rows = self.ranking.top()
                self.bg.update()
                self.bg.draw(self.screen)
                back = rank_screen.handle(events)
                rank_screen.draw(self.screen, self.bg, rows)
                if back:
                    self.scene = "menu"

            elif self.scene == "how":
                self.bg.update()
                self.bg.draw(self.screen)
                back = how_screen.handle(events)
                how_screen.draw(self.screen, self.bg)
                if back:
                    self.scene = "menu"
 
            elif self.scene == "game":
                self.update_game(dt)
                self.draw_game()

            elif self.scene == "gameover":
                if go_screen is None:
                    go_screen = GameOverScreen()
                rows = self.ranking.top()
                action = go_screen.handle(events)
                go_screen.draw(self.screen, self.bg,
                               self.gs.score, self.ranking.best_score, rows)
                if action == "again":
                    go_screen = None
                    self.start_game()
                elif action == "menu":
                    go_screen = None
                    self.scene = "menu"

            pygame.display.flip()


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    game = Game()
    game.run()
