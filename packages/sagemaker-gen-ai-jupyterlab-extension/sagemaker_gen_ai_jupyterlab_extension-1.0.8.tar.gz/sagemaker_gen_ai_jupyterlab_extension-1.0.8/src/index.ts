import {
  ILabShell,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { Panel, Widget } from '@lumino/widgets';
import { WebSocketHandler } from './webSocketHandler';
import { registerMessageListeners } from './webview';
import { QIconBlack } from './icons/QIconBlack';
import { registerContextMenuActions } from './contextMenu';
import { INotebookTracker } from '@jupyterlab/notebook';
import { setChatFeatureFlags } from './featureFlags';
import { FLARE_IFRAME_ID } from './constants';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IngressPointService } from './services/IngressPointService';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { observeSettingsChanges } from './observeSettingsChanges';

export function connectWebSocket(
  endPoint = '',
  docManager: IDocumentManager
): WebSocketHandler {
  const settings = ServerConnection.makeSettings();
  const wsUrl = URLExt.join(
    settings.wsUrl,
    'sagemaker_gen_ai_jupyterlab_extension',
    endPoint
  );

  const socket = new WebSocketHandler({ url: wsUrl, docManager });
  return socket;
}

export class FlareWidget extends Widget {
  constructor() {
    super();

    console.log('Creating Q Widget');
    this.addClass('jp-FlareWidget');
    this.node.style.height = '100%';
    this.node.style.overflow = 'hidden';

    // Create container for the iframe
    const container = document.createElement('div');
    container.id = 'jp-FlareContainer';
    container.style.width = '100%';
    container.style.height = '100%';
    this.node.appendChild(container);
  }

  onAfterAttach() {
    console.log('Q Widget attached');
    this.loadContent();
  }

  async loadContent() {
    const container = document.getElementById('jp-FlareContainer');
    if (!container) return;

    try {
      // Create iframe to load test-client.html
      const iframe = document.createElement('iframe');
      iframe.setAttribute(
        'sandbox',
        'allow-scripts allow-same-origin allow-forms allow-popups'
      );

      const settings = ServerConnection.makeSettings();
      const baseUrl = settings.baseUrl;
      iframe.src = URLExt.join(
        baseUrl,
        'sagemaker_gen_ai_jupyterlab_extension',
        'static',
        'client.html'
      );
      iframe.style.width = '100%';
      iframe.style.height = '100%';
      iframe.style.border = 'none';
      iframe.referrerPolicy = 'no-referrer';
      iframe.id = FLARE_IFRAME_ID;

      // Clear container and add iframe
      container.innerHTML = '';
      container.appendChild(iframe);
    } catch (error) {
      container.innerHTML = `<h2>Error Loading Amazon Q Chat</h2><p>${error}</p>`;
    }
  }
}

/**
 * Create a sidebar panel with the Flare widget
 */
export function createFlarePanel(): Panel {
  console.log('Creating Q Panel');
  const panel = new Panel();
  panel.id = 'flare-panel';
  panel.title.icon = QIconBlack;
  panel.title.caption = 'Amazon Q AI Assistant';
  panel.title.closable = true;

  const flareWidget = new FlareWidget();
  panel.addWidget(flareWidget);

  return panel;
}

export type GenericCommandVerb = 'Explain' | 'Refactor' | 'Fix' | 'Optimize';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker_gen_ai_jupyterlab_extension:plugin',
  autoStart: true,
  requires: [ILabShell, IDocumentManager, INotebookTracker, ISettingRegistry],
  optional: [],
  activate: async (
    app: JupyterFrontEnd,
    labShell: ILabShell,
    docManager: IDocumentManager,
    notebookTracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null
  ) => {
    console.log(
      'JupyterLab sagemaker_gen_ai_jupyterlab extension activated!',
      new Date().toISOString()
    );

    const socket = connectWebSocket('ws', docManager);
    if (!socket) {
      console.error(
        'Failed to initialize WebSocket connection. Extension functionality will be limited.'
      );
      return;
    }
    let flarePanel: Panel | null = null;

    // Function to show FlareWidget
    const showFlareWidget = () => {
      try {
        if (!flarePanel) {
          flarePanel = createFlarePanel();
          if (!flarePanel) {
            console.error('Failed to create Q panel');
            return;
          }
          labShell.add(flarePanel, 'left', { rank: Infinity });
        }
        labShell.activateById(flarePanel.id);
      } catch (error) {
        console.error('Error showing Q widget:', error);
      }
    };

    try {
      registerContextMenuActions({ app, notebookTracker, showFlareWidget });
    } catch (error) {
      console.error('Failed to register context menu actions:', error);
    }

    // update LSP server with settings changes
    observeSettingsChanges({
      socket,
      settingRegistry,
      pluginId: plugin.id
    });

    setTimeout(() => {
      try {
        flarePanel = createFlarePanel();
        if (flarePanel) {
          labShell.add(flarePanel, 'left', { rank: Infinity });
          const ingressPointService = new IngressPointService(app, flarePanel);
          ingressPointService.initialize();
          registerMessageListeners(
            socket,
            window,
            notebookTracker,
            docManager,
            labShell
          );
          setChatFeatureFlags(['mcpServers']);
        } else {
          console.error('Failed to create initial Q panel');
        }
      } catch (error) {
        console.error('Error during delayed initialization:', error);
      }
    }, 5000);
  }
};

export default plugin;
