import { storeAcknowledgements } from '../acknowledgements';

describe('acknowledgements.ts', () => {
  beforeEach(() => {
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        setItem: jest.fn(),
        getItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
      },
      writable: true
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('storeAcknowledgements', () => {
    it('should store disclaimerAcknowledged', () => {
      storeAcknowledgements('disclaimerAcknowledged');

      expect(localStorage.setItem).toHaveBeenCalledWith('disclaimerAcknowledged', 'true');
    });

    it('should store chatPromptOptionAcknowledged', () => {
      storeAcknowledgements('chatPromptOptionAcknowledged');

      expect(localStorage.setItem).toHaveBeenCalledWith('chatPromptOptionAcknowledged', 'true');
    });

    it('should handle both acknowledgement types', () => {
      storeAcknowledgements('disclaimerAcknowledged');
      storeAcknowledgements('chatPromptOptionAcknowledged');

      expect(localStorage.setItem).toHaveBeenCalledTimes(2);
      expect(localStorage.setItem).toHaveBeenNthCalledWith(1, 'disclaimerAcknowledged', 'true');
      expect(localStorage.setItem).toHaveBeenNthCalledWith(2, 'chatPromptOptionAcknowledged', 'true');
    });
  });
});