"""
Pydantic schemas for API request/response validation.

These schemas define the contract between the frontend and backend,
ensuring type safety and automatic documentation via FastAPI.
"""

from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Dict, Any


# ─── Request Schemas ───────────────────────────────────────────────

class SearchRequest(BaseModel):
    """Request body for running a single search algorithm."""
    grid: List[List[int]] = Field(
        ...,
        description="2D array of terrain values (0=Road, 1=Grass, 2=Swamp, 3=Wall)"
    )
    start: List[int] = Field(
        ...,
        min_length=2, max_length=2,
        description="Start position as [row, col]"
    )
    goal: List[int] = Field(
        ...,
        min_length=2, max_length=2,
        description="Goal position as [row, col]"
    )
    algorithm: str = Field(
        ...,
        description="Algorithm name: bfs, dfs, ucs, astar, greedy, iddfs, bidirectional, ida_star"
    )


class CompareRequest(BaseModel):
    """Request body for comparing all algorithms on the same grid."""
    grid: List[List[int]] = Field(
        ...,
        description="2D array of terrain values"
    )
    start: List[int] = Field(
        ...,
        min_length=2, max_length=2,
        description="Start position as [row, col]"
    )
    goal: List[int] = Field(
        ...,
        min_length=2, max_length=2,
        description="Goal position as [row, col]"
    )


class MazeGenerateRequest(BaseModel):
    """Request body for generating a random maze."""
    width: int = Field(default=20, ge=5, le=50, description="Grid width")
    height: int = Field(default=20, ge=5, le=50, description="Grid height")
    wall_density: float = Field(
        default=0.3, ge=0.0, le=0.8,
        description="Fraction of cells that are walls (0.0 to 0.8)"
    )
    terrain_variety: bool = Field(
        default=True,
        description="Whether to include grass/swamp terrain"
    )


# ─── Response Schemas ──────────────────────────────────────────────

class StepResponse(BaseModel):
    """A single visualization step for animation playback."""
    action: str = Field(
        ...,
        description="Step type: explore, add_to_frontier, found_goal, no_path"
    )
    state: List[int] = Field(..., description="Cell [row, col] for this step")
    g_cost: float = 0.0
    h_cost: float = 0.0
    f_cost: float = 0.0
    depth: int = 0
    frontier: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshot of the frontier at this step"
    )
    explored_count: int = 0
    extra: Dict[str, Any] = Field(default_factory=dict)


class SearchResultResponse(BaseModel):
    """Result of running a single search algorithm."""
    algorithm_name: str
    path: List[List[int]] = Field(
        default_factory=list,
        description="Ordered list of [row, col] cells from start to goal"
    )
    path_found: bool
    path_cost: float
    nodes_explored: int
    max_frontier_size: int
    execution_time_ms: float
    steps: List[StepResponse] = Field(
        default_factory=list,
        description="Visualization steps (omitted in compare mode)"
    )


class SearchResponse(BaseModel):
    """Top-level response for a single-algorithm search."""
    success: bool = True
    result: SearchResultResponse


class CompareResponse(BaseModel):
    """Top-level response for comparing all algorithms."""
    success: bool = True
    results: List[SearchResultResponse]


class MazeResponse(BaseModel):
    """Response for maze generation."""
    success: bool = True
    grid: List[List[int]]
    start: List[int]
    goal: List[int]


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
