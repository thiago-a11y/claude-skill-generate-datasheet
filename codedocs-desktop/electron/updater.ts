import { autoUpdater } from "electron-updater";
import { app, BrowserWindow } from "electron";

export function setupAutoUpdater(mainWindow: BrowserWindow) {
  // Only run in packaged builds
  if (!app.isPackaged) return;

  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on("update-available", (info) => {
    mainWindow.webContents.send("update-status", {
      type: "available",
      version: info.version,
    });
  });

  autoUpdater.on("download-progress", (progress) => {
    mainWindow.webContents.send("update-status", {
      type: "downloading",
      percent: Math.round(progress.percent),
    });
  });

  autoUpdater.on("update-downloaded", () => {
    mainWindow.webContents.send("update-status", { type: "ready" });
  });

  autoUpdater.on("error", (err) => {
    console.error("[updater]", err.message);
  });

  autoUpdater.checkForUpdatesAndNotify();
}
