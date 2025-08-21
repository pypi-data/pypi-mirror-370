import { registerContextMenuActions, GenericCommandVerb } from '../contextMenu';
import { postToWebView } from '../webview';

jest.mock('../webview', () => ({
  postToWebView: jest.fn()
}));

describe('contextMenu', () => {
  let mockApp: any;
  let mockNotebookTracker: any;
  let mockShowFlareWidget: jest.Mock;
  let mockActiveCell: any;
  let mockEditor: any;
  let mockOutputs: any;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'log').mockImplementation();

    mockShowFlareWidget = jest.fn();

    mockOutputs = {
      length: 0,
      get: jest.fn()
    };

    mockEditor = {
      getSelection: jest.fn(() => ({
        start: { line: 0, column: 0 },
        end: { line: 0, column: 0 }
      })),
      model: {
        sharedModel: {
          getSource: jest.fn(() => 'test code')
        }
      },
      getOffsetAt: jest.fn(() => 0)
    };

    mockActiveCell = {
      model: {
        type: 'code',
        sharedModel: {
          getSource: jest.fn(() => 'test code')
        },
        outputs: mockOutputs
      },
      editor: mockEditor
    };

    mockNotebookTracker = {
      currentWidget: {
        content: {
          activeCell: mockActiveCell
        }
      }
    };

    mockApp = {
      commands: {
        addCommand: jest.fn()
      },
      contextMenu: {
        addItem: jest.fn()
      }
    };
  });

  it('should register commands for all verbs', () => {
    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    const verbs: GenericCommandVerb[] = [
      'Explain',
      'Refactor',
      'Fix',
      'Optimize'
    ];
    expect(mockApp.commands.addCommand).toHaveBeenCalledTimes(verbs.length);

    verbs.forEach(verb => {
      expect(mockApp.commands.addCommand).toHaveBeenCalledWith(
        `sagemaker-gen-ai:${verb.toLowerCase()}`,
        expect.objectContaining({
          label: verb,
          isEnabled: expect.any(Function),
          execute: expect.any(Function)
        })
      );
    });
  });

  it('should add context menu items for code cells and file editors', () => {
    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    expect(mockApp.contextMenu.addItem).toHaveBeenCalledTimes(1);
    expect(mockApp.contextMenu.addItem).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'submenu',
        selector: '.jp-CodeCell',
        rank: 0
      })
    );
  });

  describe('command execution', () => {
    beforeEach(() => {
      registerContextMenuActions({
        app: mockApp,
        notebookTracker: mockNotebookTracker,
        showFlareWidget: mockShowFlareWidget
      });
    });

    it('should execute explain command with cell content', () => {
      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      explainCommand.execute();

      expect(mockShowFlareWidget).toHaveBeenCalled();
      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Explain',
          selection: 'test code',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should execute command with selected text when available', () => {
      mockEditor.getSelection.mockReturnValue({
        start: { line: 0, column: 0 },
        end: { line: 0, column: 5 }
      });
      mockEditor.model.sharedModel.getSource.mockReturnValue('selected text');
      mockEditor.getOffsetAt.mockReturnValueOnce(0).mockReturnValueOnce(8);

      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      explainCommand.execute();

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Explain',
          selection: 'selected',
          triggerType: 'contextMenu'
        }
      });
    });

    it('should handle fix command with error output', () => {
      mockOutputs.length = 1;
      mockOutputs.get.mockReturnValue({
        type: 'error',
        _raw: {
          ename: 'ValueError',
          evalue: 'invalid value',
          traceback: ['line 1', 'line 2']
        }
      });

      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      fixCommand.execute();

      expect(postToWebView).toHaveBeenCalledWith({
        command: 'genericCommand',
        params: {
          genericCommand: 'Fix',
          selection:
            'Code:\ntest code\n\nError:\nErrorType: ValueError; ErrorValue: invalid value; Trace: line 1,line 2',
          triggerType: 'contextMenu'
        }
      });
    });
  });

  describe('isEnabled conditions', () => {
    beforeEach(() => {
      registerContextMenuActions({
        app: mockApp,
        notebookTracker: mockNotebookTracker,
        showFlareWidget: mockShowFlareWidget
      });
    });

    it('should enable fix command only when error exists', () => {
      const fixCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:fix'
      )[1];

      // No error
      expect(fixCommand.isEnabled()).toBe(false);

      // With error
      mockOutputs.length = 1;
      mockOutputs.get.mockReturnValue({ type: 'error' });
      expect(fixCommand.isEnabled()).toBe(true);
    });

    it('should always enable non-fix commands', () => {
      const explainCommand = mockApp.commands.addCommand.mock.calls.find(
        (call: any) => call[0] === 'sagemaker-gen-ai:explain'
      )[1];

      expect(explainCommand.isEnabled()).toBe(true);
    });
  });

  it('should handle missing notebook widget', () => {
    mockNotebookTracker.currentWidget = null;

    registerContextMenuActions({
      app: mockApp,
      notebookTracker: mockNotebookTracker,
      showFlareWidget: mockShowFlareWidget
    });

    const explainCommand = mockApp.commands.addCommand.mock.calls.find(
      (call: any) => call[0] === 'sagemaker-gen-ai:explain'
    )[1];

    explainCommand.execute();

    expect(postToWebView).not.toHaveBeenCalled();
    expect(mockShowFlareWidget).not.toHaveBeenCalled();
  });
});
