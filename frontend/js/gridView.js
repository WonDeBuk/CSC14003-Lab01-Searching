/**
 * Grid Canvas Renderer.
 * Draws the grid with terrain, search overlay, start/goal markers.
 * Handles click/drag interaction for editing terrain.
 */
class GridView {
    constructor(canvas, container) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.container = container;
        this.rows = 20;
        this.cols = 20;
        this.cellSize = 0;

        // Grid data: 0=road, 1=grass, 2=swamp, 3=wall
        this.gridData = this._emptyGrid(this.rows, this.cols);
        this.start = null;
        this.goal = null;

        // Search overlay state
        this.overlay = {};       // key "r,c" -> { state, g, h, f }
        this.pathCells = new Set();
        this._exploredCount = 0;

        // Interaction state
        this.terrainBrush = 'wall';    // 'wall' | 'grass' | 'swamp' | 'road' | 'eraser'
        this.placementMode = null;     // 'start' | 'goal' | null
        this.isDragging = false;

        // Colors
        this.terrainColors = {
            0: '#1e293b', 1: '#14532d', 2: '#451a03', 3: '#374151',
        };

        this._resizeCanvas();
        this._bindEvents();
    }

    _emptyGrid(rows, cols) {
        return Array.from({ length: rows }, () => new Array(cols).fill(0));
    }

    _resizeCanvas() {
        const maxW = this.container.clientWidth - 16;
        const maxH = this.container.clientHeight - 16;
        const maxDim = Math.min(maxW, maxH, 700);
        this.cellSize = Math.floor(maxDim / Math.max(this.rows, this.cols));
        this.canvas.width = this.cellSize * this.cols;
        this.canvas.height = this.cellSize * this.rows;
        this.draw();
    }

    _bindEvents() {
        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 2) return;
            this.isDragging = true;
            this._handleClick(e);
        });
        this.canvas.addEventListener('mousemove', (e) => {
            this._updateTooltip(e);
            if (this.isDragging) this._handleClick(e);
        });
        this.canvas.addEventListener('mouseup', () => this.isDragging = false);
        this.canvas.addEventListener('mouseleave', () => {
            this.isDragging = false;
            this._hideTooltip();
        });
        this.canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const cell = this._cellAt(e);
            if (cell) { this._erase(cell.r, cell.c); }
        });
        window.addEventListener('resize', () => this._resizeCanvas());
    }

    _cellAt(e) {
        const rect = this.canvas.getBoundingClientRect();
        const c = Math.floor((e.clientX - rect.left) / this.cellSize);
        const r = Math.floor((e.clientY - rect.top) / this.cellSize);
        if (r >= 0 && r < this.rows && c >= 0 && c < this.cols) return { r, c };
        return null;
    }

    _handleClick(e) {
        const cell = this._cellAt(e);
        if (!cell) return;
        const { r, c } = cell;

        if (this.placementMode === 'start') {
            this.start = [r, c];
            this.gridData[r][c] = 0;
            this.placementMode = null;
        } else if (this.placementMode === 'goal') {
            this.goal = [r, c];
            this.gridData[r][c] = 0;
            this.placementMode = null;
        } else {
            const map = { wall: 3, grass: 1, swamp: 2, road: 0 };
            if (this.terrainBrush === 'eraser') {
                this._erase(r, c);
                return;
            }
            this.gridData[r][c] = map[this.terrainBrush] ?? 3;
        }
        this.draw();
    }

    _erase(r, c) {
        if (this.start && this.start[0] === r && this.start[1] === c) this.start = null;
        if (this.goal && this.goal[0] === r && this.goal[1] === c) this.goal = null;
        this.gridData[r][c] = 0;
        this.draw();
    }

    _updateTooltip(e) {
        const cell = this._cellAt(e);
        if (!cell) { this._hideTooltip(); return; }
        const tooltip = document.getElementById('gridTooltip');
        if (!tooltip) return;
        const names = ['Road (1)', 'Grass (3)', 'Swamp (5)', 'Wall'];
        const key = `${cell.r},${cell.c}`;
        let text = `(${cell.r}, ${cell.c}) ${names[this.gridData[cell.r][cell.c]]}`;
        const ov = this.overlay[key];
        if (ov && ov.g !== undefined) {
            text += ` | g=${ov.g.toFixed(1)}`;
            if (ov.h !== undefined) text += ` h=${ov.h.toFixed(1)}`;
            if (ov.f !== undefined) text += ` f=${ov.f.toFixed(1)}`;
        }
        tooltip.textContent = text;
        tooltip.style.display = 'block';
        const rect = this.canvas.getBoundingClientRect();
        tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
        tooltip.style.top = (e.clientY - rect.top - 28) + 'px';
    }

    _hideTooltip() {
        const t = document.getElementById('gridTooltip');
        if (t) t.style.display = 'none';
    }

    // ─── Drawing ─────────────────────────────────────────

    draw() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.cols; c++) {
                const x = c * cs, y = r * cs;
                const key = `${r},${c}`;

                // Terrain
                ctx.fillStyle = this.terrainColors[this.gridData[r][c]] || '#1e293b';
                ctx.fillRect(x, y, cs, cs);

                // Overlay
                if (this.pathCells.has(key)) {
                    ctx.fillStyle = 'rgba(34, 211, 238, 0.7)';
                    ctx.fillRect(x, y, cs, cs);
                } else if (this.overlay[key]) {
                    const s = this.overlay[key].state;
                    if (s === 'explored') {
                        const a = Math.min(0.4 + 0.4 * (this.overlay[key].order || 0), 0.85);
                        ctx.fillStyle = `rgba(99, 102, 241, ${a})`;
                        ctx.fillRect(x, y, cs, cs);
                    } else if (s === 'frontier') {
                        ctx.fillStyle = 'rgba(251, 191, 36, 0.5)';
                        ctx.fillRect(x, y, cs, cs);
                    }
                }

                // Grid lines
                ctx.strokeStyle = 'rgba(255,255,255,0.06)';
                ctx.lineWidth = 1;
                ctx.strokeRect(x + 0.5, y + 0.5, cs - 1, cs - 1);
            }
        }

        // Start marker
        if (this.start) this._drawMarker(this.start, '#34d399', '#059669', 'S');
        // Goal marker
        if (this.goal) this._drawMarker(this.goal, '#f87171', '#dc2626', 'G');
    }

    _drawMarker(pos, fill, stroke, label) {
        const cs = this.cellSize;
        const cx = pos[1] * cs + cs / 2;
        const cy = pos[0] * cs + cs / 2;
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, cs * 0.35, 0, Math.PI * 2);
        this.ctx.fillStyle = fill;
        this.ctx.fill();
        this.ctx.strokeStyle = stroke;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        this.ctx.fillStyle = '#0a0a12';
        this.ctx.font = `bold ${cs * 0.4}px 'Geist', sans-serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(label, cx, cy + 1);
    }

    // ─── Search Overlay API ──────────────────────────────

    applyStep(step) {
        const key = `${step.state[0]},${step.state[1]}`;
        if (step.action === 'explore') {
            this.overlay[key] = {
                state: 'explored', order: this._exploredCount / 400,
                g: step.g_cost, h: step.h_cost, f: step.f_cost,
            };
            this._exploredCount++;
        } else if (step.action === 'add_to_frontier') {
            if (!this.overlay[key] || this.overlay[key].state !== 'explored') {
                this.overlay[key] = {
                    state: 'frontier', g: step.g_cost, h: step.h_cost, f: step.f_cost,
                };
            }
        }
        this.draw();
    }

    showPath(path) {
        this.pathCells = new Set();
        if (path) path.forEach(([r, c]) => this.pathCells.add(`${r},${c}`));
        this.draw();
    }

    clearOverlay() {
        this.overlay = {};
        this.pathCells = new Set();
        this._exploredCount = 0;
        this.draw();
    }

    // ─── Grid Data API ───────────────────────────────────

    exportGrid() {
        return {
            grid: this.gridData.map(r => [...r]),
            start: this.start ? [...this.start] : null,
            goal: this.goal ? [...this.goal] : null,
        };
    }

    loadGrid(data, start, goal) {
        this.rows = data.length;
        this.cols = data[0].length;
        this.gridData = data.map(r => [...r]);
        this.start = start;
        this.goal = goal;
        this.clearOverlay();
        this._resizeCanvas();
    }

    clearGrid() {
        this.gridData = this._emptyGrid(this.rows, this.cols);
        this.start = null;
        this.goal = null;
        this.clearOverlay();
    }

    setSize(rows, cols) {
        this.rows = rows;
        this.cols = cols;
        this.gridData = this._emptyGrid(rows, cols);
        this.start = null;
        this.goal = null;
        this.clearOverlay();
        this._resizeCanvas();
    }
}
