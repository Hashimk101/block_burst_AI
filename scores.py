# scores.py
# Grid cells are plain integers — 0 = empty, any nonzero = filled.
# No Box instances are involved here; clearing is purely about the 2D array.

import boxes


def get_full_rows(grid):
    """Return list of row indices that are completely filled."""
    return [r for r, row in enumerate(grid) if all(cell != 0 for cell in row)]


def get_full_cols(grid):
    """Return list of col indices that are completely filled."""
    col_size = len(grid[0])
    row_size = len(grid)
    return [c for c in range(col_size) if all(grid[r][c] != 0 for r in range(row_size))]


def clear_lines(grid):
    """
    Clear all full rows and columns from the grid in-place.
    Returns (rows_cleared, cols_cleared) as lists of indices.
    """
    full_rows = get_full_rows(grid)
    full_cols = get_full_cols(grid)

    for r in full_rows:
        for c in range(len(grid[r])):
            grid[r][c] = 0

    for c in full_cols:
        for r in range(len(grid)):
            grid[r][c] = 0

    return full_rows, full_cols


def calculate_score(rows_cleared, cols_cleared):
    """
    Score based on total lines cleared (rows + cols) in one move.
    Combo bonus for clearing multiple lines at once.
    """
    total = len(rows_cleared) + len(cols_cleared)
    if total == 0:
        return 0
    base_scores = {1: 100, 2: 300, 3: 500, 4: 800}
    return base_scores.get(total, 800 + (total - 4) * 200)


def process_move(grid):
    """
    Call after placing a block. Clears full lines and returns the score earned.
    """
    rows_cleared, cols_cleared = clear_lines(grid)
    return calculate_score(rows_cleared, cols_cleared), rows_cleared, cols_cleared


def check_game_over(grid, blocks):
    '''
        Check if any of the given blocks can be placed on the grid. If not, game is over.
    '''
    for block in blocks:
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if boxes.is_valid_placement(block.block_type, r, c):
                    return False
    return True

