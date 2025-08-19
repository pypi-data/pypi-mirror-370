import { IJCadWorker, IJCadWorkerRegistry } from '@jupytercad/schema';
export declare class JupyterCadWorkerRegistry implements IJCadWorkerRegistry {
    constructor();
    registerWorker(workerId: string, worker: IJCadWorker): void;
    unregisterWorker(workerId: string): void;
    getDefaultWorker(): IJCadWorker;
    getWorker(workerId: string): IJCadWorker | undefined;
    getAllWorkers(): IJCadWorker[];
    private _registry;
    private _defaultWorker;
}
