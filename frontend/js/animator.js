/**
 * Step-by-step animation engine.
 * Loads search steps from the API result and plays them forward/backward.
 */
class Animator {
    constructor(gridView) {
        this.gridView = gridView;
        this.steps = [];
        this.result = null;
        this.currentIndex = -1;
        this.isPlaying = false;
        this.isFinished = false;
        this.speed = 150;    // ms per step
        this._timer = null;

        // Callbacks set by App
        this.onStepChanged = null;   // (current, total, step)
        this.onFinished = null;      // (result)
        this.onStateChanged = null;  // (isPlaying)
    }

    get hasData() { return this.steps.length > 0; }
    get totalSteps() { return this.steps.length; }

    load(steps, result) {
        this.pause();
        this.steps = steps || [];
        this.result = result;
        this.currentIndex = -1;
        this.isFinished = false;
        this.gridView.clearOverlay();
    }

    play() {
        if (!this.hasData || this.isFinished) return;
        this.isPlaying = true;
        this._notify('state');
        this._tick();
    }

    pause() {
        this.isPlaying = false;
        clearTimeout(this._timer);
        this._timer = null;
        this._notify('state');
    }

    nextStep() {
        if (!this.hasData) return;
        if (this.currentIndex >= this.steps.length - 1) {
            this._finish();
            return;
        }
        this.currentIndex++;
        const step = this.steps[this.currentIndex];
        this.gridView.applyStep(step);
        this._notify('step');
    }

    prevStep() {
        if (!this.hasData || this.currentIndex <= 0) return;
        this.isFinished = false;
        this.currentIndex--;
        // Replay from scratch up to currentIndex
        this.gridView.clearOverlay();
        for (let i = 0; i <= this.currentIndex; i++) {
            const step = this.steps[i];
            const key = `${step.state[0]},${step.state[1]}`;
            if (step.action === 'explore') {
                this.gridView.overlay[key] = {
                    state: 'explored', order: i / 400,
                    g: step.g_cost, h: step.h_cost, f: step.f_cost,
                };
                this.gridView._exploredCount++;
            } else if (step.action === 'add_to_frontier') {
                if (!this.gridView.overlay[key] || this.gridView.overlay[key].state !== 'explored') {
                    this.gridView.overlay[key] = {
                        state: 'frontier', g: step.g_cost, h: step.h_cost, f: step.f_cost,
                    };
                }
            }
        }
        this.gridView.draw();
        this._notify('step');
    }

    reset() {
        this.pause();
        this.currentIndex = -1;
        this.isFinished = false;
        this.gridView.clearOverlay();
        this._notify('step');
    }

    setSpeed(ms) {
        this.speed = ms;
    }

    _tick() {
        if (!this.isPlaying) return;
        if (this.currentIndex >= this.steps.length - 1) {
            this._finish();
            return;
        }
        this.nextStep();
        this._timer = setTimeout(() => this._tick(), this.speed);
    }

    _finish() {
        this.pause();
        this.isFinished = true;
        // Show the final path
        if (this.result && this.result.path_found && this.result.path) {
            this.gridView.showPath(this.result.path);
        }
        if (this.onFinished) this.onFinished(this.result);
    }

    _notify(type) {
        if (type === 'step' && this.onStepChanged) {
            const step = this.currentIndex >= 0 ? this.steps[this.currentIndex] : null;
            this.onStepChanged(this.currentIndex + 1, this.steps.length, step);
        }
        if (type === 'state' && this.onStateChanged) {
            this.onStateChanged(this.isPlaying);
        }
    }
}
