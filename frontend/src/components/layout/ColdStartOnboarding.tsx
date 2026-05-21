import { useState, useEffect } from "react";
import { checkHealth } from "@/lib/api";
import { Server, Activity, BarChart, ShieldCheck } from "lucide-react";

export default function ColdStartOnboarding() {
  const [isReady, setIsReady] = useState(false);
  const [showSplash, setShowSplash] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Server is waking up...",
      desc: "We use serverless architecture to keep FairLens AI free. It might take up to 50 seconds to boot the ML engine. While you wait, here is how it works:",
      icon: <Server className="w-12 h-12 text-primary mx-auto animate-pulse" />
    },
    {
      title: "Step 1: Upload Data",
      desc: "Drop your tabular CSV dataset containing sensitive attributes like race, gender, or age, along with the decision column (target).",
      icon: <Activity className="w-12 h-12 text-blue-400 mx-auto" />
    },
    {
      title: "Step 2: Detect Bias",
      desc: "Our engine scans for disparate impact and inequality using advanced fairness metrics like Demographic Parity and Equalized Odds.",
      icon: <BarChart className="w-12 h-12 text-orange-400 mx-auto" />
    },
    {
      title: "Step 3: Fix & Mitigate",
      desc: "Apply enterprise-grade mitigation strategies (Pre-processing, In-processing, Post-processing) to algorithmically fix the bias and download the fair dataset.",
      icon: <ShieldCheck className="w-12 h-12 text-success mx-auto" />
    }
  ];

  useEffect(() => {
    let isMounted = true;
    
    // Check health immediately
    checkHealth().then((healthy) => {
      if (healthy && isMounted) {
        setIsReady(true);
      } else {
        // If not healthy immediately, we might be in cold start.
        // Try again every 5 seconds until healthy.
        const interval = setInterval(async () => {
          const ok = await checkHealth();
          if (ok && isMounted) {
            setIsReady(true);
            clearInterval(interval);
          }
        }, 5000);
      }
    });

    // If not ready after 1 second, show the splash screen to avoid flashing it for fast loads
    const splashTimer = setTimeout(() => {
      if (isMounted && !isReady) setShowSplash(true);
    }, 1000);

    // Rotate steps every 8 seconds
    const rotateTimer = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 8000);

    return () => {
      isMounted = false;
      clearTimeout(splashTimer);
      clearInterval(rotateTimer);
    };
  }, [isReady, steps.length]);

  if (isReady || !showSplash) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-md p-4">
      <div className="max-w-md w-full bg-background-surface border border-border p-8 rounded-2xl shadow-2xl text-center relative overflow-hidden">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/5 animate-pulse opacity-50" />
        
        <div className="relative z-10">
          <div className="mb-6 flex justify-center h-16 items-center transition-all duration-500">
            {steps[currentStep].icon}
          </div>
          
          <h2 className="text-xl font-display font-bold text-foreground mb-3 transition-opacity duration-500">
            {steps[currentStep].title}
          </h2>
          
          <p className="text-sm text-foreground-secondary leading-relaxed transition-opacity duration-500 h-20">
            {steps[currentStep].desc}
          </p>

          <div className="flex justify-center gap-2 mt-6">
            {steps.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentStep(i)}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  currentStep === i ? "bg-primary w-6" : "bg-border-hover"
                }`}
              />
            ))}
          </div>

          <div className="mt-8 flex justify-center items-center gap-2 text-xs font-mono text-primary/70 animate-pulse">
            <span className="w-4 h-4 border-2 border-primary/50 border-t-primary rounded-full animate-spin" />
            Waking up server...
          </div>
        </div>
      </div>
    </div>
  );
}
