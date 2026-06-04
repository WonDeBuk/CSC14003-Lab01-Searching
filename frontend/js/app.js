/**
 * Main Application Controller.
 * Initializes all modules, wires events between them, handles all user flows.
 */
class App {
    constructor() {
        // Initialize modules
        this.gridView = new GridView(
            document.getElementById('gridCanvas'),
            document.getElementById('gridContainer'),
        );

        this.animator = new Animator(this.gridView);
        this.statsPanel = new StatsPanel();
        this.comparisonView = new ComparisonView();
        this.loadingOverlay = document.getElementById('loadingOverlay');

        // Wire control panel
        this.controlPanel = new ControlPanel({
            onStart: () => this.startSearch(),
            onPause: () => this.pauseSearch(),
            onNextStep: () => this.nextStep(),
            onPrevStep: () => this.prevStep(),
            onReset: () => this.resetSearch(),
            onMaze: () => this.generateMaze(),
            onClearGrid: () => this.clearGrid(),
            onCompare: () => this.compareAll(),
            onAlgorithmChange: () => { if (this.animator.isPlaying) this.animator.pause(); },
            onSpeedChange: (speed) => this.animator.setSpeed(speed),
            onGridSizeChange: (size) => {
                this.gridView.setSize(size, size);
                this.statsPanel.reset();
                this.controlPanel.setIdleState();
                this.controlPanel.setStatus('Ready');
            },
            onTerrainChange: (terrain) => {
                this.gridView.terrainBrush = terrain;
                this.gridView.placementMode = null;
            },
            onPlacementChange: (mode) => {
                this.gridView.placementMode = mode;
            },
        });

        // Wire animator callbacks
        this.animator.onStepChanged = (current, total, step) => {
            this.statsPanel.onStep(current, total, step);
        };
        this.animator.onFinished = (result) => {
            this.statsPanel.showResult(result);
            this.controlPanel.setPlayingState(false);
            this.controlPanel.setDataLoaded(true);
            this.controlPanel.setStatus(result?.path_found ? 'Path Found' : 'No Path');
        };
        this.animator.onStateChanged = (isPlaying) => {
            this.controlPanel.setPlayingState(isPlaying);
            this.controlPanel.setStatus(isPlaying ? 'Searching...' : 'Paused');
        };

        // Set initial speed
        this.animator.setSpeed(this.controlPanel.getSpeed());
        this.controlPanel.setIdleState();
        this.controlPanel.setStatus('Ready');

        // Initial draw after layout settles
        requestAnimationFrame(() => {
            this.gridView._resizeCanvas();
        });
    }

    // ─── Search Flow ─────────────────────────────────────

    async startSearch() {
        // Resume if paused
        if (this.animator.hasData && !this.animator.isFinished) {
            this.animator.play();
            return;
        }

        const { grid, start, goal } = this.gridView.exportGrid();
        if (!start || !goal) {
            this.controlPanel.setStatus('Place start & goal first');
            return;
        }

        const algorithm = this.controlPanel.getAlgorithm();
        this.showLoading(true);
        this.controlPanel.setStatus('Running...');

        try {
            const result = await api.search(grid, start, goal, algorithm);
            this.gridView.clearOverlay();
            this.statsPanel.reset();
            this.animator.load(result.steps, result);
            this.controlPanel.setDataLoaded(true);
            this.showLoading(false);
            this.animator.play();
        } catch (err) {
            this.showLoading(false);
            this.controlPanel.setStatus('Error');
            console.error('Search failed:', err);
            alert('Search failed: ' + err.message);
        }
    }

    pauseSearch() { this.animator.pause(); }
    nextStep() { if (this.animator.hasData) this.animator.nextStep(); }
    prevStep() { if (this.animator.hasData) this.animator.prevStep(); }

    resetSearch() {
        this.animator.reset();
        this.statsPanel.reset();
        this.controlPanel.setIdleState();
        this.controlPanel.setStatus('Ready');
    }

    // ─── Maze Generation ─────────────────────────────────

    async generateMaze() {
        const size = this.controlPanel.getGridSize();
        this.showLoading(true);
        this.controlPanel.setStatus('Generating maze...');

        try {
            const data = await api.generateMaze(size, size, 0.3);
            this.gridView.loadGrid(data.grid, data.start, data.goal);
            this.statsPanel.reset();
            this.controlPanel.setIdleState();
            this.controlPanel.setStatus('Maze generated');
            this.showLoading(false);
        } catch (err) {
            this.showLoading(false);
            console.error('Maze generation failed:', err);
            // Fallback local maze
            this._localMaze(size);
            this.controlPanel.setStatus('Local maze generated');
        }
    }

    _localMaze(size) {
        const grid = [];
        for (let r = 0; r < size; r++) {
            grid[r] = [];
            for (let c = 0; c < size; c++) {
                const rand = Math.random();
                if (rand < 0.25) grid[r][c] = 3;       // wall
                else if (rand < 0.35) grid[r][c] = 1;   // grass
                else if (rand < 0.40) grid[r][c] = 2;   // swamp
                else grid[r][c] = 0;                     // road
            }
        }
        const start = [0, 0];
        const goal = [size - 1, size - 1];
        grid[0][0] = 0;
        grid[size - 1][size - 1] = 0;
        this.gridView.loadGrid(grid, start, goal);
        this.statsPanel.reset();
        this.controlPanel.setIdleState();
    }

    // ─── Grid Management ─────────────────────────────────

    clearGrid() {
        this.gridView.clearGrid();
        this.statsPanel.reset();
        this.controlPanel.setIdleState();
        this.controlPanel.setStatus('Grid cleared');
    }

    // ─── Compare All ─────────────────────────────────────

    async compareAll() {
        const { grid, start, goal } = this.gridView.exportGrid();
        if (!start || !goal) {
            this.controlPanel.setStatus('Place start & goal first');
            return;
        }

        this.showLoading(true);
        this.controlPanel.setStatus('Comparing algorithms...');

        try {
            const results = await api.compare(grid, start, goal);
            this.comparisonView.render(results);
            this.showLoading(false);
            this.controlPanel.setStatus('Comparison complete');
        } catch (err) {
            this.showLoading(false);
            this.controlPanel.setStatus('Error');
            console.error('Comparison failed:', err);
            alert('Comparison failed: ' + err.message);
        }
    }

    // ─── Utilities ───────────────────────────────────────

    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
}

// ─── Bootstrap ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
