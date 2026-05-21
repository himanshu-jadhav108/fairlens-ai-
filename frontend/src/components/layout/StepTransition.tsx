import { useEffect, useRef, useState, type ReactNode } from "react";
import { useApp, type StepId } from "@/context/AppContext";

const stepOrder: StepId[] = ["upload", "analyze", "explain", "fix", "compare"];

interface StepTransitionProps {
  stepId: StepId;
  children: ReactNode;
}

function StepTransition({ stepId, children }: StepTransitionProps) {
  const { state } = useApp();
  const [displayed, setDisplayed] = useState(false);
  const [direction, setDirection] = useState<"left" | "right">("right");
  const [phase, setPhase] = useState<"enter" | "idle" | "exit">("enter");
  const prevStep = useRef<StepId>(state.activeStep);

  const isActive = state.activeStep === stepId;

  useEffect(() => {
    if (isActive) {
      const prevIndex = stepOrder.indexOf(prevStep.current);
      const nextIndex = stepOrder.indexOf(stepId);
      setDirection(nextIndex >= prevIndex ? "right" : "left");
      setDisplayed(true);
      setPhase("enter");
      // Trigger enter animation on next frame
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setPhase("idle"));
      });
    } else if (displayed) {
      setPhase("exit");
      const timer = setTimeout(() => setDisplayed(false), 250);
      return () => clearTimeout(timer);
    }
    prevStep.current = state.activeStep;
  }, [isActive, stepId, displayed, state.activeStep]);

  if (!displayed) return null;

  const enterFrom = direction === "right" ? "translate-x-6" : "-translate-x-6";
  const exitTo = direction === "right" ? "-translate-x-6" : "translate-x-6";

  const className =
    phase === "enter"
      ? `opacity-0 ${enterFrom}`
      : phase === "exit"
        ? `opacity-0 ${exitTo} transition-all duration-250 ease-in`
        : "opacity-100 translate-x-0 transition-all duration-300 ease-out";

  return <div className={className}>{children}</div>;
}

export default StepTransition;
