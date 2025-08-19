import { IAnnotationModel, IJCadExternalCommandRegistry, IJCadFormSchemaRegistry, IJCadWorkerRegistry, IJupyterCadTracker } from '@jupytercad/schema';
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
export declare const trackerPlugin: JupyterFrontEndPlugin<IJupyterCadTracker>;
export declare const annotationPlugin: JupyterFrontEndPlugin<IAnnotationModel>;
export declare const workerRegistryPlugin: JupyterFrontEndPlugin<IJCadWorkerRegistry>;
export declare const formSchemaRegistryPlugin: JupyterFrontEndPlugin<IJCadFormSchemaRegistry>;
export declare const externalCommandRegistryPlugin: JupyterFrontEndPlugin<IJCadExternalCommandRegistry>;
