/**
 * Backend API client.
 * Wraps fetch() calls to the FastAPI backend.
 */
const api = {
    BASE: '',

    async search(grid, start, goal, algorithm) {
        const res = await fetch(`${this.BASE}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid, start, goal, algorithm }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Search failed');
        }
        const data = await res.json();
        return data.result;
    },

    async compare(grid, start, goal) {
        const res = await fetch(`${this.BASE}/api/search/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid, start, goal }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Compare failed');
        }
        const data = await res.json();
        return data.results;
    }
};
