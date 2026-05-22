interface Props {
  label: string;
  desc: string;
  before: number;
  after: number;
  lowerIsBetter: boolean;
}

export default function MetricDeltaRow({ label, desc, before, after, lowerIsBetter }: Props) {
  const safeBefore = (typeof before === 'number' && !isNaN(before)) ? before : 0;
  const safeAfter = (typeof after === 'number' && !isNaN(after)) ? after : 0;
  const diff = safeAfter - safeBefore;
  const improved = lowerIsBetter ? diff < 0 : diff > 0;
  const pctChange = safeBefore !== 0 ? Math.abs((diff / safeBefore) * 100) : 0;

  const displayBefore = Number(safeBefore).toFixed(4);
  const displayAfter = Number(safeAfter).toFixed(4);
  const displayPct = Number(pctChange).toFixed(1);

  return (
    <div className="grid grid-cols-3 gap-4 py-5 items-center">
      {/* Before */}
      <div className="text-center">
        <p className="font-mono text-2xl text-danger font-medium">{displayBefore}</p>
        <p className="text-foreground-muted text-[10px] font-mono mt-1">Before</p>
      </div>

      {/* Center label + pill */}
      <div className="text-center">
        <p className="font-display text-xs text-foreground-secondary font-bold mb-2">{label}</p>
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-mono ${
          improved ? "bg-success/15 text-success" : "bg-danger/15 text-danger"
        }`}>
          {improved ? "↓" : "↑"} {improved ? "Improved" : "Regressed"} {displayPct}%
        </span>
        <p className="text-foreground-muted text-[10px] font-mono mt-2">{desc}</p>
      </div>

      {/* After */}
      <div className="text-center">
        <p className="font-mono text-2xl text-success font-medium">{displayAfter}</p>
        <p className="text-foreground-muted text-[10px] font-mono mt-1">After</p>
      </div>
    </div>
  );
}

