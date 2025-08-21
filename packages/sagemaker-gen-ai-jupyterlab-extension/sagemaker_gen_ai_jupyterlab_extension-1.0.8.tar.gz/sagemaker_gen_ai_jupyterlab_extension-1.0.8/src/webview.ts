import { ILabShell } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker } from '@jupyterlab/notebook';
import { storeAcknowledgements } from './acknowledgements';
import {
  DEFAULT_CURSOR_STATE,
  FLARE_IFRAME_ID,
  QUICK_ACTIONS,
  WORKSPACE_ROOT_PATH
} from './constants';
import {
  getActiveFileContext,
  getSelectionOrCellContent,
  insertToCursorPosition
} from './utils';
import { Message, WebSocketHandler } from './webSocketHandler';

interface IOpenLinkMessage {
  type: 'openLink';
  url: string;
}

export const postToWebView = (payload: any) => {
  const chatFrame = document.getElementById(
    FLARE_IFRAME_ID
  ) as HTMLIFrameElement;

  if (!chatFrame || !chatFrame.contentWindow) {
    throw new Error('Q Chat UI not mounted');
  }

  chatFrame.contentWindow.postMessage(payload, window.location.origin);
};

// Outbound commands
export function registerMessageListeners(
  socket: WebSocketHandler,
  container: Window,
  notebookTracker: INotebookTracker,
  docManager: IDocumentManager,
  labShell: ILabShell
) {
  container.addEventListener('message', async (event: { data: Message }) => {
    const message = event.data;
    const command = message.command;
    const tabId = message.params?.tabId as string | undefined;

    switch (command) {
      case 'aws/chat/sendChatPrompt':
        try {
          const activeFileContext = getActiveFileContext({
            docManager,
            labShell
          });

          const response = await socket.sendRequest({
            ...message,
            tabId,
            params: {
              ...message.params,
              textDocument: activeFileContext
                ? {
                    uri: `file://${WORKSPACE_ROOT_PATH}/${activeFileContext?.path}`
                  }
                : undefined,
              cursorState: [DEFAULT_CURSOR_STATE]
            }
          });
          postToWebView(response);
        } catch (error) {
          console.error(error);
        }
        break;
      case 'aws/chat/buttonClick':
      case 'aws/chat/listMcpServers':
      case 'aws/chat/mcpServerClick':
      case 'aws/chat/listConversations':
      case 'aws/chat/listRules':
      case 'aws/chat/conversationClick':
        try {
          const response = await socket.sendRequest({
            ...message,
            tabId
          });
          postToWebView(response);
        } catch (error) {
          console.error(error);
        }
        break;
      case 'aws/chat/ready':
        {
          socket.sendNotification(message);

          const chatOptionsEvent = {
            command: 'chatOptions',
            params: {
              mcpServers: true,
              history: true
            }
          };

          postToWebView(chatOptionsEvent);

          // Temporary fix for MCP Servers not refreshing on ChatUI mount bug
          const refreshMCPListEvent = {
            command: 'aws/chat/mcpServerClick',
            params: {
              id: 'refresh-mcp-list'
            }
          };

          window.postMessage(refreshMCPListEvent, '*');
        }
        break;
      case 'aws/chat/sendChatQuickAction':
        try {
          const response = await socket.sendRequest({
            ...message,
            tabId
          });
          const quickAction = message.params.quickAction;

          if (quickAction === QUICK_ACTIONS.HELP) {
            postToWebView({
              ...response,
              command: 'aws/chat/sendChatPrompt'
            });
            return;
          }

          if (
            typeof quickAction === 'string' &&
            [
              QUICK_ACTIONS.FIX,
              QUICK_ACTIONS.EXPLAIN,
              QUICK_ACTIONS.OPTIMIZE,
              QUICK_ACTIONS.REFACTOR
            ].includes(quickAction as any)
          ) {
            const command = quickAction.slice(1); // removes leading slash

            postToWebView({
              command: 'genericCommand',
              params: {
                genericCommand: command,
                selection:
                  message.params.prompt ||
                  getSelectionOrCellContent(
                    notebookTracker,
                    command === 'fix' ? 'Fix' : undefined
                  ),
                triggerType: 'contextMenu'
              }
            });
          }
        } catch (error) {
          console.error(error);
        }
        break;
      case 'aws/chat/tabAdd':
      case 'aws/chat/tabChange':
      case 'aws/chat/tabRemove':
      case 'aws/chat/pinnedContextAdd':
      case 'aws/chat/pinnedContextRemove':
      case 'aws/chat/createPrompt':
      case 'aws/chat/fileClick':
      case 'stopChatResponse':
      case 'aws/chat/openTab':
      case 'aws/chat/promptInputOptionChange':
        socket.sendNotification(message);
        break;
      case 'chatPromptOptionAcknowledged':
      case 'disclaimerAcknowledged':
        storeAcknowledgements(command);
        break;
      case 'aws/chat/linkClick':
      case 'aws/chat/infoLinkClick':
        // post a message to the iframe parent (SMUS app shell)
        // app shell will be responsible for opening the link
        const openLinkMessage: IOpenLinkMessage = {
          type: 'openLink',
          url: message.params.link as string
        };
        window.parent.postMessage(openLinkMessage, '*');
        break;
      case 'insertToCursorPosition': {
        if (notebookTracker && message.params) {
          const code = message.params.code as string;
          if (code) {
            insertToCursorPosition(notebookTracker, code);
          }
        }
        break;
      }
      default:
        // Uncomment the following for debugging/development purposes
        // console.log(`Unhandled outbound command: ${command}`);
        break;
    }
  });
}
