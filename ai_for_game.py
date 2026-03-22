"""
Train a MaskablePPO agent on BlockBurstEnv, then optionally hand its
decisions to gui.py

Usage
-----
  python ai_for_game.py train          # train one stage and save
  python ai_for_game.py train 5000000  # train with custom timesteps
  python ai_for_game.py play           # load model, play visually via gui
"""

import sys
import os
import numpy as np
from block_burst_env import BlockBurstEnv
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

MODEL_PATH    = "blockburst_ppo"          # saves as blockburst_ppo.zip
STAGE_STEPS   = 10_000                    # steps per train call (change freely)
TOTAL_TARGET  = 10_000_000               # optional long-run goal


# ── Env factory ──────────────────────────────────────────────────────────────

def make_env():
    env = BlockBurstEnv()
    env = ActionMasker(env, lambda e: e.get_action_mask())
    return env


# ── Stage training ───────────────────────────────────────────────────────────

def load_progress():
    """Read how many total timesteps have been trained so far."""
    progress_file = MODEL_PATH + "_progress.txt"
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            return int(f.read().strip())
    return 0


def save_progress(total_steps):
    with open(MODEL_PATH + "_progress.txt", "w") as f:
        f.write(str(total_steps))


def train(stage_steps=STAGE_STEPS):
    env       = make_env()
    completed = load_progress()

    if os.path.exists(MODEL_PATH + ".zip"):
        print(f"Resuming from {MODEL_PATH}.zip  ({completed:,} steps done so far)")
        model = MaskablePPO.load(MODEL_PATH, env=env)
        # Restore the learning rate schedule after reload
        model.learning_rate = 3e-4
    else:
        print("No saved model found — starting fresh")
        model = MaskablePPO(
            "MultiInputPolicy",
            env,
            verbose=1,
            n_steps=2048,
            batch_size=64,
            learning_rate=3e-4,
        )

    print(f"Training for {stage_steps:,} more steps  "
          f"(target: {TOTAL_TARGET:,}  remaining: {max(0, TOTAL_TARGET - completed):,})")

    model.learn(total_timesteps=stage_steps, reset_num_timesteps=False)

    completed += stage_steps
    model.save(MODEL_PATH)
    save_progress(completed)

    print(f"\nStage done.  Total trained: {completed:,} / {TOTAL_TARGET:,}")
    if completed >= TOTAL_TARGET:
        print("Reached training target!")
    else:
        print(f"Run again to continue  ({TOTAL_TARGET - completed:,} steps left)")

    env.close()


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
    model = load_model()

    import boxes as _boxes
    flat = np.array(
        [1.0 if grid[r][c] != 0 else 0.0
         for r in range(len(grid))
         for c in range(len(grid[0]))],
        dtype=np.float32,
    )

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

    obs = {"obs": flat, "action_mask": mask}
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
