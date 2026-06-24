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

        // Grid & stats area elements (for show/hide on comparison)
        this.gridArea = document.getElementById('gridArea');
        this.statsBar = document.getElementById('statsBar');

        // Wire control panel
        this.controlPanel = new ControlPanel({
            onStart: () => this.startSearch(),
            onPause: () => this.pauseSearch(),
            onResume: () => this.resumeSearch(),
            onNextStep: () => this.nextStep(),
            onPrevStep: () => this.prevStep(),
            onReset: () => this.resetSearch(),
            onClearGrid: () => this.clearGrid(),
            onCompare: () => this.compareAll(),
            onAlgorithmChange: () => { if (this.animator.isPlaying) this.animator.pause(); },
            onSpeedChange: (speed) => this.animator.setSpeed(speed),
            onTerrainChange: (terrain) => {
                this.gridView.terrainBrush = terrain;
                this.gridView.placementMode = null;
            },
            onPlacementChange: (mode) => {
                this.gridView.placementMode = mode;
            },
        });

        // Grid modification callback
        this.gridView.onGridModified = () => {
            if (this.animator.hasData) {
                this.resetSearch();
            }
        };

        // Wire animator callbacks
        this.animator.onStepChanged = (current, total, step) => {
            this.statsPanel.onStep(current, total, step);
        };
        this.animator.onFinished = (result) => {
            this.statsPanel.showResult(result);
            this.controlPanel.setPlayingState(false);
            this.controlPanel.setDataLoaded(true);
            this.controlPanel.setStatus(result?.path_found ? 'Path Found' : 'No Path');
            this.setInteractive(true);
        };
        this.animator.onStateChanged = (isPlaying) => {
            if (isPlaying) {
                this.controlPanel.setPlayingState(true);
                this.controlPanel.setStatus('Searching...');
                this.setInteractive(false);
            } else {
                // Paused (not finished) — show Resume
                this.controlPanel.setPausedState();
                this.controlPanel.setStatus('Paused');
            }
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

    setInteractive(interactive) {
        this.gridView.isInteractive = interactive;
        this.controlPanel.setInteractive(interactive);
    }

    async startSearch() {
        const { grid, start, goal } = this.gridView.exportGrid();
        if (!start || !goal) {
            this.controlPanel.setStatus('Place start & goal first');
            return;
        }

        const algorithm = this.controlPanel.getAlgorithm();
        this.showLoading(true);
        this.controlPanel.setStatus('Running...');
        this.setInteractive(false);

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
            this.setInteractive(true);
            console.error('Search failed:', err);
            alert('Search failed: ' + err.message);
        }
    }

    pauseSearch() { this.animator.pause(); }
    resumeSearch() {
        if (this.animator.hasData && !this.animator.isFinished) {
            this.animator.play();
            return;
        }
    }
    nextStep() { if (this.animator.hasData) this.animator.nextStep(); }
    prevStep() { if (this.animator.hasData) this.animator.prevStep(); }

    resetSearch() {
        this.animator.reset();
        this.statsPanel.reset();
        this.controlPanel.setIdleState();
        this.controlPanel.setStatus('Ready');
        this.setInteractive(true);
    }

    // ─── Grid Management ─────────────────────────────────

    clearGrid() {
        this.animator.reset();
        this.gridView.clearGrid();
        this.statsPanel.reset();
        this.controlPanel.setIdleState();
        this.controlPanel.setStatus('Grid cleared');
        this.setInteractive(true);
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
        this.setInteractive(false);

        try {
            const results = await api.compare(grid, start, goal);
            // Hide grid and stats when showing comparison
            if (this.gridArea) this.gridArea.style.display = 'none';
            if (this.statsBar) this.statsBar.style.display = 'none';
            this.comparisonView.render(results);
            this.showLoading(false);
            this.controlPanel.setStatus('Comparison complete');
            this.setInteractive(true);
        } catch (err) {
            this.showLoading(false);
            this.controlPanel.setStatus('Error');
            this.setInteractive(true);
            console.error('Comparison failed:', err);
            alert('Comparison failed: ' + err.message);
        }
    }

    /** Show grid and stats again (called when closing comparison) */
    showGridAndStats() {
        if (this.gridArea) this.gridArea.style.display = '';
        if (this.statsBar) this.statsBar.style.display = '';
    }

    // ─── Utilities ───────────────────────────────────────

    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
}

// ─── Bootstrap ───────────────────────────────────────
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new App();
    });
} else {
    // DOM already parsed (scripts loaded dynamically)
    window.app = new App();
}
