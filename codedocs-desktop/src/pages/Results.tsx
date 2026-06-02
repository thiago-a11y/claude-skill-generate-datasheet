import { useState } from "react";
import TabBar, { TABS } from "../components/TabBar";
import DocumentView from "../components/DocumentView";

interface ResultsProps {
  files: Record<string, string>;
  projectName: string;
  isPro: boolean;
  onNewScan: () => void;
  onActivateClick?: () => void;
}

export default function Results({
  files,
  projectName,
  isPro,
  onNewScan,
  onActivateClick,
}: ResultsProps) {
  const [activeTab, setActiveTab] = useState("decision-brief");

  const currentTab = TABS.find((t) => t.id === activeTab) ?? TABS[0];
  const isLocked = currentTab.pro && !isPro;
  const html = files[activeTab] ?? "";

  const handleExportPDF = async () => {
    if (isLocked || !html) return;

    const today = new Date().toISOString().slice(0, 10);
    const defaultName = `${projectName}_${activeTab}_${today}.pdf`;

    try {
      const savedPath = await window.codedocs.exportPDF(html, defaultName);
      if (savedPath) {
        alert(`PDF salvo em:\n${savedPath}`);
      }
    } catch {
      alert("Erro ao exportar PDF.");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-bg text-fg">
      {/* Top bar */}
      <div className="flex items-center justify-between border-b border-bg3">
        <TabBar activeTab={activeTab} onTabChange={setActiveTab} isPro={isPro} />

        <div className="flex items-center gap-2 px-4 shrink-0">
          <button
            type="button"
            onClick={handleExportPDF}
            disabled={isLocked}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              isLocked
                ? "bg-bg3 text-fg2/50 cursor-not-allowed"
                : "bg-emerald-600 text-white hover:bg-emerald-500"
            }`}
          >
            {"\u{1F4C4}"} Exportar PDF
          </button>
          <button
            type="button"
            onClick={onNewScan}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-bg3 text-fg2 hover:text-fg hover:bg-bg3/80 transition-colors"
          >
            Novo Scan
          </button>
        </div>
      </div>

      {/* Document area */}
      <DocumentView html={html} locked={isLocked} onActivateClick={onActivateClick} />
    </div>
  );
}
