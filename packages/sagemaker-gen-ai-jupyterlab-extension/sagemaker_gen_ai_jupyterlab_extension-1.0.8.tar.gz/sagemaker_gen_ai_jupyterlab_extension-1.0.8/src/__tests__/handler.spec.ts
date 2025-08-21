import { requestAPI } from '../handler';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

// Mock dependencies
jest.mock('@jupyterlab/coreutils');
jest.mock('@jupyterlab/services');

const mockURLExt = URLExt as jest.Mocked<typeof URLExt>;
const mockServerConnection = ServerConnection as jest.Mocked<
  typeof ServerConnection
>;

describe('handler.ts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('requestAPI', () => {
    const mockSettings = {
      baseUrl: 'http://localhost:8888',
      token: 'test-token'
    };

    beforeEach(() => {
      mockServerConnection.makeSettings.mockReturnValue(mockSettings as any);
      mockURLExt.join.mockReturnValue(
        'http://localhost:8888/@amzn/sagemaker_gen_ai_jupyterlab_extension/test'
      );
    });

    it('should make successful API request with default parameters', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"data": "test"}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const result = await requestAPI();

      expect(mockServerConnection.makeSettings).toHaveBeenCalled();
      expect(mockURLExt.join).toHaveBeenCalledWith(
        'http://localhost:8888',
        '@amzn',
        'sagemaker_gen_ai_jupyterlab_extension',
        ''
      );
      expect(mockServerConnection.makeRequest).toHaveBeenCalledWith(
        'http://localhost:8888/@amzn/sagemaker_gen_ai_jupyterlab_extension/test',
        {},
        mockSettings
      );
      expect(result).toEqual({ data: 'test' });
    });

    it('should make API request with custom endpoint', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"result": "success"}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);
      mockURLExt.join.mockReturnValue(
        'http://localhost:8888/@amzn/sagemaker_gen_ai_jupyterlab_extension/custom'
      );

      const result = await requestAPI('custom');

      expect(mockURLExt.join).toHaveBeenCalledWith(
        'http://localhost:8888',
        '@amzn',
        'sagemaker_gen_ai_jupyterlab_extension',
        'custom'
      );
      expect(result).toEqual({ result: 'success' });
    });

    it('should make API request with custom init parameters', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"status": "ok"}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const customInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: 'data' })
      };

      const result = await requestAPI('endpoint', customInit);

      expect(mockServerConnection.makeRequest).toHaveBeenCalledWith(
        'http://localhost:8888/@amzn/sagemaker_gen_ai_jupyterlab_extension/test',
        customInit,
        mockSettings
      );
      expect(result).toEqual({ status: 'ok' });
    });

    it('should handle empty response body', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const result = await requestAPI();

      expect(result).toBe('');
    });

    it('should handle non-JSON response body', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('plain text response')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const consoleSpy = jest.spyOn(console, 'log');
      const result = await requestAPI();

      expect(consoleSpy).toHaveBeenCalledWith(
        'Not a JSON response body.',
        mockResponse
      );
      expect(result).toBe('plain text response');
    });

    it('should construct correct URL with multiple path segments', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"success": true}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);
      mockURLExt.join.mockReturnValue(
        'http://localhost:8888/@amzn/sagemaker_gen_ai_jupyterlab_extension/api/v1/data'
      );

      await requestAPI('api/v1/data');

      expect(mockURLExt.join).toHaveBeenCalledWith(
        'http://localhost:8888',
        '@amzn',
        'sagemaker_gen_ai_jupyterlab_extension',
        'api/v1/data'
      );
    });

    it('should handle different HTTP methods', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"updated": true}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

      for (const method of methods) {
        const init = { method };
        await requestAPI('test', init);

        expect(mockServerConnection.makeRequest).toHaveBeenCalledWith(
          expect.any(String),
          init,
          mockSettings
        );
      }
    });

    it('should preserve custom headers in request', async () => {
      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue('{"authenticated": true}')
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const customHeaders = {
        Authorization: 'Bearer token123',
        'X-Custom-Header': 'custom-value',
        'Content-Type': 'application/json'
      };

      const init = { headers: customHeaders };
      await requestAPI('secure', init);

      expect(mockServerConnection.makeRequest).toHaveBeenCalledWith(
        expect.any(String),
        init,
        mockSettings
      );
    });

    it('should handle response with nested JSON structure', async () => {
      const complexResponse = {
        data: {
          users: [
            { id: 1, name: 'John' },
            { id: 2, name: 'Jane' }
          ],
          meta: {
            total: 2,
            page: 1
          }
        }
      };

      const mockResponse = {
        ok: true,
        text: jest.fn().mockResolvedValue(JSON.stringify(complexResponse))
      };
      mockServerConnection.makeRequest.mockResolvedValue(mockResponse as any);

      const result = await requestAPI<typeof complexResponse>();

      expect(result).toEqual(complexResponse);
      expect(result.data.users).toHaveLength(2);
      expect(result.data.meta.total).toBe(2);
    });
  });
});
