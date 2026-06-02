/** Type declarations for the CodeDocs IPC bridge exposed via preload.ts */

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

export interface LicenseResult {
  valid: boolean;
  payload?: {
    app_id: string;
    edition: string;
    modules: string[];
    customer_id: string;
    expires_at: string;
  };
  error?: string;
  graceRemaining?: number;
}

export interface CodeDocsAPI {
  version: string;
  selectFolder: () => Promise<string | null>;
  startScan: (projectPath: string, options?: ScanOptions) => Promise<void>;
  onScanEvent: (callback: (event: ScanEvent) => void) => () => void;
  exportPDF: (html: string, defaultName?: string) => Promise<string | null>;
  verifyLicenseKey: (key: string) => Promise<LicenseResult>;
}

declare global {
  interface Window {
    codedocs: CodeDocsAPI;
  }
}
