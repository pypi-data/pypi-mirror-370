import { JCadWorkerSupportedFormat, WorkerAction } from '@jupytercad/schema';
import { PromiseDelegate } from '@lumino/coreutils';
import { v4 as uuid } from 'uuid';
export class ExportWorker {
    constructor(options) {
        this._ready = new PromiseDelegate();
        this._tracker = options.tracker;
        this.shapeFormat = options.shapeFormat;
    }
    get ready() {
        return this._ready.promise;
    }
    register(options) {
        const id = uuid();
        // No-op
        return id;
    }
    unregister(id) {
        // No-op
    }
    postMessage(msg) {
        var _a;
        if (msg.action !== WorkerAction.POSTPROCESS) {
            return;
        }
        if (msg.payload && Object.keys(msg.payload).length > 0) {
            const jCadObject = msg.payload['jcObject'];
            const content = msg.payload['postShape'];
            const format = ((_a = jCadObject === null || jCadObject === void 0 ? void 0 : jCadObject.shapeMetadata) === null || _a === void 0 ? void 0 : _a.shapeFormat) || this.shapeFormat;
            if (format === JCadWorkerSupportedFormat.STL &&
                typeof content === 'string') {
                this._downloadFile(jCadObject.name, content, 'stl');
            }
            else if (format === JCadWorkerSupportedFormat.BREP &&
                typeof content === 'string') {
                this._downloadFile(jCadObject.name, content, 'brep');
            }
            else {
                console.error('No valid content received for object:', jCadObject.name);
            }
        }
    }
    _downloadFile(objectName, content, ext) {
        const blob = new Blob([content], {
            type: 'application/octet-stream'
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const originalObjectName = objectName.replace(/_(STL|BREP)_Export$/, '');
        link.download = `${originalObjectName
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '_')}.${ext}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        this._cleanupExportObject(objectName);
    }
    _cleanupExportObject(exportObjectName) {
        const currentWidget = this._tracker.currentWidget;
        if (!currentWidget) {
            return;
        }
        const model = currentWidget.model;
        const sharedModel = model.sharedModel;
        if (sharedModel && sharedModel.objectExists(exportObjectName)) {
            sharedModel.transact(() => {
                sharedModel.removeObjectByName(exportObjectName);
            });
        }
    }
}
