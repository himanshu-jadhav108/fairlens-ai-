import { useApp } from "@/context/AppContext";
import MetricCard from "@/components/shared/MetricCard";
import StaggerItem from "@/components/shared/StaggerItem";
import ModelInfoPills from "./ModelInfoPills";
import GroupBarChart from "./GroupBarChart";
import GroupStatsTable from "./GroupStatsTable";

export default function BiasMetricsDashboard() {
  const { state, dispatch } = useApp();
  const result = state.analysisResult;

  if (!result) {
    return (
      <div className="card-border rounded-lg bg-background-surface p-8 text-center">
        <span className="text-4xl mb-4 block">🔍</span>
        <h2 className="font-display font-bold text-foreground text-lg mb-2">Bias Detection</h2>
        <p className="text-foreground-secondary text-sm">Run an analysis from the Upload page to see results here</p>
      </div>
    );
  }

  const groupRateData = result.group_stats.map(g => ({
    group: g.group,
    value: g.positive_rate,
  }));

  const groupAccData = result.group_stats.map(g => ({
    group: g.group,
    value: g.accuracy,
  }));

  return (
    <div className="space-y-6">
      {/* Sub-header */}
      <StaggerItem index={0}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full border border-primary/30 text-primary text-xs font-mono">
              Target: {state.targetCol}
            </span>
            <span className="text-foreground-muted text-xs">·</span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full border border-warning/30 text-warning text-xs font-mono">
              Sensitive: {state.sensitiveCol}
            </span>
            <span className="text-foreground-muted text-xs">·</span>
            <span className="text-foreground-secondary text-xs font-mono">
              Model accuracy: {(result.accuracy * 100).toFixed(1)}%
            </span>
            {result.fairness_score !== undefined && (
              <>
                <span className="text-foreground-muted text-xs">·</span>
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                  result.fairness_score >= 80 ? 'bg-success/15 text-success' :
                  result.fairness_score >= 50 ? 'bg-warning/15 text-warning' :
                  'bg-danger/15 text-danger'
                }`}>
                  Fairness Score: {result.fairness_score.toFixed(1)}/100 ({result.fairness_label})
                </span>
              </>
            )}
          </div>
          <button
            onClick={() => dispatch({ type: "SET_ACTIVE_STEP", payload: "upload" })}
            className="text-foreground-muted text-xs font-mono hover:text-foreground transition-colors cursor-pointer"
          >
            ↻ Re-run
          </button>
        </div>
      </StaggerItem>

      {/* Model info pills */}
      <StaggerItem index={1}>
        <ModelInfoPills info={result.model_info} />
      </StaggerItem>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StaggerItem index={2}>
          <MetricCard
            name="Demographic Parity Difference"
            value={result.dpd}
            description="Gap in positive prediction rates across groups. Lower values indicate more equitable outcomes."
            footnote="< 0.05 is acceptable in most fairness standards"
          />
        </StaggerItem>
        <StaggerItem index={3}>
          <MetricCard
            name="Equalized Odds Difference"
            value={result.eod}
            description="Gap in true/false positive rates across groups. Measures whether the model errs equally for all groups."
            footnote="< 0.05 is acceptable in most fairness standards"
          />
        </StaggerItem>
        <StaggerItem index={4}>
          <MetricCard
            name="Disparate Impact Ratio"
            value={result.disparate_impact_ratio}
            description="The 80% Rule. Ratio of positive outcomes for the lowest group vs highest group."
            footnote="> 0.80 is required by US legal standards"
          />
        </StaggerItem>
        <StaggerItem index={5}>
          <MetricCard
            name="Model Accuracy"
            value={result.accuracy}
            description="Overall classification accuracy of the model across all groups."
            isAccuracy
          />
        </StaggerItem>
      </div>

      {/* Bar charts */}
      <StaggerItem index={6}>
        <GroupBarChart
          title={`Positive Prediction Rate by ${state.sensitiveCol}`}
          subtitle="Bars show % of positive predictions per group. Equal bars = demographic parity."
          data={groupRateData}
          formatAsPercent
          colorOffset={0}
        />
      </StaggerItem>

      <StaggerItem index={7}>
        <GroupBarChart
          title={`Accuracy by ${state.sensitiveCol}`}
          subtitle="Per-group classification accuracy. Large differences indicate disparate model performance."
          data={groupAccData}
          formatAsPercent
          colorOffset={2}
        />
      </StaggerItem>

      {/* Group stats table */}
      <StaggerItem index={8}>
        <GroupStatsTable stats={result.group_stats} />
      </StaggerItem>

      {/* Bottom CTA */}
      <StaggerItem index={9}>
        <button
          onClick={() => dispatch({ type: "SET_ACTIVE_STEP", payload: "explain" })}
          className="w-full py-3 rounded-md border border-border text-foreground-secondary font-display font-bold text-sm hover:border-primary/40 hover:text-foreground transition-all duration-200 cursor-pointer"
        >
          Next: Explain Bias →
        </button>
      </StaggerItem>
    </div>
  );
}
