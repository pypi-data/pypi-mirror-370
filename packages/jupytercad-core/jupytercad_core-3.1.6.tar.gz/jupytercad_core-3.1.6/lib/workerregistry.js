import { OccWorker } from '@jupytercad/occ-worker';
export class JupyterCadWorkerRegistry {
    constructor() {
        this._registry = new Map();
        const worker = new Worker(new URL('@jupytercad/occ-worker/lib/worker', import.meta.url));
        this._defaultWorker = new OccWorker({ worker });
    }
    registerWorker(workerId, worker) {
        if (!this._registry.has(workerId)) {
            this._registry.set(workerId, worker);
        }
        else {
            console.error('Worker is already registered!');
        }
    }
    unregisterWorker(workerId) {
        if (!this._registry.has(workerId)) {
            this._registry.delete(workerId);
        }
    }
    getDefaultWorker() {
        return this._defaultWorker;
    }
    getWorker(workerId) {
        return this._registry.get(workerId);
    }
    getAllWorkers() {
        return [...this._registry.values()];
    }
}
