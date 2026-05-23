interface Props {
  value: number;
  label: string;
  size?: number;
  invert?: boolean; // true for DPD/EOD where lower = better
}

function getSeverityColor(value: number, invert: boolean) {
  const v = invert ? value : 1 - value;
  if (v < 0.05) return "hsl(145 63% 55%)";
  if (v < 0.15) return "hsl(38 90% 47%)";
  return "hsl(0 100% 68%)";
}

export default function SemicircleGauge({ value, label, size = 120, invert = false }: Props) {
  const radius = size * 0.38;
  const cx = size / 2;
  const cy = size * 0.55;
  const strokeWidth = size * 0.08;

  // Arc from 180° to 0° (left to right semicircle)
  const startAngle = Math.PI;
  const fairnessScore = invert ? Math.max(0, Math.min(1, 1 - value)) : Math.max(0, Math.min(1, value));
  const sweepAngle = fairnessScore * Math.PI;

  const bgX1 = cx + radius * Math.cos(startAngle);
  const bgY1 = cy - radius * Math.sin(startAngle);
  const bgX2 = cx + radius * Math.cos(0);
  const bgY2 = cy - radius * Math.sin(0);

  const endAngle = startAngle - sweepAngle;
  const fillX2 = cx + radius * Math.cos(endAngle);
  const fillY2 = cy - radius * Math.sin(endAngle);
  const largeArc = sweepAngle > Math.PI ? 1 : 0;

  const color = getSeverityColor(value, invert);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc */}
        <path
          d={`M ${bgX1} ${bgY1} A ${radius} ${radius} 0 1 1 ${bgX2} ${bgY2}`}
          fill="none"
          stroke="hsl(220 20% 15%)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Fill arc */}
        {sweepAngle > 0.01 && (
          <path
            d={`M ${bgX1} ${bgY1} A ${radius} ${radius} 0 ${largeArc} 1 ${fillX2} ${fillY2}`}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
          />
        )}
      </svg>
      <p className="font-mono text-lg font-medium -mt-1" style={{ color }}>{value.toFixed(4)}</p>
      <p className="text-foreground-muted text-[10px] font-mono mt-0.5">{label}</p>
    </div>
  );
}
