import { app, BrowserWindow, Tray, Menu, nativeImage } from "electron";
import * as path from "path";
import { startApiServer, stopApiServer } from "./apiServer";

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
// Keep reference to API server for restart functionality
// @ts-ignore - Used in tray menu restart handler
let apiServer: any = null;

const isDev = process.env.NODE_ENV !== "production";

function createWindow(): void {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: true, // Show window on startup
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false,
        },
        icon: path.join(__dirname, "../public/icon.png"),
    });

    // Load the app
    if (isDev) {
        mainWindow.loadURL("http://localhost:5173");
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
    }

    // Handle window closed
    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}

function createTray(): void {
    // Create a tray icon
    const iconPath = path.join(__dirname, "../public/tray-icon.png");
    const trayIcon = nativeImage.createFromPath(iconPath);
    tray = new Tray(trayIcon.resize({ width: 16, height: 16 }));

    const contextMenu = Menu.buildFromTemplate([
        {
            label: "Show App",
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                } else {
                    createWindow();
                }
            },
        },
        {
            type: "separator",
        },
        {
            label: "Restart API Server",
            click: async () => {
                await stopApiServer();
                apiServer = await startApiServer();
            },
        },
        {
            type: "separator",
        },
        {
            label: "Quit",
            click: () => {
                app.quit();
            },
        },
    ]);

    tray.setToolTip("Mirrai");
    tray.setContextMenu(contextMenu);

    // Show window on double click
    tray.on("double-click", () => {
        if (mainWindow) {
            mainWindow.show();
        } else {
            createWindow();
        }
    });
}

app.whenReady().then(async () => {
    // Start the API server
    try {
        apiServer = await startApiServer();
        console.log("API server started successfully");
    } catch (error) {
        console.error("Failed to start API server:", error);
    }

    createWindow();
    createTray();
});

app.on("window-all-closed", () => {
    // Quit app when all windows are closed (including on macOS)
    app.quit();
});

app.on("activate", () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on("before-quit", async event => {
    // Prevent default quit while we clean up
    event.preventDefault();

    console.log("Cleaning up before quit...");

    // Clean up API server
    try {
        await stopApiServer();
    } catch (error) {
        console.error("Error stopping API server:", error);
    }

    // Now actually quit
    console.log("Cleanup complete, exiting...");
    app.exit(0);
});

// Handle uncaught exceptions
process.on("uncaughtException", error => {
    console.error("Uncaught Exception:", error);
});

process.on("unhandledRejection", error => {
    console.error("Unhandled Rejection:", error);
});
