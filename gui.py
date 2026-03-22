import pygame
import math
import boxes
import scores
import menu as _menu


# ── Cell size ────────────────────────────────────────────────────────────────
cell_size = 45

# ── Layout ───────────────────────────────────────────────────────────────────
SIDE_PANEL_WIDTH   = 220
PICKER_PANEL_WIDTH = 130
TOP_BAR_HEIGHT     = 70
RIGHT_MARGIN       = 20

# ── Colors ───────────────────────────────────────────────────────────────────
BG_DARK      = (10, 10, 20)
BG_PANEL     = (18, 18, 35)
CELL_EMPTY   = (22, 25, 48)
GRID_LINE    = (82, 79, 105)

NEON_BLUE    = (60, 180, 255)
NEON_PURPLE  = (160, 80, 255)
NEON_PINK    = (255, 60, 160)
NEON_CYAN    = (0, 230, 230)
NEON_GREEN   = (60, 255, 160)

SCORE_GOLD   = (255, 210, 60)
SCORE_SILVER = (190, 210, 230)
DIM_WHITE    = (190, 200, 200)
DARK_TEXT    = (130, 120, 145)

# One color per picker slot (also used when the block lands on the grid)
PICKER_COLORS = [
    (60,  200, 255),
    (255, 100, 180),
    (100, 255, 160),
]


# ── Clear animation ──────────────────────────────────────────────────────────
FLASH_DURATION = 18   # frames the flash lasts

# ── Helpers ──────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def grid_origin():
    """Top-left pixel of the grid."""
    return SIDE_PANEL_WIDTH, TOP_BAR_HEIGHT


def pixel_to_cell(px, py):
    """Convert a screen pixel to (row, col), or None if outside the grid."""
    gx, gy = grid_origin()
    col = (px - gx) // cell_size
    row = (py - gy) // cell_size
    if 0 <= row < boxes.row_size and 0 <= col < boxes.col_size:
        return row, col
    return None


def picker_slot_rects():
    """Return the three picker slot pygame.Rect objects."""
    gx = SIDE_PANEL_WIDTH + boxes.col_size * cell_size
    gy = TOP_BAR_HEIGHT
    gh = boxes.row_size * cell_size
    pw = PICKER_PANEL_WIDTH
    pad = 10
    box_w = pw - pad * 2
    box_h = box_w
    spacing = (gh - 26 - 3 * box_h) // 4
    rects = []
    for i in range(3):
        bx = gx + pad
        by = gy + 26 + spacing + i * (box_h + spacing)
        rects.append(pygame.Rect(bx, by, box_w, box_h))
    return rects


# ── Drawing helpers ──────────────────────────────────────────────────────────
def draw_mini_shape(surface, offsets, color, cx, cy, mini_cell=12):
    """Draw a shape preview centered at (cx, cy) with mini_cell-sized cells."""
    if not offsets:
        return
    rows = [r for r, c in offsets]
    cols = [c for r, c in offsets]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    shape_w = (max_c - min_c + 1) * mini_cell
    shape_h = (max_r - min_r + 1) * mini_cell
    ox = cx - shape_w // 2
    oy = cy - shape_h // 2
    bright = tuple(min(v + 60, 255) for v in color)
    for r, c in offsets:
        px = ox + (c - min_c) * mini_cell
        py = oy + (r - min_r) * mini_cell
        pygame.draw.rect(surface, color,
                         pygame.Rect(px + 1, py + 1, mini_cell - 2, mini_cell - 2))
        hl = pygame.Surface((mini_cell - 2, 3), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 50))
        surface.blit(hl, (px + 1, py + 1))
        pygame.draw.rect(surface, bright, pygame.Rect(px, py, mini_cell, mini_cell), 1)


def draw_full_shape(surface, offsets, color, anchor_px, anchor_py, alpha=255):
    """Draw a shape at full cell_size, anchor_px/py = top-left of bounding box."""
    bright = tuple(min(v + 70, 255) for v in color)
    for dr, dc in offsets:
        px = anchor_px + dc * cell_size
        py = anchor_py + dr * cell_size
        inner = pygame.Rect(px + 2, py + 2, cell_size - 4, cell_size - 4)
        if alpha < 255:
            s = pygame.Surface((cell_size - 4, cell_size - 4), pygame.SRCALPHA)
            s.fill((*color, alpha))
            surface.blit(s, inner.topleft)
        else:
            pygame.draw.rect(surface, color, inner)
            hl = pygame.Surface((cell_size - 8, 4), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 60))
            surface.blit(hl, (px + 4, py + 4))
        pygame.draw.rect(surface, bright, pygame.Rect(px, py, cell_size, cell_size), 1)


def draw_background(screen):
    screen.fill(BG_DARK)
    for row in range(0, screen.get_height(), 24):
        for col in range(0, screen.get_width(), 24):
            pygame.draw.circle(screen, GRID_LINE, (col, row), 1)


def draw_top_bar(screen, fonts, tick):
    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(0, 0, screen.get_width(), TOP_BAR_HEIGHT))
    pulse = (math.sin(tick * 0.03) + 1) / 2
    sep_color = lerp_color(NEON_BLUE, NEON_CYAN, pulse)
    pygame.draw.line(screen, sep_color, (0, TOP_BAR_HEIGHT - 1),
                     (screen.get_width(), TOP_BAR_HEIGHT - 1), 2)
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


def draw_grid(screen, tick, dragging=None, drag_color=None,
              flash_rows=(), flash_cols=(), flash_t=0):
    """Draw the grid. If dragging, show ghost overlay for the hovered cell."""
    gx, gy = grid_origin()
    gw = boxes.col_size * cell_size
    gh = boxes.row_size * cell_size

    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(gx, gy, gw, gh))

    # Compute ghost anchor from mouse if dragging
    ghost_cells = set()
    valid_ghost = False
    if dragging is not None:
        mx, my = pygame.mouse.get_pos()
        offsets = dragging.offsets
        rows = [r for r, c in offsets]
        cols = [c for r, c in offsets]
        min_r, min_c = min(rows), min(cols)
        span_r = max(rows) - min_r
        span_c = max(cols) - min_c
        cell = pixel_to_cell(mx, my)
        if cell:
            cr, cc = cell
            # anchor so the shape's center cell tracks the mouse
            anchor_r = cr - (min_r + span_r // 2)
            anchor_c = cc - (min_c + span_c // 2)
            candidate = [(anchor_r + dr, anchor_c + dc) for dr, dc in offsets]
            all_inside = all(0 <= r < boxes.row_size and 0 <= c < boxes.col_size
                             for r, c in candidate)
            all_empty  = all(boxes.grid_obj[r][c] == 0
                             for r, c in candidate if 0 <= r < boxes.row_size and 0 <= c < boxes.col_size)
            valid_ghost = all_inside and all_empty
            ghost_cells = set(candidate)

    # Draw cells
    for row in range(boxes.row_size):
        for col in range(boxes.col_size):
            x = gx + col * cell_size
            y = gy + row * cell_size
            val = boxes.grid_obj[row][col]

            # Flash overlay for cleared lines (drawn on top regardless of val)
            in_flash = (row in flash_rows or col in flash_cols)

            if val != 0:
                color = PICKER_COLORS[(val - 1) % len(PICKER_COLORS)]
                draw_full_shape(screen, [(0, 0)], color, x, y)
            elif (row, col) in ghost_cells:
                shade = NEON_GREEN if valid_ghost else (180, 60, 60)
                s = pygame.Surface((cell_size - 4, cell_size - 4), pygame.SRCALPHA)
                s.fill((*shade, 80))
                screen.blit(s, (x + 2, y + 2))
                pygame.draw.rect(screen, shade, pygame.Rect(x, y, cell_size, cell_size), 1)
            else:
                pygame.draw.rect(screen, CELL_EMPTY,
                                 pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4))
                hl = pygame.Surface((cell_size - 8, 4), pygame.SRCALPHA)
                hl.fill((255, 255, 255, 14))
                screen.blit(hl, (x + 4, y + 4))

            if in_flash and flash_t > 0:
                # White flash that fades out
                alpha = int(220 * (flash_t / FLASH_DURATION))
                fs = pygame.Surface((cell_size - 2, cell_size - 2), pygame.SRCALPHA)
                fs.fill((255, 255, 255, alpha))
                screen.blit(fs, (x + 1, y + 1))

    # Grid lines
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

    return ghost_cells, valid_ghost


def draw_panel(screen, score, best, fonts, tick, ai_enabled=False):
    pw  = SIDE_PANEL_WIDTH
    pad = 14

    sc_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 16, pw - pad * 2, 108)
    pygame.draw.rect(screen, BG_PANEL, sc_rect)
    pygame.draw.rect(screen, NEON_BLUE, sc_rect, 2)
    label = fonts['label'].render("SCORE", True, DIM_WHITE)
    screen.blit(label, (sc_rect.centerx - label.get_width() // 2, sc_rect.y + 14))
    pygame.draw.line(screen, NEON_BLUE,
                     (sc_rect.x + 10, sc_rect.y + 42), (sc_rect.right - 10, sc_rect.y + 42), 1)
    s_surf = fonts['score'].render(f"{score:,}", True, SCORE_GOLD)
    screen.blit(s_surf, (sc_rect.centerx - s_surf.get_width() // 2, sc_rect.y + 54))

    bst_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 140, pw - pad * 2, 68)
    pygame.draw.rect(screen, BG_PANEL, bst_rect)
    pygame.draw.rect(screen, NEON_PURPLE, bst_rect, 1)
    bl = fonts['small'].render("BEST", True, DARK_TEXT)
    screen.blit(bl, (bst_rect.centerx - bl.get_width() // 2, bst_rect.y + 10))
    bv = fonts['medium'].render(f"{best:,}", True, SCORE_SILVER)
    screen.blit(bv, (bst_rect.centerx - bv.get_width() // 2, bst_rect.y + 32))

    # HOME button — active, clickable
    home_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 228, pw - pad * 2, 50)
    mx, my = pygame.mouse.get_pos()
    home_hov = home_rect.collidepoint(mx, my)
    home_border = NEON_CYAN if home_hov else DARK_TEXT
    pygame.draw.rect(screen, BG_PANEL, home_rect)
    pygame.draw.rect(screen, home_border, home_rect, 2 if home_hov else 1)
    hl = fonts['small'].render("HOME", True, NEON_CYAN if home_hov else DARK_TEXT)
    screen.blit(hl, (home_rect.centerx - hl.get_width() // 2,
                     home_rect.centery - hl.get_height() // 2))

    # AI toggle — glows green when on
    ai_rect = pygame.Rect(pad, TOP_BAR_HEIGHT + 294, pw - pad * 2, 50)
    ai_hov    = ai_rect.collidepoint(mx, my)
    ai_color  = NEON_GREEN if ai_enabled else DARK_TEXT
    ai_border = NEON_GREEN if ai_enabled else (NEON_BLUE if ai_hov else DARK_TEXT)
    pygame.draw.rect(screen, BG_PANEL, ai_rect)
    pygame.draw.rect(screen, ai_border, ai_rect, 2 if (ai_enabled or ai_hov) else 1)
    ai_label = f"AI: {'ON ' if ai_enabled else 'OFF'}"
    al = fonts['small'].render(ai_label, True, ai_color)
    screen.blit(al, (ai_rect.centerx - al.get_width() // 2,
                     ai_rect.centery - al.get_height() // 2))

    return home_rect, ai_rect


def draw_picker_panel(screen, fonts, picked_boxes, dragging_idx):
    gx = SIDE_PANEL_WIDTH + boxes.col_size * cell_size
    gy = TOP_BAR_HEIGHT
    gh = boxes.row_size * cell_size
    pw = PICKER_PANEL_WIDTH

    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(gx, gy, pw, gh))
    pygame.draw.line(screen, GRID_LINE, (gx, gy), (gx, gy + gh), 1)
    lbl = fonts['small'].render("NEXT", True, DARK_TEXT)
    screen.blit(lbl, (gx + pw // 2 - lbl.get_width() // 2, gy + 8))

    rects = picker_slot_rects()
    for i, (slot_rect, box) in enumerate(zip(rects, picked_boxes)):
        if box is None or i == dragging_idx:
            # Empty / being dragged — draw dimmed slot
            pygame.draw.rect(screen, CELL_EMPTY, slot_rect)
            pygame.draw.rect(screen, DARK_TEXT, slot_rect, 1)
            continue
        pygame.draw.rect(screen, CELL_EMPTY, slot_rect)
        pygame.draw.rect(screen, DARK_TEXT, slot_rect, 1)
        color = PICKER_COLORS[i % len(PICKER_COLORS)]
        draw_mini_shape(screen, box.offsets, color,
                        slot_rect.centerx, slot_rect.centery, mini_cell=12)


def draw_dragged_piece(screen, box, color, mouse_pos):
    """Draw the piece at full cell size, floating under the cursor."""
    mx, my = mouse_pos
    offsets = box.offsets
    rows = [r for r, c in offsets]
    cols = [c for r, c in offsets]
    min_r, min_c = min(rows), min(cols)
    span_r = max(rows) - min_r
    span_c = max(cols) - min_c
    anchor_px = mx - (min_c + span_c // 2) * cell_size - cell_size // 2
    anchor_py = my - (min_r + span_r // 2) * cell_size - cell_size // 2
    draw_full_shape(screen, offsets, color, anchor_px, anchor_py, alpha=200)


def draw_game_over(screen, fonts, score):
    """Dark overlay with GAME OVER text and final score."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    cx = screen.get_width()  // 2
    cy = screen.get_height() // 2

    go_surf = fonts['gameover'].render("GAME OVER", True, NEON_PINK)
    screen.blit(go_surf, (cx - go_surf.get_width() // 2, cy - 60))

    sc_surf = fonts['title'].render(f"SCORE: {score:,}", True, SCORE_GOLD)
    screen.blit(sc_surf, (cx - sc_surf.get_width() // 2, cy + 10))

    hint = fonts['small'].render("press ESC to quit", True, DARK_TEXT)
    screen.blit(hint, (cx - hint.get_width() // 2, cy + 60))


# ── Placement logic ──────────────────────────────────────────────────────────
def try_place(box, mouse_pos, color_idx):
    """Try to place box on grid. Returns True on success."""
    mx, my = mouse_pos
    offsets = box.offsets
    rows = [r for r, c in offsets]
    cols = [c for r, c in offsets]
    min_r, min_c = min(rows), min(cols)
    span_r = max(rows) - min_r
    span_c = max(cols) - min_c
    cell = pixel_to_cell(mx, my)
    if cell is None:
        return False
    cr, cc = cell
    anchor_r = cr - (min_r + span_r // 2)
    anchor_c = cc - (min_c + span_c // 2)
    return boxes.place_block(box.block_type, anchor_r, anchor_c, value=color_idx + 1)


# ── Main game loop ────────────────────────────────────────────────────────────
def run(screen, fonts, clock):
    """
    Run one game session.
    Returns when the player goes to menu (HOME button, game over, or ESC).
    Score is saved before returning.
    """

    boxes.reset_grid()

    score        = 0
    best         = max(_menu.load_highscores()[:1] or [0])
    picked_boxes = boxes.get_3_random_boxes(boxes.grid_obj)

    dragging_idx   = None
    dragging_box   = None
    dragging_color = None

    flash_rows = []
    flash_cols = []
    flash_t    = 0

    game_over        = False
    go_timer         = 0       # frames to show game-over overlay before returning
    GO_LINGER        = 120     # 2 seconds at 60fps

    # AI state
    AI_STEP_DELAY = int(30 * 1.2)  # frames between AI moves (~0.5s at 60fps), slowed by 20%
    ai_timer      = 0          # counts up; fires when >= AI_STEP_DELAY
    ai_pending    = None       # (box_idx, anchor_r, anchor_c) queued move

    tick = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _menu.save_score(score)
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _menu.save_score(score)
                return

            if game_over:
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(picker_slot_rects()):
                    if rect.collidepoint(mouse_pos) and picked_boxes[i] is not None:
                        dragging_idx   = i
                        dragging_box   = picked_boxes[i]
                        dragging_color = PICKER_COLORS[i % len(PICKER_COLORS)]
                        break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_box is not None:
                    placed = try_place(dragging_box, mouse_pos, dragging_idx)
                    if placed:
                        picked_boxes[dragging_idx] = None
                        if all(b is None for b in picked_boxes):
                            picked_boxes = boxes.get_3_random_boxes(boxes.grid_obj)

                        pts, cleared_rows, cleared_cols = scores.process_move(boxes.grid_obj)
                        if pts > 0:
                            score += pts
                            best   = max(best, score)
                            flash_rows = cleared_rows
                            flash_cols = cleared_cols
                            flash_t    = FLASH_DURATION

                        if scores.check_game_over(boxes.grid_obj, picked_boxes):
                            game_over = True

                # Check HOME / AI clicks (panel returns their rects)
                elif not dragging_box:
                    # We draw panel each frame; re-compute rects here for hit testing
                    pad = 14
                    pw  = SIDE_PANEL_WIDTH
                    home_r = pygame.Rect(pad, TOP_BAR_HEIGHT + 228, pw - pad * 2, 50)
                    ai_r   = pygame.Rect(pad, TOP_BAR_HEIGHT + 294, pw - pad * 2, 50)
                    if home_r.collidepoint(mouse_pos):
                        _menu.save_score(score)
                        return
                    if ai_r.collidepoint(mouse_pos):
                        _menu.ai_enabled = not _menu.ai_enabled

                dragging_idx   = None
                dragging_box   = None
                dragging_color = None

        # Game-over linger then return to menu
        if game_over:
            go_timer += 1
            if go_timer >= GO_LINGER:
                _menu.save_score(score)
                return

        if not game_over and scores.check_game_over(boxes.grid_obj, picked_boxes):
            game_over = True

        if flash_t > 0:
            flash_t -= 1
        else:
            flash_rows = []
            flash_cols = []

        # ── AI step ──────────────────────────────────────────────────────────
        if _menu.ai_enabled and not game_over and dragging_box is None:
            ai_timer += 1
            if ai_timer >= AI_STEP_DELAY:
                ai_timer = 0
                try:
                    from ai_for_game import get_ai_action
                    result = get_ai_action(boxes.grid_obj, picked_boxes)
                    if result is not None:
                        box_idx, anchor_r, anchor_c = result
                        box = picked_boxes[box_idx]
                        if box is not None:
                            placed = boxes.place_block(
                                box.block_type, anchor_r, anchor_c,
                                value=box_idx + 1
                            )
                            if placed:
                                picked_boxes[box_idx] = None
                                if all(b is None for b in picked_boxes):
                                    picked_boxes = boxes.get_3_random_boxes(boxes.grid_obj)
                                pts, cleared_rows, cleared_cols = scores.process_move(boxes.grid_obj)
                                if pts > 0:
                                    score += pts
                                    best   = max(best, score)
                                    flash_rows = cleared_rows
                                    flash_cols = cleared_cols
                                    flash_t    = FLASH_DURATION
                                if scores.check_game_over(boxes.grid_obj, picked_boxes):
                                    game_over = True
                except Exception as e:
                    # Model not trained yet — silently skip
                    pass

        # ── Draw ──
        draw_background(screen)
        draw_top_bar(screen, fonts, tick)
        draw_grid(screen, tick,
                  dragging=dragging_box, drag_color=dragging_color,
                  flash_rows=flash_rows, flash_cols=flash_cols, flash_t=flash_t)
        draw_panel(screen, score, best, fonts, tick,
                   ai_enabled=_menu.ai_enabled)
        draw_picker_panel(screen, fonts, picked_boxes, dragging_idx)

        if dragging_box is not None and not game_over:
            draw_dragged_piece(screen, dragging_box, dragging_color, mouse_pos)

        if game_over:
            # Fade-out overlay + message
            fade = min(1.0, go_timer / 30)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(160 * fade)))
            screen.blit(overlay, (0, 0))

            if fade > 0.4:
                cx = screen.get_width()  // 2
                cy = screen.get_height() // 2
                go_s = fonts['gameover'].render("GAME OVER", True, NEON_PINK)
                screen.blit(go_s, (cx - go_s.get_width() // 2, cy - 60))
                sc_s = fonts['title'].render(f"SCORE: {score:,}", True, SCORE_GOLD)
                screen.blit(sc_s, (cx - sc_s.get_width() // 2, cy + 10))
                hint = fonts['small'].render("returning to menu...", True, DARK_TEXT)
                screen.blit(hint, (cx - hint.get_width() // 2, cy + 60))

        pygame.display.flip()
        clock.tick(60)
        tick += 1
