interface DocumentViewProps {
  html: string;
  locked: boolean;
}

export default function DocumentView({ html, locked }: DocumentViewProps) {
  return (
    <div className="relative flex-1 min-h-0">
      <iframe
        srcDoc={html}
        sandbox="allow-same-origin"
        className={`w-full h-full border-0 bg-white ${
          locked ? "blur-sm pointer-events-none" : ""
        }`}
        title="Document preview"
      />

      {locked && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-bg/70">
          <span className="text-4xl mb-3">{"\u{1F512}"}</span>
          <h2 className="text-lg font-semibold text-fg mb-1">
            Conteudo Pro
          </h2>
          <p className="text-sm text-fg2 mb-4">
            Ative uma licenca para desbloquear
          </p>
          <button
            type="button"
            className="px-5 py-2 bg-accent text-bg text-sm font-semibold rounded-lg hover:bg-accent/90 transition-colors"
          >
            Ativar Licenca Pro
          </button>
        </div>
      )}
    </div>
  );
}
