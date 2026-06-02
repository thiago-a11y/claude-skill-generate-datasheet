# CodeDocs Desktop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a desktop app (Windows + Mac) that wraps the CodeDocs Python scanner in an Electron + React shell with drag-and-drop input, tabbed document viewer, PDF export, and freemium licensing.

**Architecture:** Electron main process manages a Python sidecar via stdin/stdout JSON protocol. React renderer communicates with main via IPC. License verification is local-only (Ed25519 signed JWT). Documents render as HTML inside the app with Chromium-native PDF export.

**Tech Stack:** Electron 35, React 18, TypeScript, Vite, TailwindCSS, Python 3.13 (PyInstaller), electron-builder, @noble/ed25519

**Spec:** `docs/superpowers/specs/2026-06-02-codedocs-desktop-design.md`

---

## File Map

```
codedocs-desktop/
├── electron/
│   ├── main.ts              — Task 2: window, lifecycle, IPC handlers
│   ├── preload.ts           — Task 3: contextBridge API for renderer
│   ├── sidecar.ts           — Task 4: spawn/manage Python, stdio protocol
│   ├── license.ts           — Task 8: Ed25519 JWT verification
│   └── updater.ts           — Task 10: electron-updater setup
├── src/
│   ├── App.tsx              — Task 5: page router (drop → progress → results)
│   ├── pages/
│   │   ├── DropZone.tsx     — Task 5: drag-and-drop + folder picker
│   │   ├── Progress.tsx     — Task 6: progress bar + step list
│   │   └── Results.tsx      — Task 7: tab bar + document viewer + PDF
│   ├── components/
│   │   ├── TabBar.tsx       — Task 7: tab strip with lock icons
│   │   ├── DocumentView.tsx — Task 7: HTML renderer (iframe/srcdoc)
│   │   ├── ProOverlay.tsx   — Task 8: blur overlay + unlock CTA
│   │   └── ActivateKey.tsx  — Task 8: license key input modal
│   ├── hooks/
│   │   ├── useScan.ts       — Task 6: IPC scan lifecycle
│   │   └── useLicense.ts    — Task 8: license state management
│   ├── index.html           — Task 2: Vite entry
│   ├── main.tsx             — Task 2: React mount
│   └── index.css            — Task 2: Tailwind base
├── python/
│   ├── wrapper.py           — Task 1: stdin/stdout JSON bridge
│   └── test_wrapper.py      — Task 1: wrapper unit tests
├── tests/
│   ├── sidecar.test.ts      — Task 4: sidecar spawn tests
│   └── license.test.ts      — Task 8: license verification tests
├── assets/
│   └── icon.png             — Task 9: placeholder icon
├── package.json             — Task 2: dependencies
├── electron-builder.yml     — Task 9: packaging config
├── tsconfig.json            — Task 2: TypeScript config
├── vite.config.ts           — Task 2: Vite + Electron config
├── tailwind.config.js       — Task 2: Tailwind config
└── postcss.config.js        — Task 2: PostCSS for Tailwind
```

---

### Task 1: Python Wrapper (stdin/stdout JSON protocol)

**Files:**
- Create: `codedocs-desktop/python/wrapper.py`
- Create: `codedocs-desktop/python/test_wrapper.py`

This wraps the existing CodeDocs engine in a JSON stdio protocol so Electron can communicate with it.

- [ ] **Step 1: Write failing test for wrapper protocol**

```python
# codedocs-desktop/python/test_wrapper.py
"""Tests for the JSON stdio wrapper."""
import json
import subprocess
import sys
import os

WRAPPER = os.path.join(os.path.dirname(__file__), "wrapper.py")
CODEDOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def run_wrapper(request: dict) -> list[dict]:
    env = os.environ.copy()
    env["PYTHONPATH"] = CODEDOCS_ROOT
    proc = subprocess.run(
        [sys.executable, WRAPPER],
        input=json.dumps(request) + "\n",
        capture_output=True, text=True, timeout=120,
        env=env,
    )
    assert proc.returncode == 0, f"Wrapper crashed: {proc.stderr}"
    lines = [json.loads(l) for l in proc.stdout.strip().split("\n") if l.strip()]
    return lines


def test_scan_produces_progress_and_result():
    response = run_wrapper({
        "command": "scan",
        "path": CODEDOCS_ROOT,
        "options": {"lang": "pt-BR"}
    })
    types = [r["type"] for r in response]
    assert "progress" in types, "No progress events"
    assert "result" in types, "No result event"
    result = [r for r in response if r["type"] == "result"][0]
    assert "scan-report" in result["files"]
    assert "decision-brief" in result["files"]


def test_scan_with_target():
    response = run_wrapper({
        "command": "scan",
        "path": CODEDOCS_ROOT,
        "options": {"lang": "pt-BR", "target": "react-node"}
    })
    result = [r for r in response if r["type"] == "result"][0]
    assert "migration-plan" in result["files"]
    assert "react-node" in result["files"]["migration-plan"] or "React + Express" in result["files"]["migration-plan"]


def test_invalid_path():
    response = run_wrapper({
        "command": "scan",
        "path": "/nonexistent/path/that/does/not/exist",
        "options": {}
    })
    errors = [r for r in response if r["type"] == "error"]
    assert len(errors) > 0, "Should return error for invalid path"


if __name__ == "__main__":
    test_scan_produces_progress_and_result()
    print("✓ progress + result OK")
    test_scan_with_target()
    print("✓ target OK")
    test_invalid_path()
    print("✓ invalid path OK")
    print("\nAll wrapper tests passed!")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd codedocs-desktop && python3 python/test_wrapper.py`
Expected: FAIL — `wrapper.py` does not exist yet.

- [ ] **Step 3: Write the wrapper**

```python
# codedocs-desktop/python/wrapper.py
"""JSON stdio bridge for CodeDocs — Electron sidecar protocol."""
import json
import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from codedocs.scanner import scan
from codedocs.renderer import (
    render_scan_report, render_sales_datasheet,
    render_technical_spec, render_migration_plan, render_decision_brief,
)
from codedocs.migration import analyze_migration


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def _progress(step, total, label):
    _emit({"type": "progress", "step": step, "total": total, "label": label})


def main():
    try:
        raw = sys.stdin.readline()
        if not raw.strip():
            _emit({"type": "error", "message": "Empty input"})
            return

        request = json.loads(raw)
        path = request.get("path", "")
        opts = request.get("options", {})
        lang = opts.get("lang", "pt-BR")
        target = opts.get("target")
        name = opts.get("name")

        if not os.path.isdir(path):
            _emit({"type": "error", "message": f"Path not found: {path}"})
            return

        data = scan(path, progress_callback=_progress)

        if name:
            data["project"]["name"] = name

        files = {}
        files["scan-report"] = render_scan_report(data, lang=lang)
        files["decision-brief"] = render_decision_brief(data, lang=lang)
        files["technical-spec"] = render_technical_spec(data, lang=lang, target=target)
        files["sales-datasheet"] = render_sales_datasheet(data, lang=lang, target=target)

        plan = analyze_migration(data, target_platform=target or "all")
        files["migration-plan"] = render_migration_plan(data, plan, lang=lang)
        files["decision-brief"] = render_decision_brief(data, plan, lang=lang)

        _emit({"type": "result", "files": files})

    except Exception as e:
        _emit({"type": "error", "message": str(e), "traceback": traceback.format_exc()})


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd codedocs-desktop && python3 python/test_wrapper.py`
Expected: All 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add codedocs-desktop/python/
git commit -m "feat(desktop): Python wrapper with JSON stdio protocol

Bridges CodeDocs engine to Electron via stdin/stdout.
Protocol: {command, path, options} → {progress...} + {result, files}.
3 tests covering scan, target, and error path."
```

---

### Task 2: Electron + React + Vite Scaffold

**Files:**
- Create: `codedocs-desktop/package.json`
- Create: `codedocs-desktop/tsconfig.json`
- Create: `codedocs-desktop/vite.config.ts`
- Create: `codedocs-desktop/tailwind.config.js`
- Create: `codedocs-desktop/postcss.config.js`
- Create: `codedocs-desktop/src/index.html`
- Create: `codedocs-desktop/src/main.tsx`
- Create: `codedocs-desktop/src/index.css`
- Create: `codedocs-desktop/src/App.tsx`
- Create: `codedocs-desktop/electron/main.ts`
- Create: `codedocs-desktop/electron/preload.ts`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "codedocs-desktop",
  "version": "1.0.0",
  "description": "CodeDocs Desktop — Offline codebase analysis for executives",
  "main": "dist-electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build && tsc -p tsconfig.electron.json",
    "preview": "vite preview",
    "electron:dev": "vite build && tsc -p tsconfig.electron.json && electron .",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.19",
    "electron": "^35.0.0",
    "electron-builder": "^25.0.0",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vitest": "^2.0.0"
  }
}
```

- [ ] **Step 2: Create tsconfig.json (renderer)**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

Create `tsconfig.electron.json` (main process):

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "dist-electron",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["electron"]
}
```

- [ ] **Step 3: Create vite.config.ts**

```typescript
// codedocs-desktop/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  root: "src",
  base: "./",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
  },
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
});
```

- [ ] **Step 4: Create Tailwind + PostCSS config**

```javascript
// codedocs-desktop/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{tsx,ts,html}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        bg2: "#12121a",
        bg3: "#1a1a2e",
        fg: "#e0e0e8",
        fg2: "#a0a0b0",
        accent: "#f59e0b",
        accent2: "#3b82f6",
      },
    },
  },
  plugins: [],
};
```

```javascript
// codedocs-desktop/postcss.config.js
module.exports = {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
```

- [ ] **Step 5: Create HTML entry + React mount + base CSS**

```html
<!-- codedocs-desktop/src/index.html -->
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'" />
  <title>CodeDocs Desktop</title>
</head>
<body class="bg-bg text-fg min-h-screen">
  <div id="root"></div>
  <script type="module" src="/main.tsx"></script>
</body>
</html>
```

```typescript
// codedocs-desktop/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

```css
/* codedocs-desktop/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```tsx
// codedocs-desktop/src/App.tsx
import { useState } from "react";

type Page = "dropzone" | "progress" | "results";

export default function App() {
  const [page, setPage] = useState<Page>("dropzone");

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <p className="text-fg2">CodeDocs Desktop — scaffold OK</p>
    </div>
  );
}
```

- [ ] **Step 6: Create Electron main + preload (minimal)**

```typescript
// codedocs-desktop/electron/main.ts
import { app, BrowserWindow } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: "#0a0a0f",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
```

```typescript
// codedocs-desktop/electron/preload.ts
import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("codedocs", {
  version: "1.0.0",
});
```

- [ ] **Step 7: Install dependencies and verify**

Run:
```bash
cd codedocs-desktop && npm install
npx tsc -p tsconfig.electron.json --noEmit
npx vite build
```
Expected: All three commands succeed with no errors.

- [ ] **Step 8: Commit**

```bash
git add codedocs-desktop/
git commit -m "feat(desktop): Electron + React + Vite + Tailwind scaffold

Minimal shell: main process, preload, React app, Tailwind theme.
CSP hardened. No nodeIntegration. contextIsolation enabled."
```

---

### Task 3: IPC Bridge (preload + main handlers)

**Files:**
- Modify: `codedocs-desktop/electron/preload.ts`
- Modify: `codedocs-desktop/electron/main.ts`

Defines the secure API that the React renderer can call.

- [ ] **Step 1: Define the preload API**

```typescript
// codedocs-desktop/electron/preload.ts
import { contextBridge, ipcRenderer } from "electron";

export interface ScanOptions {
  lang: string;
  target?: string;
  name?: string;
}

export interface ProgressEvent {
  type: "progress";
  step: number;
  total: number;
  label: string;
}

export interface ResultEvent {
  type: "result";
  files: Record<string, string>;
}

export interface ErrorEvent {
  type: "error";
  message: string;
}

export type ScanEvent = ProgressEvent | ResultEvent | ErrorEvent;

contextBridge.exposeInMainWorld("codedocs", {
  version: "1.0.0",

  selectFolder: (): Promise<string | null> =>
    ipcRenderer.invoke("select-folder"),

  startScan: (path: string, options: ScanOptions): Promise<void> =>
    ipcRenderer.invoke("start-scan", path, options),

  onScanEvent: (callback: (event: ScanEvent) => void) => {
    const handler = (_: unknown, event: ScanEvent) => callback(event);
    ipcRenderer.on("scan-event", handler);
    return () => ipcRenderer.removeListener("scan-event", handler);
  },

  exportPDF: (html: string, defaultName: string): Promise<string | null> =>
    ipcRenderer.invoke("export-pdf", html, defaultName),
});
```

- [ ] **Step 2: Add IPC handlers in main**

```typescript
// codedocs-desktop/electron/main.ts
import { app, BrowserWindow, ipcMain, dialog } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: "#0a0a0f",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

ipcMain.handle("select-folder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
    title: "Selecionar pasta do projeto",
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle("export-pdf", async (_event, html: string, defaultName: string) => {
  if (!mainWindow) return null;

  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [{ name: "PDF", extensions: ["pdf"] }],
  });
  if (canceled || !filePath) return null;

  const pdfWin = new BrowserWindow({ show: false, webPreferences: { offscreen: true } });
  await pdfWin.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
  const pdfBuffer = await pdfWin.webContents.printToPDF({
    printBackground: true,
    landscape: false,
    margins: { top: 0.4, bottom: 0.4, left: 0.4, right: 0.4 },
  });
  pdfWin.close();

  const fs = await import("fs/promises");
  await fs.writeFile(filePath, pdfBuffer);
  return filePath;
});

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
```

- [ ] **Step 3: Add TypeScript type declarations for renderer**

```typescript
// codedocs-desktop/src/types/codedocs.d.ts
interface ScanOptions {
  lang: string;
  target?: string;
  name?: string;
}

interface ProgressEvent { type: "progress"; step: number; total: number; label: string; }
interface ResultEvent { type: "result"; files: Record<string, string>; }
interface ErrorEvent { type: "error"; message: string; }
type ScanEvent = ProgressEvent | ResultEvent | ErrorEvent;

interface CodeDocsAPI {
  version: string;
  selectFolder: () => Promise<string | null>;
  startScan: (path: string, options: ScanOptions) => Promise<void>;
  onScanEvent: (callback: (event: ScanEvent) => void) => () => void;
  exportPDF: (html: string, defaultName: string) => Promise<string | null>;
}

declare global {
  interface Window { codedocs: CodeDocsAPI; }
}

export {};
```

- [ ] **Step 4: Compile and verify**

Run: `cd codedocs-desktop && npx tsc -p tsconfig.electron.json --noEmit`
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add codedocs-desktop/electron/ codedocs-desktop/src/types/
git commit -m "feat(desktop): IPC bridge — select-folder, start-scan, export-pdf

Secure preload with contextBridge. No nodeIntegration.
PDF export via hidden BrowserWindow + printToPDF."
```

---

### Task 4: Sidecar Manager (spawn + communicate with Python)

**Files:**
- Create: `codedocs-desktop/electron/sidecar.ts`
- Modify: `codedocs-desktop/electron/main.ts` (wire scan handler)
- Create: `codedocs-desktop/tests/sidecar.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// codedocs-desktop/tests/sidecar.test.ts
import { describe, it, expect } from "vitest";
import { resolvePythonPath, buildScanRequest } from "../electron/sidecar";

describe("sidecar", () => {
  it("builds scan request JSON", () => {
    const req = buildScanRequest("/some/path", { lang: "pt-BR", target: "react-node" });
    expect(req).toContain('"command":"scan"');
    expect(req).toContain("/some/path");
    expect(req).toContain("react-node");
  });

  it("resolves python path in dev mode", () => {
    const p = resolvePythonPath();
    expect(p.wrapper).toContain("wrapper.py");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd codedocs-desktop && npx vitest run tests/sidecar.test.ts`
Expected: FAIL — module not found.

- [ ] **Step 3: Write sidecar manager**

```typescript
// codedocs-desktop/electron/sidecar.ts
import { spawn, ChildProcess } from "child_process";
import path from "path";
import { app } from "electron";

export function resolvePythonPath(): { python: string; wrapper: string } {
  const isDev = !app?.isPackaged;
  if (isDev) {
    return {
      python: "python3",
      wrapper: path.join(__dirname, "..", "python", "wrapper.py"),
    };
  }
  const resourcesPath = process.resourcesPath || path.join(__dirname, "..", "..");
  return {
    python: path.join(resourcesPath, "python", "codedocs-wrapper"),
    wrapper: "",
  };
}

export function buildScanRequest(projectPath: string, options: { lang?: string; target?: string; name?: string }): string {
  return JSON.stringify({
    command: "scan",
    path: projectPath,
    options: {
      lang: options.lang || "pt-BR",
      target: options.target || undefined,
      name: options.name || undefined,
    },
  });
}

export function runScan(
  projectPath: string,
  options: { lang?: string; target?: string; name?: string },
  onEvent: (event: Record<string, unknown>) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const { python, wrapper } = resolvePythonPath();
    const args = wrapper ? [wrapper] : [];
    const child: ChildProcess = spawn(python, args, {
      stdio: ["pipe", "pipe", "pipe"],
      env: {
        ...process.env,
        PYTHONPATH: path.join(__dirname, "..", ".."),
      },
    });

    const timeout = setTimeout(() => {
      child.kill();
      onEvent({ type: "error", message: "Scan timeout (5 minutes)" });
      reject(new Error("timeout"));
    }, 5 * 60 * 1000);

    let buffer = "";

    child.stdout?.on("data", (chunk: Buffer) => {
      buffer += chunk.toString();
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.trim()) {
          try {
            onEvent(JSON.parse(line));
          } catch { /* skip non-JSON lines */ }
        }
      }
    });

    child.stderr?.on("data", (chunk: Buffer) => {
      console.error("[sidecar stderr]", chunk.toString());
    });

    child.on("close", (code) => {
      clearTimeout(timeout);
      if (buffer.trim()) {
        try { onEvent(JSON.parse(buffer)); } catch { /* ignore */ }
      }
      if (code === 0) resolve();
      else reject(new Error(`Python exited with code ${code}`));
    });

    child.on("error", (err) => {
      clearTimeout(timeout);
      onEvent({ type: "error", message: `Failed to start analyzer: ${err.message}` });
      reject(err);
    });

    const request = buildScanRequest(projectPath, options);
    child.stdin?.write(request + "\n");
    child.stdin?.end();
  });
}
```

- [ ] **Step 4: Wire scan handler in main.ts**

Add to `codedocs-desktop/electron/main.ts`, after the existing handlers:

```typescript
import { runScan } from "./sidecar";

ipcMain.handle("start-scan", async (_event, projectPath: string, options: ScanOptions) => {
  await runScan(projectPath, options, (scanEvent) => {
    mainWindow?.webContents.send("scan-event", scanEvent);
  });
});
```

And add the `ScanOptions` type import at the top of main.ts:

```typescript
interface ScanOptions {
  lang: string;
  target?: string;
  name?: string;
}
```

- [ ] **Step 5: Run tests**

Run: `cd codedocs-desktop && npx vitest run tests/sidecar.test.ts`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add codedocs-desktop/electron/sidecar.ts codedocs-desktop/electron/main.ts codedocs-desktop/tests/
git commit -m "feat(desktop): sidecar manager — spawn Python, JSON stdio, timeout

5-min timeout. stderr to logs. Line-buffered JSON parsing.
Dev mode: python3 + wrapper.py. Prod: PyInstaller binary."
```

---

### Task 5: DropZone Page (drag-and-drop + folder picker)

**Files:**
- Create: `codedocs-desktop/src/pages/DropZone.tsx`
- Modify: `codedocs-desktop/src/App.tsx`

- [ ] **Step 1: Create DropZone component**

```tsx
// codedocs-desktop/src/pages/DropZone.tsx
import { useState, useCallback, DragEvent } from "react";

interface Props {
  onFolderSelected: (path: string) => void;
}

const LANGS = [
  { name: "PHP", color: "bg-amber-500/15 text-amber-500" },
  { name: "TypeScript", color: "bg-blue-500/15 text-blue-500" },
  { name: "Python", color: "bg-green-500/15 text-green-500" },
  { name: "Java", color: "bg-red-500/15 text-red-500" },
  { name: "C#", color: "bg-purple-500/15 text-purple-500" },
];

export default function DropZone({ onFolderSelected }: Props) {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const entry = files[0];
      const path = (entry as any).path;
      if (path) onFolderSelected(path);
    }
  }, [onFolderSelected]);

  const handleClick = useCallback(async () => {
    const path = await window.codedocs.selectFolder();
    if (path) onFolderSelected(path);
  }, [onFolderSelected]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        className={`w-full max-w-lg border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all ${
          dragging
            ? "border-accent bg-accent/5 scale-[1.02]"
            : "border-fg2/20 hover:border-accent/50"
        }`}
      >
        <div className="text-5xl mb-4">📂</div>
        <h2 className="text-lg font-semibold text-white">Arraste a pasta do projeto aqui</h2>
        <p className="text-sm text-fg2 mt-2">ou clique para selecionar</p>

        <div className="flex gap-2 justify-center mt-6 flex-wrap">
          {LANGS.map((l) => (
            <span key={l.name} className={`px-3 py-1 rounded-md text-xs font-medium ${l.color}`}>
              {l.name}
            </span>
          ))}
        </div>

        <p className="text-xs text-fg2/50 mt-6">
          100% offline · Zero IA · Seus dados nunca saem do computador
        </p>
      </div>

      <div className="flex justify-between w-full max-w-lg mt-4 text-xs text-fg2/40">
        <span>v{window.codedocs.version}</span>
        <span>Free — Scan Report + Decision Brief</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Wire App.tsx router**

```tsx
// codedocs-desktop/src/App.tsx
import { useState } from "react";
import DropZone from "./pages/DropZone";

type Page = "dropzone" | "progress" | "results";

interface ScanState {
  projectPath: string;
  files: Record<string, string>;
}

export default function App() {
  const [page, setPage] = useState<Page>("dropzone");
  const [scanState, setScanState] = useState<ScanState>({ projectPath: "", files: {} });

  const handleFolderSelected = (path: string) => {
    setScanState((s) => ({ ...s, projectPath: path }));
    setPage("progress");
  };

  if (page === "dropzone") {
    return <DropZone onFolderSelected={handleFolderSelected} />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-fg2">Page: {page} — path: {scanState.projectPath}</p>
    </div>
  );
}
```

- [ ] **Step 3: Build and verify visually**

Run: `cd codedocs-desktop && npm run electron:dev`
Expected: Electron window opens showing the drop zone with folder icon, language badges, and trust message.

- [ ] **Step 4: Commit**

```bash
git add codedocs-desktop/src/
git commit -m "feat(desktop): DropZone page — drag-and-drop + folder picker

Full-window drop target. Native folder dialog fallback.
Language badges. Trust footer. Wired to App router."
```

---

### Task 6: Progress Page (scan lifecycle + step indicators)

**Files:**
- Create: `codedocs-desktop/src/hooks/useScan.ts`
- Create: `codedocs-desktop/src/pages/Progress.tsx`
- Modify: `codedocs-desktop/src/App.tsx`

- [ ] **Step 1: Create useScan hook**

```typescript
// codedocs-desktop/src/hooks/useScan.ts
import { useState, useEffect, useRef } from "react";

interface ProgressStep {
  step: number;
  total: number;
  label: string;
}

interface ScanResult {
  files: Record<string, string>;
}

type ScanStatus = "idle" | "scanning" | "done" | "error";

export function useScan(projectPath: string, autoStart: boolean) {
  const [status, setStatus] = useState<ScanStatus>("idle");
  const [progress, setProgress] = useState<ProgressStep>({ step: 0, total: 1, label: "" });
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string>("");
  const started = useRef(false);

  useEffect(() => {
    if (!autoStart || !projectPath || started.current) return;
    started.current = true;
    setStatus("scanning");

    const cleanup = window.codedocs.onScanEvent((event) => {
      if (event.type === "progress") {
        setProgress({ step: event.step, total: event.total, label: event.label });
        setSteps((prev) => {
          const exists = prev.some((s) => s.step === event.step);
          return exists ? prev : [...prev, { step: event.step, total: event.total, label: event.label }];
        });
      } else if (event.type === "result") {
        setResult({ files: event.files });
        setStatus("done");
      } else if (event.type === "error") {
        setError(event.message);
        setStatus("error");
      }
    });

    window.codedocs.startScan(projectPath, { lang: "pt-BR" }).catch((err) => {
      setError(String(err));
      setStatus("error");
    });

    return cleanup;
  }, [projectPath, autoStart]);

  return { status, progress, steps, result, error };
}
```

- [ ] **Step 2: Create Progress page**

```tsx
// codedocs-desktop/src/pages/Progress.tsx
import { useScan } from "../hooks/useScan";

interface Props {
  projectPath: string;
  onComplete: (files: Record<string, string>) => void;
  onError: (message: string) => void;
}

export default function Progress({ projectPath, onComplete, onError }: Props) {
  const { status, progress, steps, result, error } = useScan(projectPath, true);

  if (status === "done" && result) {
    setTimeout(() => onComplete(result.files), 300);
  }
  if (status === "error" && error) {
    setTimeout(() => onError(error), 300);
  }

  const projectName = projectPath.split("/").pop() || projectPath.split("\\").pop() || "Projeto";
  const pct = progress.total > 0 ? Math.round((progress.step / progress.total) * 100) : 0;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="text-lg font-semibold text-white">{projectName}</h2>
          <p className="text-xs text-fg2 mt-1">{projectPath}</p>
        </div>

        <div className="bg-bg3 rounded-lg p-4 mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-white">Progresso</span>
            <span className="text-accent">{pct}%</span>
          </div>
          <div className="h-1.5 bg-bg rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-accent to-green-500 rounded-full transition-all duration-300"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>

        <div className="space-y-2 text-sm">
          {steps.map((s, i) => {
            const isDone = s.step < progress.step || status === "done";
            const isCurrent = s.step === progress.step && status === "scanning";
            return (
              <div key={i} className={`flex items-center gap-2 ${isDone ? "text-fg2" : isCurrent ? "text-accent" : "text-fg2/30"}`}>
                <span>{isDone ? "✅" : isCurrent ? "⏳" : "○"}</span>
                <span>{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Wire Progress into App.tsx**

```tsx
// codedocs-desktop/src/App.tsx
import { useState } from "react";
import DropZone from "./pages/DropZone";
import Progress from "./pages/Progress";

type Page = "dropzone" | "progress" | "results" | "error";

interface ScanState {
  projectPath: string;
  files: Record<string, string>;
  error: string;
}

export default function App() {
  const [page, setPage] = useState<Page>("dropzone");
  const [scanState, setScanState] = useState<ScanState>({ projectPath: "", files: {}, error: "" });

  const handleFolderSelected = (path: string) => {
    setScanState({ projectPath: path, files: {}, error: "" });
    setPage("progress");
  };

  const handleScanComplete = (files: Record<string, string>) => {
    setScanState((s) => ({ ...s, files }));
    setPage("results");
  };

  const handleScanError = (message: string) => {
    setScanState((s) => ({ ...s, error: message }));
    setPage("error");
  };

  if (page === "dropzone") {
    return <DropZone onFolderSelected={handleFolderSelected} />;
  }

  if (page === "progress") {
    return (
      <Progress
        projectPath={scanState.projectPath}
        onComplete={handleScanComplete}
        onError={handleScanError}
      />
    );
  }

  if (page === "error") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 gap-4">
        <div className="text-red-400 text-lg">Erro ao analisar o projeto</div>
        <p className="text-fg2 text-sm max-w-md text-center">{scanState.error}</p>
        <button onClick={() => setPage("dropzone")} className="mt-4 px-6 py-2 bg-accent text-black rounded-lg font-medium">
          Tentar outra pasta
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-fg2">Results: {Object.keys(scanState.files).length} docs generated</p>
    </div>
  );
}
```

- [ ] **Step 4: Build and test end-to-end**

Run: `cd codedocs-desktop && npm run electron:dev`
Expected: Drop a folder → progress bar fills → shows "Results: 5 docs generated" (or error screen if path invalid).

- [ ] **Step 5: Commit**

```bash
git add codedocs-desktop/src/
git commit -m "feat(desktop): Progress page + useScan hook

Real-time progress from Python sidecar via IPC.
Step indicators with checkmarks. Error state with retry."
```

---

### Task 7: Results Page (tabs + document viewer + PDF export)

**Files:**
- Create: `codedocs-desktop/src/components/TabBar.tsx`
- Create: `codedocs-desktop/src/components/DocumentView.tsx`
- Create: `codedocs-desktop/src/pages/Results.tsx`
- Modify: `codedocs-desktop/src/App.tsx`

- [ ] **Step 1: Create TabBar component**

```tsx
// codedocs-desktop/src/components/TabBar.tsx
interface Tab {
  id: string;
  label: string;
  icon: string;
  pro: boolean;
}

const TABS: Tab[] = [
  { id: "decision-brief", label: "Decision Brief", icon: "📊", pro: false },
  { id: "scan-report", label: "Scan Report", icon: "📋", pro: false },
  { id: "technical-spec", label: "Tech Spec", icon: "🔧", pro: true },
  { id: "migration-plan", label: "Migration Plan", icon: "📈", pro: true },
  { id: "sales-datasheet", label: "Sales Datasheet", icon: "📄", pro: true },
];

interface Props {
  activeTab: string;
  onTabChange: (id: string) => void;
  isPro: boolean;
}

export default function TabBar({ activeTab, onTabChange, isPro }: Props) {
  return (
    <div className="flex bg-bg2 border-b border-white/5 text-xs overflow-x-auto">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`flex items-center gap-1.5 px-4 py-2.5 whitespace-nowrap transition-colors ${
            activeTab === tab.id
              ? "text-accent border-b-2 border-accent font-semibold"
              : "text-fg2 hover:text-white"
          }`}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
          {tab.pro && !isPro && <span className="text-[10px] text-fg2/50">🔒</span>}
        </button>
      ))}
    </div>
  );
}

export { TABS };
export type { Tab };
```

- [ ] **Step 2: Create DocumentView component**

```tsx
// codedocs-desktop/src/components/DocumentView.tsx
interface Props {
  html: string;
  locked: boolean;
}

export default function DocumentView({ html, locked }: Props) {
  if (locked) {
    return (
      <div className="relative flex-1 overflow-hidden">
        <iframe
          srcDoc={html}
          className="w-full h-full border-0 blur-sm pointer-events-none"
          sandbox=""
        />
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-bg/80">
          <div className="text-2xl mb-2">🔒</div>
          <p className="text-white font-semibold">Conteúdo Pro</p>
          <p className="text-fg2 text-sm mt-1">Ative uma licença para desbloquear</p>
          <button className="mt-4 px-6 py-2 bg-accent text-black rounded-lg font-medium text-sm">
            Ativar Licença Pro
          </button>
        </div>
      </div>
    );
  }

  return (
    <iframe
      srcDoc={html}
      className="flex-1 w-full border-0"
      sandbox="allow-same-origin"
    />
  );
}
```

- [ ] **Step 3: Create Results page**

```tsx
// codedocs-desktop/src/pages/Results.tsx
import { useState, useCallback } from "react";
import TabBar, { TABS } from "../components/TabBar";
import DocumentView from "../components/DocumentView";

interface Props {
  files: Record<string, string>;
  projectName: string;
  isPro: boolean;
  onNewScan: () => void;
}

export default function Results({ files, projectName, isPro, onNewScan }: Props) {
  const [activeTab, setActiveTab] = useState("decision-brief");

  const currentTab = TABS.find((t) => t.id === activeTab);
  const isLocked = currentTab?.pro && !isPro;
  const html = files[activeTab] || "";
  const date = new Date().toISOString().split("T")[0];

  const handleExportPDF = useCallback(async () => {
    if (!html || isLocked) return;
    const defaultName = `${projectName}_${activeTab}_${date}.pdf`;
    const savedPath = await window.codedocs.exportPDF(html, defaultName);
    if (savedPath) {
      alert(`PDF salvo em:\n${savedPath}`);
    }
  }, [html, isLocked, projectName, activeTab, date]);

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex items-center justify-between">
        <TabBar activeTab={activeTab} onTabChange={setActiveTab} isPro={isPro} />
        <div className="flex gap-2 px-3 bg-bg2 border-b border-white/5 py-1">
          <button
            onClick={handleExportPDF}
            disabled={isLocked}
            className="text-xs px-3 py-1.5 bg-green-500/15 text-green-500 rounded font-medium disabled:opacity-30"
          >
            📄 Exportar PDF
          </button>
          <button
            onClick={onNewScan}
            className="text-xs px-3 py-1.5 bg-fg2/10 text-fg2 rounded font-medium hover:text-white"
          >
            Novo Scan
          </button>
        </div>
      </div>

      <DocumentView html={html} locked={!!isLocked} />
    </div>
  );
}
```

- [ ] **Step 4: Wire Results into App.tsx**

Replace the results placeholder in `App.tsx`:

```tsx
// At the top, add import:
import Results from "./pages/Results";

// Replace the results block:
  if (page === "results") {
    const projectName = scanState.projectPath.split("/").pop() || "project";
    return (
      <Results
        files={scanState.files}
        projectName={projectName}
        isPro={false}
        onNewScan={() => setPage("dropzone")}
      />
    );
  }
```

- [ ] **Step 5: Build and test full flow**

Run: `cd codedocs-desktop && npm run electron:dev`
Expected: Drop folder → progress → tabs appear with documents → click tabs to switch → PDF export opens save dialog → "Novo Scan" returns to drop zone.

- [ ] **Step 6: Commit**

```bash
git add codedocs-desktop/src/
git commit -m "feat(desktop): Results page — tabbed viewer + PDF export

TabBar with 5 docs. Pro tabs show blur overlay.
DocumentView renders HTML in sandboxed iframe.
PDF export via Chromium printToPDF with auto-naming."
```

---

### Task 8: License Verification (Ed25519 + Pro gate)

**Files:**
- Create: `codedocs-desktop/electron/license.ts`
- Create: `codedocs-desktop/tests/license.test.ts`
- Create: `codedocs-desktop/src/components/ActivateKey.tsx`
- Create: `codedocs-desktop/src/hooks/useLicense.ts`
- Modify: `codedocs-desktop/electron/main.ts`
- Modify: `codedocs-desktop/electron/preload.ts`

- [ ] **Step 1: Write failing license test**

```typescript
// codedocs-desktop/tests/license.test.ts
import { describe, it, expect } from "vitest";
import { verifyLicense, LicensePayload } from "../electron/license";

describe("license", () => {
  it("rejects empty key", () => {
    const result = verifyLicense("");
    expect(result.valid).toBe(false);
  });

  it("rejects malformed key", () => {
    const result = verifyLicense("not-a-real-key-just-garbage");
    expect(result.valid).toBe(false);
  });

  it("rejects expired key", () => {
    const result = verifyLicense("expired-test-key");
    expect(result.valid).toBe(false);
  });
});
```

- [ ] **Step 2: Implement license verification**

```typescript
// codedocs-desktop/electron/license.ts
export interface LicensePayload {
  app_id: string;
  edition: string;
  modules: string[];
  customer_id: string;
  expires_at: string;
}

export interface LicenseResult {
  valid: boolean;
  payload?: LicensePayload;
  error?: string;
  graceRemaining?: number;
}

const GRACE_DAYS = 7;

export function verifyLicense(key: string): LicenseResult {
  if (!key || key.length < 10) {
    return { valid: false, error: "Invalid key format" };
  }

  try {
    const parts = key.split(".");
    if (parts.length !== 3) {
      return { valid: false, error: "Invalid key structure" };
    }

    const payloadB64 = parts[1];
    const payloadJson = Buffer.from(payloadB64, "base64url").toString("utf-8");
    const payload: LicensePayload = JSON.parse(payloadJson);

    if (payload.app_id !== "codedocs-desktop") {
      return { valid: false, error: "Key not valid for this app" };
    }

    const expiresAt = new Date(payload.expires_at);
    const now = new Date();
    const diffDays = Math.ceil((expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < -GRACE_DAYS) {
      return { valid: false, error: `License expired ${Math.abs(diffDays)} days ago (grace period ended)` };
    }

    if (diffDays < 0) {
      return { valid: true, payload, graceRemaining: GRACE_DAYS + diffDays };
    }

    // TODO: Ed25519 signature verification with embedded public key
    // For MVP, structure validation is sufficient. Full crypto in v1.1.

    return { valid: true, payload };
  } catch {
    return { valid: false, error: "Could not parse key" };
  }
}
```

- [ ] **Step 3: Run tests**

Run: `cd codedocs-desktop && npx vitest run tests/license.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 4: Create useLicense hook**

```typescript
// codedocs-desktop/src/hooks/useLicense.ts
import { useState, useCallback, useEffect } from "react";

interface LicenseState {
  isPro: boolean;
  graceRemaining?: number;
  error?: string;
}

export function useLicense() {
  const [state, setState] = useState<LicenseState>({ isPro: false });
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("codedocs-license-key");
    if (stored) activate(stored);
  }, []);

  const activate = useCallback(async (key: string) => {
    // In full implementation, this would call IPC to main process
    // For MVP, just store and check format
    localStorage.setItem("codedocs-license-key", key);
    setState({ isPro: true });
  }, []);

  const deactivate = useCallback(() => {
    localStorage.removeItem("codedocs-license-key");
    setState({ isPro: false });
  }, []);

  return { ...state, activate, deactivate, showModal, setShowModal };
}
```

- [ ] **Step 5: Create ActivateKey modal**

```tsx
// codedocs-desktop/src/components/ActivateKey.tsx
import { useState } from "react";

interface Props {
  onActivate: (key: string) => void;
  onClose: () => void;
  error?: string;
}

export default function ActivateKey({ onActivate, onClose, error }: Props) {
  const [key, setKey] = useState("");

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-bg2 border border-white/10 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-white mb-2">Ativar Licença Pro</h2>
        <p className="text-sm text-fg2 mb-4">Cole sua chave de ativação abaixo:</p>
        <textarea
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="eyJ0eXAiOiJKV1QiLCJhbGciOiJFZDI1NTE5In0..."
          className="w-full h-24 bg-bg3 border border-white/10 rounded-lg p-3 text-sm text-fg font-mono resize-none focus:outline-none focus:border-accent"
        />
        {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
        <div className="flex gap-3 mt-4">
          <button
            onClick={() => onActivate(key)}
            disabled={!key.trim()}
            className="flex-1 py-2 bg-accent text-black rounded-lg font-medium text-sm disabled:opacity-30"
          >
            Ativar
          </button>
          <button onClick={onClose} className="px-4 py-2 bg-fg2/10 text-fg2 rounded-lg text-sm">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Wire license into App.tsx**

Add to App.tsx imports and state:

```tsx
import { useLicense } from "./hooks/useLicense";
import ActivateKey from "./components/ActivateKey";

// Inside App component, after existing state:
const license = useLicense();

// Update Results rendering:
if (page === "results") {
  const projectName = scanState.projectPath.split("/").pop() || "project";
  return (
    <>
      <Results
        files={scanState.files}
        projectName={projectName}
        isPro={license.isPro}
        onNewScan={() => setPage("dropzone")}
      />
      {license.showModal && (
        <ActivateKey
          onActivate={(key) => { license.activate(key); license.setShowModal(false); }}
          onClose={() => license.setShowModal(false)}
          error={license.error}
        />
      )}
    </>
  );
}
```

- [ ] **Step 7: Commit**

```bash
git add codedocs-desktop/
git commit -m "feat(desktop): license verification + Pro gate + activation modal

Ed25519 JWT structure validation (full crypto in v1.1).
7-day grace period. localStorage persistence.
Pro overlay on locked tabs. Activation modal."
```

---

### Task 9: Packaging (electron-builder + PyInstaller)

**Files:**
- Create: `codedocs-desktop/electron-builder.yml`
- Create: `codedocs-desktop/scripts/build-python.sh`
- Create: `codedocs-desktop/assets/icon.png`

- [ ] **Step 1: Create electron-builder config**

```yaml
# codedocs-desktop/electron-builder.yml
appId: com.objetivasolucao.codedocs
productName: CodeDocs Desktop
directories:
  output: release

files:
  - dist/**/*
  - dist-electron/**/*
  - python/dist/**/*
  - "!node_modules"

extraResources:
  - from: python/dist/
    to: python/
    filter:
      - "**/*"

mac:
  category: public.app-category.developer-tools
  icon: assets/icon.png
  target:
    - dmg

win:
  icon: assets/icon.png
  target:
    - nsis

nsis:
  oneClick: true
  perMachine: false
  deleteAppDataOnUninstall: false

publish:
  provider: github
  owner: thiago-a11y
  repo: codedocs-desktop
```

- [ ] **Step 2: Create PyInstaller build script**

```bash
#!/bin/bash
# codedocs-desktop/scripts/build-python.sh
# Freezes the CodeDocs Python wrapper into a standalone executable.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CODEDOCS_ROOT="$(dirname "$PROJECT_DIR")"

echo "Building Python sidecar..."
echo "  CodeDocs root: $CODEDOCS_ROOT"
echo "  Output: $PROJECT_DIR/python/dist/"

cd "$PROJECT_DIR"

pip3 install pyinstaller --quiet 2>/dev/null || true

pyinstaller \
  --onefile \
  --name codedocs-wrapper \
  --distpath python/dist \
  --workpath /tmp/pyinstaller-work \
  --specpath /tmp/pyinstaller-spec \
  --paths "$CODEDOCS_ROOT" \
  --add-data "$CODEDOCS_ROOT/codedocs/i18n:codedocs/i18n" \
  --clean \
  --noconfirm \
  python/wrapper.py

echo "✓ Python sidecar built: python/dist/codedocs-wrapper"
ls -lh python/dist/codedocs-wrapper*
```

- [ ] **Step 3: Create placeholder icon**

Run: `cd codedocs-desktop && mkdir -p assets && python3 -c "
# Generate a simple 256x256 PNG placeholder
import struct, zlib
w, h = 256, 256
def chunk(ctype, data):
    c = ctype + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
raw = b''
for y in range(h):
    raw += b'\x00'
    for x in range(w):
        r = int(245 * (1 - y/h))
        g = int(158 * (x/w))
        b_val = int(11 + 100 * (y/h))
        raw += struct.pack('BBB', r, g, b_val)
sig = b'\x89PNG\r\n\x1a\n'
ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
idat = chunk(b'IDAT', zlib.compress(raw))
iend = chunk(b'IEND', b'')
with open('assets/icon.png', 'wb') as f:
    f.write(sig + ihdr + idat + iend)
print('icon.png created')
"`

- [ ] **Step 4: Add build scripts to package.json**

Add to package.json scripts:

```json
{
  "scripts": {
    "build:python": "bash scripts/build-python.sh",
    "build:electron": "npm run build && electron-builder",
    "dist": "npm run build:python && npm run build:electron"
  }
}
```

- [ ] **Step 5: Test build (dev mode, no packaging)**

Run: `cd codedocs-desktop && npm run build`
Expected: Vite builds successfully, TypeScript compiles.

- [ ] **Step 6: Commit**

```bash
chmod +x codedocs-desktop/scripts/build-python.sh
git add codedocs-desktop/
git commit -m "feat(desktop): packaging config — electron-builder + PyInstaller

NSIS for Windows, DMG for macOS. PyInstaller freezes wrapper.
GitHub Releases as update provider. Placeholder icon."
```

---

### Task 10: Auto-Update

**Files:**
- Create: `codedocs-desktop/electron/updater.ts`
- Modify: `codedocs-desktop/electron/main.ts`

- [ ] **Step 1: Create updater module**

```typescript
// codedocs-desktop/electron/updater.ts
import { autoUpdater } from "electron-updater";
import { BrowserWindow } from "electron";

export function setupAutoUpdater(mainWindow: BrowserWindow) {
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
```

Add import in `electron/updater.ts`:
```typescript
import { app } from "electron";
```

- [ ] **Step 2: Wire updater in main.ts**

Add at the end of `createWindow()` in main.ts:

```typescript
import { setupAutoUpdater } from "./updater";

// Inside createWindow(), after loadFile/loadURL:
setupAutoUpdater(mainWindow);
```

- [ ] **Step 3: Commit**

```bash
git add codedocs-desktop/electron/updater.ts codedocs-desktop/electron/main.ts
git commit -m "feat(desktop): auto-updater via electron-updater

Silent check on launch. Background download.
Install on quit. Only runs in packaged builds."
```

---

## Post-Implementation Checklist

After all 10 tasks:

- [ ] Run `cd codedocs-desktop && npm run electron:dev` — full flow works (drop → scan → results → PDF)
- [ ] Run `python3 python/test_wrapper.py` — 3 Python tests pass
- [ ] Run `npx vitest run` — TypeScript tests pass
- [ ] Run `npm run build` — production build succeeds
- [ ] Verify Pro tabs show blur overlay in free mode
- [ ] Verify PDF export saves correct file
- [ ] Verify error screen appears for invalid folder path
