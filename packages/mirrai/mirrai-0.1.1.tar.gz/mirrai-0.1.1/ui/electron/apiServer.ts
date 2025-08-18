import { spawn, ChildProcess, exec } from "child_process";
import * as path from "path";
import * as fs from "fs";
import { app, dialog } from "electron";
import fetch from "node-fetch";
import { promisify } from "util";

const execAsync = promisify(exec);

/**
 * API Server Manager for Mirrai Electron Application
 *
 * Manages the lifecycle of the Python API server subprocess, including:
 * - Starting/stopping the server
 * - Port conflict resolution
 * - Health monitoring
 * - Graceful shutdown
 */
class APIServerManager {
    private process: ChildProcess | null = null;
    private port: number;
    private host: string;
    private healthCheckInterval: NodeJS.Timeout | null = null;

    constructor(port = 8777, host = "127.0.0.1") {
        this.port = port;
        this.host = host;
    }

    /**
     * Get the path to the Mirrai executable
     * In production: uses packaged binary
     * In development: uses Python virtual environment
     */
    private getAPIBinaryPath(): string {
        const isProduction = app.isPackaged;

        if (isProduction) {
            // In production, binaries are in resources/bin
            const binPath = path.join(
                process.resourcesPath,
                "bin",
                process.platform === "win32" ? "mirrai.exe" : "mirrai"
            );
            return binPath;
        } else {
            // In development, use the Python venv
            return this.findDevelopmentExecutable();
        }
    }

    private findDevelopmentExecutable(): string {
        const possiblePaths = [
            path.join(__dirname, "../../.venv/Scripts/mirrai.exe"),
            path.join(__dirname, "../../.venv/bin/mirrai"),
        ];

        for (const execPath of possiblePaths) {
            if (fs.existsSync(execPath)) {
                return execPath;
            }
        }

        return "mirrai"; // Fallback to system PATH
    }

    private async findProcessOnPort(port: number): Promise<{ pid: string; name: string } | null> {
        try {
            if (process.platform === "win32") {
                const { stdout: netstatOutput } = await execAsync(`netstat -ano | findstr :${port}`);
                const lines = netstatOutput.trim().split("\n");

                for (const line of lines) {
                    if (line.includes("LISTENING")) {
                        const parts = line.trim().split(/\s+/);
                        const pid = parts[parts.length - 1];

                        try {
                            const { stdout: tasklistOutput } = await execAsync(`tasklist /FI "PID eq ${pid}" /FO CSV`);
                            const processLines = tasklistOutput.trim().split("\n");
                            if (processLines.length > 1) {
                                const processInfo = processLines[1].split(",");
                                const processName = processInfo[0].replace(/"/g, "");
                                return { pid, name: processName };
                            }
                        } catch {
                            return { pid, name: "Unknown Process" };
                        }
                    }
                }
            } else {
                const { stdout } = await execAsync(`lsof -i :${port} -t`);
                const pid = stdout.trim();
                if (pid) {
                    try {
                        const { stdout: psOutput } = await execAsync(`ps -p ${pid} -o comm=`);
                        const processName = psOutput.trim();
                        return { pid, name: processName };
                    } catch {
                        return { pid, name: "Unknown Process" };
                    }
                }
            }
        } catch (error) {
            // No process found on port
            return null;
        }
        return null;
    }

    private async handlePortConflict(): Promise<boolean> {
        const processInfo = await this.findProcessOnPort(this.port);

        if (processInfo) {
            const result = await dialog.showMessageBox({
                type: "warning",
                title: "Port Conflict",
                message: `Port ${this.port} is already in use`,
                detail: `The process "${processInfo.name}" (PID: ${processInfo.pid}) is currently using port ${this.port}.\n\nYou can either:\n1. Terminate it and start a new Mirrai API server\n2. Use the existing server (useful for debugging)\n3. Cancel`,
                buttons: ["Terminate and Start New", "Use Existing Server", "Cancel"],
                defaultId: 1,
                cancelId: 2,
            });

            if (result.response === 0) {
                // User chose to terminate
                try {
                    if (process.platform === "win32") {
                        await execAsync(`taskkill /PID ${processInfo.pid} /F`);
                    } else {
                        await execAsync(`kill -9 ${processInfo.pid}`);
                    }
                    console.log(`Terminated process ${processInfo.name} (PID: ${processInfo.pid})`);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    return true; // Start new server
                } catch (error) {
                    console.error("Failed to terminate process:", error);
                    throw new Error(`Failed to terminate process ${processInfo.name}`);
                }
            } else if (result.response === 1) {
                // User chose to use existing server
                console.log("Using existing API server on port", this.port);
                return false; // Don't start new server
            } else {
                throw new Error("User cancelled - port is in use");
            }
        }

        return true; // No conflict, start new server
    }

    /**
     * Start the API server
     * Checks for port conflicts and handles them according to user preference
     */
    async start(): Promise<void> {
        if (this.process) {
            console.log("API server already running");
            return;
        }

        // Check for port conflicts
        const shouldStartNew = await this.handlePortConflict();
        if (!shouldStartNew) {
            console.log("Using existing API server, not starting a new one");
            return; // Using existing server
        }

        const binaryPath = this.getAPIBinaryPath();

        return new Promise((resolve, reject) => {
            // Spawn the API server with minimal interference to avoid blocking Python's asyncio
            this.process = spawn(binaryPath, ["api", "serve", "--host", this.host, "--port", this.port.toString()], {
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: "1", // Prevent Python output buffering
                },
                stdio: "ignore", // Critical: Don't interfere with Python's I/O
                detached: true, // Run independently from parent
                shell: process.platform === "win32", // Required on Windows to find executable
                cwd: path.join(__dirname, "../.."), // Run from repo root
            });

            // Unref the process so Node.js doesn't wait for it to exit
            if (this.process.unref) {
                this.process.unref();
            }

            // Handle spawn errors
            this.process.on("error", error => {
                console.error("Failed to start API server:", error);
                this.process = null;
                reject(error);
            });

            // Wait for API to be healthy before resolving
            this.waitForHealthy(resolve, reject);
        });
    }

    /**
     * Poll the health endpoint until the API server is ready
     */
    private async waitForHealthy(resolve: () => void, reject: (error: Error) => void, attempts = 0): Promise<void> {
        const maxAttempts = 30; // 15 seconds timeout

        if (attempts >= maxAttempts) {
            reject(new Error("API server failed to become healthy"));
            return;
        }

        try {
            const response = await fetch(`http://${this.host}:${this.port}/health`);
            if (response.ok) {
                console.log("API server is healthy");
                this.startHealthMonitoring();
                resolve();
            } else {
                setTimeout(() => this.waitForHealthy(resolve, reject, attempts + 1), 500);
            }
        } catch (error) {
            setTimeout(() => this.waitForHealthy(resolve, reject, attempts + 1), 500);
        }
    }

    /**
     * Start continuous health monitoring
     * Automatically restarts the API if it becomes unhealthy
     */
    private startHealthMonitoring(): void {
        this.healthCheckInterval = setInterval(async () => {
            try {
                const response = await fetch(`http://${this.host}:${this.port}/health`, { timeout: 5000 });

                if (!response.ok) {
                    console.error("API server unhealthy, restarting...");
                    await this.restart();
                }
            } catch (error) {
                console.error("API server not responding, restarting...");
                await this.restart();
            }
        }, 30000); // Check every 30 seconds
    }

    /**
     * Stop the API server gracefully
     */
    async stop(): Promise<void> {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        if (!this.process) return;

        return new Promise(resolve => {
            const timeout = setTimeout(() => {
                // Force kill after timeout
                if (this.process) {
                    this.process.kill("SIGKILL");
                }
                resolve();
            }, 5000);

            this.process!.once("exit", () => {
                clearTimeout(timeout);
                this.process = null;
                resolve();
            });

            // Try graceful shutdown first
            if (process.platform === "win32") {
                // Windows doesn't have SIGTERM
                this.process!.kill();
            } else {
                this.process!.kill("SIGTERM");
            }
        });
    }

    async restart(): Promise<void> {
        await this.stop();
        await this.start();
    }

    isRunning(): boolean {
        return this.process !== null;
    }

    getPort(): number {
        return this.port;
    }

    getHost(): string {
        return this.host;
    }
}

// Singleton instance
const apiServerInstance = new APIServerManager();

// Public API for main process
export async function startApiServer(): Promise<ChildProcess | null> {
    await apiServerInstance.start();
    return null; // Class-based approach doesn't expose the process directly
}

export async function stopApiServer(): Promise<void> {
    await apiServerInstance.stop();
}

export async function checkApiHealth(): Promise<boolean> {
    try {
        const response = await fetch(`http://${apiServerInstance.getHost()}:${apiServerInstance.getPort()}/health`, {
            timeout: 2000,
        } as any);
        return response.ok;
    } catch {
        return false;
    }
}

// Constants
export const API_PORT = 8777;
export const API_HOST = "127.0.0.1";

// Ensure cleanup on app quit
app.on("before-quit", async () => {
    await apiServerInstance.stop();
});
