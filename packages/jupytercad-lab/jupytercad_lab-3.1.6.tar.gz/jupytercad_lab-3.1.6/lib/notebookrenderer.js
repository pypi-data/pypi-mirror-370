import { ICollaborativeDrive } from '@jupyter/collaborative-drive';
import { JupyterCadPanel, JupyterCadOutputWidget, ToolbarWidget } from '@jupytercad/base';
import { IJCadWorkerRegistryToken, IJCadExternalCommandRegistryToken, IJupyterCadDocTracker, JupyterCadModel } from '@jupytercad/schema';
import { showErrorMessage } from '@jupyterlab/apputils';
import { MessageLoop } from '@lumino/messaging';
import { Panel, Widget } from '@lumino/widgets';
import { IJupyterYWidgetManager, JupyterYModel, JupyterYDoc } from 'yjs-widgets';
import { ConsolePanel } from '@jupyterlab/console';
import { PathExt } from '@jupyterlab/coreutils';
import { NotebookPanel } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
const SETTINGS_ID = '@jupytercad/jupytercad-core:jupytercad-settings';
export const CLASS_NAME = 'jupytercad-notebook-widget';
export class YJupyterCADModel extends JupyterYModel {
}
export class YJupyterCADLuminoWidget extends Panel {
    constructor(options) {
        super();
        this.onResize = () => {
            if (this._jcadWidget) {
                MessageLoop.sendMessage(this._jcadWidget, Widget.ResizeMessage.UnknownSize);
            }
        };
        /**
         * Build the widget and add it to the panel.
         * @param options
         */
        this._buildWidget = (options) => {
            const { commands, workerRegistry, model, externalCommands, tracker } = options;
            const content = new JupyterCadPanel({
                model: model,
                workerRegistry: workerRegistry
            });
            let toolbar = undefined;
            if (model.filePath) {
                toolbar = new ToolbarWidget({
                    commands,
                    model,
                    externalCommands: (externalCommands === null || externalCommands === void 0 ? void 0 : externalCommands.getCommands()) || []
                });
            }
            this._jcadWidget = new JupyterCadOutputWidget({
                model,
                content,
                toolbar
            });
            this.addWidget(this._jcadWidget);
            tracker === null || tracker === void 0 ? void 0 : tracker.add(this._jcadWidget);
        };
        const { model } = options;
        this.addClass(CLASS_NAME);
        this._buildWidget(options);
        // If the filepath was not set when building the widget, the toolbar is not built.
        // The widget has to be built again to include the toolbar.
        const onchange = (_, args) => {
            if (args.stateChange) {
                args.stateChange.forEach((change) => {
                    var _a;
                    if (change.name === 'path') {
                        (_a = this.layout) === null || _a === void 0 ? void 0 : _a.removeWidget(this._jcadWidget);
                        this._jcadWidget.dispose();
                        this._buildWidget(options);
                    }
                });
            }
        };
        model.sharedModel.changed.connect(onchange);
    }
    get jcadWidget() {
        return this._jcadWidget;
    }
}
export const notebookRenderePlugin = {
    id: 'jupytercad:yjswidget-plugin',
    autoStart: true,
    requires: [IJCadWorkerRegistryToken],
    optional: [
        IJCadExternalCommandRegistryToken,
        IJupyterCadDocTracker,
        IJupyterYWidgetManager,
        ICollaborativeDrive,
        ISettingRegistry
    ],
    activate: async (app, workerRegistry, externalCommandRegistry, jcadTracker, yWidgetManager, drive, settingRegistry) => {
        let settings = null;
        if (settingRegistry) {
            try {
                settings = await settingRegistry.load(SETTINGS_ID);
                console.log(`Loaded settings for ${SETTINGS_ID}`, settings);
            }
            catch (error) {
                console.warn(`Failed to load settings for ${SETTINGS_ID}`, error);
            }
        }
        if (!yWidgetManager) {
            console.error('Missing IJupyterYWidgetManager token!');
            return;
        }
        class YJupyterCADModelFactory extends YJupyterCADModel {
            async initialize(commMetadata) {
                const { path, format, contentType } = commMetadata;
                const fileFormat = format;
                if (!drive) {
                    showErrorMessage('Error using the JupyterCAD Python API', 'You cannot use the JupyterCAD Python API without a collaborative drive. You need to install a package providing collaboration features (e.g. jupyter-collaboration).');
                    throw new Error('Failed to create the YDoc without a collaborative drive');
                }
                // The path of the project is relative to the path of the notebook
                let currentWidgetPath = '';
                const currentWidget = app.shell.currentWidget;
                if (currentWidget instanceof NotebookPanel ||
                    currentWidget instanceof ConsolePanel) {
                    currentWidgetPath = currentWidget.sessionContext.path;
                }
                let localPath = '';
                if (path) {
                    localPath = PathExt.join(PathExt.dirname(currentWidgetPath), path);
                    // If the file does not exist yet, create it
                    try {
                        await app.serviceManager.contents.get(localPath);
                    }
                    catch (e) {
                        await app.serviceManager.contents.save(localPath, {
                            content: btoa('{}'),
                            format: 'base64'
                        });
                    }
                }
                else {
                    // If the user did not provide a path, do not create
                    localPath = PathExt.join(PathExt.dirname(currentWidgetPath), 'unsaved_project');
                }
                const sharedModel = drive.sharedModelFactory.createNew({
                    path: localPath,
                    format: fileFormat,
                    contentType,
                    collaborative: true
                });
                const jupyterCadDoc = sharedModel;
                this.jupyterCADModel = new JupyterCadModel({
                    sharedModel: jupyterCadDoc,
                    settingRegistry: settingRegistry
                });
                this.jupyterCADModel.contentsManager = app.serviceManager.contents;
                this.jupyterCADModel.filePath = localPath;
                this.ydoc = this.jupyterCADModel.sharedModel.ydoc;
                this.sharedModel = new JupyterYDoc(commMetadata, this.ydoc);
            }
        }
        class YJupyterCadOutputwidget {
            constructor(yModel, node) {
                this.yModel = yModel;
                this.node = node;
                const widget = new YJupyterCADLuminoWidget({
                    commands: app.commands,
                    externalCommands: externalCommandRegistry,
                    model: yModel.jupyterCADModel,
                    workerRegistry: workerRegistry,
                    tracker: jcadTracker
                });
                // Widget.attach(widget, node);
                MessageLoop.sendMessage(widget, Widget.Msg.BeforeAttach);
                node.appendChild(widget.node);
                MessageLoop.sendMessage(widget, Widget.Msg.AfterAttach);
            }
        }
        yWidgetManager.registerWidget('@jupytercad:widget', YJupyterCADModelFactory, YJupyterCadOutputwidget);
    }
};
