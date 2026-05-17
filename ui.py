# ui.py — Interface, HUD, menus e telas do Missão Biblioteca

import pygame
import math
import random
from config import *
from player import AVATAR_COLORS


# ── Helpers de fontes ────────────────────────────────────────────────────────

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    names = ["Comic Sans MS", "Arial Rounded MT Bold", "Trebuchet MS", "Arial"]
    for name in names:
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)


def draw_text(surf, text, font, color, cx, cy, shadow=True):
    if shadow:
        sh = font.render(text, True, BLACK)
        surf.blit(sh, (cx - sh.get_width() // 2 + 2, cy - sh.get_height() // 2 + 2))
    img = font.render(text, True, color)
    surf.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))


# ── Fundo animado ─────────────────────────────────────────────────────────────

class Background:
    def __init__(self):
        self.stars = [(random.randint(0, SCREEN_W),
                       random.randint(0, SCREEN_H),
                       random.uniform(0.3, 1.5)) for _ in range(80)]
        self.books_bg = []
        for _ in range(12):
            self.books_bg.append({
                "x": random.randint(0, SCREEN_W),
                "y": random.randint(0, SCREEN_H),
                "angle": random.uniform(0, 360),
                "rot_speed": random.uniform(-0.3, 0.3),
                "color": random.choice([BLUE, GREEN, RED, PURPLE, ORANGE, CYAN, PINK]),
                "size": random.randint(20, 40),
                "alpha": random.randint(30, 70),
            })
        self.t = 0

    def update(self):
        self.t += 1
        for b in self.books_bg:
            b["angle"] += b["rot_speed"]
            b["y"] -= 0.3
            if b["y"] < -60:
                b["y"] = SCREEN_H + 60
                b["x"] = random.randint(0, SCREEN_W)

    def draw(self, surf, fever=False):
        # Gradiente de fundo
        if fever:
            top = (60, 10, 60)
            bot = (20, 5, 40)
        else:
            top = (15, 15, 45)
            bot = (5, 5, 20)

        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))

        # Estrelas
        for sx, sy, bri in self.stars:
            alpha = int(100 + 80 * math.sin(self.t * 0.05 + sx))
            pygame.draw.circle(surf, (255, 255, 255), (int(sx), int(sy)), 1 if bri < 1 else 2)

        # Livros decorativos no fundo
        for b in self.books_bg:
            s = pygame.Surface((b["size"], b["size"] + 10), pygame.SRCALPHA)
            pygame.draw.rect(s, (*b["color"], b["alpha"]), (0, 0, b["size"] - 4, b["size"] + 10), border_radius=4)
            rotated = pygame.transform.rotate(s, b["angle"])
            r = rotated.get_rect(center=(int(b["x"]), int(b["y"])))
            surf.blit(rotated, r)

        # Estantes no rodapé
        shelf_color = (60, 35, 15)
        pygame.draw.rect(surf, shelf_color, (0, SCREEN_H - 15, SCREEN_W, 15))
        pygame.draw.rect(surf, (80, 50, 20), (0, SCREEN_H - 17, SCREEN_W, 3))


# ── HUD em jogo ───────────────────────────────────────────────────────────────

class HUD:
    def __init__(self):
        self.font_big   = get_font(28, bold=True)
        self.font_med   = get_font(20, bold=True)
        self.font_small = get_font(16)
        self.record_val = 0

    def draw(self, surf, player_name, score, time_left, combo,
             best_score, fever, fever_timer, shield, magnet, paused):
        # Barra superior
        bar = pygame.Surface((SCREEN_W, 60), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surf.blit(bar, (0, 0))

        # Nome
        draw_text(surf, player_name, self.font_med, CYAN, 90, 20)

        # Pontuação
        score_color = GOLD if fever else WHITE
        draw_text(surf, f"⭐ {score}", self.font_big, score_color, SCREEN_W // 2, 22)

        # Tempo
        secs = max(0, int(time_left))
        timer_color = RED if secs <= 10 else (YELLOW if secs <= 20 else WHITE)
        pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 200) if secs <= 10 else 1.0
        timer_font = get_font(int(28 * pulse), bold=True)
        draw_text(surf, f"⏱ {secs}s", timer_font, timer_color, SCREEN_W - 90, 22)

        # Combo
        if combo >= 3:
            combo_color = GOLD if combo >= 10 else ORANGE
            draw_text(surf, f"🔥 x{combo}", self.font_med, combo_color, 90, 48)

        # Recorde
        draw_text(surf, f"🏆 {best_score}", self.font_small, (180, 180, 180), SCREEN_W // 2, 50)

        # Modo Febre
        if fever:
            t = pygame.time.get_ticks()
            r = int(200 + 55 * math.sin(t / 80))
            g = int(100 + 60 * math.sin(t / 100))
            fever_color = (r, g, 50)
            draw_text(surf, "🔥 MODO FEBRE! 🔥", get_font(24, bold=True), fever_color,
                      SCREEN_W // 2, 80)
            # Barra de febre
            bar_w = int(200 * fever_timer / (FEVER_DURATION * FPS))
            pygame.draw.rect(surf, (60, 20, 20), (SCREEN_W // 2 - 100, 94, 200, 8), border_radius=4)
            pygame.draw.rect(surf, fever_color, (SCREEN_W // 2 - 100, 94, bar_w, 8), border_radius=4)

        # Ícones de status
        icon_x = SCREEN_W - 30
        if shield:
            draw_text(surf, "🛡", self.font_med, BLUE, icon_x, SCREEN_H - 60)
            icon_x -= 35
        if magnet:
            draw_text(surf, "🧲", self.font_med, RED, icon_x, SCREEN_H - 60)

        # Pausa
        if paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surf.blit(overlay, (0, 0))
            draw_text(surf, "⏸ PAUSADO", get_font(54, bold=True), YELLOW,
                      SCREEN_W // 2, SCREEN_H // 2 - 20)
            draw_text(surf, "Pressione P para continuar", get_font(22), WHITE,
                      SCREEN_W // 2, SCREEN_H // 2 + 40)


# ── Botão genérico ────────────────────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, text, color=BLUE, hover_color=None, font_size=24):
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color or tuple(min(255, c + 40) for c in color)
        self.font = get_font(font_size, bold=True)
        self.hovered = False
        self.anim = 0.0

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self.anim += (target - self.anim) * 0.15

    def draw(self, surf):
        color = tuple(int(self.color[i] + (self.hover_color[i] - self.color[i]) * self.anim)
                      for i in range(3))
        scale = 1.0 + 0.05 * self.anim
        w = int(self.rect.w * scale)
        h = int(self.rect.h * scale)
        rect = pygame.Rect(self.rect.centerx - w // 2, self.rect.centery - h // 2, w, h)
        # Sombra
        shadow_r = rect.move(3, 4)
        pygame.draw.rect(surf, (0, 0, 0, 100), shadow_r, border_radius=12)
        # Corpo
        pygame.draw.rect(surf, color, rect, border_radius=12)
        # Borda
        border = tuple(min(255, c + 60) for c in color)
        pygame.draw.rect(surf, border, rect, 2, border_radius=12)
        # Texto
        draw_text(surf, self.text, self.font, WHITE,
                  self.rect.centerx, self.rect.centery)

    def clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Tela Inicial ──────────────────────────────────────────────────────────────

class MainMenu:
    def __init__(self):
        self.name_input = ""
        self.avatar_idx = 0
        self.active_input = False

        cx = SCREEN_W // 2

        self.btn_play    = Button(cx, 350, 220, 52, "▶ JOGAR",    GREEN,  font_size=26)
        self.btn_rank    = Button(cx, 415, 220, 48, "🏆 RANKING",  BLUE,   font_size=22)
        self.btn_how     = Button(cx, 470, 220, 48, "❓ COMO JOGAR", PURPLE, font_size=20)
        self.btn_quit    = Button(cx, 525, 220, 44, "✕ SAIR",     RED,    font_size=20)
        self.btn_av_l    = Button(cx - 80, 275, 36, 36, "◀", DARKISH)
        self.btn_av_r    = Button(cx + 80, 275, 36, 36, "▶", DARKISH)

        self.input_rect  = pygame.Rect(cx - 130, 195, 260, 44)
        self.font_title  = get_font(56, bold=True)
        self.font_sub    = get_font(20)
        self.font_input  = get_font(22)

        self.t = 0

    def handle(self, events) -> str | None:
        """Retorna 'play', 'rank', 'how', 'quit' ou None."""
        mouse = pygame.mouse.get_pos()
        for btn in [self.btn_play, self.btn_rank, self.btn_how, self.btn_quit,
                    self.btn_av_l, self.btn_av_r]:
            btn.update(mouse)

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(ev.pos):
                    self.active_input = True
                else:
                    self.active_input = False

            if ev.type == pygame.KEYDOWN and self.active_input:
                if ev.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif ev.key == pygame.K_RETURN:
                    self.active_input = False
                elif len(self.name_input) < 16 and ev.unicode.isprintable():
                    self.name_input += ev.unicode

            if self.btn_play.clicked(ev):
                if not self.name_input.strip():
                    self.name_input = "Aluno"
                return "play"
            if self.btn_rank.clicked(ev):
                return "rank"
            if self.btn_how.clicked(ev):
                return "how"
            if self.btn_quit.clicked(ev):
                return "quit"
            if self.btn_av_l.clicked(ev):
                self.avatar_idx = (self.avatar_idx - 1) % len(AVATAR_COLORS)
            if self.btn_av_r.clicked(ev):
                self.avatar_idx = (self.avatar_idx + 1) % len(AVATAR_COLORS)

        return None

    def draw(self, surf, bg: Background):
        self.t += 1
        bg.update()
        bg.draw(surf)

        cx = SCREEN_W // 2

        # Título
        bob = int(5 * math.sin(self.t * 0.05))
        t_color = (
            int(200 + 55 * math.sin(self.t * 0.04)),
            int(200 + 55 * math.sin(self.t * 0.04 + 2)),
            255
        )
        draw_text(surf, "📚 MISSÃO BIBLIOTECA", self.font_title, t_color, cx, 80 + bob)
        draw_text(surf, "Pegue os livros e suba no ranking!", self.font_sub, (180, 220, 255), cx, 128)

        # Campo de nome
        border_color = CYAN if self.active_input else (100, 100, 140)
        pygame.draw.rect(surf, (20, 20, 50), self.input_rect, border_radius=10)
        pygame.draw.rect(surf, border_color, self.input_rect, 2, border_radius=10)
        draw_text(surf, "Seu nome:", self.font_sub, (160, 160, 200), cx, 188)
        display_name = self.name_input + ("|" if self.active_input and self.t % 30 < 15 else "")
        draw_text(surf, display_name or "Digite seu nome...", self.font_input,
                  WHITE if self.name_input else (80, 80, 100), cx, 218)

        # Seleção de avatar
        draw_text(surf, "Avatar:", self.font_sub, (160, 160, 200), cx, 255)
        color = AVATAR_COLORS[self.avatar_idx]
        pygame.draw.circle(surf, color, (cx, 275), 22)
        pygame.draw.circle(surf, WHITE, (cx, 275), 22, 2)
        self.btn_av_l.draw(surf)
        self.btn_av_r.draw(surf)

        for btn in [self.btn_play, self.btn_rank, self.btn_how, self.btn_quit]:
            btn.draw(surf)


# ── Tela de Ranking ───────────────────────────────────────────────────────────

class RankingScreen:
    def __init__(self):
        self.btn_back = Button(SCREEN_W // 2, 555, 200, 46, "← VOLTAR", BLUE)
        self.font_title = get_font(40, bold=True)
        self.font_row   = get_font(22)
        self.font_head  = get_font(18)

    def handle(self, events) -> bool:
        mouse = pygame.mouse.get_pos()
        self.btn_back.update(mouse)
        for ev in events:
            if self.btn_back.clicked(ev):
                return True
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return True
        return False

    def draw(self, surf, bg: Background, rows: list):
        bg.draw(surf)
        cx = SCREEN_W // 2

        # Painel
        panel = pygame.Surface((500, 420), pygame.SRCALPHA)
        panel.fill((10, 10, 40, 200))
        pygame.draw.rect(panel, GOLD, (0, 0, 500, 420), 2, border_radius=12)
        surf.blit(panel, (cx - 250, 70))

        draw_text(surf, "🏆 RANKING TOP 5", self.font_title, GOLD, cx, 100)

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, (name, score, date) in enumerate(rows):
            y = 165 + i * 58
            color = GOLD if i == 0 else (WHITE if i < 3 else (180, 180, 180))
            draw_text(surf, f"{medals[i]}  {name}", self.font_row, color, cx - 60, y)
            draw_text(surf, f"{score} pts", self.font_row, color, cx + 150, y)
            draw_text(surf, date, self.font_head, (140, 140, 180), cx + 150, y + 22)

        if not rows:
            draw_text(surf, "Nenhum registro ainda!", self.font_row,
                      (150, 150, 200), cx, 260)

        self.btn_back.draw(surf)


# ── Tela de Como Jogar ────────────────────────────────────────────────────────

class HowToPlay:
    def __init__(self):
        self.btn_back = Button(SCREEN_W // 2, 555, 200, 46, "← VOLTAR", BLUE)
        self.font_title = get_font(36, bold=True)
        self.font_body  = get_font(17)

    TIPS = [
        ("⬅ ➡  Setas / A,D", "Mover o personagem"),
        ("📚 Livros",         "Pegue para ganhar pontos"),
        ("📱 Celular",        "Perde 50 pontos!"),
        ("🚬 Cigarro",        "ZERA sua pontuação!"),
        ("⭐ Livro Dourado",  "+100 pts — some em 3s!"),
        ("🔥 3 seguidos",     "Bônus de combo!"),
        ("🔥×10 FEBRE",       "Pontos dobrados por 5s!"),
        ("⏰ Relógio",        "+10 segundos extras"),
        ("🛡 Escudo",         "Bloqueia 1 item negativo"),
        ("🧲 Ímã",           "Atrai livros próximos"),
        ("P",                 "Pausar / retomar"),
        ("M",                 "Mutar / ativar som"),
    ]

    def handle(self, events) -> bool:
        mouse = pygame.mouse.get_pos()
        self.btn_back.update(mouse)
        for ev in events:
            if self.btn_back.clicked(ev):
                return True
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return True
        return False

    def draw(self, surf, bg: Background):
        bg.draw(surf)
        cx = SCREEN_W // 2

        panel = pygame.Surface((560, 450), pygame.SRCALPHA)
        panel.fill((10, 10, 40, 210))
        pygame.draw.rect(panel, CYAN, (0, 0, 560, 450), 2, border_radius=12)
        surf.blit(panel, (cx - 280, 55))

        draw_text(surf, "❓ COMO JOGAR", self.font_title, CYAN, cx, 82)

        cols = 2
        per_col = (len(self.TIPS) + 1) // cols
        for i, (key, desc) in enumerate(self.TIPS):
            col = i // per_col
            row = i % per_col
            x = cx - 240 + col * 290
            y = 130 + row * 38
            draw_text(surf, key,  self.font_body, YELLOW, x + 100, y)
            draw_text(surf, desc, self.font_body, WHITE,  x + 240, y)

        self.btn_back.draw(surf)


# ── Tela de Game Over ─────────────────────────────────────────────────────────

class GameOverScreen:
    def __init__(self):
        cx = SCREEN_W // 2
        self.btn_again = Button(cx - 115, 470, 200, 50, "🔄 JOGAR NOVAMENTE", GREEN, font_size=18)
        self.btn_menu  = Button(cx + 115, 470, 180, 50, "🏠 MENU",           BLUE,  font_size=20)
        self.font_big   = get_font(52, bold=True)
        self.font_med   = get_font(26, bold=True)
        self.font_small = get_font(18)
        self.t = 0

    def handle(self, events) -> str | None:
        mouse = pygame.mouse.get_pos()
        self.btn_again.update(mouse)
        self.btn_menu.update(mouse)
        for ev in events:
            if self.btn_again.clicked(ev):
                return "again"
            if self.btn_menu.clicked(ev):
                return "menu"
        return None

    def draw(self, surf, bg: Background, score, best, rows):
        self.t += 1
        bg.update()
        bg.draw(surf)
        cx = SCREEN_W // 2

        panel = pygame.Surface((520, 360), pygame.SRCALPHA)
        panel.fill((10, 5, 30, 220))
        pygame.draw.rect(panel, GOLD, (0, 0, 520, 360), 2, border_radius=16)
        surf.blit(panel, (cx - 260, 80))

        draw_text(surf, "GAME OVER", self.font_big, RED, cx, 115)

        is_new_record = score >= best and score > 0
        score_color = GOLD if is_new_record else WHITE
        draw_text(surf, f"Pontuação: {score}", self.font_med, score_color, cx, 175)
        if is_new_record:
            pulse = int(200 + 55 * math.sin(self.t * 0.12))
            draw_text(surf, "🎉 NOVO RECORDE! 🎉", get_font(24, bold=True),
                      (pulse, pulse, 0), cx, 210)

        # Top 3 do ranking
        draw_text(surf, "— TOP RANKING —", self.font_small, (180, 180, 220), cx, 250)
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, sc, _) in enumerate(rows[:3]):
            y = 275 + i * 32
            c = GOLD if i == 0 else WHITE
            draw_text(surf, f"{medals[i]} {name} — {sc}", self.font_small, c, cx, y)

        self.btn_again.draw(surf)
        self.btn_menu.draw(surf)


# ── Tela de Loading ───────────────────────────────────────────────────────────

class LoadingScreen:
    def __init__(self):
        self.font = get_font(32, bold=True)
        self.sub  = get_font(18)
        self.t    = 0

    def draw(self, surf):
        surf.fill(DARK)
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        
        # Correção: Garante que o valor RGB não ultrapasse 255
        dynamic_color = (min(255, 100 + self.t * 3), 150, 255)
        
        draw_text(surf, "📚 MISSÃO BIBLIOTECA", self.font,
                  dynamic_color, cx, cy - 40)
                  
        draw_text(surf, "Carregando...", self.sub, WHITE, cx, cy + 10)
        
        # Barra de progresso
        progress = min(1.0, self.t / 60)
        pygame.draw.rect(surf, (30, 30, 80), (cx - 150, cy + 40, 300, 16), border_radius=8)
        pygame.draw.rect(surf, CYAN, (cx - 150, cy + 40, int(300 * progress), 16), border_radius=8)
        
        self.t += 1

    @property
    def done(self):
        return self.t >= 65
