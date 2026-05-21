import { useApp } from "@/context/AppContext";
import { useAuth } from "@/context/AuthContext";
import { Menu, LogOut } from "lucide-react";
import { Link } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

const stepLabels: Record<string, { icon: string; label: string }> = {
  upload: { icon: "📂", label: "Upload & Configure" },
  analyze: { icon: "🔍", label: "Bias Detection" },
  explain: { icon: "🔬", label: "Explainability" },
  fix: { icon: "🛠", label: "Bias Mitigation" },
  compare: { icon: "📊", label: "Full Report" },
};

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { state } = useApp();
  const { currentUser, logout } = useAuth();

  const step = stepLabels[state.activeStep];
  const completedSteps = [
    state.uploadResult && state.targetCol && state.sensitiveCol ? 1 : 0,
    state.analysisResult ? 1 : 0,
    state.shapResult || state.aiExplanation ? 1 : 0,
    state.fixResult ? 1 : 0,
    0,
  ].reduce((a, b) => a + b, 0);

  const progress = (completedSteps / 5) * 100;

  return (
    <header className="sticky top-0 z-40 h-12 md:h-14 bg-background-surface/95 backdrop-blur-md border-b border-border flex items-center px-3 md:px-6 gap-3 md:gap-6">
      {/* Mobile menu button - hidden since we have bottom nav, but keep for sidebar access */}
      <button onClick={onMenuClick} className="hidden md:hidden p-1 text-foreground-muted hover:text-foreground">
        <Menu className="w-5 h-5" />
      </button>

      {/* Left: step info */}
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-base md:text-lg">{step.icon}</span>
        <span className="font-display font-bold text-foreground text-xs md:text-sm truncate">{step.label}</span>
        <span className="text-foreground-muted text-xs font-mono ml-1 hidden sm:inline">{completedSteps}/5 complete</span>
      </div>

      {/* Center: progress bar */}
      <div className="flex-1 max-w-xs md:max-w-md hidden sm:block">
        <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${progress}%`,
              background: "linear-gradient(90deg, hsl(168 47% 52%), hsl(210 60% 50%))",
            }}
          />
        </div>
      </div>

      {/* Mobile progress indicator */}
      <div className="flex-1 sm:hidden">
        <div className="h-1 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${progress}%`,
              background: "linear-gradient(90deg, hsl(168 47% 52%), hsl(210 60% 50%))",
            }}
          />
        </div>
      </div>

      {/* Right: filename chip + theme toggle */}
      <div className="flex items-center gap-2 md:gap-3 ml-auto flex-shrink-0">
        {state.uploadResult && (
          <div className="px-2 md:px-3 py-0.5 md:py-1 rounded-full border border-primary/30 text-primary text-[10px] md:text-xs font-mono hidden sm:block truncate max-w-[140px]">
            {state.uploadResult.filename}
          </div>
        )}
        <ThemeToggle />

        {/* Auth Section */}
        {currentUser ? (
          <div className="flex items-center gap-3 ml-2 border-l border-border pl-3">
            <div className="hidden sm:flex flex-col items-end">
              <span className="text-xs font-bold text-foreground truncate max-w-[120px]">{currentUser.email}</span>
            </div>
            <button 
              onClick={() => logout()}
              className="p-1.5 text-foreground-muted hover:text-danger hover:bg-danger/10 rounded-md transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 ml-2 border-l border-border pl-3">
            <Link to="/login" className="text-xs font-display font-bold text-foreground hover:text-primary transition-colors">
              Sign In
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
