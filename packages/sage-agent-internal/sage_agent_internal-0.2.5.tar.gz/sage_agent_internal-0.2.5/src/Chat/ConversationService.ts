import { ChatMessages } from './ChatMessages';
import { ToolService } from '../Services/ToolService';
import { IChatService } from '../Services/IChatService';
import { ChatRequestStatus } from '../types';
import { NotebookStateService } from '../Notebook/NotebookStateService';
import { CodeConfirmationDialog } from '../Components/CodeConfirmationDialog';
import { RejectionFeedbackDialog } from '../Components/RejectionFeedbackDialog';
import {
  ActionHistory,
  ActionType,
  IActionHistoryEntry
} from './ActionHistory';
import { NotebookDiffManager } from '../Notebook/NotebookDiffManager';
import { Contents } from '@jupyterlab/services';
import { AppStateService } from '../AppState';
import {
  ConversationContext,
  ConversationServiceUtils,
  StreamingState
} from './ConversationServiceUtils';
import { DiffStateService } from '../Services/DiffStateService';
import { STATE_DB_KEYS, StateDBCachingService } from '../utils/stateDBCaching';

export interface LoadingIndicatorManager {
  updateLoadingIndicator(text?: string): void;
  removeLoadingIndicator(): void;
}

/**
 * Service responsible for processing conversations with AI
 */
export class ConversationService {
  public chatService: IChatService;
  private toolService: ToolService;
  private messageComponent: ChatMessages;
  private notebookStateService: NotebookStateService;
  private codeConfirmationDialog: CodeConfirmationDialog;
  private loadingManager: LoadingIndicatorManager;
  private chatHistory: HTMLDivElement;
  private actionHistory: ActionHistory;
  private diffManager: NotebookDiffManager | null = null;
  private isActiveToolExecution: boolean = false; // Track if we're in a tool execution phase
  private autoRun: boolean = false; // New flag to control automatic code execution
  private notebookId: string | null = null;
  private streamingElement: HTMLDivElement | null = null; // Element for streaming text
  private contentManager: Contents.IManager;

  // Update the property to handle multiple templates
  private templates: Array<{ name: string; content: string }> = [];

  constructor(
    chatService: IChatService,
    toolService: ToolService,
    contentManager: Contents.IManager,
    messageComponent: ChatMessages,
    chatHistory: HTMLDivElement,
    loadingManager: LoadingIndicatorManager,
    diffManager?: NotebookDiffManager
  ) {
    this.chatService = chatService;
    this.toolService = toolService;
    this.messageComponent = messageComponent;
    this.chatHistory = chatHistory;
    this.loadingManager = loadingManager;
    this.actionHistory = new ActionHistory();
    this.diffManager = diffManager || null;
    this.contentManager = contentManager;

    // Initialize dependent services
    this.notebookStateService = new NotebookStateService(toolService);
    this.codeConfirmationDialog = new CodeConfirmationDialog(
      chatHistory,
      messageComponent
    );

    // Ensure chat service has the full conversation history
    this.syncChatServiceHistory();
  }

  public updateNotebookId(newId: string): void {
    this.notebookId = newId;
    this.notebookStateService.updateNotebookId(newId);
  }

  /**
   * Sync the chat service's history with the message component's history
   * This ensures the LLM has full context of the conversation
   */
  private syncChatServiceHistory(): void {
    // Reset chat service history
    this.chatService.resetConversationHistory();

    // Get current message history from the message component
    const messageHistory = this.messageComponent.getMessageHistory();

    // Add each message to the chat service history
    for (const message of messageHistory) {
      if (message.role === 'assistant') {
        this.chatService.addToolResult(
          { role: 'assistant', content: message.content },
          null
        );
      } else if (message.role === 'user') {
        this.chatService.addToolResult(null, message.content);
      }
    }

    if (messageHistory.length > 0) {
      this.messageComponent.scrollToBottom();
    }

    console.log(
      `Synchronized ${messageHistory.length} messages to chat service history`
    );
  }

  /**
   * Set the autorun flag
   * @param enabled Whether to automatically run code without confirmation
   */
  public setAutoRun(enabled: boolean): void {
    this.autoRun = enabled;
    console.log(`Auto-run mode ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Set the diff manager instance
   */
  public setDiffManager(diffManager: NotebookDiffManager): void {
    this.diffManager = diffManager;
    console.log('NotebookDiffManager set in ConversationService');
  }

  /**
   * Set the current notebook ID
   * @param notebookId ID of the notebook to interact with
   */
  public setNotebookId(notebookId: string): void {
    this.notebookId = notebookId;
    console.log(`[ConversationService] Set notebook ID: ${notebookId}`);
  }

  /**
   * Handles the case when a cell execution is rejected
   */
  public async handleCellRejection(
    mode: 'agent' | 'ask' | 'fast' = 'agent'
  ): Promise<void> {
    this.messageComponent.addSystemMessage(
      'Cell execution rejected. Asking for corrections based on user feedback...'
    );

    const rejectionDialog = new RejectionFeedbackDialog();
    const rejectionReason = await rejectionDialog.showDialog();

    // Add the special user feedback message
    const rejectionMessage = {
      role: 'user',
      content: `I rejected the previous cell execution because: ${rejectionReason}`
    };

    // Add the feedback to the visible message history
    this.messageComponent.addUserMessage(
      `I rejected the previous cell execution because: ${rejectionReason}`
    );

    // Process conversation with just the new rejection message
    await this.processConversation([rejectionMessage], [], mode);
  }

  /**
   * Process a tool call ensuring the notebook ID is passed through
   */
  private async processToolCall(toolCall: any): Promise<any> {
    return await ConversationServiceUtils.processToolCall(
      {
        chatService: this.chatService,
        toolService: this.toolService,
        messageComponent: this.messageComponent,
        notebookStateService: this.notebookStateService,
        codeConfirmationDialog: this.codeConfirmationDialog,
        loadingManager: this.loadingManager,
        diffManager: this.diffManager,
        actionHistory: this.actionHistory,
        autoRun: this.autoRun,
        notebookId: this.notebookId,
        templates: this.templates,
        isActiveToolExecution: this.isActiveToolExecution,
        chatHistory: this.chatHistory
      },
      toolCall
    );
  }

  /**
   * Execute all approved cells from the diff manager
   * @param contentId The content ID for tracking tool results
   * @returns Promise resolving to true if cells were executed, false if none to execute
   */
  public async executeAllApprovedCells(contentId: string): Promise<boolean> {
    return await ConversationServiceUtils.checkExecutedCells(
      {
        chatService: this.chatService,
        toolService: this.toolService,
        messageComponent: this.messageComponent,
        notebookStateService: this.notebookStateService,
        codeConfirmationDialog: this.codeConfirmationDialog,
        loadingManager: this.loadingManager,
        diffManager: this.diffManager,
        actionHistory: this.actionHistory,
        autoRun: this.autoRun,
        notebookId: this.notebookId,
        templates: this.templates,
        isActiveToolExecution: this.isActiveToolExecution,
        chatHistory: this.chatHistory
      },
      contentId
    );
  }

  public async createErrorMessage(message: any) {
    console.log('Creating error message dump...');
    console.log(message);
    try {
      // Get existing error logs from stateDB
      const existingLogs = await StateDBCachingService.getValue(
        STATE_DB_KEYS.ERROR_LOGS,
        ''
      );

      // Create new log entry
      const newLogEntry = `\n\n---\n\n${new Date().toISOString()}\n\n${JSON.stringify(message)}`;
      let updatedLogs = existingLogs + newLogEntry;

      // Trim logs to stay within 100,000 words limit
      const words = updatedLogs.split(/\s+/);
      if (words.length > 100000) {
        // Keep only the most recent 90,000 words to leave room for future entries
        const trimmedWords = words.slice(-90000);
        updatedLogs = trimmedWords.join(' ');

        // Add a marker to indicate logs were trimmed
        updatedLogs =
          '[...logs trimmed to maintain 100,000 word limit...]\n\n' +
          updatedLogs;
      }

      // Save back to stateDB
      await StateDBCachingService.setValue(
        STATE_DB_KEYS.ERROR_LOGS,
        updatedLogs
      );
    } catch (err) {
      console.error('Failed to save error log to stateDB:', err);
    }
  }

  /**
   * Process the conversation with the AI service
   */
  public async processConversation(
    newMessages: any[],
    systemPromptMessages: string[] = [],
    mode: 'agent' | 'ask' | 'fast' = 'agent'
  ): Promise<void> {
    // Create context object for utility functions
    const context: ConversationContext = {
      chatService: this.chatService,
      toolService: this.toolService,
      messageComponent: this.messageComponent,
      notebookStateService: this.notebookStateService,
      codeConfirmationDialog: this.codeConfirmationDialog,
      loadingManager: this.loadingManager,
      diffManager: this.diffManager,
      actionHistory: this.actionHistory,
      autoRun: this.autoRun,
      notebookId: this.notebookId,
      templates: this.templates,
      isActiveToolExecution: this.isActiveToolExecution,
      chatHistory: this.chatHistory
    };

    // Initialize streaming state
    const streamingState: StreamingState = {
      currentStreamingMessage: null,
      currentStreamingToolCall: null,
      streamingToolCall: undefined,
      operationQueue: {}
    };

    try {
      // Step 1: Initialize conversation processing
      const { preparedMessages, tools } =
        await ConversationServiceUtils.initializeConversation(
          context,
          newMessages,
          systemPromptMessages,
          mode
        );

      // Step 2: Send message to AI service with streaming handlers
      const response = await ConversationServiceUtils.sendMessageWithStreaming(
        context,
        preparedMessages,
        tools,
        mode,
        systemPromptMessages,
        streamingState,
        this.createErrorMessage.bind(this)
      );

      // Check for cancellation after response
      if (response?.cancelled || this.chatService.isRequestCancelled()) {
        console.log('Response processing skipped due to cancellation');
        ConversationServiceUtils.cleanupStreamingElements(
          context,
          streamingState
        );
        this.loadingManager.removeLoadingIndicator();
        return;
      }

      // Check for cell rejection signal
      if (response.needsFreshContext === true) {
        this.loadingManager.removeLoadingIndicator();
        await this.handleCellRejection(mode);
        return;
      }

      // Step 4: Handle response and finalize streaming elements
      await ConversationServiceUtils.finalizeStreamingElements(
        context,
        response,
        streamingState
      );

      // Check for cancellation before processing tool calls
      if (this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED) {
        console.log('Request was cancelled, skipping tool call processing');
        this.loadingManager.removeLoadingIndicator();
        return;
      }

      // Step 5: Add usage information if in token mode
      ConversationServiceUtils.addUsageInformation(context, response);

      // Step 6: Process tool calls from the response
      const { hasToolCalls, shouldContinue } =
        await ConversationServiceUtils.processToolCalls(
          context,
          response,
          streamingState,
          systemPromptMessages,
          mode
        );

      if (!shouldContinue) {
        return;
      }

      // Handle recursive call for continuing conversation after tool use
      if (hasToolCalls) {
        // Check if user has made approval decisions that should stop the LLM loop
        const hasApprovalDecisions =
          ConversationServiceUtils.checkForApprovalDecisions(context);

        if (hasApprovalDecisions) {
          console.log(
            '[ConversationService] Approval decisions detected - stopping recursive LLM loop'
          );
          return; // Stop the recursive loop
        }

        // Check if any tool call needs further processing
        let needsRecursiveCall = false;
        for (const content of response.content || []) {
          if (
            content.type === 'tool_use' &&
            content.name !== 'notebook-wait_user_reply'
          ) {
            if (content.name === 'notebook-run_cell')
              DiffStateService.getInstance().clearAllDiffs(this.notebookId);
            needsRecursiveCall = true;
            break;
          }
        }

        if (needsRecursiveCall) {
          const llmStateDisplay =
            AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
          llmStateDisplay?.hidePendingDiffs();
          llmStateDisplay?.show('Generating...');
          await this.processConversation([], systemPromptMessages, mode);
        }
      }

      // Step 7: Handle pending diffs if no tool calls were made
      await ConversationServiceUtils.handlePendingDiffsAfterToolCalls(context);

      // Update instance state from context
      this.isActiveToolExecution = context.isActiveToolExecution;
    } catch (error) {
      // If cancelled, just return without showing an error
      if (this.chatService.isRequestCancelled()) {
        console.log('Request was cancelled, skipping error handling');
        ConversationServiceUtils.cleanupStreamingElements(
          context,
          streamingState
        );
        this.loadingManager.removeLoadingIndicator();
        return;
      }

      this.loadingManager.removeLoadingIndicator();
      throw error;
    }

    // Remove loading indicator at the end of processing
    this.loadingManager.removeLoadingIndicator();
  }

  /**
   * Check if there are any actions that can be undone
   * @returns True if there are actions in the history
   */
  public canUndo(): boolean {
    return this.actionHistory.canUndo();
  }

  /**
   * Get the description of the last action
   * @returns Description of the last action or null if none
   */
  public getLastActionDescription(): string | null {
    return this.actionHistory.getLastActionDescription();
  }

  /**
   * Undo the last action
   * @returns True if an action was undone, false if no actions to undo
   */
  public async undoLastAction(): Promise<boolean> {
    const action = this.actionHistory.popLastAction();
    if (!action) {
      return false;
    }

    try {
      this.loadingManager.updateLoadingIndicator('Undoing action...');

      switch (action.type) {
        case ActionType.ADD_CELL:
          await this.undoAddCell(action);
          break;

        case ActionType.EDIT_CELL:
          await this.undoEditCell(action);
          break;

        case ActionType.REMOVE_CELLS:
          await this.undoRemoveCells(action);
          break;
      }

      // Add a system message to indicate the action was undone
      this.messageComponent.addSystemMessage(
        `✓ Undid action: ${action.description}`
      );
      this.loadingManager.removeLoadingIndicator();
      return true;
    } catch (error) {
      console.error('Error undoing action:', error);
      this.messageComponent.addErrorMessage(
        `Failed to undo action: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      this.loadingManager.removeLoadingIndicator();
      return false;
    }
  }

  /**
   * Undo adding a cell
   */
  private async undoAddCell(action: IActionHistoryEntry): Promise<void> {
    // Use trackingId if available, fallback to cellId for backward compatibility
    const trackingId = action.data.trackingId || action.data.cellId;

    // Remove the added cell using tracking ID
    await this.toolService.executeTool({
      id: 'undo_add_cell',
      name: 'notebook-remove_cells',
      input: {
        cell_ids: [trackingId],
        remove_from_notebook: true
      }
    });
  }

  /**
   * Undo editing a cell
   */
  private async undoEditCell(action: IActionHistoryEntry): Promise<void> {
    // Use trackingId if available, fallback to cellId for backward compatibility
    const trackingId = action.data.trackingId || action.data.cellId;

    // Restore the original cell content using tracking ID
    await this.toolService.executeTool({
      id: 'undo_edit_cell',
      name: 'notebook-edit_cell',
      input: {
        cell_id: trackingId,
        new_source: action.data.originalContent,
        summary: action.data.originalSummary || 'Restored by undo',
        is_tracking_id: true
      }
    });
  }

  /**
   * Undo removing cells
   */
  private async undoRemoveCells(action: IActionHistoryEntry): Promise<void> {
    // Re-add each removed cell
    if (action.data.removedCells) {
      for (let i = 0; i < action.data.removedCells.length; i++) {
        const cell = action.data.removedCells[i];
        // Generate a tracking ID if none was saved
        const trackingId = cell.trackingId || `restored-${Date.now()}-${i}`;

        await this.toolService.executeTool({
          id: 'undo_remove_cell',
          name: 'notebook-add_cell',
          input: {
            cell_type: cell.type,
            source: cell.content,
            summary: cell.custom?.summary || 'Restored by undo',
            position: cell.custom?.index, // Use index from custom metadata if available
            tracking_id: trackingId // Provide tracking ID to reuse
          }
        });
      }
    }
  }

  /**
   * Clear the action history
   */
  public clearActionHistory(): void {
    this.actionHistory.clear();
  }
}
