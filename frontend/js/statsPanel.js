/**
 * Stats Panel.
 * Updates the stat cards and progress bar in real-time during animation.
 */
class StatsPanel {
    constructor() {
        this.elExplored = document.getElementById('statExplored');
        this.elPathCost = document.getElementById('statPathCost');
        this.elPathLength = document.getElementById('statPathLength');
        this.elMaxFrontier = document.getElementById('statMaxFrontier');
        this.elTime = document.getElementById('statTime');
        this.elStep = document.getElementById('statStep');
        this.elProgress = document.getElementById('progressFill');
        this._maxFrontier = 0;
    }

    onStep(current, total, step) {
        this.elStep.textContent = `${current} / ${total}`;
        const pct = total > 0 ? (current / total * 100) : 0;
        this.elProgress.style.width = pct + '%';

        if (step) {
            this.elExplored.textContent = step.explored_count || 0;
            // Track max frontier from step data
            if (step.frontier && step.frontier.length > this._maxFrontier) {
                this._maxFrontier = step.frontier.length;
            }
            this.elMaxFrontier.textContent = this._maxFrontier;
        }
    }

    showResult(result) {
        if (!result) return;
        this.elExplored.textContent = result.nodes_explored;
        this.elPathCost.textContent = result.path_found ? result.path_cost.toFixed(1) : 'N/A';
        this.elPathLength.textContent = result.path_found ? result.path.length : 'N/A';
        this.elMaxFrontier.textContent = result.max_frontier_size;
        this.elTime.textContent = result.execution_time_ms.toFixed(2) + 'ms';
    }

    reset() {
        this.elExplored.textContent = '0';
        this.elPathCost.textContent = '--';
        this.elPathLength.textContent = '--';
        this.elMaxFrontier.textContent = '0';
        this.elTime.textContent = '--';
        this.elStep.textContent = '0 / 0';
        this.elProgress.style.width = '0%';
        this._maxFrontier = 0;
    }
}
