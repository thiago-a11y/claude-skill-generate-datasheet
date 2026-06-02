import { useEffect } from "react";
import useScan from "../hooks/useScan";

interface ProgressProps {
  projectPath: string;
  onComplete: (files: Record<string, string>) => void;
  onError: (message: string) => void;
}

function projectName(path: string): string {
  const segments = path.replace(/[/\\]+$/, "").split(/[/\\]/);
  return segments[segments.length - 1] || path;
}

export default function Progress({
  projectPath,
  onComplete,
  onError,
}: ProgressProps) {
  const { status, progress, steps, result, error } = useScan(projectPath);

  useEffect(() => {
    if (status === "done" && result) {
      onComplete(result);
    }
  }, [status, result, onComplete]);

  useEffect(() => {
    if (status === "error" && error) {
      onError(error);
    }
  }, [status, error, onError]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-bg text-fg p-8">
      {/* Project info */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold">{projectName(projectPath)}</h1>
        <p className="text-sm text-fg2 mt-1 max-w-md truncate">
          {projectPath}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full max-w-md mb-8">
        <div className="flex justify-between text-sm text-fg2 mb-2">
          <span>Escaneando...</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full h-2 bg-bg3 rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step checklist */}
      <div className="w-full max-w-md space-y-2">
        {steps.map((step, i) => {
          const isLast = i === steps.length - 1;
          const icon = step.completed
            ? "✅"
            : isLast
              ? "⏳"
              : "○";

          return (
            <div key={i} className="flex items-center gap-3 text-sm">
              <span className="w-5 text-center">{icon}</span>
              <span className={step.completed ? "text-fg" : "text-fg2"}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
