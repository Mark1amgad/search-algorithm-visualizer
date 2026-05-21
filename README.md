# 🔍 Search Algorithm Visualizer

> An interactive algorithm exploration platform for AIE111.  
> Watch BFS, DFS, DLS, IDS, UCS, Greedy, and A\* search in real time —  
> then compare them side-by-side with live metrics.

---

## ✨ Features

| Feature | Description |
|---|---|
| **7 Algorithms** | BFS, DFS, DLS, IDS, UCS, Greedy Best-First, A\* |
| **Step-by-step animation** | Watch each algorithm explore the grid, one node at a time |
| **Speed control** | 10 speed levels — from slow-motion to near-instant |
| **Live metrics** | Nodes explored, path length, and execution time update in real time |
| **Wall drawing** | Click and drag to draw/erase walls interactively |
| **Maze generation** | Random obstacles or perfect recursive-backtracker mazes |
| **Compare mode** | Run all 7 algorithms instantly and compare results in a table |
| **Theory overlay** | Educational panel with complexity, completeness, and key idea |
| **Keyboard shortcuts** | Full keyboard control for fast interaction |

---

## 🚀 Setup & Launch

### Option 1 — Double-click (Windows)

1. Double-click **`install.bat`** — installs dependencies (first time only)
2. Double-click **`start.bat`** — launches the visualizer

### Option 2 — Command line

```bash
pip install -r requirements.txt
python main.py
```

### Requirements

- Python 3.8+
- pygame >= 2.5.0

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `SPACE` | Run / Pause algorithm |
| `R` | Reset grid (clear all) |
| `C` | Clear path (keep walls) |
| `M` | Generate random maze |
| `P` | Generate perfect maze (recursive backtracker) |
| `F` | Compare all 7 algorithms instantly |
| `T` | Toggle theory overlay for selected algorithm |
| `ESC` | Close theory overlay |
| `Q` | Exit application |
| `1` – `7` | Select algorithm (BFS→DFS→DLS→IDS→UCS→Greedy→A\*) |
| `S` + drag | Move the **Start** node |
| `G` + drag | Move the **Goal** node |

---

## 🖱️ Mouse Controls

| Action | Effect |
|---|---|
| **Left-click drag** on grid | Draw walls |
| **Right-click drag** on grid | Erase walls |
| **Click** sidebar buttons | Select algorithm, control speed, run actions, exit |

---

## 📊 Algorithms Covered

| Key | Algorithm | Complete | Optimal | Time | Space |
|---|---|---|---|---|---|
| 1 | BFS | ✅ Yes | ✅ Yes (unweighted) | O(b^d) | O(b^d) |
| 2 | DFS | ❌ No | ❌ No | O(b^m) | O(bm) |
| 3 | DLS | ❌ No | ❌ No | O(b^l) | O(bl) |
| 4 | IDS | ✅ Yes | ✅ Yes (unweighted) | O(b^d) | O(bd) |
| 5 | UCS | ✅ Yes | ✅ Yes | O(b^(C\*/e)) | O(b^(C\*/e)) |
| 6 | Greedy | ❌ No | ❌ No | O(b^m) | O(b^m) |
| 7 | A\* | ✅ Yes | ✅ Yes (admissible h) | O(b^d) | O(b^d) |

> **DLS** runs with depth limit = 15 by default (configurable in `main.py`).

---

## 🎨 Cell Color Legend

| Color | Meaning |
|---|---|
| 🟢 Green | Start node |
| 🔴 Red | Goal node |
| 🔵 Blue | Visited node |
| 🟡 Yellow/Amber | Frontier (open list) |
| 🩵 Cyan | Current node being expanded |
| 💚 Light green | Shortest path found |
| ⬛ Dark | Wall |

---

## 🔬 Compare Mode

Press **`F`** (or click **Compare All**) to run all 7 algorithms on the current grid simultaneously.

The sidebar shows a results table with:
- **Nodes Explored** — how much of the grid each algorithm searched
- **Path Length** — length of the solution found (✗ if not found)
- **Time (ms)** — actual execution time

**Best values are highlighted** in the table for easy comparison.

---

## 🏗️ Architecture

```
search_visualizer/
├── __init__.py     Package declaration
├── grid.py         Grid data structure + maze generators
├── algorithms.py   7 search algorithms as step-by-step generators
├── renderer.py     Pygame rendering engine + color scheme
├── theory.py       Algorithm metadata (complexity, completeness)
└── ui.py           Sidebar panel, buttons, metrics, theory overlay

main.py             App loop, event handling, state machine
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `grid.py` | 2D grid, wall management, `generate_random_maze()`, `generate_recursive_maze()` |
| `algorithms.py` | Generator-based BFS/DFS/DLS/IDS/UCS/Greedy/A\*, `AlgorithmState`, `run_algorithm_to_completion()` |
| `renderer.py` | `GridRenderer.draw()`, `Colors` palette, header, legend |
| `theory.py` | `ALGORITHM_INFO` dict with complexity + descriptions |
| `ui.py` | `Button`, `SidebarPanel`, `TheoryOverlay` |
| `main.py` | `App` class — event loop, `AppState` machine, wiring |

---

## 📐 Metrics Explained

| Metric | What it tells you |
|---|---|
| **Nodes Explored** | How many grid cells the algorithm examined before finding (or failing to find) a path. Lower = more efficient. |
| **Path Length** | Number of steps in the solution path from Start to Goal. Lower = shorter path. |
| **Time (ms)** | Wall-clock time for the algorithm to run. Useful for comparing computational overhead. |

---

## 📁 Project Info

- **Course**: AIE111 — Artificial Intelligence
- **Topic**: Search Algorithms Analysis and Visualization
- **Platform**: Python + Pygame
