import { useApp, type StepId } from "@/context/AppContext";
import { Upload, Search, Lightbulb, Wrench, BarChart3 } from "lucide-react";

const steps: { id: StepId; label: string; icon: typeof Upload }[] = [
  { id: "upload", label: "Upload", icon: Upload },
  { id: "analyze", label: "Detect", icon: Search },
  { id: "explain", label: "Explain", icon: Lightbulb },
  { id: "fix", label: "Fix", icon: Wrench },
  { id: "compare", label: "Report", icon: BarChart3 },
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

export default function MobileBottomNav() {
  const { state, dispatch } = useApp();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-background-surface border-t border-border backdrop-blur-lg bg-opacity-95">
      <div className="flex items-center justify-around px-1 py-1.5 safe-area-bottom">
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
                }
              }}
              disabled={!accessible}
              className={`flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-lg min-w-[56px] transition-all duration-200
                ${active ? "bg-primary/15 text-primary" : ""}
                ${!active && accessible ? "text-foreground-muted active:bg-secondary/50" : ""}
                ${!accessible ? "opacity-30 cursor-not-allowed" : "cursor-pointer"}
              `}
            >
              <div className="relative">
                <Icon className={`w-5 h-5 ${active ? "text-primary" : ""}`} />
                {complete && (
                  <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-success" />
                )}
              </div>
              <span className={`text-[10px] font-display font-bold leading-tight ${active ? "text-primary" : ""}`}>
                {step.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
