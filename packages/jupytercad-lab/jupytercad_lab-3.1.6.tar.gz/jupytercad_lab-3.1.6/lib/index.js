import { ControlPanelModel, logoIcon, LeftPanelWidget, RightPanelWidget, addCommands, CommandIDs } from '@jupytercad/base';
import { IAnnotationToken, IJCadFormSchemaRegistryToken, IJCadWorkerRegistryToken, IJupyterCadDocTracker } from '@jupytercad/schema';
import { ILayoutRestorer } from '@jupyterlab/application';
import { ICompletionProviderManager } from '@jupyterlab/completer';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';
import { notebookRenderePlugin } from './notebookrenderer';
import { IForkManagerToken } from '@jupyter/docprovider';
import { ICollaborativeDrive } from '@jupyter/collaborative-drive';
const NAME_SPACE = 'jupytercad';
const plugin = {
    id: 'jupytercad:lab:main-menu',
    autoStart: true,
    requires: [
        IJupyterCadDocTracker,
        IJCadFormSchemaRegistryToken,
        IJCadWorkerRegistryToken
    ],
    optional: [IMainMenu, ITranslator, ICompletionProviderManager],
    activate: (app, tracker, formSchemaRegistry, workerRegistry, mainMenu, translator, completionProviderManager) => {
        console.log('jupytercad:lab:main-menu is activated!');
        translator = translator !== null && translator !== void 0 ? translator : nullTranslator;
        const isEnabled = () => {
            return (tracker.currentWidget !== null &&
                tracker.currentWidget === app.shell.currentWidget);
        };
        addCommands(app, tracker, translator, formSchemaRegistry, workerRegistry, completionProviderManager);
        if (mainMenu) {
            populateMenus(mainMenu, isEnabled);
        }
    }
};
const controlPanel = {
    id: 'jupytercad:lab:controlpanel',
    autoStart: true,
    requires: [
        ILayoutRestorer,
        IJupyterCadDocTracker,
        IAnnotationToken,
        IJCadFormSchemaRegistryToken
    ],
    optional: [ICollaborativeDrive, IForkManagerToken],
    activate: (app, restorer, tracker, annotationModel, formSchemaRegistry, collaborativeDrive, forkManager) => {
        const controlModel = new ControlPanelModel({ tracker });
        const leftControlPanel = new LeftPanelWidget({
            model: controlModel,
            tracker,
            formSchemaRegistry
        });
        leftControlPanel.id = 'jupytercad::leftControlPanel';
        leftControlPanel.title.caption = 'JupyterCad Control Panel';
        leftControlPanel.title.icon = logoIcon;
        const rightControlPanel = new RightPanelWidget({
            model: controlModel,
            tracker,
            annotationModel,
            forkManager,
            collaborativeDrive
        });
        rightControlPanel.id = 'jupytercad::rightControlPanel';
        rightControlPanel.title.caption = 'JupyterCad Control Panel';
        rightControlPanel.title.icon = logoIcon;
        if (restorer) {
            restorer.add(leftControlPanel, `${NAME_SPACE}-left`);
            restorer.add(rightControlPanel, `${NAME_SPACE}-right`);
        }
        app.shell.add(leftControlPanel, 'left', { rank: 2000 });
        app.shell.add(rightControlPanel, 'right', { rank: 2000, activate: false });
    }
};
/**
 * Populates the application menus for the notebook.
 */
function populateMenus(mainMenu, isEnabled) {
    mainMenu.fileMenu.addItem({
        command: CommandIDs.exportJcad
    });
    // Add undo/redo hooks to the edit menu.
    mainMenu.editMenu.undoers.redo.add({
        id: CommandIDs.redo,
        isEnabled
    });
    mainMenu.editMenu.undoers.undo.add({
        id: CommandIDs.undo,
        isEnabled
    });
}
export default [plugin, controlPanel, notebookRenderePlugin];
