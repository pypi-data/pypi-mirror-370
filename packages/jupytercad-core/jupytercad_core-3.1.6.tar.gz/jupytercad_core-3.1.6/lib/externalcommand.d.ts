import { IJCadExternalCommand, IJCadExternalCommandRegistry } from '@jupytercad/schema';
export declare class JupyterCadExternalCommandRegistry implements IJCadExternalCommandRegistry {
    constructor();
    registerCommand(cmd: IJCadExternalCommand): void;
    getCommands(): IJCadExternalCommand[];
    private _registry;
}
