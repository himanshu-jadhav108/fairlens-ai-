import { useApp } from "@/context/AppContext";
import StaggerItem from "@/components/shared/StaggerItem";
import SemicircleGauge from "./SemicircleGauge";
import FairnessRadar from "./FairnessRadar";
import SideBySideChart from "./SideBySideChart";
import { exportAuditPdf } from "@/lib/exportPdf";
import { API_BASE_URL } from "@/lib/api";
import { Download } from "lucide-react";

export default function CompareResults() {
  const { state, dispatch } = useApp();
  const { fixResult, analysisResult } = state;

  if (!fixResult) return null;

  const before = fixResult.original_metrics;
  const after = fixResult.fixed_metrics;

  const metrics = [
    { key: "DPD", label: "Demographic Parity", before: before.dpd, after: after.dpd, lowerBetter: true },
    { key: "EOD", label: "Equalized Odds", before: before.eod, after: after.eod, lowerBetter: true },
    { key: "Accuracy", label: "Accuracy", before: before.accuracy, after: after.accuracy, lowerBetter: false },
  ];

  const avgImprovement = metrics.reduce((sum, m) => {
    const diff = m.before - m.after;
    const pct = m.before !== 0 ? Math.abs(diff / m.before) * 100 : 0;
    return sum + (m.lowerBetter ? (diff > 0 ? pct : -pct) : (diff < 0 ? pct : -pct));
  }, 0) / metrics.length;

  const groupRatesAfter = fixResult.comparison.group_rates_after;

  return (
    <div className="space-y-6">
      {/* Hero Gauge Overview */}
      <StaggerItem index={0}>
        <div className="card-border rounded-lg bg-background-surface overflow-hidden">
          <div className="p-5 border-b border-border">
            <h2 className="font-display font-bold text-foreground text-lg">🎯 Fairness Score Overview</h2>
          </div>
          <div className="p-5">
            <div className="grid grid-cols-1 xl:grid-cols-[1fr_auto_1fr] gap-6 items-center">
              <div>
                <p className="text-center font-display text-xs text-foreground-muted mb-4">Before Mitigation</p>
                <div className="flex flex-wrap justify-center gap-2 sm:gap-4">
                  <SemicircleGauge value={before.dpd} label="DPD" invert />
                  <SemicircleGauge value={before.eod} label="EOD" invert />
                  <SemicircleGauge value={before.accuracy} label="Accuracy" />
                </div>
              </div>
              <div className="flex flex-col items-center gap-2 px-2 hidden xl:flex">
                <div className="w-px h-12 bg-gradient-to-b from-transparent via-primary/40 to-transparent" />
                <span className="px-2 py-1 rounded text-[10px] font-mono bg-primary/10 text-primary whitespace-nowrap">
                  {fixResult.strategy}
                </span>
                <div className="w-px h-12 bg-gradient-to-b from-transparent via-primary/40 to-transparent" />
              </div>
              <div>
                <p className="text-center font-display text-xs text-foreground-muted mb-4">After Mitigation</p>
                <div className="flex flex-wrap justify-center gap-2 sm:gap-4">
                  <SemicircleGauge value={after.dpd} label="DPD" invert />
                  <SemicircleGauge value={after.eod} label="EOD" invert />
                  <SemicircleGauge value={after.accuracy} label="Accuracy" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </StaggerItem>

      {/* Two-column charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StaggerItem index={1}>
          <div className="card-border rounded-lg bg-background-surface overflow-hidden h-full">
            <div className="p-5 border-b border-border">
              <h2 className="font-display font-bold text-foreground text-sm">🕸 Fairness Profile</h2>
            </div>
            <div className="p-4">
              <FairnessRadar before={before} after={after} />
              <p className="text-foreground-muted text-[10px] font-mono text-center mt-2">
                DPD/EOD axes inverted (larger = fairer)
              </p>
            </div>
          </div>
        </StaggerItem>

        <StaggerItem index={2}>
          <div className="card-border rounded-lg bg-background-surface overflow-hidden h-full">
            <div className="p-5 border-b border-border">
              <h2 className="font-display font-bold text-foreground text-sm">📊 Side-by-Side Metrics</h2>
            </div>
            <div className="p-4">
              <SideBySideChart before={before} after={after} />
            </div>
          </div>
        </StaggerItem>
      </div>

      {/* Detailed Comparison Table */}
      <StaggerItem index={3}>
        <div className="card-border rounded-lg bg-background-surface overflow-hidden">
          <div className="p-5 border-b border-border">
            <h2 className="font-display font-bold text-foreground text-sm">📋 Detailed Comparison</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-foreground-muted font-mono text-xs">Metric</th>
                  <th className="text-center py-3 px-4 text-foreground-muted font-mono text-xs">Before</th>
                  <th className="text-center py-3 px-4 text-foreground-muted font-mono text-xs">After</th>
                  <th className="text-center py-3 px-4 text-foreground-muted font-mono text-xs">Change</th>
                  <th className="text-center py-3 px-4 text-foreground-muted font-mono text-xs">Status</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m) => {
                  const diff = m.after - m.before;
                  const pct = m.before !== 0 ? Math.abs(diff / m.before) * 100 : 0;
                  const improved = m.lowerBetter ? diff < 0 : diff > 0;
                  return (
                    <tr key={m.key} className="border-b border-border/50 hover:bg-background-elevated/50 transition-colors duration-200">
                      <td className="py-3 px-4 font-display text-foreground text-sm">{m.label}</td>
                      <td className="py-3 px-4 text-center font-mono text-danger">{m.before.toFixed(4)}</td>
                      <td className="py-3 px-4 text-center font-mono text-success">{m.after.toFixed(4)}</td>
                      <td className="py-3 px-4 text-center font-mono text-foreground-secondary">
                        {diff > 0 ? "↑" : "↓"} {pct.toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono ${
                          improved ? "bg-success/15 text-success" : "bg-danger/15 text-danger"
                        }`}>
                          {improved ? "Improved" : "Regressed"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </StaggerItem>

      {/* Post-Mitigation Group Table */}
      <StaggerItem index={4}>
        <div className="card-border rounded-lg bg-background-surface overflow-hidden">
          <div className="p-5 border-b border-border">
            <h2 className="font-display font-bold text-foreground text-sm">👥 Post-Mitigation Group Rates</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-foreground-muted font-mono text-xs">Group</th>
                  <th className="text-center py-3 px-4 text-foreground-muted font-mono text-xs">Positive Rate (After)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(groupRatesAfter).map(([group, rate]) => (
                  <tr key={group} className="border-b border-border/50 hover:bg-background-elevated/50 transition-colors duration-200">
                    <td className="py-3 px-4 font-mono text-primary">{group}</td>
                    <td className="py-3 px-4 text-center font-mono text-foreground">{(rate * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </StaggerItem>

      {/* Final CTA Banner */}
      <StaggerItem index={5}>
        <div
          className="card-border rounded-lg bg-primary/5 p-6"
          style={{ borderLeftWidth: 3, borderLeftColor: "hsl(168 47% 52%)", boxShadow: "0 0 20px hsla(168,47%,52%,0.1)" }}
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="font-display font-bold text-foreground text-lg">✅ Audit Complete</h3>
              <p className="text-foreground-secondary text-sm font-mono mt-1">
                Average fairness improvement:{" "}
                <span className="text-success">{avgImprovement.toFixed(1)}%</span>
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <a
                href={`${API_BASE_URL}/api/download-fixed/${state.sessionId}`}
                download="fairlens_mitigated_dataset.csv"
                className="flex items-center gap-2 px-5 py-2 rounded border border-primary/40 text-primary text-sm font-display hover:bg-primary/10 transition-colors duration-200"
              >
                <Download className="w-4 h-4" />
                Dataset (CSV)
              </a>
              <button
                onClick={() =>
                  exportAuditPdf({
                    analysisResult: analysisResult!,
                    fixResult,
                    shapResult: state.shapResult,
                    aiExplanation: state.aiExplanation,
                    filename: state.uploadResult?.filename || "dataset",
                  })
                }
                className="flex items-center gap-2 px-5 py-2 rounded bg-primary text-primary-foreground text-sm font-display hover:opacity-90 transition-opacity duration-200"
              >
                <Download className="w-4 h-4" />
                Export PDF
              </button>
              <button
                onClick={() => dispatch({ type: "RESET" })}
                className="px-5 py-2 rounded border border-border-hover text-foreground-secondary text-sm font-display hover:bg-background-elevated transition-colors duration-200"
              >
                ↩ New Audit
              </button>
            </div>
          </div>
        </div>
      </StaggerItem>
    </div>
  );
}
