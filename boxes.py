row_size = 8
col_size = 8

# ---------------------------------------------------------------------------
# Grid philosophy:
#   grid_obj is a plain 2D list of integers.
#   0           = empty
#   nonzero int = filled (value encodes the color index used at placement time)
#
#   Box instances are only used to look up shape offsets before placement.
#   Once place_block() writes values into grid_obj, the Box is discarded —
#   there is no back-reference from a grid cell to its original Box.
#   This makes line-clearing trivial: just zero out the relevant cells.
# ---------------------------------------------------------------------------
grid_obj = [[0 for _ in range(col_size)] for _ in range(row_size)]

# ---------------------------------------------------------------------------
# Shape definitions
# Each shape is a list of (row_offset, col_offset) relative to the anchor.
# Anchor is always (0, 0) — top-left cell of the bounding box.
# ---------------------------------------------------------------------------
SHAPES = {
    # ── Standard Tetris pieces ───────────────────────────────────────────────

    # I  □□□□  (horizontal)
    "I_H":  [(0,0),(0,1),(0,2),(0,3)],

    # I  vertical
    "I_V":  [(0,0),(1,0),(2,0),(3,0)],

    # O  □□
    #    □□
    "O":    [(0,0),(0,1),(1,0),(1,1)],

    # T  □□□
    #     □
    "T_U":  [(0,0),(0,1),(0,2),(1,1)],
    "T_D":  [(0,1),(1,0),(1,1),(1,2)],
    "T_L":  [(0,0),(1,0),(1,1),(2,0)],
    "T_R":  [(0,1),(1,0),(1,1),(2,1)],

    # S  .□□
    #    □□.
    "S_H":  [(0,1),(0,2),(1,0),(1,1)],
    "S_V":  [(0,0),(1,0),(1,1),(2,1)],

    # Z  □□.
    #    .□□
    "Z_H":  [(0,0),(0,1),(1,1),(1,2)],
    "Z_V":  [(0,1),(1,0),(1,1),(2,0)],

    # L  □.
    #    □.
    #    □□
    "L_U":  [(0,0),(1,0),(2,0),(2,1)],
    "L_D":  [(0,0),(0,1),(1,0),(2,0)],
    "L_L":  [(0,0),(0,1),(0,2),(1,0)],
    "L_R":  [(0,2),(1,0),(1,1),(1,2)],

    # J  .□
    #    .□
    #    □□
    "J_U":  [(0,1),(1,1),(2,0),(2,1)],
    "J_D":  [(0,0),(1,0),(1,1),(1,2)],
    "J_L":  [(0,0),(0,1),(0,2),(1,2)],
    "J_R":  [(0,0),(0,1),(1,0),(2,0)],

    # ── Extra pieces ─────────────────────────────────────────────────────────

    # 3×3 solid square
    "SQ3":  [(r,c) for r in range(3) for c in range(3)],

    # 2×3 rectangle (2 rows, 3 cols)
    "R2x3": [(r,c) for r in range(2) for c in range(3)],

    # 3×2 rectangle (3 rows, 2 cols)
    "R3x2": [(r,c) for r in range(3) for c in range(2)],
}


def get_anchor(block_type):
    """Return the anchor offset (always top-left, i.e. (0,0))."""
    return (0, 0)


def get_cells(block_type, anchor_row, anchor_col):
    """Return absolute (row, col) grid positions for a placed shape."""
    return [(anchor_row + dr, anchor_col + dc) for dr, dc in SHAPES[block_type]]


def is_valid_placement(block_type, anchor_row, anchor_col):
    """True if all cells are inside the grid and currently empty."""
    for r, c in get_cells(block_type, anchor_row, anchor_col):
        if r < 0 or r >= row_size or c < 0 or c >= col_size:
            return False
        if grid_obj[r][c] != 0:
            return False
    return True


def place_block(block_type, anchor_row, anchor_col, value=1):
    """Write a block onto the grid. Returns True on success."""
    if not is_valid_placement(block_type, anchor_row, anchor_col):
        return False
    for r, c in get_cells(block_type, anchor_row, anchor_col):
        grid_obj[r][c] = value
    return True


class Box:
    def __init__(self, block_type):
        if block_type not in SHAPES:
            raise ValueError(f"Unknown block type: '{block_type}'. "
                             f"Valid types: {list(SHAPES.keys())}")
        self.block_type = block_type
        self.anchor_row = None
        self.anchor_col = None

    @property
    def offsets(self):
        """Cell offsets relative to anchor."""
        return SHAPES[self.block_type]

    def place(self, anchor_row, anchor_col, value=1):
        """Place this box on the global grid at the given anchor."""
        self.anchor_row = anchor_row
        self.anchor_col = anchor_col
        return place_block(self.block_type, anchor_row, anchor_col, value)

    def cells(self):
        """Absolute (row, col) positions (requires placement first)."""
        if self.anchor_row is None:
            raise RuntimeError("Box has not been placed yet.")
        return get_cells(self.block_type, self.anchor_row, self.anchor_col)

    def __repr__(self):
        return (f"Box(type={self.block_type}, "
                f"anchor=({self.anchor_row}, {self.anchor_col}))")



def get_3_random_boxes():
    """Return 3 fresh random Box instances."""
    import random
    keys = random.sample(list(SHAPES.keys()), 3)
    return [Box(k) for k in keys]


def reset_grid():
    """Zero out the entire grid (e.g. new game)."""
    for r in range(row_size):
        for c in range(col_size):
            grid_obj[r][c] = 0
