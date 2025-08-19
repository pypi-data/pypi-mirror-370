import { JupyterCadModel } from '@jupytercad/schema';
import { JupyterCadStepDoc } from './model';
class JupyterCadStepModel extends JupyterCadModel {
    constructor(options) {
        super({
            sharedModel: options.sharedModel,
            languagePreference: options.languagePreference,
            settingRegistry: options.settingRegistry
        });
    }
    fromString(data) {
        this.sharedModel.source = data;
        this.dirty = true;
    }
    createSharedModel() {
        return JupyterCadStepDoc.create();
    }
}
/**
 * A Model factory to create new instances of JupyterCadModel.
 */
export class JupyterCadStepModelFactory {
    constructor(options) {
        /**
         * Whether the model is collaborative or not.
         */
        this.collaborative = true;
        this._disposed = false;
        this._settingRegistry = options.settingRegistry;
    }
    /**
     * The name of the model.
     *
     * @returns The name
     */
    get name() {
        return 'jupytercad-stepmodel';
    }
    /**
     * The content type of the file.
     *
     * @returns The content type
     */
    get contentType() {
        return 'step';
    }
    /**
     * The format of the file.
     *
     * @returns the file format
     */
    get fileFormat() {
        return 'text';
    }
    /**
     * Get whether the model factory has been disposed.
     *
     * @returns disposed status
     */
    get isDisposed() {
        return this._disposed;
    }
    /**
     * Dispose the model factory.
     */
    dispose() {
        this._disposed = true;
    }
    /**
     * Get the preferred language given the path on the file.
     *
     * @param path path of the file represented by this document model
     * @returns The preferred language
     */
    preferredLanguage(path) {
        return '';
    }
    /**
     * Create a new instance of JupyterCadStepModel.
     *
     * @returns The model
     */
    createNew(options) {
        const model = new JupyterCadStepModel({
            sharedModel: options.sharedModel,
            languagePreference: options.languagePreference,
            settingRegistry: this._settingRegistry
        });
        model.initSettings();
        return model;
    }
}
