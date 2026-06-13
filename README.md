# Block Blast AI

A Block Blast-style puzzle game built with Python and Pygame, featuring an autonomous AI agent trained with Deep Reinforcement Learning to master piece placement strategy.

---

## Play the Game (Windows)

No Python or libraries required.

1. Go to the [latest release](https://github.com/Hashimk101/block_burst_AI/releases/tag/v1.0.0)
2. Download `BlockBurst_AI_v1.0.0.zip`
3. Extract the ZIP fully
4. Double-click `main.exe`

---

## How to Play

- Three pieces are shown in the right panel each round
- Drag and drop pieces onto the 8×8 grid
- Fill a complete row or column to clear it and score points
- Game ends when none of the three pieces can be placed anywhere on the board
- Toggle **AI: ON** from the menu or in-game to watch the agent play

---

## How the AI Works

The agent is trained using **Maskable PPO** (Proximal Policy Optimization with action masking) via `sb3-contrib`.

**Observation space** — the agent sees:
- The current 8×8 board state (filled/empty per cell)
- The shape footprint of each of the 3 available pieces
- Total input: 256 values (4 × 64 cells)

**Action masking** — only valid placements are ever considered. The agent never wastes learning capacity on physically impossible moves.

**Reward function** — the agent is rewarded for:
- Surviving each placement (+0.1)
- Clearing lines (scaled by combo)
- Maintaining future placement flexibility (normalized valid move count)
- Reducing flexibility delta (penalises moves that close off options)
- Making progress toward full rows/cols (squared fill ratio)

**Piece generation** — pieces offered to the agent are guaranteed to be placeable either directly or after a line clear (depth-2 lookahead), preventing unwinnable states.

---

## Developer Setup

### Prerequisites

Python 3.10–3.11 recommended. Python 3.14 may have compatibility issues with SB3.

### 1. Clone the repo

```bash
git clone https://github.com/Hashimk101/block_burst_AI.git
cd block_burst_AI
```

### 2. Install dependencies

```bash
pip install pygame-ce stable-baselines3 sb3-contrib gymnasium
```

### 3. Run the game

```bash
python main.py
```

---

## Retrain the AI

Training is designed for Google Colab with GPU. See `ai_for_game.py` for the full training script.

### Quick start (local, CPU)

```bash
python ai_for_game.py train          # train one stage (500k steps)
python ai_for_game.py train 1000000  # custom step count
python ai_for_game.py play           # watch trained agent play
```

### Colab training (recommended)

```python
# In a Colab notebook cell
!git clone https://github.com/Hashimk101/block_burst_AI.git
%cd block_burst_AI
!pip install stable-baselines3 sb3-contrib gymnasium -q

from google.colab import drive
drive.mount('/content/drive')

# Then run the SubprocVecEnv training loop from ai_for_game.py
# Model saves directly to Drive — survives session resets
```

Training uses `SubprocVecEnv` with 8 parallel environments for ~800 fps throughput on Colab.

---

## Project Structure

```
block_burst_AI/
├── main.py              # Entry point
├── gui.py               # Pygame rendering and game loop
├── menu.py              # Main menu, highscores, AI toggle
├── boxes.py             # Grid logic, shapes, piece generation
├── scores.py            # Line clearing, scoring, game over check
├── block_burst_env.py   # Gymnasium environment for RL training
├── ai_for_game.py       # Training script and inference hook
├── blockburst_ppo.zip   # Trained model weights
└── highscores.json      # Local highscore persistence
```

---

## Built With

- [Pygame-CE](https://pyga.me) — game rendering
- [Stable Baselines3](https://stable-baselines3.readthedocs.io) — PPO implementation
- [sb3-contrib](https://sb3-contrib.readthedocs.io) — MaskablePPO
- [Gymnasium](https://gymnasium.farama.org) — RL environment interface
