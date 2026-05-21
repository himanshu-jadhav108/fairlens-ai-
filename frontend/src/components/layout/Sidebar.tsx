import { useApp, type StepId } from "@/context/AppContext";
import { CheckCircle, X, Play, Upload, Search, Lightbulb, Wrench, BarChart3 } from "lucide-react";
import {
  mockUploadResult, mockTargetCol, mockSensitiveCol,
  mockAnalysisResult, mockShapResult, mockAiExplanation, mockFixResult,
} from "@/lib/mockData";

const steps: { id: StepId; label: string; num: string; icon: typeof Upload }[] = [
  { id: "upload", label: "Upload", num: "01", icon: Upload },
  { id: "analyze", label: "Detect", num: "02", icon: Search },
  { id: "explain", label: "Explain", num: "03", icon: Lightbulb },
  { id: "fix", label: "Fix", num: "04", icon: Wrench },
  { id: "compare", label: "Report", num: "05", icon: BarChart3 },
];

function isStepAccessible(step: StepId, state: ReturnType<typeof useApp>["state"]): boolean {
  switch (step) {
    case "upload": return true;
    case "analyze": return state.uploadResult !== null;
    case "explain": return state.analysisResult !== null;
    case "fix": return state.analysisResult !== null;
    case "compare": return state.fixResult !== null;
    default: return false;
  }
}

function isStepComplete(step: StepId, state: ReturnType<typeof useApp>["state"]): boolean {
  switch (step) {
    case "upload": return state.uploadResult !== null && state.targetCol !== "" && state.sensitiveCol !== "";
    case "analyze": return state.analysisResult !== null;
    case "explain": return state.shapResult !== null || state.aiExplanation !== null;
    case "fix": return state.fixResult !== null;
    case "compare": return false;
    default: return false;
  }
}

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const { state, dispatch } = useApp();

  const completedCount = steps.filter(s => isStepComplete(s.id, state)).length;

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed left-0 top-0 h-screen w-64 md:w-60 bg-background-surface border-r border-border flex flex-col z-50
          transition-transform duration-300 ease-in-out
          ${open ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0
        `}
      >
        {/* Logo */}
        <div className="px-5 py-5 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/fairlens-logo.png" alt="FairLens AI Logo" className="w-10 h-10 object-contain" />
            <div>
              <span className="font-display font-extrabold text-foreground text-base tracking-tight">FairLens</span>
              <p className="text-[10px] text-foreground-muted tracking-wider uppercase">AI Bias Auditor</p>
            </div>
          </div>
          <button onClick={onClose} className="md:hidden p-1.5 rounded-md text-foreground-muted hover:text-foreground hover:bg-secondary transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Pipeline steps */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          <p className="text-[10px] text-foreground-muted uppercase tracking-widest px-2 mb-3">Pipeline</p>
          {steps.map((step) => {
            const accessible = isStepAccessible(step.id, state);
            const active = state.activeStep === step.id;
            const complete = isStepComplete(step.id, state);
            const Icon = step.icon;

            return (
              <button
                key={step.id}
                onClick={() => {
                  if (accessible) {
                    dispatch({ type: "SET_ACTIVE_STEP", payload: step.id });
                    onClose?.();
                  }
                }}
                disabled={!accessible}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200
                  ${active ? "bg-primary/10 text-primary border border-primary/20 shadow-sm" : ""}
                  ${!active && accessible ? "text-foreground-secondary hover:bg-secondary/60 hover:text-foreground" : ""}
                  ${!accessible ? "opacity-30 cursor-not-allowed" : "cursor-pointer"}
                `}
              >
                {complete ? (
                  <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                ) : (
                  <Icon className={`w-4.5 h-4.5 flex-shrink-0 ${active ? "text-primary" : "text-foreground-muted"}`} />
                )}
                <span className="font-display font-bold text-xs tracking-wide">{step.label}</span>
                {active && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Demo mode */}
        <div className="px-3 mb-3">
          <button
            onClick={() => {
              dispatch({
                type: "LOAD_DEMO",
                payload: {
                  uploadResult: mockUploadResult,
                  targetCol: mockTargetCol,
                  sensitiveCol: mockSensitiveCol,
                  analysisResult: mockAnalysisResult,
                  shapResult: mockShapResult,
                  aiExplanation: mockAiExplanation,
                  fixResult: mockFixResult,
                },
              });
              onClose?.();
            }}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-gradient-to-r from-primary/15 to-primary/5 hover:from-primary/25 hover:to-primary/10 border border-primary/20 text-primary text-xs font-display font-bold transition-all duration-200"
          >
            <Play className="w-3.5 h-3.5" />
            Load Demo Data
          </button>
        </div>

        {/* History Link */}
        <div className="px-3 mb-4">
          <a
            href="/history"
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border border-border text-foreground-secondary text-xs font-display font-bold hover:bg-secondary/60 hover:text-foreground transition-all duration-200"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            My Audits
          </a>
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-border">
          <div className="flex items-center gap-2 text-[11px] text-foreground-muted">
            <span className="w-2 h-2 rounded-full bg-success pulse-dot" />
            <span>API Connected</span>
          </div>
          <div className="flex items-center justify-between mt-1.5">
            <p className="text-[10px] text-foreground-muted">v1.0.0</p>
            <p className="text-[10px] text-foreground-muted font-mono">{completedCount}/5 steps</p>
          </div>
        </div>
      </aside>
    </>
  );
}
