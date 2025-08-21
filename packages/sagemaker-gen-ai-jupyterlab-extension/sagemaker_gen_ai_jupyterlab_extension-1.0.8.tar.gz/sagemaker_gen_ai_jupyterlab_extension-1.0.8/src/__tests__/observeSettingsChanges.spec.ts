import { observeSettingsChanges } from '../observeSettingsChanges';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { WebSocketHandler } from '../webSocketHandler';

// Mock WebSocketHandler
jest.mock('../webSocketHandler');

describe('observeSettingsChanges', () => {
  let mockSocket: jest.Mocked<WebSocketHandler>;
  let mockSettingRegistry: jest.Mocked<ISettingRegistry>;
  let mockSettings: any;
  let mockChangedSignal: any;

  beforeEach(() => {
    // Mock WebSocketHandler
    mockSocket = {
      sendNotification: jest.fn()
    } as any;

    // Mock changed signal
    mockChangedSignal = {
      connect: jest.fn()
    };

    // Mock settings object
    mockSettings = {
      get: jest.fn(),
      changed: mockChangedSignal
    };

    // Mock setting registry
    mockSettingRegistry = {
      load: jest.fn().mockResolvedValue(mockSettings)
    } as any;

    // Mock console.log
    jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should load settings and connect to changed signal', async () => {
    const pluginId = 'test-plugin-id';

    observeSettingsChanges({
      socket: mockSocket,
      settingRegistry: mockSettingRegistry,
      pluginId
    });

    // Wait for promise to resolve
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(mockSettingRegistry.load).toHaveBeenCalledWith(pluginId);
    expect(mockChangedSignal.connect).toHaveBeenCalled();
  });

  it('should send notification when settings change', async () => {
    const pluginId = 'test-plugin-id';

    // Mock the setting value
    mockSettings.get.mockReturnValue({ composite: true });

    observeSettingsChanges({
      socket: mockSocket,
      settingRegistry: mockSettingRegistry,
      pluginId
    });

    // Wait for promise to resolve
    await new Promise(resolve => setTimeout(resolve, 0));

    // Get the callback function passed to connect
    const changeCallback = mockChangedSignal.connect.mock.calls[0][0];

    // Trigger the callback
    changeCallback();

    expect(mockSocket.sendNotification).toHaveBeenCalledWith({
      command: 'workspace/didChangeConfiguration',
      params: {}
    });
  });

  it('should handle null settingRegistry gracefully', () => {
    const pluginId = 'test-plugin-id';

    expect(() => {
      observeSettingsChanges({
        socket: mockSocket,
        settingRegistry: null as any,
        pluginId
      });
    }).not.toThrow();

    expect(mockSocket.sendNotification).not.toHaveBeenCalled();
  });

  it('should handle null settings gracefully', async () => {
    const pluginId = 'test-plugin-id';

    // Mock load to return undefined
    mockSettingRegistry.load.mockResolvedValue(undefined as any);

    observeSettingsChanges({
      socket: mockSocket,
      settingRegistry: mockSettingRegistry,
      pluginId
    });

    // Wait for promise to resolve
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(mockSocket.sendNotification).not.toHaveBeenCalled();
  });
});
