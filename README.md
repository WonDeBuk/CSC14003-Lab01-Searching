# AI Search Algorithm Visualizer

An interactive web-based visualizer for comparing search algorithms on a weighted grid. Built for the **Introduction to Artificial Intelligence (24C08) - Lab 1**.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Overview

This project visualizes **8 search algorithms** operating on a 20x20 weighted grid with multiple terrain types. Users can interactively build maps, watch algorithms explore step-by-step, and compare performance metrics across all algorithms.

### Algorithms Implemented

| # | Algorithm | Category | Optimal? | Complete? |
|---|---|---|:---:|:---:|
| 1 | **Breadth-First Search (BFS)** | Uninformed | No (weighted) | Yes |
| 2 | **Depth-First Search (DFS)** | Uninformed | No | Yes |
| 3 | **Uniform Cost Search (UCS)** | Uninformed | Yes | Yes |
| 4 | **A* Search** | Informed | Yes | Yes |
| 5 | **Greedy Best-First Search** | Informed | No | Yes |
| 6 | **Iterative Deepening DFS (IDDFS)** | Uninformed | No (weighted) | Yes |
| 7 | **Bidirectional BFS** | Uninformed | No (weighted) | Yes |
| 8 | **IDA* (Iterative Deepening A*)** | Informed | Yes | Yes |

### Terrain Types

| Terrain | Cost | Description |
|---|:---:|---|
| Road | 1 | Normal traversal (lowest cost) |
| Grass | 3 | Moderate difficulty |
| Swamp | 5 | High difficulty |
| Wall | Blocked | Impassable obstacle |

## Quick Start

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- A modern web browser (Chrome, Firefox, or Edge)

### One-Click Run

**Windows:**
```bash
# Double-click start.bat or run:
start.bat
```

**macOS / Linux:**
```bash
chmod +x start.sh
./start.sh
```

This will automatically:
1. Create a Python virtual environment
2. Install all dependencies
3. Start the server at **http://localhost:8000**

### Manual Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the server
uvicorn main:app --reload --port 8000

# 6. Open http://localhost:8000 in your browser
```

## How to Use

### Building a Map

1. **Place Start Point** - Select "Start" from the terrain brush, click on the grid
2. **Place Goal Point** - Select "Goal" from the terrain brush, click on the grid
3. **Draw Obstacles** - Select Wall/Grass/Swamp, click and drag on the grid
4. **Erase** - Select "Eraser" or right-click on any cell to reset to Road
5. **Random Maze** - Click "Generate Maze" for an auto-generated map

### Running Algorithms

1. **Select Algorithm** from the dropdown menu
2. **Adjust Speed** using the speed slider (faster/slower animation)
3. **Click Start** to begin the visualization
4. **Step Controls**:
   - **Next Step** - Advance one search step
   - **Previous Step** - Go back one step
   - **Pause** - Pause auto-play
   - **Reset** - Clear the search visualization (keeps the map)

### Comparing Algorithms

Click **"Compare All"** to run all 8 algorithms on the current map and see a side-by-side comparison table with:
- Path cost
- Nodes explored
- Maximum frontier size
- Execution time
- Optimality

## Project Structure

```
Lab1_Searching/
├── backend/
│   ├── main.py                    # FastAPI application & API endpoints
│   ├── requirements.txt           # Python dependencies
│   ├── algorithms/
│   │   ├── base.py                # Abstract base class & data types
│   │   ├── bfs.py                 # Breadth-First Search
│   │   ├── dfs.py                 # Depth-First Search
│   │   ├── ucs.py                 # Uniform Cost Search
│   │   ├── astar.py               # A* Search
│   │   ├── greedy_best_first.py   # Greedy Best-First Search
│   │   ├── iddfs.py               # Iterative Deepening DFS
│   │   ├── bidirectional.py       # Bidirectional BFS
│   │   └── ida_star.py            # IDA* Search
│   ├── models/
│   │   ├── grid.py                # Grid model (terrain, costs, neighbors)
│   │   └── schemas.py             # Pydantic API schemas
│   └── utils/
│       ├── heuristics.py          # Manhattan distance heuristic
│       └── maze_generator.py      # Random maze generation
│
├── frontend/
│   ├── index.html                 # Main application page
│   ├── css/
│   │   ├── main.css               # Global styles & dark theme
│   │   ├── grid.css               # Grid visualization styles
│   │   ├── controls.css           # Control panel styles
│   │   └── comparison.css         # Comparison view styles
│   └── js/
│       ├── app.js                 # Main application controller
│       ├── api.js                 # Backend API client
│       ├── gridView.js            # Canvas grid renderer
│       ├── animator.js            # Step-by-step playback engine
│       ├── controlPanel.js        # UI controls logic
│       ├── statsPanel.js          # Live metrics display
│       └── comparisonView.js      # Comparison table & charts
│
├── start.bat                      # One-click start (Windows)
├── start.sh                       # One-click start (macOS/Linux)
├── .gitignore
└── README.md
```

## API Reference

### `POST /api/search`

Run a single algorithm on the given grid.

**Request:**
```json
{
  "grid": [[0,0,0,...], [0,3,3,...], ...],
  "start": [0, 2],
  "goal": [19, 17],
  "algorithm": "astar"
}
```

**Response:**
```json
{
  "algorithm_name": "AStar",
  "path": [[0,2], [1,2], ...],
  "path_found": true,
  "path_cost": 18.0,
  "nodes_explored": 156,
  "max_frontier_size": 31,
  "execution_time_ms": 9.8,
  "steps": [...]
}
```

### `POST /api/search/compare`

Run all 8 algorithms and return comparison results.

### `POST /api/maze/generate`

Generate a random maze with terrain variety.

**Request:**
```json
{
  "width": 20,
  "height": 20,
  "wall_density": 0.25,
  "terrain_variety": true
}
```

## Problem Modeling

The 20x20 grid is modeled as a weighted graph **G = (V, E, W)** where:
- **V** = all non-wall cells (up to 400 nodes)
- **E** = edges between orthogonally adjacent non-wall cells
- **W(e)** = cost of entering the destination cell (Road=1, Grass=3, Swamp=5)

**Heuristic**: Manhattan distance `h(n) = |row_n - row_goal| + |col_n - col_goal|`
- Admissible: `h(n) <= h*(n)` since minimum edge cost is 1
- Consistent: `h(n) - h(n') <= 1 <= W(n,n')` for adjacent cells

## Tech Stack

- **Backend**: Python 3.8+, FastAPI, Uvicorn, Pydantic
- **Frontend**: Vanilla HTML/CSS/JavaScript, HTML5 Canvas, Chart.js
- **Architecture**: REST API (backend computes, frontend animates)

## License

This project is for educational purposes as part of the Introduction to Artificial Intelligence course (24C08).
