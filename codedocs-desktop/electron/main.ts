import { app, BrowserWindow, dialog, ipcMain } from "electron";
import path from "path";
import fs from "fs";
import { runScan } from "./sidecar";
import type { ScanEvent } from "./preload";
import { verifyLicense } from "./license";
import { setupAutoUpdater } from "./updater";

const VITE_DEV_SERVER_URL = process.env.VITE_DEV_SERVER_URL;

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  const preload = path.join(__dirname, "preload.js");

  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: "#0a0a0f",
    webPreferences: {
      preload,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  setupAutoUpdater(mainWindow);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ── IPC: select-folder ──────────────────────────────────────────────
ipcMain.handle("select-folder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
    title: "Select project folder",
  });
  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
});

// ── IPC: start-scan ─────────────────────────────────────────────────
ipcMain.handle("start-scan", async (_event, projectPath: string, options: Record<string, string>) => {
  await runScan(projectPath, options, (scanEvent: ScanEvent) => {
    mainWindow?.webContents.send("scan-event", scanEvent);
  });
});

// ── IPC: export-pdf ─────────────────────────────────────────────────
ipcMain.handle("export-pdf", async (_event, html: string, defaultName: string) => {
  const saveResult = await dialog.showSaveDialog({
    defaultPath: defaultName,
    filters: [{ name: "PDF", extensions: ["pdf"] }],
  });

  if (saveResult.canceled || !saveResult.filePath) {
    return null;
  }

  const pdfWindow = new BrowserWindow({
    show: false,
    width: 1024,
    height: 768,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  try {
    await pdfWindow.loadURL(
      `data:text/html;charset=utf-8,${encodeURIComponent(html)}`
    );
    const pdfData = await pdfWindow.webContents.printToPDF({
      printBackground: true,
      pageSize: "A4",
    });
    fs.writeFileSync(saveResult.filePath, pdfData);
    return saveResult.filePath;
  } finally {
    pdfWindow.close();
  }
});

// ── IPC: verify-license ─────────────────────────────────────────────
ipcMain.handle("verify-license", (_event, key: string) => {
  return verifyLicense(key);
});

// ── IPC: save-file (write to folder) ────────────────────────────────
ipcMain.handle("save-file", async (_event, folder: string, filename: string, content: string) => {
  const filepath = path.join(folder, filename);
  await fs.promises.mkdir(path.dirname(filepath), { recursive: true });
  await fs.promises.writeFile(filepath, content, "utf-8");
});

// ── IPC: save-text-file (save dialog) ───────────────────────────────
ipcMain.handle("save-text-file", async (_event, content: string, defaultName: string) => {
  if (!mainWindow) return null;
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [{ name: "Markdown", extensions: ["md"] }],
  });
  if (canceled || !filePath) return null;
  await fs.promises.writeFile(filePath, content, "utf-8");
  return filePath;
});

// ── App lifecycle ───────────────────────────────────────────────────
app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
