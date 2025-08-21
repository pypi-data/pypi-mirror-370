import { IngressPointService } from '../services/IngressPointService';
import { JupyterFrontEnd, LabShell } from '@jupyterlab/application';
import { Panel } from '@lumino/widgets';
import { TOGGLE_AI_CHAT_MESSAGE } from '../constants';

// Mock dependencies
jest.mock('wildcard-match');
import wcmatch from 'wildcard-match';

describe('IngressPointService', () => {
  let service: IngressPointService;
  let mockApp: jest.Mocked<JupyterFrontEnd>;
  let mockChatPanel: jest.Mocked<Panel>;
  let mockShell: jest.Mocked<LabShell>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock Panel
    mockChatPanel = {
      id: 'test-chat-panel'
    } as jest.Mocked<Panel>;

    // Mock LabShell
    mockShell = {
      widgets: jest.fn(),
      activateById: jest.fn(),
      collapseLeft: jest.fn(),
      collapseRight: jest.fn()
    } as unknown as jest.Mocked<LabShell>;

    // Mock JupyterFrontEnd
    mockApp = {
      shell: mockShell
    } as unknown as jest.Mocked<JupyterFrontEnd>;

    service = new IngressPointService(mockApp, mockChatPanel);
  });

  afterEach(() => {
    window.removeEventListener('message', (service as any).messageListener);
    jest.clearAllMocks();
  });

  describe('initialize', () => {
    it('should add message event listener', async () => {
      const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
      
      await service.initialize();
      
      expect(addEventListenerSpy).toHaveBeenCalledWith('message', expect.any(Function));
    });
  });

  describe('messageListener', () => {
    beforeEach(async () => {
      await service.initialize();
    });

    it('should ignore messages from invalid origins', () => {
      (wcmatch as jest.Mock).mockImplementation(() => () => false);

      const toggleSpy = jest.spyOn(service as any, 'toggleQChat');
      
      const event = new MessageEvent('message', {
        data: TOGGLE_AI_CHAT_MESSAGE,
        origin: 'https://malicious.com'
      });

      window.dispatchEvent(event);

      expect(toggleSpy).not.toHaveBeenCalled();
    });

    it('should handle toggle message from valid origin', () => {
      (wcmatch as jest.Mock).mockImplementation(() => () => true);

      const toggleSpy = jest.spyOn(service as any, 'toggleQChat');
      
      const event = new MessageEvent('message', {
        data: TOGGLE_AI_CHAT_MESSAGE,
        origin: 'https://test.sagemaker.us-east-1.on.aws'
      });

      window.dispatchEvent(event);

      expect(toggleSpy).toHaveBeenCalledWith(mockApp, mockChatPanel);
    });

    it('should ignore non-toggle messages', () => {
      const mockWcmatch = jest.fn().mockReturnValue(() => true);
      (wcmatch as jest.Mock).mockReturnValue(mockWcmatch);

      const toggleSpy = jest.spyOn(service as any, 'toggleQChat');
      
      const event = new MessageEvent('message', {
        data: 'other-message',
        origin: 'https://test.sagemaker.us-east-1.on.aws'
      });

      window.dispatchEvent(event);

      expect(toggleSpy).not.toHaveBeenCalled();
    });
  });

  describe('isMessageOriginValid', () => {
    it('should return true for valid AWS domains', () => {
      (wcmatch as jest.Mock).mockImplementation(() => () => true);

      const event = new MessageEvent('message', {
        origin: 'https://test.sagemaker.us-east-1.on.aws'
      });

      const result = (service as any).isMessageOriginValid(event);

      expect(result).toBe(true);
    });

    it('should return false for invalid domains', () => {
      (wcmatch as jest.Mock).mockImplementation(() => () => false);

      const event = new MessageEvent('message', {
        origin: 'https://malicious.com'
      });

      const result = (service as any).isMessageOriginValid(event);

      expect(result).toBe(false);
    });
  });

  describe('toggleQChat', () => {
    it('should throw error when widget has no id', () => {
      const panelWithoutId = { id: undefined } as unknown as Panel;
      
      expect(() => {
        (service as any).toggleQChat(mockApp, panelWithoutId);
      }).toThrow('Chat widget not found.');
    });
  });
});