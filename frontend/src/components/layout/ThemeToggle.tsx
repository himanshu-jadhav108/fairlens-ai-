import { useState, useEffect } from "react";
import { Moon, Sun } from "lucide-react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    if (typeof window === "undefined") return true;
    const saved = localStorage.getItem("fairlens-theme");
    if (saved) return saved === "dark";
    return !document.documentElement.classList.contains("light");
  });

  useEffect(() => {
    const root = document.documentElement;
    // Use View Transitions API if available for smooth crossfade
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        root.classList.toggle("light", !dark);
      });
    } else {
      root.style.transition = "background-color 0.4s ease, color 0.4s ease";
      root.classList.toggle("light", !dark);
      setTimeout(() => { root.style.transition = ""; }, 500);
    }
    localStorage.setItem("fairlens-theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <button
      onClick={() => setDark((d) => !d)}
      className="p-1.5 rounded-md text-foreground-muted hover:text-foreground hover:bg-secondary transition-colors duration-200"
      aria-label="Toggle theme"
    >
      {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>
  );
}
