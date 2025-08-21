import { INotebookTracker } from '@jupyterlab/notebook';
import type { ILabShell } from '@jupyterlab/application';
import type { IDocumentManager } from '@jupyterlab/docmanager';
import { FileContext } from './types';

export type GenericCommandVerb = 'Explain' | 'Refactor' | 'Fix' | 'Optimize';

const CELL_MODEL_TYPE = {
  CODE: 'code'
} as const;

const getActiveNotebookCell = (notebookTracker: INotebookTracker) => {
  const notebook = notebookTracker.currentWidget;
  return notebook ? notebook.content.activeCell : undefined;
};

export const insertToCursorPosition = (
  notebookTracker: INotebookTracker,
  code: string
) => {
  const activeCell = getActiveNotebookCell(notebookTracker);
  if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
    const editor = activeCell.editor;
    if (editor) {
      try {
        // Get the current cursor position
        const position = editor.getCursorPosition();

        // Get the current content
        const currentContent = editor.model.sharedModel.source;

        // Split the content at the cursor position
        const beforeCursor = currentContent.substring(
          0,
          editor.getOffsetAt(position)
        );
        const afterCursor = currentContent.substring(
          editor.getOffsetAt(position)
        );

        // Insert the new code at the cursor position
        const newContent = beforeCursor + code + afterCursor;

        // Update the editor content
        editor.model.sharedModel.source = newContent;

        // Move the cursor to the end of the inserted code
        const newPosition = editor.getPositionAt(
          beforeCursor.length + code.length
        );
        if (newPosition) {
          editor.setCursorPosition(newPosition);
        }
      } catch (error) {
        console.error('Error inserting the code:', error);
      }
    }
  }
};

// Helper function to get error message text
export const getErrorMessage = (notebookTracker: INotebookTracker): string => {
  const activeCell = getActiveNotebookCell(notebookTracker);
  if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
    const outputs = (activeCell.model as any).outputs;
    if (outputs) {
      for (let i = 0; i < outputs.length; i++) {
        const output = outputs.get(i);
        if (output.type === 'error') {
          return `ErrorType: ${output._raw.ename}; ErrorValue: ${output._raw.evalue}; Trace: ${output._raw.traceback?.toString()}`;
        }
      }
    }
  }
  return '';
};

// Helper function to check for errors in cell output
export const hasError = (notebookTracker: INotebookTracker): boolean => {
  const activeCell = getActiveNotebookCell(notebookTracker);
  if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
    const outputs = (activeCell.model as any).outputs;
    if (outputs) {
      for (let i = 0; i < outputs.length; i++) {
        const output = outputs.get(i);
        if (output.type === 'error') {
          return true;
        }
      }
    }
  }
  return false;
};

// Helper function to get selection or cell content
export const getSelectionOrCellContent = (
  notebookTracker: INotebookTracker,
  verb?: GenericCommandVerb
): string => {
  // For Fix verb, return error message + cell content
  if (verb === 'Fix' && hasError(notebookTracker)) {
    const notebook = notebookTracker.currentWidget;
    const cellContent =
      notebook?.content.activeCell?.model.type === CELL_MODEL_TYPE.CODE
        ? notebook.content.activeCell.model.sharedModel.getSource()
        : '';
    const errorMessage = getErrorMessage(notebookTracker);
    return `Code:\n${cellContent}\n\nError:\n${errorMessage}`;
  }

  // For other verbs, use normal selection logic
  const activeCell = getActiveNotebookCell(notebookTracker);
  if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
    const editor = activeCell.editor;
    if (editor) {
      const selection = editor.getSelection();
      if (
        selection.start.line !== selection.end.line ||
        selection.start.column !== selection.end.column
      ) {
        const selectedText = editor.model.sharedModel
          .getSource()
          .substring(
            editor.getOffsetAt(selection.start),
            editor.getOffsetAt(selection.end)
          );
        if (selectedText.trim()) {
          return selectedText;
        }
      }
    }
    return activeCell.model.sharedModel.getSource();
  }

  return '';
};

export const getActiveFileContext = ({
  docManager,
  labShell
}: {
  docManager: IDocumentManager;
  labShell: ILabShell;
}): FileContext | undefined => {
  const currentWidget = labShell.currentWidget;
  if (!currentWidget) {
    return undefined;
  }

  const context = docManager.contextForWidget(currentWidget);

  if (!context || !context.path) {
    return undefined;
  }

  return {
    path: context.path
  };
};
