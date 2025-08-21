import { setChatFeatureFlags } from '../featureFlags';

// Mock webview module
jest.mock('../webview', () => ({
  postToWebView: jest.fn()
}));

describe('featureFlags.ts', () => {
  const getMockPostToWebView = () => {
    const { postToWebView } = require('../webview');
    return postToWebView;
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('setChatFeatureFlags', () => {
    it('should set single feature flag', () => {
      setChatFeatureFlags(['mcpServers']);

      expect(getMockPostToWebView()).toHaveBeenCalledWith({
        command: 'chatOptions',
        params: {
          mcpServers: true
        }
      });
    });

    it('should set multiple feature flags', () => {
      setChatFeatureFlags(['mcpServers', 'history', 'export']);

      expect(getMockPostToWebView()).toHaveBeenCalledWith({
        command: 'chatOptions',
        params: {
          mcpServers: true,
          history: true,
          export: true
        }
      });
    });

    it('should handle empty feature flags array', () => {
      setChatFeatureFlags([]);

      expect(getMockPostToWebView()).toHaveBeenCalledWith({
        command: 'chatOptions',
        params: {}
      });
    });

    it('should set all flags to true', () => {
      setChatFeatureFlags(['flag1', 'flag2', 'flag3']);

      expect(getMockPostToWebView()).toHaveBeenCalledWith({
        command: 'chatOptions',
        params: {
          flag1: true,
          flag2: true,
          flag3: true
        }
      });
    });
  });
});