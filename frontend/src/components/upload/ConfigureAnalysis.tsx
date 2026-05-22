import type { ColumnInfo } from "@/context/AppContext";
import ScanLineLoader from "@/components/shared/ScanLineLoader";
import ErrorAlert from "@/components/shared/ErrorAlert";
import { Settings, Zap } from "lucide-react";

interface ConfigureAnalysisProps {
  columns: ColumnInfo[];
  targetCol: string;
  sensitiveCol: string;
  onTargetChange: (v: string) => void;
  onSensitiveChange: (v: string) => void;
  onAnalyze: () => void;
  loading: boolean;
  error: string | null;
  onDismissError: () => void;
}

export default function ConfigureAnalysis({
  columns,
  targetCol,
  sensitiveCol,
  onTargetChange,
  onSensitiveChange,
  onAnalyze,
  loading,
  error,
  onDismissError,
}: ConfigureAnalysisProps) {
  const canAnalyze = targetCol !== "" && sensitiveCol !== "" && !loading;
  const sensitiveOptions = columns.filter(c => c.name !== targetCol);

  return (
    <div className="card-border card-border-hover rounded-lg bg-background-surface p-6 transition-all duration-200">
      <div className="flex items-center gap-2 mb-5">
        <Settings className="w-4 h-4 text-foreground-muted" />
        <h2 className="font-display font-bold text-foreground text-base">Configure Analysis</h2>
      </div>

      {error && (
        <div className="mb-4">
          <ErrorAlert message={error} onDismiss={onDismissError} />
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Target column */}
        <div className="space-y-2">
          <label className="text-foreground-secondary text-xs font-mono">Target Column (what to predict)</label>
          <select
            value={targetCol}
            onChange={(e) => {
              onTargetChange(e.target.value);
              if (e.target.value === sensitiveCol) onSensitiveChange("");
            }}
            className="w-full bg-secondary border border-border rounded-md px-3 py-2.5 text-foreground text-sm font-mono appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary transition-all duration-200"
          >
            <option value="" className="text-foreground-muted">— Select target —</option>
            {columns.map(col => (
              <option key={col.name} value={col.name}>{col.name}</option>
            ))}
          </select>
          {targetCol && (
            <p className="text-foreground-muted text-[11px] font-mono">Binary classification (0/1 outcome)</p>
          )}
        </div>

        {/* Sensitive attribute */}
        <div className="space-y-2">
          <label className="text-foreground-secondary text-xs font-mono">Sensitive Attribute (protected group)</label>
          <select
            value={sensitiveCol}
            onChange={(e) => onSensitiveChange(e.target.value)}
            className="w-full bg-secondary border border-border rounded-md px-3 py-2.5 text-foreground text-sm font-mono appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary transition-all duration-200"
          >
            <option value="" className="text-foreground-muted">— Select attribute —</option>
            {sensitiveOptions.map(col => (
              <option key={col.name} value={col.name}>{col.name}</option>
            ))}
          </select>
          {sensitiveCol && (
            <p className="text-foreground-muted text-[11px] font-mono">Fairness audit will run across {sensitiveCol} groups</p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="py-4">
          <ScanLineLoader text="Running Analysis…" />
        </div>
      ) : (
        <button
          onClick={onAnalyze}
          disabled={!canAnalyze}
          className={`w-full flex items-center justify-center gap-2 py-3 rounded-md font-display font-bold text-sm transition-all duration-200
            ${canAnalyze
              ? "bg-primary text-primary-foreground cursor-pointer hover:opacity-90 glow-primary"
              : "bg-primary/40 text-primary-foreground/40 cursor-not-allowed opacity-40"
            }
          `}
        >
          <Zap className="w-4 h-4" />
          Run Bias Analysis
        </button>
      )}
    </div>
  );
}
