import { contextBridge, ipcRenderer } from "electron";
import type { LicenseResult } from "./license";

export interface ScanOptions {
  lang?: string;
  target?: string;
}

export interface ScanEvent {
  type: "progress" | "result" | "error";
  step?: number;
  total?: number;
  label?: string;
  files?: Record<string, string>;
  message?: string;
}

contextBridge.exposeInMainWorld("codedocs", {
  version: "1.0.0",

  selectFolder: (): Promise<string | null> =>
    ipcRenderer.invoke("select-folder"),

  startScan: (projectPath: string, options?: ScanOptions): Promise<void> =>
    ipcRenderer.invoke("start-scan", projectPath, options ?? {}),

  onScanEvent: (callback: (event: ScanEvent) => void): (() => void) => {
    const handler = (_ipcEvent: Electron.IpcRendererEvent, scanEvent: ScanEvent) => {
      callback(scanEvent);
    };
    ipcRenderer.on("scan-event", handler);
    return () => {
      ipcRenderer.removeListener("scan-event", handler);
    };
  },

  exportPDF: (html: string, defaultName?: string): Promise<string | null> =>
    ipcRenderer.invoke("export-pdf", html, defaultName ?? "codedocs-report.pdf"),

  verifyLicenseKey: (key: string): Promise<LicenseResult> =>
    ipcRenderer.invoke("verify-license", key),

  saveFile: (folder: string, filename: string, content: string): Promise<void> =>
    ipcRenderer.invoke("save-file", folder, filename, content),

  saveTextFile: (content: string, defaultName: string): Promise<string | null> =>
    ipcRenderer.invoke("save-text-file", content, defaultName),
});
