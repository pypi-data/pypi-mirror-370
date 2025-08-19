import { JupyterCadOutputWidget, JupyterCadTracker } from '@jupytercad/base';
import { IJCadWorkerRegistry, IJCadExternalCommandRegistry, JupyterCadModel } from '@jupytercad/schema';
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { Panel } from '@lumino/widgets';
import { JupyterYModel } from 'yjs-widgets';
import { CommandRegistry } from '@lumino/commands';
export declare const CLASS_NAME = "jupytercad-notebook-widget";
export interface ICommMetadata {
    create_ydoc: boolean;
    path: string;
    format: string;
    contentType: string;
    ymodel_name: string;
}
export declare class YJupyterCADModel extends JupyterYModel {
    jupyterCADModel: JupyterCadModel;
}
export declare class YJupyterCADLuminoWidget extends Panel {
    constructor(options: IOptions);
    onResize: () => void;
    get jcadWidget(): JupyterCadOutputWidget;
    /**
     * Build the widget and add it to the panel.
     * @param options
     */
    private _buildWidget;
    private _jcadWidget;
}
interface IOptions {
    commands: CommandRegistry;
    workerRegistry?: IJCadWorkerRegistry;
    model: JupyterCadModel;
    externalCommands?: IJCadExternalCommandRegistry;
    tracker?: JupyterCadTracker;
}
export declare const notebookRenderePlugin: JupyterFrontEndPlugin<void>;
export {};
