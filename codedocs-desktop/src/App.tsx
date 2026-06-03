import { useState, useCallback } from "react";
import DropZone from "./pages/DropZone";
import Progress from "./pages/Progress";
import Results from "./pages/Results";
import ActivateKey from "./components/ActivateKey";
import useLicense from "./hooks/useLicense";

type Page = "dropzone" | "progress" | "results" | "error";

interface ScanState {
  projectPath: string;
  fullDocs: boolean;
  files: Record<string, string> | null;
  error: string | null;
}

function App() {
  const [page, setPage] = useState<Page>("dropzone");
  const [scanState, setScanState] = useState<ScanState>({
    projectPath: "",
    fullDocs: false,
    files: null,
    error: null,
  });
  const license = useLicense();

  const handleFolderSelected = useCallback((path: string) => {
    setScanState({ projectPath: path, fullDocs: true, files: null, error: null });
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
    setScanState({ projectPath: "", fullDocs: false, files: null, error: null });
    setPage("dropzone");
  }, []);

  const content = (() => {
    switch (page) {
      case "dropzone":
        return <DropZone onFolderSelected={handleFolderSelected} />;

      case "progress":
        return (
          <Progress
            projectPath={scanState.projectPath}
            fullDocs={scanState.fullDocs}
            onComplete={handleScanComplete}
            onError={handleScanError}
          />
        );

      case "results": {
        const projectName =
          scanState.projectPath.split("/").filter(Boolean).pop() ?? "project";
        return (
          <Results
            files={scanState.files ?? {}}
            projectName={projectName}
            isPro={license.isPro}
            onNewScan={handleReset}
            onActivateClick={() => license.setShowModal(true)}
          />
        );
      }

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
  })();

  return (
    <>
      {content}
      {license.showModal && (
        <ActivateKey
          onActivate={license.activate}
          onClose={() => license.setShowModal(false)}
          error={license.error}
        />
      )}
    </>
  );
}

export default App;
