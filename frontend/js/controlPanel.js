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
        this.statusEl = document.getElementById('headerStatus');

        this.btnStart = document.getElementById('btnStart');
        this.btnPause = document.getElementById('btnPause');
        this.btnNext = document.getElementById('btnNext');
        this.btnPrev = document.getElementById('btnPrev');
        this.btnReset = document.getElementById('btnReset');
        this.btnClearGrid = document.getElementById('btnClearGrid');
        this.btnCompare = document.getElementById('btnCompare');

        this.btnPlaceStart = document.getElementById('btnPlaceStart');
        this.btnPlaceGoal = document.getElementById('btnPlaceGoal');

        // Track the current active mode: 'terrain' | 'start' | 'goal'
        this._activeMode = 'terrain';
        // Track whether animator is paused (for pause/resume toggle)
        this._isPaused = false;

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

        // Action buttons
        this.btnStart.addEventListener('click', () => this.cb.onStart?.());
        this.btnPause.addEventListener('click', () => this._handlePauseResume());
        this.btnNext.addEventListener('click', () => this.cb.onNextStep?.());
        this.btnPrev.addEventListener('click', () => this.cb.onPrevStep?.());
        this.btnReset.addEventListener('click', () => this.cb.onReset?.());
        this.btnClearGrid.addEventListener('click', () => this.cb.onClearGrid?.());
        this.btnCompare.addEventListener('click', () => this.cb.onCompare?.());

        // Placement buttons — these activate placement mode and deactivate terrain brush
        this.btnPlaceStart.addEventListener('click', () => {
            this._setActiveMode('start');
            this.cb.onPlacementChange?.('start');
        });
        this.btnPlaceGoal.addEventListener('click', () => {
            this._setActiveMode('goal');
            this.cb.onPlacementChange?.('goal');
        });

        // Terrain brush radios — these activate terrain mode and deactivate placement
        document.querySelectorAll('#terrainBrushGroup input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    this._setActiveMode('terrain');
                    this.cb.onTerrainChange?.(radio.value);
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
            switch (e.code) {
                case 'Space': e.preventDefault(); this.cb.onStart?.(); break;
                case 'KeyP': this._handlePauseResume(); break;
                case 'KeyN': this.cb.onNextStep?.(); break;
                case 'KeyB': this.cb.onPrevStep?.(); break;
                case 'KeyR': this.cb.onReset?.(); break;
            }
        });
    }

    /** Handle pause/resume toggle */
    _handlePauseResume() {
        if (this._isPaused) {
            this.cb.onResume?.();
        } else {
            this.cb.onPause?.();
        }
    }

    /** Switch the active mode, updating UI highlights accordingly */
    _setActiveMode(mode) {
        this._activeMode = mode;

        if (mode === 'terrain') {
            // Deactivate placement buttons
            this.btnPlaceStart.classList.remove('active');
            this.btnPlaceGoal.classList.remove('active');
        } else if (mode === 'start') {
            // Activate start, deactivate goal, deselect terrain radios visually
            this.btnPlaceStart.classList.add('active');
            this.btnPlaceGoal.classList.remove('active');
            // Uncheck all terrain radios
            document.querySelectorAll('#terrainBrushGroup input[type="radio"]').forEach(r => r.checked = false);
        } else if (mode === 'goal') {
            // Activate goal, deactivate start, deselect terrain radios visually
            this.btnPlaceGoal.classList.add('active');
            this.btnPlaceStart.classList.remove('active');
            // Uncheck all terrain radios
            document.querySelectorAll('#terrainBrushGroup input[type="radio"]').forEach(r => r.checked = false);
        }
    }

    getAlgorithm() { return this.algorithmSelect.value; }
    getSpeed() { return parseInt(this.speedSlider.value); }

    setStatus(text) {
        this.statusEl.textContent = text;
    }

    /** Update the pause button to show Pause or Resume state */
    setPauseResumeState(isPlaying) {
        const pauseIcon = this.btnPause.querySelector('.pause-icon');
        const resumeIcon = this.btnPause.querySelector('.resume-icon');
        const label = this.btnPause.querySelector('.pause-label');

        if (isPlaying) {
            // Animation is playing — show "Pause" option
            this._isPaused = false;
            this.btnPause.disabled = false;
            if (pauseIcon) pauseIcon.style.display = '';
            if (resumeIcon) resumeIcon.style.display = 'none';
            if (label) label.textContent = 'Pause';
        } else if (this.btnPause.disabled === false) {
            // Animation was playing and now paused — show "Resume" option
            this._isPaused = true;
            if (pauseIcon) pauseIcon.style.display = 'none';
            if (resumeIcon) resumeIcon.style.display = '';
            if (label) label.textContent = 'Resume';
        }
    }

    setPlayingState(playing) {
        this.btnStart.disabled = playing;
        this.btnPause.disabled = !playing;
        this.btnNext.disabled = playing;
        this.btnPrev.disabled = playing;
        this.setPauseResumeState(playing);
    }

    setDataLoaded(loaded) {
        this.btnNext.disabled = !loaded;
        this.btnPrev.disabled = !loaded;
    }

    /** Mark the animation as paused (not idle) — show Resume */
    setPausedState() {
        this.btnStart.disabled = false;
        this.btnPause.disabled = false;
        this._isPaused = true;
        this.btnNext.disabled = false;
        this.btnPrev.disabled = false;

        const pauseIcon = this.btnPause.querySelector('.pause-icon');
        const resumeIcon = this.btnPause.querySelector('.resume-icon');
        const label = this.btnPause.querySelector('.pause-label');
        if (pauseIcon) pauseIcon.style.display = 'none';
        if (resumeIcon) resumeIcon.style.display = '';
        if (label) label.textContent = 'Resume';
    }

    setIdleState() {
        this.btnStart.disabled = false;
        this.btnPause.disabled = true;
        this.btnNext.disabled = true;
        this.btnPrev.disabled = true;
        this._isPaused = false;

        // Reset to Pause label
        const pauseIcon = this.btnPause.querySelector('.pause-icon');
        const resumeIcon = this.btnPause.querySelector('.resume-icon');
        const label = this.btnPause.querySelector('.pause-label');
        if (pauseIcon) pauseIcon.style.display = '';
        if (resumeIcon) resumeIcon.style.display = 'none';
        if (label) label.textContent = 'Pause';
    }

    setInteractive(interactive) {
        this.btnPlaceStart.disabled = !interactive;
        this.btnPlaceGoal.disabled = !interactive;
        document.querySelectorAll('#terrainBrushGroup input[type="radio"]').forEach(r => r.disabled = !interactive);
    }
}
