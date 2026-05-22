import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  value: number;
  className?: string;
}

function getSeverity(value: number): { label: string; color: string } {
  if (value < 0.05) return { label: "Low Bias", color: "text-success bg-success/10 border-success/20" };
  if (value <= 0.15) return { label: "Moderate Bias", color: "text-warning bg-warning/10 border-warning/20" };
  return { label: "High Bias", color: "text-danger bg-danger/10 border-danger/20" };
}

export default function SeverityBadge({ value, className }: SeverityBadgeProps) {
  const { label, color } = getSeverity(value);
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono border", color, className)}>
      {label}
    </span>
  );
}

export { getSeverity };
