import { ConsolePanel, IConsoleTracker } from '@jupyterlab/console';
import { JupyterCadModel, IJCadWorkerRegistry, IJCadExternalCommandRegistry, IJupyterCadTracker } from '@jupytercad/schema';
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { CommandRegistry } from '@lumino/commands';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IEditorMimeTypeService } from '@jupyterlab/codeeditor';
import { JupyterCadDocumentWidget } from '@jupytercad/base';
import { ServiceManager } from '@jupyterlab/services';
interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    tracker: IJupyterCadTracker;
    commands: CommandRegistry;
    workerRegistry: IJCadWorkerRegistry;
    externalCommandRegistry: IJCadExternalCommandRegistry;
    manager?: ServiceManager.IManager;
    contentFactory?: ConsolePanel.IContentFactory;
    mimeTypeService?: IEditorMimeTypeService;
    rendermime?: IRenderMimeRegistry;
    consoleTracker?: IConsoleTracker;
    backendCheck?: () => boolean;
}
export declare class JupyterCadDocumentWidgetFactory extends ABCWidgetFactory<JupyterCadDocumentWidget, JupyterCadModel> {
    private options;
    constructor(options: IOptions);
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    protected createNewWidget(context: DocumentRegistry.IContext<JupyterCadModel>): JupyterCadDocumentWidget;
    private _commands;
    private _workerRegistry;
    private _externalCommandRegistry;
    private _backendCheck?;
}
export declare const JupyterCadWidgetFactory: typeof JupyterCadDocumentWidgetFactory;
export {};
