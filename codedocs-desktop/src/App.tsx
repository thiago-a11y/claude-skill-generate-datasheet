import { useState, useCallback } from "react";
import DropZone from "./pages/DropZone";
import Progress from "./pages/Progress";

type Page = "dropzone" | "progress" | "results" | "error";

interface ScanState {
  projectPath: string;
  files: Record<string, string> | null;
  error: string | null;
}

function App() {
  const [page, setPage] = useState<Page>("dropzone");
  const [scanState, setScanState] = useState<ScanState>({
    projectPath: "",
    files: null,
    error: null,
  });

  const handleFolderSelected = useCallback((path: string) => {
    setScanState({ projectPath: path, files: null, error: null });
    setPage("progress");
  }, []);

  const handleScanComplete = useCallback((files: Record<string, string>) => {
    setScanState((prev) => ({ ...prev, files }));
    setPage("results");
  }, []);

  const handleScanError = useCallback((message: string) => {
    setScanState((prev) => ({ ...prev, error: message }));
    setPage("error");
  }, []);

  const handleReset = useCallback(() => {
    setScanState({ projectPath: "", files: null, error: null });
    setPage("dropzone");
  }, []);

  switch (page) {
    case "dropzone":
      return <DropZone onFolderSelected={handleFolderSelected} />;

    case "progress":
      return (
        <Progress
          projectPath={scanState.projectPath}
          onComplete={handleScanComplete}
          onError={handleScanError}
        />
      );

    case "results":
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-bg text-fg p-8">
          <h1 className="text-2xl font-semibold mb-4">Scan completo</h1>
          <p className="text-fg2 mb-8">
            {scanState.files
              ? `${Object.keys(scanState.files).length} docs gerados`
              : "Nenhum documento gerado"}
          </p>
          <button
            type="button"
            onClick={handleReset}
            className="px-6 py-2 bg-accent text-bg font-medium rounded-lg hover:bg-accent/90 transition-colors"
          >
            Escanear outro projeto
          </button>
        </div>
      );

    case "error":
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-bg text-fg p-8">
          <div className="text-center max-w-md">
            <h1 className="text-2xl font-semibold text-red-400 mb-4">
              Erro no scan
            </h1>
            <p className="text-fg2 mb-8">{scanState.error}</p>
            <button
              type="button"
              onClick={handleReset}
              className="px-6 py-2 bg-accent text-bg font-medium rounded-lg hover:bg-accent/90 transition-colors"
            >
              Tentar outra pasta
            </button>
          </div>
        </div>
      );
  }
}

export default App;
