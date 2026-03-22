import gymnasium as gym
from gymnasium import spaces
import numpy as np
import boxes
import scores
from boxes import grid_obj, row_size, col_size, get_3_random_boxes, reset_grid


class BlockBurstEnv(gym.Env):
    metadata = {}
    def __init__(self):
        self.n_actions = 3 * row_size * col_size  # 3 boxes to place in grid
        self.action_space = spaces.Discrete(self.n_actions)

        self.observation_space = spaces.Dict(
            {
                "obs": spaces.Box(low=0, high=1, shape=(row_size * col_size * 4,), dtype=np.float32),
                "action_mask": spaces.Box(low=0, high=1, shape=(self.n_actions,), dtype=bool)
            }
        )

        self._grid = [[0 for _ in range(col_size)] for _ in range(row_size)]
        self._boxes = []
        self.reset()



    def _is_valid(self, block_type, anchor_row, anchor_col):
        """Check if a block can be placed at the given anchor."""
        for r, c in boxes.get_cells(block_type, anchor_row, anchor_col):
            if r < 0 or r >= row_size or c < 0 or c >= col_size:
                return False
            if self._grid[r][c] != 0:
                return False
        return True

    def _place(self, block_type, anchor_row, anchor_col, value=1):
        """Write a block onto the grid. Returns True on success."""
        if not self._is_valid(block_type, anchor_row, anchor_col):
            return False
        for r, c in boxes.get_cells(block_type, anchor_row, anchor_col):
            self._grid[r][c] = value
        return True


    def _check_game_over(self):
        """Game is over if no valid _placements remain."""
        for block in self._boxes:
            if block is None:
                continue
            for r in range(row_size):
                for c in range(col_size):
                    if self._is_valid(block.block_type, r, c):
                        return False
        return True


    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._grid  = [[0] * boxes.col_size for _ in range(boxes.row_size)]
        self._boxes = boxes.get_3_random_boxes(self._grid)
        return self._get_obs(), {}

    def decode_action(self, action):
        box_idx = action // (row_size * col_size)
        cell_idx = action % (row_size * col_size)
        row = cell_idx // col_size
        col = cell_idx % col_size
        return box_idx, row, col

    def get_action_mask(self):
        mask = np.zeros(self.n_actions, dtype=bool)
        for box_idx, box in enumerate(self._boxes):
            if box is None:
                continue
            for r in range(row_size):
                for c in range(col_size):
                    if self._is_valid(box.block_type, r, c):
                        action_idx = box_idx * (row_size * col_size) + r * col_size + c
                        mask[action_idx] = True
        return mask


    def _process_move(self):
        """Clear full rows/cols in own grid, return (pts, rows, cols)."""
        full_rows = [r for r in range(boxes.row_size)
                     if all(self._grid[r][c] != 0 for c in range(boxes.col_size))]
        full_cols = [c for c in range(boxes.col_size)
                     if all(self._grid[r][c] != 0 for r in range(boxes.row_size))]
        for r in full_rows:
            for c in range(boxes.col_size):
                self._grid[r][c] = 0
        for c in full_cols:
            for r in range(boxes.row_size):
                self._grid[r][c] = 0
        total = len(full_rows) + len(full_cols)
        base  = {1: 100, 2: 300, 3: 500, 4: 800}
        pts   = base.get(total, 800 + (total - 4) * 200) if total else 0
        return pts, full_rows, full_cols

    def step(self, action):
        mask = self.get_action_mask()
        if not mask[action]:
            # Should never happen when the agent respects the mask
            return self._get_obs(), -1.0, False, False, {}

        box_idx, r, c = self.decode_action(action)
        box = self._boxes[box_idx]

        self._place(box.block_type, r, c, value=box_idx + 1)
        self._boxes[box_idx] = None

        pts, _, _ = self._process_move()

        # connectivity reward — keep board open
        connectivity = scores.findMaxConnectedSquares(self._grid)
        max_possible = boxes.row_size * boxes.col_size
        connectivity_reward = (connectivity / max_possible) * 0.5

        reward = 0.3 + pts / 100.0 + connectivity_reward

        if all(b is None for b in self._boxes):
            self._boxes = boxes.get_3_random_boxes(self._grid)

        terminated = self._check_game_over()
        if terminated:
            reward -= 5.0

        return self._get_obs(), reward, terminated, False, {}

    def _get_obs(self):
        # Board state — 1.0 filled, 0.0 empty
        flat = np.array(
            [1.0 if self._grid[r][c] != 0 else 0.0
             for r in range(boxes.row_size)
             for c in range(boxes.col_size)],
            dtype=np.float32,
        )

        # Piece encodings — each slot gets a full board-sized footprint
        # showing where that piece's cells are (relative to top-left anchor)
        piece_obs = np.zeros(3 * boxes.row_size * boxes.col_size, dtype=np.float32)
        for box_idx, box in enumerate(self._boxes):
            if box is None:
                continue
            for dr, dc in box.offsets:
                cell = dr * boxes.col_size + dc
                piece_obs[box_idx * boxes.row_size * boxes.col_size + cell] = 1.0

        obs = np.concatenate([flat, piece_obs])
        return {"obs": obs, "action_mask": self.get_action_mask()}
