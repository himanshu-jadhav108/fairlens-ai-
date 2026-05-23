import { useApp } from "@/context/AppContext";
import { explainShap, aiExplain, getErrorMessage } from "@/lib/api";
import ScanLineLoader from "@/components/shared/ScanLineLoader";
import ErrorAlert from "@/components/shared/ErrorAlert";
import StaggerItem from "@/components/shared/StaggerItem";
import ShapChart from "./ShapChart";
import ShapTable from "./ShapTable";
import MarkdownRenderer from "./MarkdownRenderer";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DisparityChart from "./DisparityChart";
import LocalExplanationCard from "./LocalExplanationCard";

export default function ExplainSection() {
  const { state, dispatch } = useApp();
  const { shapResult, aiExplanation, loading, errors } = state;

  const runShap = async () => {
    dispatch({ type: "SET_LOADING", payload: { key: "explain", value: true } });
    dispatch({ type: "SET_ERROR", payload: { key: "explain", value: null } });
    try {
      if (!state.sessionId) throw new Error("No session active.");
      const data = await explainShap(state.sessionId);
      dispatch({ type: "SET_SHAP_RESULT", payload: data });
    } catch (err) {
      const msg = getErrorMessage(err);
      if (msg.includes("SESSION_EXPIRED")) {
        dispatch({ type: "HANDLE_SESSION_EXPIRED", payload: "Your session has expired or the backend was restarted. Please re-upload your data." });
      } else {
        dispatch({ type: "SET_ERROR", payload: { key: "explain", value: msg } });
      }
    } finally {
      dispatch({ type: "SET_LOADING", payload: { key: "explain", value: false } });
    }
  };

  const runAiExplain = async () => {
    dispatch({ type: "SET_LOADING", payload: { key: "aiExplain", value: true } });
    dispatch({ type: "SET_ERROR", payload: { key: "aiExplain", value: null } });
    try {
      if (!state.sessionId) throw new Error("No session active.");
      const data = await aiExplain(state.sessionId);
      dispatch({ type: "SET_AI_EXPLANATION", payload: data });
    } catch (err) {
      const msg = getErrorMessage(err);
      if (msg.includes("SESSION_EXPIRED")) {
        dispatch({ type: "HANDLE_SESSION_EXPIRED", payload: "Your session has expired or the backend was restarted. Please re-upload your data." });
      } else {
        dispatch({ type: "SET_ERROR", payload: { key: "aiExplain", value: msg } });
      }
    } finally {
      dispatch({ type: "SET_LOADING", payload: { key: "aiExplain", value: false } });
    }
  };

  const canProceed = shapResult || aiExplanation;

  return (
    <div className="space-y-6">
      {/* SHAP Card */}
      <StaggerItem index={0}>
        <div className="card-border rounded-lg bg-background-surface overflow-hidden">
          <div className="flex items-center justify-between p-5 border-b border-border">
            <div>
              <h2 className="font-display font-bold text-foreground text-lg">🔬 SHAP Explainability Engine</h2>
              {shapResult && (
                <p className="text-foreground-muted text-xs font-mono mt-1">
                  Method: {shapResult.method}
                </p>
              )}
            </div>
            <button
              onClick={runShap}
              disabled={loading.explain}
              className="px-4 py-2 rounded border border-primary/40 text-primary text-sm font-display hover:bg-primary/10 transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {shapResult ? "↻ Recompute" : "⚡ Run Explainability Engine"}
            </button>
          </div>

          <div className="p-5">
            {errors.explain && (
              <ErrorAlert
                message={errors.explain}
                onDismiss={() => dispatch({ type: "SET_ERROR", payload: { key: "explain", value: null } })}
              />
            )}

            {loading.explain ? (
              <div className="py-12">
                <ScanLineLoader />
                <p className="text-center text-foreground-muted text-sm mt-4 font-mono">
                  Computing Deep SHAP attributions… This may take 10–30s.
                </p>
              </div>
            ) : shapResult ? (
              <Tabs defaultValue="global" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-6 bg-background-elevated">
                  <TabsTrigger value="global">Global Features</TabsTrigger>
                  <TabsTrigger value="demographic">Demographic Disparity</TabsTrigger>
                  <TabsTrigger value="local">Local Case Study</TabsTrigger>
                </TabsList>
                
                <TabsContent value="global" className="space-y-6 animate-fade-in">
                  <ShapChart data={shapResult?.global_importance || []} />
                  <div className="border-t border-border pt-4">
                    <h3 className="font-display text-sm text-foreground-secondary mb-3">Feature Importance Table</h3>
                    <ShapTable data={shapResult?.global_importance || []} />
                  </div>
                </TabsContent>
                
                <TabsContent value="demographic" className="space-y-6 animate-fade-in">
                  <div className="mb-4">
                    <h3 className="font-display text-foreground font-bold">Feature Disparities</h3>
                    <p className="text-sm text-foreground-muted mt-1">These features impact demographic groups differently. A high disparity means the feature acts as a proxy variable that penalizes specific groups disproportionately.</p>
                  </div>
                  <DisparityChart data={(shapResult?.demographic_analysis && shapResult.demographic_analysis.top_disparities) ? shapResult.demographic_analysis.top_disparities : []} />
                </TabsContent>
                
                <TabsContent value="local" className="animate-fade-in">
                  {shapResult?.local_explanation ? (
                    <LocalExplanationCard data={shapResult.local_explanation} />
                  ) : (
                    <div className="text-center py-8 text-foreground-muted border border-dashed border-border rounded">No local explanation available.</div>
                  )}
                </TabsContent>
              </Tabs>
            ) : (
              <div className="py-16 text-center">
                <span className="text-4xl mb-4 block">📊</span>
                <p className="text-foreground-secondary text-sm">Click &apos;Run Explainability Engine&apos; to slice SHAP data across global, demographic, and local levels.</p>
              </div>
            )}
          </div>
        </div>
      </StaggerItem>

      {/* AI Explanation Card */}
      <StaggerItem index={1}>
        <div className="card-border rounded-lg bg-background-surface overflow-hidden">
          <div className="flex items-center justify-between p-5 border-b border-border">
            <div>
              <h2 className="font-display font-bold text-foreground text-lg">🤖 AI Bias Explanation</h2>
              <p className="text-foreground-muted text-xs font-mono mt-1">
                Human-readable interpretation powered by Gemini
              </p>
            </div>
            <button
              onClick={runAiExplain}
              disabled={loading.aiExplain}
              className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm font-display font-bold hover:opacity-90 transition-opacity duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {aiExplanation ? "↻ Regenerate" : "✨ Explain Bias"}
            </button>
          </div>

          <div className="p-5">
            {errors.aiExplain && (
              <ErrorAlert
                message={errors.aiExplain}
                onDismiss={() => dispatch({ type: "SET_ERROR", payload: { key: "aiExplain", value: null } })}
              />
            )}

            {loading.aiExplain ? (
              <div className="py-12">
                <ScanLineLoader />
                <p className="text-center text-foreground-muted text-sm mt-4 font-mono">
                  Generating AI explanation…
                </p>
              </div>
            ) : aiExplanation ? (
              <div className="space-y-4">
                {/* Summary badges */}
                <div className="flex flex-wrap gap-2">
                  <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-mono ${
                    aiExplanation.summary.verdict.toLowerCase().includes("fair")
                      ? "bg-success/15 text-success"
                      : "bg-danger/15 text-danger"
                  }`}>
                    {aiExplanation.summary.verdict.toLowerCase().includes("fair") ? "✅" : "⚠️"} {aiExplanation.summary.verdict}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-mono bg-background-elevated text-foreground-secondary">
                    DPD: {aiExplanation.summary.dpd_severity}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-mono bg-background-elevated text-foreground-secondary">
                    EOD: {aiExplanation.summary.eod_severity}
                  </span>
                </div>

                {/* Explanation content */}
                <div className="rounded-lg bg-background-elevated p-5">
                  <MarkdownRenderer text={aiExplanation.explanation} />
                </div>
              </div>
            ) : (
              <div className="py-16 text-center">
                <span className="text-4xl mb-4 block">🤖</span>
                <p className="text-foreground-secondary text-sm">Click &apos;Explain Bias&apos; for a human-readable analysis report</p>
              </div>
            )}
          </div>
        </div>
      </StaggerItem>

      {/* Bottom CTA */}
      <StaggerItem index={2}>
        <button
          onClick={() => dispatch({ type: "SET_ACTIVE_STEP", payload: "fix" })}
          disabled={!canProceed}
          className="w-full py-3 rounded-lg border border-warning/40 text-warning font-display font-bold text-sm hover:bg-warning/10 transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          🛠 Next: Apply Bias Fix →
        </button>
      </StaggerItem>
    </div>
  );
}
