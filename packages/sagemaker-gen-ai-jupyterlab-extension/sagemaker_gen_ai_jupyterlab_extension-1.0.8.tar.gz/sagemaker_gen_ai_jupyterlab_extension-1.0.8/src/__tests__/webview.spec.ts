import { postToWebView, registerMessageListeners } from '../webview';
import { FLARE_IFRAME_ID, DEFAULT_CURSOR_STATE } from '../constants';
import { WebSocketHandler, Message } from '../webSocketHandler';
import { INotebookTracker } from '@jupyterlab/notebook';
import { storeAcknowledgements } from '../acknowledgements';
import * as utils from '../utils';

jest.mock('../webSocketHandler');

// Mock acknowledgements module
jest.mock('../acknowledgements', () => ({
  storeAcknowledgements: jest.fn()
}));

const insertToCursorPositionSpy = jest.spyOn(utils, 'insertToCursorPosition');

const mockActiveFilePath = 'file:///home/sagemaker-user/src/active.ts';
const mockContext = {
  path: 'src/active.ts'
};

const mockLabShell = {
  add: jest.fn(),
  activateById: jest.fn(),
  currentWidget: jest.fn()
} as any;
const mockDocManager = {
  services: {},
  contextForWidget: jest.fn().mockReturnValue(mockContext)
} as any;

describe('webview.ts', () => {
  let mockIframe: HTMLIFrameElement;
  let mockContentWindow: Window;
  let mockSocket: jest.Mocked<WebSocketHandler>;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'log').mockImplementation();

    // Reset mocks
    (storeAcknowledgements as jest.Mock).mockClear();
    (insertToCursorPositionSpy as jest.Mock).mockClear();

    // Mock iframe and content window
    mockContentWindow = {
      postMessage: jest.fn()
    } as any;

    mockIframe = {
      contentWindow: mockContentWindow
    } as HTMLIFrameElement;

    // Mock WebSocketHandler
    mockSocket = {
      sendRequest: jest.fn().mockResolvedValue({}),
      sendNotification: jest.fn()
    } as any;

    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: {
        origin: 'http://localhost:8888'
      },
      writable: true
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('postToWebView', () => {
    it('should post message to iframe content window', () => {
      jest.spyOn(document, 'getElementById').mockReturnValue(mockIframe);

      const payload = { type: 'test', data: 'hello' };
      postToWebView(payload);

      expect(document.getElementById).toHaveBeenCalledWith(FLARE_IFRAME_ID);
      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        payload,
        'http://localhost:8888'
      );
    });

    it('should throw error when iframe not found', () => {
      jest.spyOn(document, 'getElementById').mockReturnValue(null);

      expect(() => postToWebView({ test: 'data' })).toThrow(
        'Q Chat UI not mounted'
      );
    });

    it('should throw error when iframe has no content window', () => {
      const iframeWithoutContent = { contentWindow: null } as HTMLIFrameElement;
      jest
        .spyOn(document, 'getElementById')
        .mockReturnValue(iframeWithoutContent);

      expect(() => postToWebView({ test: 'data' })).toThrow(
        'Q Chat UI not mounted'
      );
    });

    it('should handle complex payload objects', () => {
      jest.spyOn(document, 'getElementById').mockReturnValue(mockIframe);

      const complexPayload = {
        command: 'aws/chat/response',
        params: {
          tabId: 'tab-123',
          messages: [
            { role: 'user', content: 'Hello' },
            { role: 'assistant', content: 'Hi there!' }
          ],
          metadata: {
            timestamp: Date.now(),
            requestId: 'req-456'
          }
        }
      };

      postToWebView(complexPayload);

      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        complexPayload,
        'http://localhost:8888'
      );
    });

    it('should handle different window origins', () => {
      jest.spyOn(document, 'getElementById').mockReturnValue(mockIframe);

      // Change window origin
      Object.defineProperty(window, 'location', {
        value: { origin: 'https://example.com:3000' },
        writable: true
      });

      const payload = { message: 'test' };
      postToWebView(payload);

      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        payload,
        'https://example.com:3000'
      );
    });
  });

  describe('registerMessageListeners', () => {
    let mockContainer: Window;
    let eventListeners: { [key: string]: Function };
    let mockNotebookTracker: INotebookTracker;

    beforeEach(() => {
      eventListeners = {};
      mockContainer = {
        addEventListener: jest.fn((event, callback) => {
          eventListeners[event] = callback;
        })
      } as any;

      mockNotebookTracker = {
        currentWidget: null
      } as any;

      jest.spyOn(document, 'getElementById').mockReturnValue(mockIframe);

      registerMessageListeners(
        mockSocket,
        mockContainer,
        mockNotebookTracker,
        mockDocManager,
        mockLabShell
      );
    });

    it('should register message event listener', () => {
      expect(mockContainer.addEventListener).toHaveBeenCalledWith(
        'message',
        expect.any(Function)
      );
    });

    it('should handle aws/chat/sendChatPrompt command', async () => {
      const message: Message = {
        command: 'aws/chat/sendChatPrompt',
        params: {
          tabId: 'tab-123',
          prompt: 'Hello, how are you?',
          cursorState: [DEFAULT_CURSOR_STATE],
          textDocument: { uri: mockActiveFilePath }
        }
      };

      const mockResponse = { response: 'I am doing well, thank you!' };
      (mockSocket.sendRequest as jest.Mock).mockResolvedValue(mockResponse);

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendRequest).toHaveBeenCalledWith({
        ...message,
        tabId: 'tab-123'
      });
      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        mockResponse,
        'http://localhost:8888'
      );
    });

    it('should handle aws/chat/buttonClick command', async () => {
      const message: Message = {
        command: 'aws/chat/buttonClick',
        params: {
          tabId: 'tab-456',
          buttonId: 'accept-suggestion'
        }
      };

      const mockResponse = { success: true };
      (mockSocket.sendRequest as jest.Mock).mockResolvedValue(mockResponse);

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendRequest).toHaveBeenCalledWith({
        ...message,
        tabId: 'tab-456'
      });
      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        mockResponse,
        'http://localhost:8888'
      );
    });

    it('should handle aws/chat/ready notifications, send chatOptions and call mcpServerClick', async () => {
      const message: Message = {
        command: 'aws/chat/ready',
        params: { ready: true }
      };

      const windowPostMessageSpy = jest.spyOn(window, 'postMessage');

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendNotification).toHaveBeenCalledWith(message);
      expect(mockContentWindow.postMessage).toHaveBeenCalledWith(
        {
          command: 'chatOptions',
          params: {
            mcpServers: true,
            history: true
          }
        },
        'http://localhost:8888'
      );
      expect(windowPostMessageSpy).toHaveBeenCalledWith(
        {
          command: 'aws/chat/mcpServerClick',
          params: {
            id: 'refresh-mcp-list'
          }
        },
        '*'
      );
      expect(mockSocket.sendRequest).not.toHaveBeenCalled();
    });

    it('should handle aws/chat/tabAdd notification', async () => {
      const message: Message = {
        command: 'aws/chat/tabAdd',
        params: {
          tabId: 'new-tab-789',
          title: 'New Chat Tab'
        }
      };

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendNotification).toHaveBeenCalledWith(message);
      expect(mockSocket.sendRequest).not.toHaveBeenCalled();
    });

    it('should handle acknowledgement commands', async () => {
      const disclaimerMessage: Message = {
        command: 'disclaimerAcknowledged',
        params: {}
      };

      const chatPromptMessage: Message = {
        command: 'chatPromptOptionAcknowledged',
        params: {}
      };

      await eventListeners['message']({ data: disclaimerMessage });
      await eventListeners['message']({ data: chatPromptMessage });

      expect(storeAcknowledgements).toHaveBeenCalledWith(
        'disclaimerAcknowledged'
      );
      expect(storeAcknowledgements).toHaveBeenCalledWith(
        'chatPromptOptionAcknowledged'
      );
    });

    it('should handle unknown commands', async () => {
      const message: Message = {
        command: 'unknown/command',
        params: { test: 'data' }
      };

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendRequest).not.toHaveBeenCalled();
      expect(mockSocket.sendNotification).not.toHaveBeenCalled();
    });

    it('should handle messages without tabId', async () => {
      const message: Message = {
        command: 'aws/chat/sendChatPrompt',
        params: {
          prompt: 'Hello without tabId',
          cursorState: [DEFAULT_CURSOR_STATE],
          textDocument: { uri: mockActiveFilePath }
        }
      };

      const mockResponse = { response: 'Response without tabId' };
      (mockSocket.sendRequest as jest.Mock).mockResolvedValue(mockResponse);

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendRequest).toHaveBeenCalledWith({
        ...message,
        tabId: undefined
      });
    });

    it('should handle messages without params', async () => {
      const message: Message = {
        command: 'aws/chat/ready',
        params: {}
      };

      await eventListeners['message']({ data: message });

      expect(mockSocket.sendNotification).toHaveBeenCalledWith(message);
    });

    it('should handle multiple message types in sequence', async () => {
      const messages: Message[] = [
        { command: 'aws/chat/ready', params: { ready: true } },
        {
          command: 'aws/chat/sendChatPrompt',
          params: { tabId: 'tab-1', prompt: 'Hello' }
        },
        { command: 'aws/chat/tabAdd', params: { tabId: 'tab-2' } },
        {
          command: 'aws/chat/buttonClick',
          params: { tabId: 'tab-1', buttonId: 'btn-1' }
        }
      ];

      (mockSocket.sendRequest as jest.Mock).mockResolvedValue({
        success: true
      });

      for (const message of messages) {
        await eventListeners['message']({ data: message });
      }

      expect(mockSocket.sendNotification).toHaveBeenCalledTimes(2);
      expect(mockSocket.sendRequest).toHaveBeenCalledTimes(2);
    });

    it('should preserve message structure when forwarding', async () => {
      const originalMessage: Message = {
        command: 'aws/chat/sendChatPrompt',
        params: {
          tabId: 'preserve-test',
          prompt: 'Test message',
          metadata: {
            timestamp: 1234567890,
            userId: 'user-123'
          }
        }
      };

      const mockResponse = { response: 'Preserved response' };
      (mockSocket.sendRequest as jest.Mock).mockResolvedValue(mockResponse);

      await eventListeners['message']({ data: originalMessage });

      expect(mockSocket.sendRequest).toHaveBeenCalledWith({
        command: 'aws/chat/sendChatPrompt',
        params: {
          tabId: 'preserve-test',
          prompt: 'Test message',
          metadata: {
            timestamp: 1234567890,
            userId: 'user-123'
          },
          cursorState: [DEFAULT_CURSOR_STATE],
          textDocument: { uri: mockActiveFilePath }
        },
        tabId: 'preserve-test'
      });
    });

    it('should handle concurrent message processing', async () => {
      const message1: Message = {
        command: 'aws/chat/sendChatPrompt',
        params: { tabId: 'tab-1', prompt: 'First message' }
      };

      const message2: Message = {
        command: 'aws/chat/sendChatPrompt',
        params: { tabId: 'tab-2', prompt: 'Second message' }
      };

      (mockSocket.sendRequest as jest.Mock)
        .mockResolvedValueOnce({ response: 'First response' })
        .mockResolvedValueOnce({ response: 'Second response' });

      // Process messages concurrently
      await Promise.all([
        eventListeners['message']({ data: message1 }),
        eventListeners['message']({ data: message2 })
      ]);

      expect(mockSocket.sendRequest).toHaveBeenCalledTimes(2);
      expect(mockContentWindow.postMessage).toHaveBeenCalledTimes(2);
    });

    it('should handle insertToCursorPosition command', async () => {
      const message: Message = {
        command: 'insertToCursorPosition',
        params: {
          code: 'console.log("Hello from SMUS..!!");'
        }
      };

      const insertToCursorPositionSpy = jest
        .spyOn(utils, 'insertToCursorPosition')
        .mockImplementation(() => {
          return message;
        });

      await eventListeners['message']({ data: message });

      expect(insertToCursorPositionSpy).toHaveBeenCalledWith(
        mockNotebookTracker,
        'console.log("Hello from SMUS..!!");'
      );
    });

    it('should not call insertToCursorPosition when notebookTracker is null', async () => {
      const nullNotebookTracker = null;
      registerMessageListeners(
        mockSocket,
        mockContainer,
        nullNotebookTracker as any,
        mockDocManager,
        mockLabShell
      );

      const message: Message = {
        command: 'insertToCursorPosition',
        params: {
          code: 'console.log("Hello from SMUS..!!");'
        }
      };

      await eventListeners['message']({ data: message });

      expect(insertToCursorPositionSpy).not.toHaveBeenCalled();
    });

    it('should not call insertToCursorPosition when params is missing', async () => {
      const message = {
        command: 'insertToCursorPosition',
        params: {}
      } as Message;

      await eventListeners['message']({ data: message });

      expect(insertToCursorPositionSpy).not.toHaveBeenCalled();
    });

    it('should not call insertToCursorPosition when code is empty', async () => {
      const message: Message = {
        command: 'insertToCursorPosition',
        params: {
          code: ''
        }
      };

      await eventListeners['message']({ data: message });

      expect(insertToCursorPositionSpy).not.toHaveBeenCalled();
    });
  });
});
