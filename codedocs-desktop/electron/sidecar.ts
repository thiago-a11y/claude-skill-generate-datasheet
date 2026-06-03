/**
 * Sidecar Manager — spawns the Python CodeDocs engine as a child process.
 *
 * Dev mode:  uses system python3 + wrapper.py from source tree
 * Prod mode: uses bundled python binary from app resources
 */

import { spawn } from "child_process";
import path from "path";

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

/**
 * Resolve the Python interpreter and wrapper script paths.
 *
 * In dev (app.isPackaged === false or no app available):
 *   - python = "python3"
 *   - wrapper = <repo>/codedocs-desktop/python/wrapper.py
 *
 * In prod (app.isPackaged === true):
 *   - python = <resources>/python/codedocs-wrapper
 *   - wrapper = "" (the bundled binary IS the wrapper)
 */
export function resolvePythonPath(isPackaged?: boolean, resourcesPath?: string): {
  python: string;
  wrapper: string;
  repoRoot: string;
} {
  // Repo root is two levels up from dist-electron/ (at runtime) or electron/ (at dev)
  const repoRoot = path.resolve(__dirname, "..", "..");

  if (isPackaged && resourcesPath) {
    const pythonDir = path.join(resourcesPath, "python");
    const isWin = process.platform === "win32";

    if (isWin) {
      return {
        python: path.join(pythonDir, "python.exe"),
        wrapper: path.join(pythonDir, "wrapper.py"),
        repoRoot: pythonDir,
      };
    }
    return {
      python: path.join(pythonDir, "codedocs-wrapper"),
      wrapper: "",
      repoRoot,
    };
  }

  // Dev mode: wrapper.py sits in codedocs-desktop/python/
  const desktopRoot = path.resolve(__dirname, "..");
  return {
    python: "python3",
    wrapper: path.join(desktopRoot, "python", "wrapper.py"),
    repoRoot,
  };
}

/**
 * Build the JSON request string for the wrapper protocol.
 */
export function buildScanRequest(
  projectPath: string,
  options?: ScanOptions
): string {
  return JSON.stringify({
    command: "scan",
    path: projectPath,
    options: {
      lang: options?.lang ?? "pt-BR",
      ...(options?.target ? { target: options.target } : {}),
    },
  });
}

/**
 * Spawn the Python sidecar, send the scan request, and stream JSON-line events.
 *
 * The wrapper reads one JSON line from stdin and emits JSON lines on stdout:
 *   {"type": "progress", "step": 1, "total": 19, "label": "..."}
 *   {"type": "result",   "files": {...}}
 *   {"type": "error",    "message": "..."}
 */
export function runScan(
  projectPath: string,
  options: ScanOptions,
  onEvent: (event: ScanEvent) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    let resolved: boolean | undefined;

    // Dynamic import avoidance: app may not be available in test env.
    // The caller (main.ts) should pass isPackaged/resourcesPath if needed.
    const paths = resolvePythonPath();

    const args = paths.wrapper ? [paths.wrapper] : [];
    const env = {
      ...process.env,
      PYTHONPATH: paths.repoRoot + (process.env.PYTHONPATH ? path.delimiter + process.env.PYTHONPATH : ""),
    };

    const child = spawn(paths.python, args, {
      env,
      stdio: ["pipe", "pipe", "pipe"],
    });

    // 5-minute timeout
    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        child.kill("SIGKILL");
        reject(new Error("Scan timed out after 5 minutes"));
      }
    }, 5 * 60 * 1000);

    // Stream stdout line by line
    let buffer = "";
    child.stdout.on("data", (chunk: Buffer) => {
      buffer += chunk.toString();
      const lines = buffer.split("\n");
      // Keep the last partial line in buffer
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event: ScanEvent = JSON.parse(trimmed);
          onEvent(event);
        } catch {
          console.error("[sidecar] non-JSON stdout line:", trimmed);
        }
      }
    });

    // stderr -> console.error
    child.stderr.on("data", (chunk: Buffer) => {
      console.error("[sidecar/stderr]", chunk.toString());
    });

    child.on("close", (code) => {
      clearTimeout(timeout);
      if (resolved) return;
      resolved = true;

      // Flush remaining buffer
      if (buffer.trim()) {
        try {
          const event: ScanEvent = JSON.parse(buffer.trim());
          onEvent(event);
        } catch {
          console.error("[sidecar] non-JSON trailing data:", buffer.trim());
        }
      }

      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Sidecar exited with code ${code}`));
      }
    });

    child.on("error", (err) => {
      clearTimeout(timeout);
      if (!resolved) {
        resolved = true;
        reject(err);
      }
    });

    // Send the scan request
    const request = buildScanRequest(projectPath, options);
    child.stdin.write(request + "\n");
    child.stdin.end();
  });
}
