"""
FastAPI backend for the AI Search Algorithm Visualizer.

Provides endpoints to:
- Run a single search algorithm with step-by-step visualization data
- Compare all 8 algorithms on the same grid
- Serve the frontend static files

Start with: uvicorn main:app --reload --port 8000
"""

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models.grid import Grid
from models.schemas import (
    SearchRequest, SearchResponse, SearchResultResponse, StepResponse,
    CompareRequest, CompareResponse,
    ErrorResponse,
)
from algorithms import ALGORITHM_MAP


# ─── App Setup ─────────────────────────────────────────────────────

app = FastAPI(
    title="AI Search Algorithm Visualizer",
    description="Backend API for visualizing BFS, DFS, UCS, A*, Greedy, IDDFS, Bidirectional BFS, and IDA*",
    version="1.0.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helper Functions ──────────────────────────────────────────────

def _convert_result(result, include_steps: bool = True) -> SearchResultResponse:
    """Convert an internal SearchResult to the API response schema."""
    steps = []
    if include_steps:
        steps = [
            StepResponse(
                action=step.action,
                state=list(step.state),
                g_cost=step.g_cost,
                h_cost=step.h_cost,
                f_cost=step.f_cost,
                depth=step.depth,
                frontier=step.frontier,
                explored_count=step.explored_count,
                extra=step.extra,
            )
            for step in result.steps
        ]

    return SearchResultResponse(
        algorithm_name=result.algorithm_name,
        path=[list(p) for p in result.path],
        path_found=result.path_found,
        path_cost=result.path_cost,
        nodes_explored=result.nodes_explored,
        max_frontier_size=result.max_frontier_size,
        execution_time_ms=round(result.execution_time_ms, 3),
        steps=steps,
    )


def _validate_request(grid_data, start, goal):
    """Validate that start and goal are within bounds and not on walls."""
    if not grid_data or not grid_data[0]:
        raise HTTPException(status_code=400, detail="Grid cannot be empty")

    height = len(grid_data)
    width = len(grid_data[0])

    sr, sc = start
    gr, gc = goal

    if not (0 <= sr < height and 0 <= sc < width):
        raise HTTPException(
            status_code=400,
            detail=f"Start position ({sr}, {sc}) is out of bounds"
        )
    if not (0 <= gr < height and 0 <= gc < width):
        raise HTTPException(
            status_code=400,
            detail=f"Goal position ({gr}, {gc}) is out of bounds"
        )
    if grid_data[sr][sc] == 3:  # WALL
        raise HTTPException(
            status_code=400, detail="Start position is on a wall"
        )
    if grid_data[gr][gc] == 3:  # WALL
        raise HTTPException(
            status_code=400, detail="Goal position is on a wall"
        )


# ─── API Endpoints ─────────────────────────────────────────────────

@app.post("/api/search", response_model=SearchResponse)
async def run_search(request: SearchRequest):
    """
    Run a single search algorithm on the provided grid.

    Returns the complete result with visualization steps for animation.
    """
    algorithm_name = request.algorithm.lower()
    if algorithm_name not in ALGORITHM_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown algorithm '{request.algorithm}'. "
                   f"Available: {', '.join(ALGORITHM_MAP.keys())}"
        )

    _validate_request(request.grid, request.start, request.goal)

    grid = Grid.from_2d_array(request.grid)
    start = tuple(request.start)
    goal = tuple(request.goal)

    algorithm_class = ALGORITHM_MAP[algorithm_name]
    algo = algorithm_class(grid, start, goal)
    result = algo.search()

    return SearchResponse(
        success=True,
        result=_convert_result(result, include_steps=True),
    )


@app.post("/api/search/compare", response_model=CompareResponse)
async def compare_algorithms(request: CompareRequest):
    """
    Run ALL 8 algorithms on the same grid and return comparative results.

    Steps are omitted for performance (only metrics are returned).
    """
    _validate_request(request.grid, request.start, request.goal)

    grid = Grid.from_2d_array(request.grid)
    start = tuple(request.start)
    goal = tuple(request.goal)

    results = []
    for name, algorithm_class in ALGORITHM_MAP.items():
        algo = algorithm_class(grid, start, goal)
        result = algo.search()
        results.append(_convert_result(result, include_steps=False))

    return CompareResponse(success=True, results=results)


# Frontend directory path
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# ─── Health Check ──────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "algorithms": list(ALGORITHM_MAP.keys()),
        "frontend_available": FRONTEND_DIR.exists(),
    }


# ─── Static File Serving (Frontend) ───────────────────────────────

# Serve frontend files from ../frontend/ directory
# NOTE: Mount AFTER all API routes so /api/* routes take priority

if FRONTEND_DIR.exists():
    @app.get("/")
    async def serve_index():
        """Serve the frontend index.html."""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Frontend not found")

    # Mount sub-directories for static assets
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"

    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")


# ─── Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, reload_includes=["*.html", "*.css", "*.js"])

