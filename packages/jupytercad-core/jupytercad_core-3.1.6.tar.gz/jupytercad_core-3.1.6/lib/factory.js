var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
import { ABCWidgetFactory } from '@jupyterlab/docregistry';
import { JupyterCadPanel, JupyterCadDocumentWidget, ToolbarWidget } from '@jupytercad/base';
export class JupyterCadDocumentWidgetFactory extends ABCWidgetFactory {
    constructor(options) {
        const { backendCheck, externalCommandRegistry } = options, rest = __rest(options, ["backendCheck", "externalCommandRegistry"]);
        super(rest);
        this.options = options;
        this._backendCheck = backendCheck;
        this._commands = options.commands;
        this._workerRegistry = options.workerRegistry;
        this._externalCommandRegistry = externalCommandRegistry;
    }
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    createNewWidget(context) {
        if (this._backendCheck) {
            const checked = this._backendCheck();
            if (!checked) {
                throw new Error('Requested backend is not installed');
            }
        }
        const { model } = context;
        model.filePath = context.localPath;
        context.pathChanged.connect(() => {
            model.filePath = context.localPath;
        });
        const content = new JupyterCadPanel({
            model,
            workerRegistry: this._workerRegistry,
            manager: this.options.manager,
            contentFactory: this.options.contentFactory,
            mimeTypeService: this.options.mimeTypeService,
            rendermime: this.options.rendermime,
            consoleTracker: this.options.consoleTracker,
            commandRegistry: this.options.commands
        });
        const toolbar = new ToolbarWidget({
            commands: this._commands,
            model,
            externalCommands: this._externalCommandRegistry.getCommands()
        });
        return new JupyterCadDocumentWidget({ context, content, toolbar });
    }
}
// Backward compat
export const JupyterCadWidgetFactory = JupyterCadDocumentWidgetFactory;
