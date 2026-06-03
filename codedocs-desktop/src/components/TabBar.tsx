export interface Tab {
  id: string;
  label: string;
  icon: string;
  pro: boolean;
}

export const TABS: Tab[] = [
  { id: "decision-brief", label: "Decision Brief", icon: "\u{1F4CA}", pro: false },
  { id: "scan-report", label: "Scan Report", icon: "\u{1F4CB}", pro: false },
  { id: "technical-spec", label: "Tech Spec", icon: "\u{1F527}", pro: true },
  { id: "migration-plan", label: "Migration Plan", icon: "\u{1F4C8}", pro: true },
  { id: "sales-datasheet", label: "Sales Datasheet", icon: "\u{1F4C4}", pro: true },
];

interface TabBarProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
  isPro: boolean;
  hasMdDocs?: boolean;
}

export default function TabBar({ activeTab, onTabChange, isPro, hasMdDocs }: TabBarProps) {
  const allTabs = hasMdDocs
    ? [...TABS, { id: "md-docs", label: "Docs MD (11)", icon: "📁", pro: false }]
    : TABS;

  return (
    <div className="flex bg-bg2 overflow-x-auto">
      {allTabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const isLocked = tab.pro && !isPro;

        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
              isActive
                ? "text-accent border-accent bg-bg3"
                : "text-fg2 border-transparent hover:text-fg hover:bg-bg3/50"
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {isLocked && <span className="ml-1 opacity-60">{"\u{1F512}"}</span>}
          </button>
        );
      })}
    </div>
  );
}
