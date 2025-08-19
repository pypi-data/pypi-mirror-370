import { SCHEMA_VERSION, JupyterCadDoc } from '@jupytercad/schema';
import { JSONExt } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
export class JupyterCadStepDoc extends JupyterCadDoc {
    constructor() {
        super();
        this.editable = false;
        this.toJcadEndpoint = 'jupytercad/export';
        this._sourceObserver = (events) => {
            const changes = [];
            events.forEach(event => {
                event.keys.forEach((change, key) => {
                    changes.push({
                        name: 'Step File',
                        key: key,
                        newValue: JSONExt.deepCopy(event.target.toJSON())
                    });
                });
            });
            this._objectChanged.emit({ objectChange: changes });
            this._changed.emit({ objectChange: changes });
        };
        this._objectChanged = new Signal(this);
        this._source = this.ydoc.getText('source');
        this._source.observeDeep(this._sourceObserver);
    }
    set source(value) {
        this._source.insert(0, value);
    }
    get version() {
        return SCHEMA_VERSION;
    }
    get objectsChanged() {
        return this._objectChanged;
    }
    get objects() {
        const source = this._source.toJSON();
        if (!source) {
            return [];
        }
        return [
            {
                name: 'Step File', // TODO get file name?
                visible: true,
                shape: 'Part::Any',
                parameters: {
                    Content: this._source.toJSON(),
                    Type: 'STEP',
                    Color: '#808080',
                    Placement: {
                        Angle: 0.0,
                        Axis: [0.0, 0.0, 1.0],
                        Position: [0.0, 0.0, 0.0]
                    }
                }
            }
        ];
    }
    setSource(value) {
        this._source.insert(0, value);
    }
    static create() {
        return new JupyterCadStepDoc();
    }
}
