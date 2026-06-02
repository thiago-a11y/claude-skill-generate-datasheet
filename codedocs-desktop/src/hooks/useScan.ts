import { useState, useEffect, useRef } from "react";
import type { ScanEvent } from "../types/codedocs";

type ScanStatus = "idle" | "scanning" | "done" | "error";

interface ScanStep {
  label: string;
  completed: boolean;
}

interface UseScanResult {
  status: ScanStatus;
  progress: number;
  steps: ScanStep[];
  result: Record<string, string> | null;
  error: string | null;
}

export default function useScan(projectPath: string): UseScanResult {
  const [status, setStatus] = useState<ScanStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<ScanStep[]>([]);
  const [result, setResult] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    setStatus("scanning");

    const cleanup = window.codedocs.onScanEvent((event: ScanEvent) => {
      switch (event.type) {
        case "progress":
          if (event.step != null && event.total != null && event.total > 0) {
            setProgress(Math.round((event.step / event.total) * 100));
          }
          if (event.label) {
            setSteps((prev) => {
              // Mark all existing as completed, add new one as in-progress
              const completed = prev.map((s) => ({ ...s, completed: true }));
              return [...completed, { label: event.label!, completed: false }];
            });
          }
          break;

        case "result":
          // Mark last step as completed
          setSteps((prev) =>
            prev.map((s) => ({ ...s, completed: true }))
          );
          setProgress(100);
          setResult(event.files ?? {});
          setStatus("done");
          break;

        case "error":
          setError(event.message ?? "Erro desconhecido durante o scan");
          setStatus("error");
          break;
      }
    });

    window.codedocs.startScan(projectPath, { lang: "pt-BR" }).catch((err) => {
      setError(err instanceof Error ? err.message : String(err));
      setStatus("error");
    });

    return cleanup;
  }, [projectPath]);

  return { status, progress, steps, result, error };
}
