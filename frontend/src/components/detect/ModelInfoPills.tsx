import type { ModelInfo } from "@/context/AppContext";

interface ModelInfoPillsProps {
  info: ModelInfo;
}

export default function ModelInfoPills({ info }: ModelInfoPillsProps) {
  const pills = [
    { label: "Model", value: info.model_type },
    { label: "Features", value: String(info.features_used) },
    { label: "Test Samples", value: info.test_samples.toLocaleString() },
    { label: "Groups", value: String(info.groups_found) },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {pills.map(p => (
        <span
          key={p.label}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-border text-xs font-mono"
        >
          <span className="text-foreground-muted">{p.label}:</span>
          <span className="text-foreground-secondary">{p.value}</span>
        </span>
      ))}
    </div>
  );
}
