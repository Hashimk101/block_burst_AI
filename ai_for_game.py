"""
Train a MaskablePPO agent on BlockBurstEnv, then optionally hand its
decisions to gui.py so you can watch it play.

Usage
-----
  python ai_for_game.py train            # train one stage (default 500k steps)
  python ai_for_game.py train 1000000   # train with custom timesteps
  python ai_for_game.py play            # load model, play visually via gui
"""

import sys
import os
import numpy as np
from block_burst_env import BlockBurstEnv
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.vec_env import SubprocVecEnv

MODEL_PATH   = "blockburst_ppo"
STAGE_STEPS  = 500_000
TOTAL_TARGET = 10_000_000
N_ENVS       = 8           # parallel envs — tune down to 4 if Colab crashes


# ── Env factory ───────────────────────────────────────────────────────────────

def make_env():
    """Single wrapped env — used as the factory for SubprocVecEnv."""
    def _init():
        env = BlockBurstEnv()
        env = ActionMasker(env, lambda e: e.get_action_mask())
        return env
    return _init


# ── Progress tracking ─────────────────────────────────────────────────────────

def load_progress():
    path = MODEL_PATH + "_progress.txt"
    if os.path.exists(path):
        with open(path) as f:
            return int(f.read().strip())
    return 0


def save_progress(total_steps):
    with open(MODEL_PATH + "_progress.txt", "w") as f:
        f.write(str(total_steps))


# ── Training ──────────────────────────────────────────────────────────────────

def train(stage_steps=STAGE_STEPS):
    # SubprocVecEnv spawns N_ENVS independent processes
    # each running its own copy of the env simultaneously
    env = SubprocVecEnv([make_env() for _ in range(N_ENVS)])

    completed = load_progress()

    if os.path.exists(MODEL_PATH + ".zip"):
        print(f"Resuming from {MODEL_PATH}.zip  ({completed:,} steps done)")
        model = MaskablePPO.load(MODEL_PATH, env=env)
        model.learning_rate = 3e-4
    else:
        print(f"Starting fresh with {N_ENVS} parallel envs")
        model = MaskablePPO(
            "MultiInputPolicy",
            env,
            verbose=1,
            n_steps=2048,
            # batch_size scales with n_envs so each update sees enough data
            batch_size=N_ENVS * 64,
            learning_rate=3e-4,
            clip_range=0.1,        # tighter clipping for more stable updates
            device="auto",         # uses GPU if available, CPU otherwise
        )

    print(f"Training for {stage_steps:,} steps  "
          f"(total so far: {completed:,} / {TOTAL_TARGET:,})")

    model.learn(total_timesteps=stage_steps, reset_num_timesteps=False)

    completed += stage_steps
    model.save(MODEL_PATH)
    save_progress(completed)
    env.close()

    print(f"\nStage done.  Total trained: {completed:,} / {TOTAL_TARGET:,}")
    remaining = TOTAL_TARGET - completed
    if remaining <= 0:
        print("Reached training target!")
    else:
        print(f"Run again to continue  ({remaining:,} steps left)")


# ── Inference (used by gui.py) ────────────────────────────────────────────────

_model = None

def load_model():
    global _model
    if _model is None:
        _model = MaskablePPO.load(MODEL_PATH)
    return _model


def get_ai_action(grid, current_boxes):
    """
    Return (box_idx, anchor_row, anchor_col) for the best move,
    or None if no valid move exists.
    """
    import boxes as _boxes
    model = load_model()

    # Board obs — must match _get_obs() in block_burst_env.py exactly
    flat = np.array(
        [1.0 if grid[r][c] != 0 else 0.0
         for r in range(len(grid))
         for c in range(len(grid[0]))],
        dtype=np.float32,
    )

    # Piece shape encodings — same logic as _get_obs()
    piece_obs = np.zeros(3 * _boxes.row_size * _boxes.col_size, dtype=np.float32)
    for box_idx, box in enumerate(current_boxes):
        if box is None:
            continue
        for dr, dc in box.offsets:
            cell = dr * _boxes.col_size + dc
            piece_obs[box_idx * _boxes.row_size * _boxes.col_size + cell] = 1.0

    obs_vec = np.concatenate([flat, piece_obs])

    # Action mask
    n_actions = 3 * _boxes.row_size * _boxes.col_size
    mask = np.zeros(n_actions, dtype=bool)
    for box_idx, box in enumerate(current_boxes):
        if box is None:
            continue
        base = box_idx * _boxes.row_size * _boxes.col_size
        for r in range(_boxes.row_size):
            for c in range(_boxes.col_size):
                if _boxes.is_valid_placement(box.block_type, r, c):
                    mask[base + r * _boxes.col_size + c] = True

    if not mask.any():
        return None

    obs = {"obs": obs_vec, "action_mask": mask}
    action, _ = model.predict(obs, deterministic=True, action_masks=mask)

    box_idx   = int(action) // (_boxes.row_size * _boxes.col_size)
    remainder = int(action)  % (_boxes.row_size * _boxes.col_size)
    row       = remainder // _boxes.col_size
    col       = remainder  % _boxes.col_size
    return box_idx, row, col


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "train"

    if cmd == "train":
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else STAGE_STEPS
        train(stage_steps=steps)

    elif cmd == "play":
        import pygame, menu, gui, boxes
        pygame.init()
        sw = gui.SIDE_PANEL_WIDTH + boxes.col_size * gui.cell_size + gui.PICKER_PANEL_WIDTH + gui.RIGHT_MARGIN
        sh = gui.TOP_BAR_HEIGHT   + boxes.row_size * gui.cell_size + gui.RIGHT_MARGIN
        screen = pygame.display.set_mode((sw, sh))
        pygame.display.set_caption("Block Blast — AI")
        fonts = menu.make_fonts()
        clock = pygame.time.Clock()
        menu.ai_enabled = True
        gui.run(screen, fonts, clock)
        pygame.quit()

    else:
        print("Usage: python ai_for_game.py [train [steps] | play]")
