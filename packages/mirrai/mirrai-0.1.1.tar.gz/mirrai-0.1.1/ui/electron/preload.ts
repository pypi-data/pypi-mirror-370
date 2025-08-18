import { contextBridge, ipcRenderer } from "electron";

// Define the API interface
interface ElectronAPI {
    getApiUrl: () => string;
    send: (channel: string, data?: any) => void;
    receive: (channel: string, func: (...args: any[]) => void) => void;
    getEnv: () => {
        isDev: boolean;
        apiKey: string;
    };
}

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld("electronAPI", {
    // API server info
    getApiUrl: () => "http://127.0.0.1:8777",

    // IPC communication (if needed later)
    send: (channel: string, data?: any) => {
        const validChannels = ["restart-api", "show-window", "hide-window"];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },

    receive: (channel: string, func: (...args: any[]) => void) => {
        const validChannels = ["api-status", "execution-update"];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (_event, ...args) => func(...args));
        }
    },

    // Environment
    getEnv: () => ({
        isDev: process.env.NODE_ENV !== "production",
        apiKey: process.env.ANTHROPIC_API_KEY || "",
    }),
} as ElectronAPI);

// Add type declaration for window
declare global {
    interface Window {
        electronAPI: ElectronAPI;
    }
}
