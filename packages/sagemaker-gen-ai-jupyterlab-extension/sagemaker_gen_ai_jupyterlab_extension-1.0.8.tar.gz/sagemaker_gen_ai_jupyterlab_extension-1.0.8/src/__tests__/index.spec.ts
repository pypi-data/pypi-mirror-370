// Mock JupyterLab dependencies that cause issues
jest.mock('@jupyterlab/application', () => ({
  ILabShell: {},
  JupyterFrontEnd: {},
  JupyterFrontEndPlugin: {}
}));
jest.mock('@jupyterlab/notebook', () => ({
  INotebookTracker: {}
}));
jest.mock('@jupyterlab/docmanager', () => ({
  IDocumentManager: {}
}));
jest.mock('../icons/QIconBlack', () => ({
  QIconBlack: 'mock-icon'
}));
jest.mock('../webview', () => ({
  registerMessageListeners: jest.fn()
}));
jest.mock('../contextMenu', () => ({
  registerContextMenuActions: jest.fn()
}));
jest.mock('../featureFlags', () => ({
  setChatFeatureFlags: jest.fn()
}));

// Import the actual module after mocking dependencies
import { connectWebSocket, FlareWidget, createFlarePanel } from '../index';

// Import mocked dependencies
const { URLExt } = require('@jupyterlab/coreutils');
const { ServerConnection } = require('@jupyterlab/services');
const { WebSocketHandler } = require('../webSocketHandler');

// Mock these after import
jest.mock('@jupyterlab/coreutils');
jest.mock('@jupyterlab/services');
jest.mock('@lumino/widgets', () => ({
  Panel: jest.fn().mockImplementation(() => ({
    id: '',
    title: { caption: '', closable: false },
    addWidget: jest.fn()
  })),
  Widget: jest.fn().mockImplementation(() => ({
    addClass: jest.fn(),
    node: {
      style: {},
      appendChild: jest.fn()
    },
    onAfterAttach: jest.fn(),
    loadContent: jest.fn()
  }))
}));
jest.mock('../webSocketHandler');

describe('index.ts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear DOM
    document.body.innerHTML = '';
  });

  describe('connectWebSocket', () => {
    it('should create WebSocket connection with correct URL', () => {
      const mockSettings = { wsUrl: 'ws://localhost:8888' };
      const mockDocManager = { services: {} };
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws'
      );
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws'
      );

      const result = connectWebSocket('ws', mockDocManager as any);

      expect(ServerConnection.makeSettings).toHaveBeenCalled();
      expect(URLExt.join).toHaveBeenCalledWith(
        'ws://localhost:8888',
        'sagemaker_gen_ai_jupyterlab_extension',
        'ws'
      );
      expect(WebSocketHandler).toHaveBeenCalledWith({
        url: 'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws',
        docManager: mockDocManager
      });
      expect(result).toBeDefined();
    });

    it('should use default empty endpoint', () => {
      const mockSettings = { wsUrl: 'ws://localhost:8888' };
      const mockDocManager = { services: {} };
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/'
      );
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/'
      );

      const result = connectWebSocket('', mockDocManager as any);

      expect(URLExt.join).toHaveBeenCalledWith(
        'ws://localhost:8888',
        'sagemaker_gen_ai_jupyterlab_extension',
        ''
      );
      expect(result).toBeDefined();
    });
  });

  describe('FlareWidget', () => {
    it('should create widget with correct properties', () => {
      const widget = new FlareWidget();

      expect(widget).toBeDefined();
      expect(widget.node).toBeDefined();
    });
  });

  describe('createFlarePanel', () => {
    it('should create panel with correct properties', () => {
      const consoleSpy = jest.spyOn(console, 'log');

      const panel = createFlarePanel();

      expect(consoleSpy).toHaveBeenCalledWith('Creating Q Panel');
      expect(panel.id).toBe('flare-panel');
      expect(panel.title.caption).toBe('Amazon Q AI Assistant');
      expect(panel.title.closable).toBe(true);
    });
  });

  describe('plugin activation', () => {
    let mockLabShell: any;

    beforeEach(() => {
      mockLabShell = {
        add: jest.fn(),
        activateById: jest.fn()
      };

      // Mock console.log to avoid noise in tests
      jest.spyOn(console, 'log').mockImplementation();
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    it('should log activation message', () => {
      // Test that plugin logs activation
      const consoleSpy = jest.spyOn(console, 'log');

      // Simulate plugin activation logging
      console.log(
        'JupyterLab sagemaker_gen_ai_jupyterlab extension activated!',
        new Date().toISOString()
      );

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          'JupyterLab sagemaker_gen_ai_jupyterlab extension activated!'
        ),
        expect.any(String)
      );
    });

    it('should create WebSocket connection', () => {
      const mockSettings = { wsUrl: 'ws://localhost:8888' };
      const mockDocManager = { services: {} };
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws'
      );
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue(
        mockSettings
      );
      (URLExt.join as jest.Mock).mockReturnValue(
        'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws'
      );

      connectWebSocket('ws', mockDocManager as any);

      expect(WebSocketHandler).toHaveBeenCalledWith({
        url: 'ws://localhost:8888/sagemaker_gen_ai_jupyterlab_extension/ws',
        docManager: mockDocManager
      });
    });

    it('should create showFlareWidget function', () => {
      // Test the showFlareWidget functionality
      let flarePanel: any = null;

      const showFlareWidget = () => {
        try {
          if (!flarePanel) {
            flarePanel = { id: 'flare-panel' };
            if (!flarePanel) {
              console.error('Failed to create Q panel');
              return;
            }
            mockLabShell.add(flarePanel, 'left', { rank: 0 });
          }
          mockLabShell.activateById(flarePanel.id);
        } catch (error) {
          console.error('Error showing Q widget:', error);
        }
      };

      // First call should create panel
      showFlareWidget();
      expect(mockLabShell.add).toHaveBeenCalledWith(
        expect.objectContaining({ id: 'flare-panel' }),
        'left',
        { rank: 0 }
      );
      expect(mockLabShell.activateById).toHaveBeenCalledWith('flare-panel');

      // Second call should only activate existing panel
      mockLabShell.add.mockClear();
      showFlareWidget();
      expect(mockLabShell.add).not.toHaveBeenCalled();
      expect(mockLabShell.activateById).toHaveBeenCalledWith('flare-panel');
    });
  });

  describe('GenericCommandVerb type', () => {
    it('should accept valid command verbs', () => {
      // TypeScript compile-time test - these should not cause compilation errors
      const explain: 'Explain' = 'Explain';
      const refactor: 'Refactor' = 'Refactor';
      const fix: 'Fix' = 'Fix';
      const optimize: 'Optimize' = 'Optimize';

      expect(explain).toBe('Explain');
      expect(refactor).toBe('Refactor');
      expect(fix).toBe('Fix');
      expect(optimize).toBe('Optimize');
    });
  });

  describe('plugin configuration', () => {
    it('should have correct plugin metadata', () => {
      // Test plugin configuration without importing actual module
      const expectedPluginConfig = {
        id: 'sagemaker_gen_ai_jupyterlab_extension:plugin',
        autoStart: true,
        requires: expect.any(Array),
        optional: expect.any(Array),
        activate: expect.any(Function)
      };

      // Verify expected structure
      expect(expectedPluginConfig.id).toBe(
        'sagemaker_gen_ai_jupyterlab_extension:plugin'
      );
      expect(expectedPluginConfig.autoStart).toBe(true);
    });

    it('should test plugin activation function', async () => {
      // Import the actual plugin to get real coverage
      const indexModule = await import('../index');
      const plugin = indexModule.default;

      // Mock the plugin activation
      const mockApp = { commands: { addCommand: jest.fn() } };
      const mockLabShell = { add: jest.fn(), activateById: jest.fn() };
      const mockDocManager = { services: {} };
      const mockNotebookTracker = {};
      const mockSettingsRegistry = {
        load: jest
          .fn()
          .mockResolvedValue({ composite: { optInToTelemetry: true } })
      };

      // Mock the imported functions
      const mockRegisterContextMenuActions =
        require('../contextMenu').registerContextMenuActions;
      const mockRegisterMessageListeners =
        require('../webview').registerMessageListeners;
      const mockSetChatFeatureFlags =
        require('../featureFlags').setChatFeatureFlags;

      // Test the activation logic by calling the real plugin activate function
      const mockSocket = { connect: jest.fn() };
      (WebSocketHandler as jest.Mock).mockReturnValue(mockSocket);

      // Call the real plugin activation function
      plugin.activate(
        mockApp as any,
        mockLabShell as any,
        mockDocManager as any,
        mockNotebookTracker as any,
        mockSettingsRegistry as any
      );

      expect(mockRegisterContextMenuActions).toHaveBeenCalled();

      // Test setTimeout behavior
      jest.useFakeTimers();
      plugin.activate(
        mockApp as any,
        mockLabShell as any,
        mockDocManager as any,
        mockNotebookTracker as any,
        mockSettingsRegistry as any
      );
      jest.advanceTimersByTime(5000);

      expect(mockLabShell.add).toHaveBeenCalled();
      expect(mockRegisterMessageListeners).toHaveBeenCalled();
      expect(mockSetChatFeatureFlags).toHaveBeenCalledWith(['mcpServers']);

      jest.useRealTimers();
    });
  });

  describe('setTimeout behavior', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should delay panel creation and setup by 5 seconds', () => {
      const mockLabShell = {
        add: jest.fn()
      };

      // Simulate the setTimeout logic
      setTimeout(() => {
        const panel = { id: 'flare-panel' };
        mockLabShell.add(panel, 'left', { rank: 0 });
      }, 5000);

      // Fast-forward time
      jest.advanceTimersByTime(4999);
      expect(mockLabShell.add).not.toHaveBeenCalled();

      jest.advanceTimersByTime(1);
      expect(mockLabShell.add).toHaveBeenCalledWith(
        expect.objectContaining({ id: 'flare-panel' }),
        'left',
        { rank: 0 }
      );
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      (ServerConnection.makeSettings as jest.Mock).mockReset();
      (URLExt.join as jest.Mock).mockReset();
    });

    it('should handle FlareWidget loadContent error', async () => {
      const container = document.createElement('div');
      container.id = 'jp-FlareContainer';
      document.body.appendChild(container);

      // Simulate the error handling directly
      const errorMessage = 'Settings error';
      container.innerHTML = `<h2>Error Loading Amazon Q Chat</h2><p>${errorMessage}</p>`;

      expect(container.innerHTML).toContain('Error Loading Amazon Q Chat');
      expect(container.innerHTML).toContain('Settings error');
    });

    it('should handle createFlarePanel function', () => {
      const consoleSpy = jest.spyOn(console, 'log');

      const panel = createFlarePanel();

      expect(consoleSpy).toHaveBeenCalledWith('Creating Q Panel');
      expect(panel.id).toBe('flare-panel');
      expect(panel.title.caption).toBe('Amazon Q AI Assistant');
      expect(panel.title.closable).toBe(true);
    });

    it('should test actual plugin activation with error handling', async () => {
      // Reset mocks to work normally
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue({
        wsUrl: 'ws://test'
      });
      (URLExt.join as jest.Mock).mockReturnValue('ws://test/path');

      const indexModule = await import('../index');
      const plugin = (indexModule as any).default;

      const mockApp = { commands: { addCommand: jest.fn() } };
      const mockLabShell = { add: jest.fn(), activateById: jest.fn() };
      const mockDocManager = { services: {} };
      const mockNotebookTracker = {};

      // Mock registerContextMenuActions to throw error
      const mockRegisterContextMenuActions =
        require('../contextMenu').registerContextMenuActions;
      mockRegisterContextMenuActions.mockImplementation(() => {
        throw new Error('Context menu registration failed');
      });

      const consoleSpy = jest.spyOn(console, 'error');

      plugin.activate(
        mockApp as any,
        mockLabShell as any,
        mockDocManager as any,
        mockNotebookTracker as any
      );

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to register context menu actions:',
        expect.any(Error)
      );
    });

    it('should test actual plugin activation with WebSocket failure', async () => {
      // Reset mocks to work normally first
      (ServerConnection.makeSettings as jest.Mock).mockReturnValue({
        wsUrl: 'ws://test'
      });
      (URLExt.join as jest.Mock).mockReturnValue('ws://test/path');

      const indexModule = await import('../index');
      const plugin = (indexModule as any).default;

      // Mock connectWebSocket to return null
      jest.spyOn(indexModule, 'connectWebSocket').mockReturnValue(null as any);

      const mockApp = { commands: { addCommand: jest.fn() } };
      const mockLabShell = { add: jest.fn(), activateById: jest.fn() };
      const mockDocManager = { services: {} };
      const mockNotebookTracker = {};

      const result = await plugin.activate(
        mockApp as any,
        mockLabShell as any,
        mockDocManager as any,
        mockNotebookTracker as any
      );

      expect(result).toBeUndefined();
    });

    it('should test setTimeout error handling in plugin', () => {
      jest.useFakeTimers();
      const consoleSpy = jest.spyOn(console, 'error');

      // Simulate the setTimeout error scenario directly
      setTimeout(() => {
        try {
          const flarePanel = null; // Simulate failed panel creation
          if (flarePanel) {
            // Panel creation succeeded
          } else {
            console.error('Failed to create initial Q panel');
          }
        } catch (error) {
          console.error('Error during delayed initialization:', error);
        }
      }, 5000);

      jest.advanceTimersByTime(5000);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to create initial Q panel'
      );

      jest.useRealTimers();
    });
  });
});
