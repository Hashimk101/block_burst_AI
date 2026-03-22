import pygame
import menu
import gui
import boxes

def main():
    pygame.init()

    sw = menu.SIDE_PANEL_WIDTH_HINT = (
        gui.SIDE_PANEL_WIDTH + boxes.col_size * gui.cell_size
        + gui.PICKER_PANEL_WIDTH + gui.RIGHT_MARGIN
    )
    sh = gui.TOP_BAR_HEIGHT + boxes.row_size * gui.cell_size + gui.RIGHT_MARGIN

    screen = pygame.display.set_mode((sw, sh + 30))
    pygame.display.set_caption("Block Blast")

    fonts  = menu.make_fonts()
    clock  = pygame.time.Clock()

    while True:
        result = menu.run_menu(screen, fonts, clock)
        if result == menu.QUIT:
            break
        if result == menu.PLAY:
            gui.run(screen, fonts, clock)   # returns when game ends / HOME pressed

    pygame.quit()

if __name__ == "__main__":
    main()
