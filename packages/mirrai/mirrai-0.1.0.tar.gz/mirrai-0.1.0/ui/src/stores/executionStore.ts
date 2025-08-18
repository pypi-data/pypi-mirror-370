import { create } from "zustand";

export type MessageRole = "user" | "assistant" | "system";

export interface Message {
    id: string; // Now comes from server
    role: MessageRole;
    content: string;
    timestamp: Date;
}

export interface ToolUse {
    id: string;
    action: string;
    details: any;
    timestamp: Date;
}

export interface ExecutionState {
    // Current execution
    executionId: string | null;
    status: "idle" | "starting" | "running" | "completed" | "error";
    task: string;
    windowSpec: string | null;

    // Progress
    currentIteration: number;
    maxIterations: number;

    // Messages and events
    messages: Message[];
    toolUses: ToolUse[];

    // Error state
    error: string | null;
}

interface ExecutionActions {
    // Start new execution
    startExecution: (task: string, windowSpec?: string) => Promise<string>;

    // Update execution state
    setStatus: (status: ExecutionState["status"]) => void;
    setError: (error: string | null) => void;

    // Add events
    addMessage: (role: MessageRole, content: string, id?: string, timestamp?: Date) => void;
    addToolUse: (action: string, details: any) => void;
    updateIteration: (current: number, max: number) => void;

    // Load initial state
    loadInitialMessages: (messages: Message[]) => void;

    // Clear/reset
    reset: () => void;
}

const initialState: ExecutionState = {
    executionId: null,
    status: "idle",
    task: "",
    windowSpec: null,
    currentIteration: 0,
    maxIterations: 0,
    messages: [],
    toolUses: [],
    error: null,
};

export const useExecutionStore = create<ExecutionState & ExecutionActions>()((set, get) => ({
    ...initialState,

    startExecution: async (task: string, windowSpec?: string) => {
        // Reset state
        set({
            ...initialState,
            status: "starting",
            task,
            windowSpec: windowSpec || null,
        });

        try {
            // Get API URL from Electron
            const apiUrl = window.electronAPI?.getApiUrl() || "http://127.0.0.1:8777";

            // Start execution via API
            const response = await fetch(`${apiUrl}/agent/executions`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify({
                    task,
                    window: windowSpec,
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to start execution: ${response.statusText}`);
            }

            const data = await response.json();
            const executionId = data.execution_id;

            set({
                executionId,
                status: "running",
            });

            return executionId;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "Unknown error";
            set({
                status: "error",
                error: errorMessage,
            });
            throw error;
        }
    },

    setStatus: status => set({ status }),

    setError: error => set({ error, status: "error" }),

    addMessage: (role, content, id?: string, timestamp?: Date) => {
        const message: Message = {
            id: id || Date.now().toString(),
            role,
            content,
            timestamp: timestamp || new Date(),
        };

        set(state => {
            // Check for duplicate by ID to prevent adding the same message twice
            const exists = state.messages.some(m => m.id === message.id);
            if (exists) {
                return state;
            }

            // Add message and sort by timestamp
            const messages = [...state.messages, message].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

            return { messages };
        });
    },

    addToolUse: (action, details) => {
        const toolUse: ToolUse = {
            id: Date.now().toString(),
            action,
            details,
            timestamp: new Date(),
        };
        set(state => ({
            toolUses: [...state.toolUses, toolUse],
        }));
    },

    updateIteration: (current, max) => {
        set({
            currentIteration: current,
            maxIterations: max,
        });
    },

    loadInitialMessages: messages => {
        set(state => {
            // Convert server messages to client format
            const newMessages = messages.map(msg => ({
                ...msg,
                timestamp: new Date(msg.timestamp),
            }));

            // Merge with existing messages, avoiding duplicates by ID
            const existingIds = new Set(state.messages.map(m => m.id));
            const toAdd = newMessages.filter(m => !existingIds.has(m.id));

            if (toAdd.length === 0) {
                return state;
            }

            // Combine and sort by timestamp
            const combined = [...state.messages, ...toAdd].sort(
                (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
            );

            return { messages: combined };
        });
    },

    reset: () => set(initialState),
}));
