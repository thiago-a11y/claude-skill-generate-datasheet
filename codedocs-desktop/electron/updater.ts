import { app, BrowserWindow } from "electron";

export function setupAutoUpdater(mainWindow: BrowserWindow) {
  if (!app.isPackaged) return;

  try {
    const { autoUpdater } = require("electron-updater");

    autoUpdater.autoDownload = true;
    autoUpdater.autoInstallOnAppQuit = true;

    autoUpdater.on("update-available", (info: any) => {
      mainWindow.webContents.send("update-status", {
        type: "available",
        version: info.version,
      });
    });

    autoUpdater.on("download-progress", (progress: any) => {
      mainWindow.webContents.send("update-status", {
        type: "downloading",
        percent: Math.round(progress.percent),
      });
    });

    autoUpdater.on("update-downloaded", () => {
      mainWindow.webContents.send("update-status", { type: "ready" });
    });

    autoUpdater.on("error", (err: Error) => {
      console.error("[updater]", err.message);
    });

    autoUpdater.checkForUpdatesAndNotify();
  } catch {
    console.log("[updater] electron-updater not available — skipping auto-update");
  }
}
