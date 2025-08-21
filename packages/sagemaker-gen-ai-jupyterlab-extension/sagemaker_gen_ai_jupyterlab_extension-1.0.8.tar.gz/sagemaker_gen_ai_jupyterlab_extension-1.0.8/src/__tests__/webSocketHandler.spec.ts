import { Message, Response, WebSocketHandler } from '../webSocketHandler';
import { postToWebView } from '../webview';

jest.mock('uuid', () => ({
  v4: jest.fn(() => 'test-uuid-123')
}));

jest.mock('../webview', () => ({
  postToWebView: jest.fn()
}));

jest.mock('@jupyterlab/docmanager', () => ({
  IDocumentManager: {}
}));

interface MockWebSocket {
  OPEN: number;
  CLOSED: number;
  send: jest.Mock;
  close: jest.Mock;
  readyState: number;
  onopen: (() => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
}

const mockWebSocket: MockWebSocket = {
  OPEN: 1,
  CLOSED: 3,
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1,
  onopen: null,
  onclose: null,
  onerror: null,
  onmessage: null
};

// Mock WebSocket constructor
const MockWebSocketConstructor = jest
  .fn()
  .mockImplementation(() => mockWebSocket);
(MockWebSocketConstructor as any).OPEN = 1;
(MockWebSocketConstructor as any).CLOSED = 3;

global.WebSocket = MockWebSocketConstructor as any;

describe('WebSocketHandler', () => {
  let handler: WebSocketHandler;
  let mockDocManager: any;

  beforeEach(async () => {
    jest.clearAllMocks();
    jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation();
    jest.spyOn(console, 'warn').mockImplementation();

    // Reset mock state
    mockWebSocket.readyState = 1;
    mockWebSocket.send.mockClear();

    // Create mock document manager
    mockDocManager = {
      services: {},
      registry: {}
    };

    handler = new WebSocketHandler({
      url: 'ws://test',
      docManager: mockDocManager
    });
    mockWebSocket.onopen?.();
    mockWebSocket.readyState = WebSocket.OPEN;
  });

  it('should initialize correctly', () => {
    expect(handler).toBeDefined();
    expect(global.WebSocket).toHaveBeenCalledWith('ws://test');
  });

  it('should handle open event', () => {
    expect(console.log).toHaveBeenCalledWith(
      'WebSocket connection established'
    );
  });

  it('should handle message with matching origin', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });

    const responseData: Response = {
      id: 'test-id',
      command: 'test',
      params: {}
    };
    const mockHandler: jest.Mock = jest.fn();
    (handler as any).pendingRequests.set('test-id', mockHandler);

    const event: MessageEvent = {
      data: JSON.stringify(responseData),
      origin: 'wss://localhost'
    } as MessageEvent;
    mockWebSocket.onmessage!(event);

    expect(mockHandler).toHaveBeenCalledWith(responseData);
  });

  it('should reject message from different origin', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const responseData: Response = {
      id: 'test-id',
      command: 'test',
      params: {}
    };
    const mockHandler: jest.Mock = jest.fn();
    (handler as any).pendingRequests.set('test-id', mockHandler);

    const event: MessageEvent = {
      data: JSON.stringify(responseData),
      origin: 'wss://malicious.com'
    } as MessageEvent;
    mockWebSocket.onmessage!(event);

    expect(mockHandler).not.toHaveBeenCalled();
    expect(console.warn).toHaveBeenCalledWith(
      'Rejected message from unauthorized origin: wss://malicious.com'
    );
  });

  it('should reject message from insecure websocket', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const responseData: Response = {
      id: 'test-id',
      command: 'test',
      params: {}
    };
    const mockHandler: jest.Mock = jest.fn();
    (handler as any).pendingRequests.set('test-id', mockHandler);

    const event: MessageEvent = {
      data: JSON.stringify(responseData),
      origin: 'ws://localhost'
    } as MessageEvent;
    mockWebSocket.onmessage!(event);

    expect(mockHandler).not.toHaveBeenCalled();
    expect(console.warn).toHaveBeenCalledWith(
      'Rejected message from insecure websocket connection: ws://localhost'
    );
  });

  it('should handle inbound event with secure origin', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const messageData: Message = {
      command: 'aws/chat/sendChatPrompt',
      params: {}
    };
    const event: MessageEvent = {
      data: JSON.stringify(messageData),
      origin: 'wss://localhost'
    } as MessageEvent;

    mockWebSocket.onmessage!(event);

    expect(postToWebView).toHaveBeenCalledWith(messageData);
  });

  it('should handle chat update event', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const chatUpdateData: Message = {
      command: 'aws/chat/sendChatUpdate',
      params: {}
    };
    const chatUpdateEvent: MessageEvent = {
      data: JSON.stringify(chatUpdateData),
      origin: 'wss://localhost'
    } as MessageEvent;

    mockWebSocket.onmessage!(chatUpdateEvent);

    expect(postToWebView).toHaveBeenCalledWith(chatUpdateData);
  });

  it('should handle aws/chat/chatOptionsUpdate event', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const chatOptionsUpdateData: Message = {
      command: 'aws/chat/chatOptionsUpdate',
      params: {}
    };
    const chatOptionsUpdateEvent: MessageEvent = {
      data: JSON.stringify(chatOptionsUpdateData),
      origin: 'wss://localhost'
    } as MessageEvent;

    mockWebSocket.onmessage!(chatOptionsUpdateEvent);

    expect(postToWebView).toHaveBeenCalledWith(chatOptionsUpdateData);
  });

  it('should handle aws/openFileDiff command', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    mockDocManager.openOrReveal = jest.fn();

    const messageData: Message = {
      command: 'aws/openFileDiff',
      params: { originalFileUri: 'home/sagemaker-user/test.py' }
    };
    const event: MessageEvent = {
      data: JSON.stringify(messageData),
      origin: 'wss://localhost'
    } as MessageEvent;

    mockWebSocket.onmessage!(event);

    expect(mockDocManager.openOrReveal).toHaveBeenCalledWith('test.py');
  });

  it('should handle unknown inbound command', () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const messageData: Message = { command: 'unknown/command', params: {} };
    const event: MessageEvent = {
      data: JSON.stringify(messageData),
      origin: 'wss://localhost'
    } as MessageEvent;

    mockWebSocket.onmessage!(event);

    expect(console.log).toHaveBeenCalledWith(
      'Unhandled inbound command: unknown/command'
    );
  });

  it('should send request successfully', async () => {
    Object.defineProperty(window, 'location', {
      value: { origin: 'https://localhost' }
    });
    const message: Message = { command: 'test', params: {} };
    const responseData: Response = {
      id: 'test-uuid-123',
      command: 'test',
      params: {}
    };

    const requestPromise: Promise<Response> = handler.sendRequest(message);
    await Promise.resolve();

    const event: MessageEvent = {
      data: JSON.stringify(responseData),
      origin: 'wss://localhost'
    } as MessageEvent;
    mockWebSocket.onmessage!(event);
    const result: Response = await requestPromise;

    expect(result).toEqual(responseData);
    expect(mockWebSocket.send).toHaveBeenCalled();
  });

  it('should try to reconnect 3 times on closed websocket', async () => {
    jest.useFakeTimers();

    const mockSocketFailure = (attempt: number) => {
      expect(console.log).toHaveBeenCalledWith(
        `Attempting to connect, attempt #${attempt + 1}`
      );
      mockWebSocket?.onerror?.(new Event('test-error'));
      jest.runAllTimers();
    };

    const retryHandler = new WebSocketHandler({
      url: 'ws://test',
      docManager: mockDocManager
    }) as any;

    const setupPromise = retryHandler.setupSocket();
    for (let i = 0; i < 3; i++) {
      mockSocketFailure(i);
    }

    const result = await setupPromise;
    expect(result).toBe(false);

    jest.useRealTimers();
  });

  it('should send notification', async () => {
    const message: Message = { command: 'test', params: {} };

    await handler.sendNotification(message);
    expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(message));
  });

  it('should initialize with docManager', () => {
    expect((handler as any).docManager).toBe(mockDocManager);
  });

  describe('Error Handling with sendErrorToWebview', () => {
    it('should test sendErrorToWebview helper function', () => {
      const testHandler = handler as any;

      testHandler.sendErrorToWebview('Test Title', 'Test Message', 'test-tab');

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Test Title',
          message: 'Test Message',
          tabId: 'test-tab'
        }
      });
    });

    it('should use sendErrorToWebview for connection errors', async () => {
      jest.spyOn(handler as any, 'setupSocket').mockResolvedValueOnce(false);

      const message: Message = {
        command: 'test',
        params: {},
        tabId: 'test-tab'
      };

      const result = handler.sendRequest(message);

      await Promise.resolve();
      await expect(result).rejects.toThrow('WebSocket is not connected');
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Connection Error',
          message: 'WebSocket is not connected, please refresh your page.',
          tabId: 'test-tab'
        }
      });
    });

    it('should use sendErrorToWebview for timeout errors', async () => {
      jest.useFakeTimers();
      const message: Message = {
        command: 'test',
        params: {},
        tabId: 'test-tab'
      };

      const requestPromise = handler.sendRequest(message);
      await Promise.resolve();
      jest.advanceTimersByTime(600000);

      await expect(requestPromise).rejects.toThrow('Request timed out: test');
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Request Timeout',
          message: 'Request timed out: test',
          tabId: 'test-tab'
        }
      });
      jest.useRealTimers();
    });

    it('should use sendErrorToWebview for send errors', async () => {
      mockWebSocket.send.mockImplementation(() => {
        throw new Error('Send failed');
      });

      const message: Message = {
        command: 'test',
        params: {},
        tabId: 'test-tab'
      };

      const result = handler.sendRequest(message);
      await Promise.resolve();
      await expect(result).rejects.toThrow('Send failed');
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Message Sending Error',
          message:
            'Failed to send message, please refresh browser and try again.',
          tabId: 'test-tab'
        }
      });
    });
  });

  describe('sendRequest error handling', () => {
    beforeEach(() => {
      mockWebSocket.send.mockReset();
      Object.defineProperty(window, 'location', {
        value: { origin: 'https://localhost:8080' }
      });
    });

    it('should send error to webview for subscription error', async () => {
      const message = {
        command: 'aws/chat/sendChatPrompt',
        params: { prompt: 'test' },
        tabId: 'tab-1'
      };

      const sendRequestPromise = handler.sendRequest(message);
      await Promise.resolve();

      const errorResponse = {
        id: 'test-uuid-123',
        command: 'aws/chat/sendChatPrompt',
        params: {},
        error: 'You are not subscribed to Amazon Q Developer'
      };

      mockWebSocket.onmessage!({
        data: JSON.stringify(errorResponse),
        origin: 'wss://localhost:8080'
      } as MessageEvent);

      await expect(sendRequestPromise).rejects.toThrow(
        'You are not subscribed to Amazon Q Developer'
      );

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'No active subscription',
          message: 'You are not subscribed to Amazon Q Developer',
          tabId: 'tab-1'
        }
      });
    });

    it('should send server error to webview for 500 errors', async () => {
      const message = {
        command: 'aws/chat/sendChatPrompt',
        params: { prompt: 'test' },
        tabId: 'tab-2'
      };

      const sendRequestPromise = handler.sendRequest(message);
      await Promise.resolve();

      const errorResponse = {
        id: 'test-uuid-123',
        command: 'aws/chat/sendChatPrompt',
        params: {},
        error: 'Something went wrong. Please try again later.'
      };

      if (mockWebSocket.onmessage) {
        mockWebSocket.onmessage({
          data: JSON.stringify(errorResponse),
          origin: 'wss://localhost:8080'
        } as MessageEvent);
      }

      await expect(sendRequestPromise).rejects.toThrow(
        'Something went wrong. Please try again later.'
      );

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Internal Server Error',
          message: 'Something went wrong. Please try again later.',
          tabId: 'tab-2'
        }
      });
    });

    it('should send client error to webview for 400 errors', async () => {
      const message = {
        command: 'aws/chat/sendChatPrompt',
        params: { prompt: 'test' },
        tabId: 'tab-3'
      };

      const sendRequestPromise = handler.sendRequest(message);
      await Promise.resolve();

      const errorResponse = {
        id: 'test-uuid-123',
        command: 'aws/chat/sendChatPrompt',
        params: {},
        error: 'Bad request: Invalid parameters'
      };

      if (mockWebSocket.onmessage) {
        mockWebSocket.onmessage({
          data: JSON.stringify(errorResponse),
          origin: 'wss://localhost:8080'
        } as MessageEvent);
      }

      await expect(sendRequestPromise).rejects.toThrow(
        'Bad request: Invalid parameters'
      );

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'errorMessage',
        params: {
          title: 'Response Error',
          message: 'Bad request: Invalid parameters',
          tabId: 'tab-3'
        }
      });
    });
  });
});
