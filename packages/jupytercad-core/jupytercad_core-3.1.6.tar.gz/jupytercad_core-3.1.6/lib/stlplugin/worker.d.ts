import { IJCadWorker, IJupyterCadTracker, IWorkerMessageBase, JCadWorkerSupportedFormat } from '@jupytercad/schema';
export declare class ExportWorker implements IJCadWorker {
    constructor(options: ExportWorker.IOptions);
    shapeFormat: JCadWorkerSupportedFormat;
    get ready(): Promise<void>;
    register(options: {
        messageHandler: ((msg: any) => void) | ((msg: any) => Promise<void>);
        thisArg?: any;
    }): string;
    unregister(id: string): void;
    postMessage(msg: IWorkerMessageBase): void;
    private _downloadFile;
    private _cleanupExportObject;
    private _ready;
    private _tracker;
}
export declare namespace ExportWorker {
    interface IOptions {
        tracker: IJupyterCadTracker;
        shapeFormat: JCadWorkerSupportedFormat;
    }
}
