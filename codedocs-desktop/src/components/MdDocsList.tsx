interface Props {
  mdDocs: Record<string, string>;
  projectName: string;
}

const DOC_LABELS: Record<string, string> = {
  "architecture.md": "Arquitetura do Sistema",
  "data-dictionary.md": "Dicionário de Dados",
  "endpoints.md": "Endpoints da API",
  "glossary.md": "Glossário",
  "CHANGELOG.md": "Changelog",
  "security.md": "Controles de Segurança",
  "bugs-known.md": "Bugs Conhecidos",
  "contributing.md": "Guia de Contribuição",
  "health-score.md": "Health Score",
  "bus-factor-report.md": "Relatório de Bus Factor",
  "evolution-report.md": "Relatório de Evolução",
};

export default function MdDocsList({ mdDocs, projectName }: Props) {
  const files = Object.entries(mdDocs);

  const handleSaveAll = async () => {
    const folder = await window.codedocs.selectFolder();
    if (!folder) return;

    let saved = 0;
    for (const [filename, content] of files) {
      try {
        await window.codedocs.saveFile(folder, filename, content);
        saved++;
      } catch {
        // continue with others
      }
    }
    alert(`${saved} arquivos salvos em:\n${folder}`);
  };

  const handleSaveOne = async (filename: string, content: string) => {
    const defaultName = `${projectName}_${filename}`;
    const path = await window.codedocs.saveTextFile(content, defaultName);
    if (path) {
      alert(`Salvo em:\n${path}`);
    }
  };

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-white">Documentação Completa</h2>
            <p className="text-sm text-fg2 mt-1">{files.length} arquivos Markdown gerados</p>
          </div>
          <button
            onClick={handleSaveAll}
            className="px-4 py-2 bg-accent text-black rounded-lg font-medium text-sm hover:bg-accent/90"
          >
            📁 Salvar Todos
          </button>
        </div>

        <div className="space-y-2">
          {files.map(([filename, content]) => {
            const label = DOC_LABELS[filename] || filename;
            const lines = content.split("\n").length;
            return (
              <div
                key={filename}
                className="flex items-center justify-between p-3 bg-bg2 border border-white/5 rounded-lg hover:border-white/10"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">📄</span>
                  <div>
                    <p className="text-sm font-medium text-white">{label}</p>
                    <p className="text-xs text-fg2">{filename} · {lines} linhas</p>
                  </div>
                </div>
                <button
                  onClick={() => handleSaveOne(filename, content)}
                  className="px-3 py-1.5 text-xs bg-fg2/10 text-fg2 rounded hover:text-white hover:bg-fg2/20"
                >
                  Salvar
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
