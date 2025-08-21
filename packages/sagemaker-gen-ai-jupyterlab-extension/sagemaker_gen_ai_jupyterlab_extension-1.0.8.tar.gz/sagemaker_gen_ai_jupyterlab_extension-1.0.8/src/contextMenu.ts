import { JupyterFrontEnd } from '@jupyterlab/application';
import { Menu } from '@lumino/widgets';
import { INotebookTracker } from '@jupyterlab/notebook';
import { postToWebView } from './webview';
import { getSelectionOrCellContent, hasError } from './utils';

export type GenericCommandVerb = 'Explain' | 'Refactor' | 'Fix' | 'Optimize';

/**
 * This function adds a context menu item for Amazon Q and the related commands to
 * pass content to Q chat. These context menus are available in notebook views.
 */
export const registerContextMenuActions = ({
  app,
  notebookTracker,
  showFlareWidget
}: {
  app: JupyterFrontEnd;
  notebookTracker: INotebookTracker;
  showFlareWidget: () => void;
}) => {
  const verbs: GenericCommandVerb[] = [
    'Explain',
    'Refactor',
    'Fix',
    'Optimize'
  ];

  // Register individual commands
  verbs.forEach(verb => {
    const commandId = `sagemaker-gen-ai:${verb.toLowerCase()}`;

    app.commands.addCommand(commandId, {
      label: `${verb}`,
      isEnabled: () => (verb === 'Fix' ? hasError(notebookTracker) : true),
      execute: () => {
        const selection = getSelectionOrCellContent(notebookTracker, verb);
        if (selection) {
          console.log(`${verb}:`, selection);
          showFlareWidget();
          postToWebView({
            command: 'genericCommand',
            params: {
              genericCommand: verb,
              selection,
              triggerType: 'contextMenu'
            }
          });
        }
      }
    });
  });

  // Create submenu
  const submenu = new Menu({ commands: app.commands });
  submenu.title.label = 'Amazon Q';

  // Add commands to the submenu
  verbs.forEach(verb => {
    submenu.addItem({
      command: `sagemaker-gen-ai:${verb.toLowerCase()}`
    });
  });

  const selectorsWhereQMenuIsRendered = ['.jp-CodeCell'];

  selectorsWhereQMenuIsRendered.forEach(selector =>
    app.contextMenu.addItem({
      type: 'submenu',
      submenu: submenu,
      selector,
      rank: 0
    })
  );
};
