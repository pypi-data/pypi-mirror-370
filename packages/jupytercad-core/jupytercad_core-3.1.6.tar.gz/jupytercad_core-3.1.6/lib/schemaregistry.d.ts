import { IDict, IJCadFormSchemaRegistry } from '@jupytercad/schema';
export declare class JupyterCadFormSchemaRegistry implements IJCadFormSchemaRegistry {
    constructor();
    registerSchema(name: string, schema: IDict): void;
    has(name: string): boolean;
    getSchemas(): Map<string, IDict>;
    private _registry;
}
