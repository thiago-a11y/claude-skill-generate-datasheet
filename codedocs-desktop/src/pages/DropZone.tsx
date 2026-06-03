import { useState, useCallback } from "react";

interface DropZoneProps {
  onFolderSelected: (path: string, fullDocs: boolean) => void;
}

const langBadges = [
  { name: "PHP", color: "bg-indigo-600" },
  { name: "TypeScript", color: "bg-blue-600" },
  { name: "Python", color: "bg-yellow-600" },
  { name: "Java", color: "bg-red-600" },
  { name: "C#", color: "bg-purple-600" },
];

export default function DropZone({ onFolderSelected }: DropZoneProps) {
  const [dragging, setDragging] = useState(false);
  const [fullDocs, setFullDocs] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        // Electron exposes .path on dropped files
        const filePath = (file as File & { path: string }).path;
        if (filePath) {
          onFolderSelected(filePath, fullDocs);
        }
      }
    },
    [onFolderSelected]
  );

  const handleClick = useCallback(async () => {
    const folder = await window.codedocs.selectFolder();
    if (folder) {
      onFolderSelected(folder, fullDocs);
    }
  }, [onFolderSelected, fullDocs]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-bg text-fg p-8 select-none">
      {/* Drop area */}
      <button
        type="button"
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          flex flex-col items-center justify-center gap-4
          w-full max-w-lg aspect-square rounded-2xl
          border-2 border-dashed cursor-pointer
          transition-all duration-200
          ${
            dragging
              ? "border-accent bg-accent/5 scale-[1.02]"
              : "border-fg2/30 hover:border-fg2/60 bg-bg2"
          }
        `}
      >
        <span className="text-6xl" role="img" aria-label="folder">
          {"📂"}
        </span>
        <span className="text-lg font-medium text-fg">
          Arraste a pasta do projeto aqui
        </span>
        <span className="text-sm text-fg2">ou clique para selecionar</span>
      </button>

      {/* Language badges */}
      <div className="flex flex-wrap justify-center gap-2 mt-8">
        {langBadges.map((lang) => (
          <span
            key={lang.name}
            className={`${lang.color} text-white text-xs font-medium px-3 py-1 rounded-full`}
          >
            {lang.name}
          </span>
        ))}
      </div>

      {/* Full docs toggle */}
      <label className="flex items-center gap-3 mt-6 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={fullDocs}
          onChange={(e) => setFullDocs(e.target.checked)}
          className="w-4 h-4 rounded border-fg2/30 bg-bg2 text-accent accent-amber-500 cursor-pointer"
        />
        <span className="text-sm text-fg2">
          Gerar documentação completa (11 arquivos Markdown extras)
        </span>
      </label>

      {/* Trust message */}
      <p className="mt-4 text-sm text-fg2 text-center">
        100% offline &middot; Zero IA &middot; Seus dados nunca saem do
        computador
      </p>

      {/* Footer */}
      <footer className="absolute bottom-6 text-center text-xs text-fg2/60">
        <span>CodeDocs v{window.codedocs.version}</span>
        <span className="mx-2">&middot;</span>
        <span>Free &mdash; Scan Report + Decision Brief</span>
      </footer>
    </div>
  );
}
