import { IDocumentManager } from '@jupyterlab/docmanager';
import { v4 as uuid } from 'uuid';
import { ContextCommandParams } from './types';
import { postToWebView } from './webview';

type MessageData = Record<string, unknown>;

export interface Message {
  command: string;
  params: MessageData;
  tabId?: string;
}

export interface Response extends Message {
  id: string;
  error?: string;
}

interface WebSocketHandlerParams {
  url: string;
  docManager: IDocumentManager;
  reconnectInterval?: number;
  timeout?: number;
}

export class WebSocketHandler {
  private socket!: WebSocket; // Using definite assignment assertion
  private pendingRequests = new Map<string, (response: Response) => void>();
  private timeout: number;
  private docManager: IDocumentManager;
  private url: string;
  private reconnectInterval: number;
  private heartbeatInterval?: NodeJS.Timeout;
  private connectionPromise?: Promise<boolean>;

  private sendErrorToWebview(
    title: string,
    message: string,
    tabId?: string
  ): void {
    const errorPayload = {
      command: 'errorMessage',
      params: {
        title,
        message,
        tabId
      }
    };
    postToWebView(errorPayload);
  }

  constructor({
    url,
    docManager,
    reconnectInterval = 1000,
    timeout = 600000
  }: WebSocketHandlerParams) {
    this.url = url;
    this.reconnectInterval = reconnectInterval;
    this.timeout = timeout;
    this.docManager = docManager;
    this.setupSocket();
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.sendNotification({ command: 'ping', params: {} });
    }, 20 * 1000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = undefined;
    }
  }

  private setupSocket(maxAttempts: number = 3): Promise<boolean> {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return Promise.resolve(true);
    }

    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = new Promise(resolve => {
      let attempts = 0;

      const tryConnect = () => {
        if (attempts >= maxAttempts) {
          this.connectionPromise = undefined;
          resolve(false);
          return;
        }

        attempts++;
        console.log(`Attempting to connect, attempt #${attempts}`);
        const newSocket = new WebSocket(this.url);

        newSocket.onopen = () => {
          console.log('WebSocket connection established');
          this.socket = newSocket;
          this.socket.onmessage = this.onMessage.bind(this);
          this.startHeartbeat();

          this.socket.onerror = error =>
            console.error('WebSocket error:', error);
          this.socket.onclose = event => {
            console.log(
              'WebSocket connection closed:',
              event.code,
              event.reason
            );
            this.stopHeartbeat();
            this.connectionPromise = undefined;
            this.setupSocket(5);
          };

          this.connectionPromise = undefined;
          resolve(true);
        };

        newSocket.onerror = () => {
          const delay = this.reconnectInterval * Math.pow(2, attempts - 1);
          setTimeout(tryConnect, delay);
        };
      };

      tryConnect();
    });

    return this.connectionPromise;
  }

  private onMessage(event: MessageEvent<string>): void {
    if (event.origin && !event.origin.startsWith('wss://')) {
      console.warn(
        `Rejected message from insecure websocket connection: ${event.origin}`
      );
      return;
    }
    // Only allow messages from the same origin
    if (
      event.origin &&
      event.origin.replace('wss://', '') !==
        window.location.origin.replace('https://', '')
    ) {
      console.warn(
        `Rejected message from unauthorized origin: ${event.origin}`
      );
      return;
    }

    try {
      const message = JSON.parse(event.data);
      const id = message.id;
      console.log('WebSocket message received:', message);

      if (id) {
        const handler = this.pendingRequests.get(id);
        if (handler) {
          handler(message);
        } else {
          console.warn(`No handler found for message with id: ${id}`);
        }
      } else {
        this.handleInboundEvent(message);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      const message = JSON.parse(event.data);
      this.sendErrorToWebview(
        'Message Processing Error',
        'Failed to process message, please refresh browser and try again.',
        message.tabId
      );
    }
  }

  private handleInboundEvent(message: Message): void {
    try {
      const command = message.command;
      console.log('Handling inbound event:', { command });

      switch (command) {
        case 'aws/chat/sendChatPrompt':
        case 'aws/chat/buttonClick':
        case 'aws/chat/sendPinnedContext':
        case 'aws/chat/openTab':
        case 'aws/chat/sendChatUpdate':
        case 'aws/chat/chatOptionsUpdate':
          postToWebView(message);
          break;
        case 'aws/chat/sendContextCommands':
          const workingCommands = ['Folders', 'Files'];

          const contextCommandParams =
            message.params as unknown as ContextCommandParams;

          const filteredContextCommandGroups =
            contextCommandParams.contextCommandGroups.map(
              contextCommandGroup => {
                const filteredCommands = contextCommandGroup?.commands.filter(
                  command => workingCommands.includes(command.command)
                );
                return {
                  ...contextCommandGroup,
                  commands: filteredCommands
                };
              }
            );

          postToWebView({
            ...message,
            params: {
              ...message.params,
              contextCommandGroups: filteredContextCommandGroups
            }
          });
          break;
        case 'aws/openFileDiff':
          // TODO: Add diff visual
          this.docManager.openOrReveal(
            (message.params.originalFileUri as string).replace(
              'home/sagemaker-user/',
              ''
            )
          );
          break;
        case 'ping':
          console.log('Received ping');
          break;
        default:
          console.log(`Unhandled inbound command: ${command}`);
      }
    } catch (error) {
      console.error('Error handling event:', error);
      this.sendErrorToWebview(
        'Event Handling Error',
        'Failed to handle inbound event, please refresh browser and try again.',
        message.tabId
      );
    }
  }

  public async sendRequest(message: Message): Promise<Response> {
    const isConnected = await this.setupSocket();
    if (!isConnected) {
      this.sendErrorToWebview(
        'Connection Error',
        'WebSocket is not connected, please refresh your page.',
        message.tabId
      );
      return Promise.reject(new Error('WebSocket is not connected'));
    }

    const id = uuid();
    console.log(`Sending request with id: ${id}, command: ${message.command}`);

    return new Promise<Response>((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        console.error(`Request timed out: ${message.command} (id: ${id})`);
        this.sendErrorToWebview(
          'Request Timeout',
          `Request timed out: ${message.command}`,
          message.tabId
        );
        reject(new Error(`Request timed out: ${message.command}`));
      }, this.timeout);

      this.pendingRequests.set(id, response => {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);

        if (response.error) {
          if (
            response.error
              .toLowerCase()
              .includes('you are not subscribed to amazon q developer')
          ) {
            this.sendErrorToWebview(
              'No active subscription',
              response.error,
              message.tabId
            );
          } else if (response.error.includes('Something went wrong')) {
            this.sendErrorToWebview(
              'Internal Server Error',
              response.error,
              message.tabId
            );
          } else {
            this.sendErrorToWebview(
              'Response Error',
              response.error,
              message.tabId
            );
          }
          reject(new Error(response.error));
        } else {
          console.log(`Received response for id: ${id}`);
          resolve(response);
        }
      });

      try {
        const payload = { ...message, id };
        console.log('Sending payload:', payload);
        this.socket.send(JSON.stringify(payload));
      } catch (error) {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);
        this.sendErrorToWebview(
          'Message Sending Error',
          'Failed to send message, please refresh browser and try again.',
          message.tabId
        );
        reject(error);
      }
    });
  }

  public async sendNotification(message: Message): Promise<boolean> {
    const isConnected = await this.setupSocket();
    if (isConnected) {
      console.log(`Sending notification: ${message.command}`);
      this.socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }
}
