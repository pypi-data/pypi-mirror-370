import { AnnotationModel } from '@jupytercad/base';
import { IAnnotationToken, IJCadExternalCommandRegistryToken, IJCadFormSchemaRegistryToken, IJCadWorkerRegistryToken, IJupyterCadDocTracker } from '@jupytercad/schema';
import { WidgetTracker } from '@jupyterlab/apputils';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { ITranslator } from '@jupyterlab/translation';
import { JupyterCadWorkerRegistry } from './workerregistry';
import { JupyterCadFormSchemaRegistry } from './schemaregistry';
import { JupyterCadExternalCommandRegistry } from './externalcommand';
const NAME_SPACE = 'jupytercad';
export const trackerPlugin = {
    id: 'jupytercad:core:tracker',
    autoStart: true,
    requires: [ITranslator],
    optional: [IMainMenu],
    provides: IJupyterCadDocTracker,
    activate: (app, translator, mainMenu) => {
        const tracker = new WidgetTracker({
            namespace: NAME_SPACE
        });
        console.log('jupytercad:core:tracker is activated!');
        return tracker;
    }
};
export const annotationPlugin = {
    id: 'jupytercad:core:annotation',
    autoStart: true,
    requires: [IJupyterCadDocTracker],
    provides: IAnnotationToken,
    activate: (app, tracker) => {
        var _a;
        const annotationModel = new AnnotationModel({
            model: (_a = tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.model
        });
        tracker.currentChanged.connect((_, changed) => {
            annotationModel.model = (changed === null || changed === void 0 ? void 0 : changed.model) || undefined;
        });
        return annotationModel;
    }
};
export const workerRegistryPlugin = {
    id: 'jupytercad:core:worker-registry',
    autoStart: true,
    requires: [],
    provides: IJCadWorkerRegistryToken,
    activate: (app) => {
        const workerRegistry = new JupyterCadWorkerRegistry();
        return workerRegistry;
    }
};
export const formSchemaRegistryPlugin = {
    id: 'jupytercad:core:form-schema-registry',
    autoStart: true,
    requires: [],
    provides: IJCadFormSchemaRegistryToken,
    activate: (app) => {
        const registry = new JupyterCadFormSchemaRegistry();
        return registry;
    }
};
export const externalCommandRegistryPlugin = {
    id: 'jupytercad:core:external-command-registry',
    autoStart: true,
    requires: [],
    provides: IJCadExternalCommandRegistryToken,
    activate: (app) => {
        const registry = new JupyterCadExternalCommandRegistry();
        return registry;
    }
};
