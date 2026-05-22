import SeverityBadge from "./SeverityBadge";

interface MetricCardProps {
  name: string;
  value: number;
  description: string;
  footnote?: string;
  isAccuracy?: boolean;
}

function getSeverityColor(value: number): string {
  if (value < 0.05) return "bg-success";
  if (value <= 0.15) return "bg-warning";
  return "bg-danger";
}

function getSeverityBorderClass(value: number): string {
  if (value < 0.05) return "severity-border-low";
  if (value <= 0.15) return "severity-border-moderate";
  return "severity-border-high";
}

function getValueColor(value: number): string {
  if (value < 0.05) return "text-success";
  if (value <= 0.15) return "text-warning";
  return "text-danger";
}

export default function MetricCard({ name, value, description, footnote, isAccuracy }: MetricCardProps) {
  const safeValue = typeof value === 'number' ? value : 0;
  const displayValue = isAccuracy ? `${(safeValue * 100).toFixed(1)}%` : safeValue.toFixed(4);
  const barWidth = isAccuracy ? safeValue * 100 : Math.min(safeValue / 0.3, 1) * 100;
  const severityVal = isAccuracy ? (1 - safeValue) : safeValue;

  return (
    <div className={`card-border card-border-hover rounded-lg bg-background-surface p-5 transition-all duration-200 ${getSeverityBorderClass(severityVal)}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-bold text-foreground text-sm">{name}</h3>
        {!isAccuracy && <SeverityBadge value={safeValue} />}
      </div>

      <p className={`font-mono text-[28px] font-medium mb-3 ${isAccuracy ? "text-primary" : getValueColor(safeValue)}`}>
        {displayValue}
      </p>

      <div className="h-1.5 bg-secondary rounded-full overflow-hidden mb-3">
        <div
          className={`h-full rounded-full transition-all duration-500 ${isAccuracy ? "bg-primary" : getSeverityColor(safeValue)}`}
          style={{ width: `${barWidth}%` }}
        />
      </div>

      <p className="text-foreground-secondary text-xs leading-relaxed">{description}</p>
      {footnote && (
        <p className="text-foreground-muted text-[11px] italic mt-2">{footnote}</p>
      )}
    </div>
  );
}
