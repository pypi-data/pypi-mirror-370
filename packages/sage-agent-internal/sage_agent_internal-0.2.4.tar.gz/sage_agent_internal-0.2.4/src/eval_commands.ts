import { JupyterFrontEnd } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { AppStateService } from './AppState';
import { NotebookActions } from '@jupyterlab/notebook';
import { ChatHistoryManager } from './Chat/ChatHistoryManager';
import { timeout } from './utils';

/**
 * Register all commands for the sage-ai extension
 */
export function registerEvalCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  // Register test add with diff command
  registerRunEvals(app, palette);
}

/**
 * Register the test add with diff command
 */
function registerRunEvals(
  app: JupyterFrontEnd,
  palette: ICommandPalette
): void {
  const runEvalCommand: string = 'sage-ai:run_eval';

  app.commands.addCommand(runEvalCommand, {
    label: 'Run Eval',
    execute: async () => {
      const notebookTools = AppStateService.getNotebookTools();
      const diffManager = AppStateService.getNotebookDiffManager();
      const notebooks = AppStateService.getNotebookTracker();

      const { commands, shell } = app;
      const current = shell.currentWidget;
      const notebookPath = 'evals.ipynb';
      console.log(
        'CURRENT NOTEBOOK ID:',
        AppStateService.getNotebookTracker().currentWidget?.sessionContext.path
      );
      // Switch to the right notebook
      if (
        current &&
        AppStateService.getNotebookTracker().currentWidget?.sessionContext
          .path !== notebookPath
      ) {
        // Open new notebook as a tab in place of the current widget
        commands
          .execute('docmanager:open', {
            path: notebookPath,
            // Optionally specify the factory: e.g., factory: 'Notebook'
            options: { mode: 'tab-after', ref: current.id, activate: true }
          })
          .then(() => {
            // Close the old widget to replace it
            current.close();
          });
      } else {
        // Fallback: if no current widget, just open normally
        await commands.execute('docmanager:open', { path: notebookPath });
      }

      await timeout(500); // Wait for the notebook to open

      // Get the unique_id from the opened notebook metadata
      const currentNotebook = notebooks.currentWidget;
      let notebookUniqueId: string | null = null;

      if (currentNotebook) {
        try {
          const contentManager = AppStateService.getContentManager();
          const nbFile = await contentManager?.get(
            currentNotebook.context.path
          );
          if (nbFile?.content?.metadata?.sage_ai?.unique_id) {
            notebookUniqueId = nbFile.content.metadata.sage_ai.unique_id;
          }
        } catch (error) {
          console.warn(
            'Could not get notebook metadata for eval notebook:',
            error
          );
        }
      }

      AppStateService.setCurrentNotebookId(notebookUniqueId || notebookPath);

      const notebook = notebooks.currentWidget?.content;
      if (notebook)
        await NotebookActions.runAll(
          notebook,
          notebooks.currentWidget?.sessionContext
        );

      const chatWidget = AppStateService.getChatContainerSafe()?.chatWidget;
      if (!chatWidget) {
        console.error('Chat widget not found');
        return;
      }

      const contentManager = AppStateService.getContentManager();
      const prompt = await contentManager.get('eval_prompt.txt');

      if (!prompt || !prompt.content) {
        console.error('Prompt content not found');
        return;
      }

      await chatWidget.threadManager.createNewThread();
      await timeout(200);

      chatWidget.conversationService.setAutoRun(true);
      chatWidget.inputManager.setInputValue(prompt.content);
      await chatWidget.inputManager.sendMessage();

      const chatHistory = chatWidget.chatHistoryManager.getCurrentThread();

      if (!chatHistory) {
        console.error('Chat history not found');
        return;
      }

      const cleanedMessages =
        ChatHistoryManager.getCleanMessageArrayWithTimestamps(chatHistory);

      notebooks.currentWidget?.sessionContext.restartKernel();

      // Create json file and save messages
      const filename = 'eval_output.json';
      await contentManager.save(filename, {
        type: 'file',
        format: 'text',
        content: JSON.stringify(cleanedMessages, null, 2)
      });

      console.log('Cleaned Messages:', cleanedMessages);

      return cleanedMessages;
    }
  });

  palette.addItem({ command: runEvalCommand, category: 'AI Tools' });
}
