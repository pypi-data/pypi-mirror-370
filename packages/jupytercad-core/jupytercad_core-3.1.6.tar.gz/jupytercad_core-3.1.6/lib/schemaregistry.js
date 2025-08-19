import formSchema from '@jupytercad/schema/lib/_interface/forms.json';
export class JupyterCadFormSchemaRegistry {
    constructor() {
        this._registry = new Map(Object.entries(formSchema));
    }
    registerSchema(name, schema) {
        if (!this._registry.has(name)) {
            this._registry.set(name, schema);
        }
        else {
            console.error('Worker is already registered!');
        }
    }
    has(name) {
        return this._registry.has(name);
    }
    getSchemas() {
        return this._registry;
    }
}
