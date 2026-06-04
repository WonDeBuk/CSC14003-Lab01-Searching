/**
 * Comparison View.
 * Renders comparison table and Chart.js bar chart for algorithm performance.
 */
class ComparisonView {
    constructor() {
        this.section = document.getElementById('comparisonSection');
        this.tbody = document.getElementById('comparisonTableBody');
        this.chartCanvas = document.getElementById('comparisonChart');
        this.chart = null;

        // Close button
        const closeBtn = document.getElementById('btnCloseComparison');
        if (closeBtn) closeBtn.addEventListener('click', () => this.hide());
    }

    render(results) {
        if (!results || results.length === 0) return;

        // Find best values for highlighting
        const found = results.filter(r => r.path_found);
        const bestCost = found.length > 0 ? Math.min(...found.map(r => r.path_cost)) : Infinity;
        const bestExplored = Math.min(...results.map(r => r.nodes_explored));
        const bestTime = Math.min(...results.map(r => r.execution_time_ms));

        // Build table rows
        this.tbody.innerHTML = '';
        results.forEach(r => {
            const tr = document.createElement('tr');
            const isBestCost = r.path_found && r.path_cost === bestCost;
            const isBestExplored = r.nodes_explored === bestExplored;
            const isBestTime = r.execution_time_ms === bestTime;

            tr.innerHTML = `
                <td class="algo-name">${r.algorithm_name}</td>
                <td>${r.path_found ? '<span class="found-yes">Yes</span>' : '<span class="found-no">No</span>'}</td>
                <td class="${isBestCost ? 'best-value' : ''}">${r.path_found ? r.path_cost.toFixed(1) : 'N/A'}</td>
                <td>${r.path_found ? r.path.length : 'N/A'}</td>
                <td class="${isBestExplored ? 'best-value' : ''}">${r.nodes_explored}</td>
                <td>${r.max_frontier_size}</td>
                <td class="${isBestTime ? 'best-value' : ''}">${r.execution_time_ms.toFixed(3)}</td>
            `;
            this.tbody.appendChild(tr);
        });

        // Build chart
        this._buildChart(results);

        // Show section
        this.section.style.display = 'block';
        this.section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    _buildChart(results) {
        if (this.chart) this.chart.destroy();

        const labels = results.map(r => r.algorithm_name);
        const explored = results.map(r => r.nodes_explored);
        const costs = results.map(r => r.path_found ? r.path_cost : 0);

        this.chart = new Chart(this.chartCanvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Nodes Explored',
                        data: explored,
                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                    },
                    {
                        label: 'Path Cost',
                        data: costs,
                        backgroundColor: 'rgba(34, 211, 238, 0.7)',
                        borderColor: '#22d3ee',
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#8892a6', font: { family: "'Geist', sans-serif" } },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#8892a6', font: { family: "'Geist Mono', monospace", size: 11 } },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                    },
                    y: {
                        ticks: { color: '#8892a6', font: { family: "'Geist Mono', monospace", size: 11 } },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                    },
                },
            },
        });
    }

    hide() {
        this.section.style.display = 'none';
    }
}
