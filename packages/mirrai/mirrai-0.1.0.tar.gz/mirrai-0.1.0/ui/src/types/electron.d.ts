interface ElectronAPI {
    getApiUrl: () => string;
    send: (channel: string, data?: any) => void;
    receive: (channel: string, func: (...args: any[]) => void) => void;
    getEnv: () => {
        isDev: boolean;
        apiKey: string;
    };
}

declare global {
    interface Window {
        electronAPI?: ElectronAPI;
    }
}

export {};
