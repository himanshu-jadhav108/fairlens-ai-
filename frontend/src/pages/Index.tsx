import { AppProvider, useApp } from "@/context/AppContext";
import AppLayout from "@/components/layout/AppLayout";
import StepTransition from "@/components/layout/StepTransition";
import UploadSection from "@/components/upload/UploadSection";
import BiasMetricsDashboard from "@/components/detect/BiasMetricsDashboard";
import ExplainSection from "@/components/explain/ExplainSection";
import FixBiasSection from "@/components/fix/FixBiasSection";
import CompareResults from "@/components/report/CompareResults";

function StepRouter() {
  return (
    <div className="max-w-5xl mx-auto space-y-6 relative">
      <StepTransition stepId="upload"><UploadSection /></StepTransition>
      <StepTransition stepId="analyze"><BiasMetricsDashboard /></StepTransition>
      <StepTransition stepId="explain"><ExplainSection /></StepTransition>
      <StepTransition stepId="fix"><FixBiasSection /></StepTransition>
      <StepTransition stepId="compare"><CompareResults /></StepTransition>
    </div>
  );
}

export default function Index() {
  return (
    <AppProvider>
      <AppLayout>
        <StepRouter />
      </AppLayout>
    </AppProvider>
  );
}
