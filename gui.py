import pygame
import math
import boxes


''' Data related to GUI '''


# size of each cell  (20% smaller: 56 -> 45)
cell_size = 45

# Layout
SIDE_PANEL_WIDTH   = 220
PICKER_PANEL_WIDTH = 130   # piece-choice area right of the grid
TOP_BAR_HEIGHT     = 70
RIGHT_MARGIN       = 20

# Colors — dark arcade theme
BG_DARK      = (10, 10, 20)
BG_PANEL     = (18, 18, 35)
CELL_EMPTY   = (22, 25, 48)
GRID_LINE    = (82, 79, 105)

NEON_BLUE    = (60, 180, 255)
NEON_PURPLE  = (160, 80, 255)
NEON_PINK    = (255, 60, 160)
NEON_CYAN    = (0, 230, 230)

SCORE_GOLD   = (255, 210, 60)
SCORE_SILVER = (190, 210, 230)
DIM_WHITE    = (190, 200, 200)
DARK_TEXT    = (130, 120, 145)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_background(screen):
    screen.fill(BG_DARK)
    for row in range(0, screen.get_height(), 24):
        for col in range(0, screen.get_width(), 24):
            pygame.draw.circle(screen, GRID_LINE, (col, row), 1)


def draw_top_bar(screen, fonts, tick):
    bar_rect = pygame.Rect(0, 0, screen.get_width(), TOP_BAR_HEIGHT)
    pygame.draw.rect(screen, BG_PANEL, bar_rect)

    pulse = (math.sin(tick * 0.03) + 1) / 2
    sep_color = lerp_color(NEON_BLUE, NEON_CYAN, pulse)
    pygame.draw.line(screen, sep_color, (0, TOP_BAR_HEIGHT - 1), (screen.get_width(), TOP_BAR_HEIGHT - 1), 2)

    pygame.draw.line(screen, GRID_LINE,
                     (SIDE_PANEL_WIDTH, 0), (SIDE_PANEL_WIDTH, TOP_BAR_HEIGHT - 1), 1)

    tx = SIDE_PANEL_WIDTH // 2
    t1 = fonts['title'].render("BLOCK", True, NEON_CYAN)
    t2 = fonts['title'].render("BLAST", True, NEON_PINK)
    total_w = t1.get_width() + t2.get_width() + 6
    x0 = tx - total_w // 2
    ty = (TOP_BAR_HEIGHT - t1.get_height()) // 2
    screen.blit(t1, (x0, ty))
    screen.blit(t2, (x0 + t1.get_width() + 6, ty))


def draw_grid(screen, tick):
    gx = SIDE_PANEL_WIDTH
    gy = TOP_BAR_HEIGHT
    gw = boxes.col_size * cell_size
    gh = boxes.row_size * cell_size

    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(gx, gy, gw, gh))

    for row in range(boxes.row_size):
        for col in range(boxes.col_size):
            x = gx + col * cell_size
            y = gy + row * cell_size
            pygame.draw.rect(screen, CELL_EMPTY, pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4))
            hl = pygame.Surface((cell_size - 8, 4), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 14))
            screen.blit(hl, (x + 4, y + 4))

    for r in range(boxes.row_size + 1):
        y = gy + r * cell_size
        pygame.draw.line(screen, GRID_LINE, (gx, y), (gx + gw, y), 1)
    for c in range(boxes.col_size + 1):
        x = gx + c * cell_size
        pygame.draw.line(screen, GRID_LINE, (x, gy), (x, gy + gh), 1)

    pulse = (math.sin(tick * 0.04) + 1) / 2
    border_color = lerp_color(NEON_BLUE, NEON_PURPLE, pulse)
    pygame.draw.rect(screen, border_color, pygame.Rect(gx, gy, gw, gh), 2)

    pygame.draw.line(screen, GRID_LINE,
                     (SIDE_PANEL_WIDTH, TOP_BAR_HEIGHT),
                     (SIDE_PANEL_WIDTH, TOP_BAR_HEIGHT + gh), 1)


def draw_panel(screen, score, fonts, tick):
    pw  = SIDE_PANEL_WIDTH
    pad = 14

    # SCORE card
    sc_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 16, pw - pad * 2, 108)
    pygame.draw.rect(screen, BG_PANEL, sc_rect)
    pygame.draw.rect(screen, NEON_BLUE, sc_rect, 2)

    label = fonts['label'].render("SCORE", True, DIM_WHITE)
    screen.blit(label, (sc_rect.centerx - label.get_width() // 2, sc_rect.y + 14))

    pygame.draw.line(screen, NEON_BLUE,
                     (sc_rect.x + 10, sc_rect.y + 42),
                     (sc_rect.right - 10, sc_rect.y + 42), 1)

    score_str = f"{score:,}"
    s_surf = fonts['score'].render(score_str, True, SCORE_GOLD)
    screen.blit(s_surf, (sc_rect.centerx - s_surf.get_width() // 2, sc_rect.y + 54))

    # BEST card
    bst_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 140, pw - pad * 2, 68)
    pygame.draw.rect(screen, BG_PANEL, bst_rect)
    pygame.draw.rect(screen, NEON_PURPLE, bst_rect, 1)

    bl = fonts['small'].render("BEST", True, DARK_TEXT)
    screen.blit(bl, (bst_rect.centerx - bl.get_width() // 2, bst_rect.y + 10))
    bv = fonts['medium'].render("0", True, SCORE_SILVER)
    screen.blit(bv, (bst_rect.centerx - bv.get_width() // 2, bst_rect.y + 32))

    # HOME placeholder
    home_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 228, pw - pad * 2, 50)
    pygame.draw.rect(screen, BG_PANEL, home_rect)
    pygame.draw.rect(screen, DARK_TEXT, home_rect, 1)
    hl = fonts['small'].render("HOME", True, DARK_TEXT)
    screen.blit(hl, (home_rect.centerx - hl.get_width() // 2,
                     home_rect.centery - hl.get_height() // 2))

    # AI toggle placeholder
    ai_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 294, pw - pad * 2, 50)
    pygame.draw.rect(screen, BG_PANEL, ai_rect)
    pygame.draw.rect(screen, DARK_TEXT, ai_rect, 1)
    al = fonts['small'].render("AI: OFF", True, DARK_TEXT)
    screen.blit(al, (ai_rect.centerx - al.get_width() // 2,
                     ai_rect.centery - al.get_height() // 2))


def draw_picker_panel(screen, fonts):
    gx = SIDE_PANEL_WIDTH + boxes.col_size * cell_size
    gy = TOP_BAR_HEIGHT
    gh = boxes.row_size * cell_size
    pw = PICKER_PANEL_WIDTH
    pad = 12

    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(gx, gy, pw, gh))
    pygame.draw.line(screen, GRID_LINE, (gx, gy), (gx, gy + gh), 1)

    lbl = fonts['small'].render("NEXT", True, DARK_TEXT)
    screen.blit(lbl, (gx + pw // 2 - lbl.get_width() // 2, gy + 10))

    box_w = pw - pad * 2
    box_h = box_w
    spacing = (gh - 30 - 3 * box_h) // 4

    for i in range(3):
        bx = gx + pad
        by = gy + 30 + spacing + i * (box_h + spacing)
        box_rect = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(screen, CELL_EMPTY, box_rect)
        pygame.draw.rect(screen, DARK_TEXT, box_rect, 1)

        cx, cy = box_rect.centerx, box_rect.centery
        arm = 8
        mid_color = (50, 52, 72)
        pygame.draw.line(screen, mid_color, (cx - arm, cy), (cx + arm, cy), 1)
        pygame.draw.line(screen, mid_color, (cx, cy - arm), (cx, cy + arm), 1)


def run(score=0, title="Block Blast"):
    pygame.init()

    screen_width  = SIDE_PANEL_WIDTH + boxes.col_size * cell_size + PICKER_PANEL_WIDTH + RIGHT_MARGIN
    screen_height = TOP_BAR_HEIGHT + boxes.row_size * cell_size + RIGHT_MARGIN

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(title)

    fonts = {
        'title':  pygame.font.SysFont("impact", 30),
        'score':  pygame.font.SysFont("impact", 36),
        'medium': pygame.font.SysFont("impact", 26),
        'label':  pygame.font.SysFont("couriernew", 13, bold=True),
        'small':  pygame.font.SysFont("couriernew", 12, bold=True),
    }

    clock = pygame.time.Clock()
    tick  = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_background(screen)
        draw_top_bar(screen, fonts, tick)
        draw_grid(screen, tick)
        draw_panel(screen, score, fonts, tick)
        draw_picker_panel(screen, fonts)

        pygame.display.flip()
        clock.tick(60)
        tick += 1

    pygame.quit()


if __name__ == "__main__":
    run()
