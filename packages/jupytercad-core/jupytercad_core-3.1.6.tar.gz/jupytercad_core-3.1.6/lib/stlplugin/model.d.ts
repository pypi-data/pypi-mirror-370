import { IJCadObject, IJcadObjectDocChange, IJupyterCadDoc, JupyterCadDoc } from '@jupytercad/schema';
import { ISignal } from '@lumino/signaling';
export declare class JupyterCadStlDoc extends JupyterCadDoc {
    constructor();
    set source(value: string);
    get version(): string;
    get objectsChanged(): ISignal<IJupyterCadDoc, IJcadObjectDocChange>;
    get objects(): Array<IJCadObject>;
    setSource(value: string): void;
    static create(): JupyterCadStlDoc;
    editable: boolean;
    toJcadEndpoint: string;
    private _sourceObserver;
    private _source;
    private _objectChanged;
}
