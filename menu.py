import pygame
import math
import json
import os

# ── Shared color palette (mirrors gui.py) ────────────────────────────────────
BG_DARK      = (10,  10,  20)
BG_PANEL     = (18,  18,  35)
GRID_LINE    = (82,  79, 105)
CELL_EMPTY   = (22,  25,  48)
NEON_BLUE    = (60, 180, 255)
NEON_PURPLE  = (160, 80, 255)
NEON_PINK    = (255, 60, 160)
NEON_CYAN    = (0,  230, 230)
NEON_GREEN   = (60, 255, 160)
SCORE_GOLD   = (255, 210,  60)
SCORE_SILVER = (190, 210, 230)
DIM_WHITE    = (190, 200, 200)
DARK_TEXT    = (130, 120, 145)

HIGHSCORES_FILE = "highscores.json"
MAX_SCORES      = 10

# ── Game-wide AI flag ─────────────────────────────────────────────────────────
ai_enabled = False


# ── Highscore persistence ─────────────────────────────────────────────────────
def load_highscores():
    if os.path.exists(HIGHSCORES_FILE):
        try:
            with open(HIGHSCORES_FILE) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_score(score):
    """Append score, sort descending, keep top MAX_SCORES, write to disk."""
    scores = load_highscores()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:MAX_SCORES]
    with open(HIGHSCORES_FILE, "w") as f:
        json.dump(scores, f)
    return scores


# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_background(screen, tick):
    screen.fill(BG_DARK)
    for row in range(0, screen.get_height(), 24):
        for col in range(0, screen.get_width(), 24):
            pygame.draw.circle(screen, GRID_LINE, (col, row), 1)


def draw_title(screen, fonts, tick):
    cx = screen.get_width() // 2
    pulse = (math.sin(tick * 0.04) + 1) / 2
    color1 = lerp_color(NEON_CYAN,   NEON_BLUE,   pulse)
    color2 = lerp_color(NEON_PINK,   NEON_PURPLE, pulse)

    t1 = fonts['big'].render("BLOCK", True, color1)
    t2 = fonts['big'].render("BLAST", True, color2)
    gap = 10
    total_w = t1.get_width() + t2.get_width() + gap
    y = 30
    screen.blit(t1, (cx - total_w // 2, y))
    screen.blit(t2, (cx - total_w // 2 + t1.get_width() + gap, y))

    sub = fonts['small'].render("block placement puzzle", True, DARK_TEXT)
    screen.blit(sub, (cx - sub.get_width() // 2, y + t1.get_height() + 6))


def draw_button(screen, fonts, rect, label, active=True, highlight=False):
    """Draw a sharp menu button. highlight = hovered."""
    bg    = BG_PANEL
    border= NEON_BLUE  if highlight else (GRID_LINE if active else DARK_TEXT)
    text_c= DIM_WHITE  if active    else DARK_TEXT

    pygame.draw.rect(screen, bg, rect)
    pygame.draw.rect(screen, border, rect, 2 if highlight else 1)

    if highlight:
        hl = pygame.Surface((rect.width, 3), pygame.SRCALPHA)
        hl.fill((*NEON_BLUE, 60))
        screen.blit(hl, rect.topleft)

    surf = fonts['btn'].render(label, True, text_c)
    screen.blit(surf, (rect.centerx - surf.get_width()  // 2,
                        rect.centery - surf.get_height() // 2))


# ── Screens ───────────────────────────────────────────────────────────────────

# Return values from run_menu / run_highscores
PLAY      = "play"
QUIT      = "quit"
MENU      = "menu"


def run_menu(screen, fonts, clock):
    """Main menu. Returns PLAY or QUIT."""
    global ai_enabled
    sw, sh = screen.get_size()
    cx = sw // 2
    btn_w, btn_h = 260, 52
    gap = 16
    start_y = sh // 2 - 65

    btn_play   = pygame.Rect(cx - btn_w // 2, start_y,              btn_w, btn_h)
    btn_scores = pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h)
    btn_ai     = pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h)
    btn_quit   = pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 3, btn_w, btn_h)

    tick = 0
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return QUIT
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return QUIT
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play.collidepoint(mouse):
                    return PLAY
                if btn_scores.collidepoint(mouse):
                    run_highscores(screen, fonts, clock)
                if btn_ai.collidepoint(mouse):
                    ai_enabled = not ai_enabled
                if btn_quit.collidepoint(mouse):
                    return QUIT

        draw_background(screen, tick)
        draw_title(screen, fonts, tick)

        ai_label = f"AI: {'ON  ' if ai_enabled else 'OFF'}"
        ai_color  = NEON_GREEN if ai_enabled else DARK_TEXT

        for btn, label, col in [
            (btn_play,   "PLAY",       None),
            (btn_scores, "HIGHSCORES", None),
            (btn_ai,     ai_label,     ai_color),
            (btn_quit,   "QUIT",       None),
        ]:
            hovered = btn.collidepoint(mouse)
            draw_button(screen, fonts, btn, label, highlight=hovered)
            # Override text color for AI button
            if col is not None:
                surf = fonts['btn'].render(label, True, col)
                screen.blit(surf, (btn.centerx - surf.get_width()  // 2,
                                   btn.centery - surf.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)
        tick += 1


def run_highscores(screen, fonts, clock):
    """Highscores screen. Press ESC or click BACK to return."""
    sw, sh = screen.get_size()
    cx = sw // 2
    btn_back = pygame.Rect(cx - 120, sh - 80, 240, 48)

    tick = 0
    while True:
        mouse = pygame.mouse.get_pos()
        hs = load_highscores()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse):
                    return

        draw_background(screen, tick)

        title = fonts['mid'].render("HIGHSCORES", True, NEON_CYAN)
        screen.blit(title, (cx - title.get_width() // 2, 60))
        pygame.draw.line(screen, NEON_CYAN, (cx - 120, 105), (cx + 120, 105), 1)

        if not hs:
            empty = fonts['small'].render("no scores yet", True, DARK_TEXT)
            screen.blit(empty, (cx - empty.get_width() // 2, sh // 2 - 10))
        else:
            for rank, s in enumerate(hs, 1):
                y = 120 + (rank - 1) * 36
                rank_color = SCORE_GOLD if rank == 1 else (SCORE_SILVER if rank == 2 else DIM_WHITE)
                r_surf = fonts['score_small'].render(f"#{rank}", True, rank_color)
                s_surf = fonts['score_small'].render(f"{s:,}", True, rank_color)
                screen.blit(r_surf, (cx - 130, y))
                screen.blit(s_surf, (cx + 130 - s_surf.get_width(), y))
                pygame.draw.line(screen, GRID_LINE, (cx - 130, y + 28), (cx + 130, y + 28), 1)

        draw_button(screen, fonts, btn_back, "BACK", highlight=btn_back.collidepoint(mouse))

        pygame.display.flip()
        clock.tick(60)
        tick += 1


def make_fonts():
    return {
        'big':         pygame.font.SysFont("impact", 62),
        'mid':         pygame.font.SysFont("impact", 40),
        'btn':         pygame.font.SysFont("impact", 22),
        'small':       pygame.font.SysFont("couriernew", 13, bold=True),
        'score_small': pygame.font.SysFont("impact", 24),
        # game fonts (also used in gui.py)
        'title':       pygame.font.SysFont("impact", 30),
        'score':       pygame.font.SysFont("impact", 36),
        'medium':      pygame.font.SysFont("impact", 26),
        'label':       pygame.font.SysFont("couriernew", 13, bold=True),
        'gameover':    pygame.font.SysFont("impact", 54),
    }
