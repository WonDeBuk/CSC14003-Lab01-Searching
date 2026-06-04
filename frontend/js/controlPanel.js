/**
 * Control Panel.
 * Wires up sidebar UI elements and manages button states.
 */
class ControlPanel {
    constructor(callbacks) {
        this.cb = callbacks;

        // Elements
        this.algorithmSelect = document.getElementById('algorithmSelect');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedValue = document.getElementById('speedValue');
        this.gridSizeSelect = document.getElementById('gridSizeSelect');
        this.statusEl = document.getElementById('headerStatus');

        this.btnStart = document.getElementById('btnStart');
        this.btnPause = document.getElementById('btnPause');
        this.btnNext = document.getElementById('btnNext');
        this.btnPrev = document.getElementById('btnPrev');
        this.btnReset = document.getElementById('btnReset');
        this.btnMaze = document.getElementById('btnMaze');
        this.btnClearGrid = document.getElementById('btnClearGrid');
        this.btnCompare = document.getElementById('btnCompare');

        this.btnPlaceStart = document.getElementById('btnPlaceStart');
        this.btnPlaceGoal = document.getElementById('btnPlaceGoal');

        this._wireEvents();
    }

    _wireEvents() {
        // Algorithm select
        this.algorithmSelect.addEventListener('change', () => {
            this.cb.onAlgorithmChange?.(this.algorithmSelect.value);
        });

        // Speed slider
        this.speedSlider.addEventListener('input', () => {
            const val = parseInt(this.speedSlider.value);
            this.speedValue.textContent = val + 'ms';
            this.cb.onSpeedChange?.(val);
        });

        // Grid size
        this.gridSizeSelect.addEventListener('change', () => {
            this.cb.onGridSizeChange?.(parseInt(this.gridSizeSelect.value));
        });

        // Action buttons
        this.btnStart.addEventListener('click', () => this.cb.onStart?.());
        this.btnPause.addEventListener('click', () => this.cb.onPause?.());
        this.btnNext.addEventListener('click', () => this.cb.onNextStep?.());
        this.btnPrev.addEventListener('click', () => this.cb.onPrevStep?.());
        this.btnReset.addEventListener('click', () => this.cb.onReset?.());
        this.btnMaze.addEventListener('click', () => this.cb.onMaze?.());
        this.btnClearGrid.addEventListener('click', () => this.cb.onClearGrid?.());
        this.btnCompare.addEventListener('click', () => this.cb.onCompare?.());

        // Placement buttons
        this.btnPlaceStart.addEventListener('click', () => {
            this.cb.onPlacementChange?.('start');
            this.btnPlaceStart.classList.add('active');
            this.btnPlaceGoal.classList.remove('active');
        });
        this.btnPlaceGoal.addEventListener('click', () => {
            this.cb.onPlacementChange?.('goal');
            this.btnPlaceGoal.classList.add('active');
            this.btnPlaceStart.classList.remove('active');
        });

        // Terrain brush radios
        document.querySelectorAll('#terrainBrushGroup input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    this.cb.onTerrainChange?.(radio.value);
                    this.btnPlaceStart.classList.remove('active');
                    this.btnPlaceGoal.classList.remove('active');
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
            switch (e.code) {
                case 'Space': e.preventDefault(); this.cb.onStart?.(); break;
                case 'KeyP': this.cb.onPause?.(); break;
                case 'KeyN': this.cb.onNextStep?.(); break;
                case 'KeyB': this.cb.onPrevStep?.(); break;
                case 'KeyR': this.cb.onReset?.(); break;
                case 'KeyM': this.cb.onMaze?.(); break;
            }
        });
    }

    getAlgorithm() { return this.algorithmSelect.value; }
    getSpeed() { return parseInt(this.speedSlider.value); }
    getGridSize() { return parseInt(this.gridSizeSelect.value); }

    setStatus(text) {
        this.statusEl.textContent = text;
    }

    setPlayingState(playing) {
        this.btnStart.disabled = playing;
        this.btnPause.disabled = !playing;
        this.btnNext.disabled = playing;
        this.btnPrev.disabled = playing;
    }

    setDataLoaded(loaded) {
        this.btnNext.disabled = !loaded;
        this.btnPrev.disabled = !loaded;
    }

    setIdleState() {
        this.btnStart.disabled = false;
        this.btnPause.disabled = true;
        this.btnNext.disabled = true;
        this.btnPrev.disabled = true;
    }
}
