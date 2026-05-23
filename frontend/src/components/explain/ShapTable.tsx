import type { FeatureImportance } from "@/context/AppContext";

const COLORS = [
  "hsl(168 47% 52%)", "hsl(38 90% 47%)", "hsl(270 60% 60%)",
  "hsl(210 70% 55%)", "hsl(145 63% 55%)", "hsl(0 100% 68%)",
  "hsl(50 80% 55%)", "hsl(190 70% 50%)",
];

interface Props {
  data: FeatureImportance[];
}

export default function ShapTable({ data }: Props) {
  const top8 = data.slice(0, 8);
  const maxVal = Math.max(...top8.map(d => d.importance));

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-2 px-3 text-foreground-muted font-mono text-xs">Rank</th>
            <th className="text-left py-2 px-3 text-foreground-muted font-mono text-xs">Feature</th>
            <th className="text-left py-2 px-3 text-foreground-muted font-mono text-xs">SHAP Importance</th>
            <th className="text-left py-2 px-3 text-foreground-muted font-mono text-xs">Relative</th>
          </tr>
        </thead>
        <tbody>
          {top8.map((f, i) => {
            const pct = maxVal > 0 ? (f.importance / maxVal) * 100 : 0;
            return (
              <tr key={f.feature} className="border-b border-border/50 hover:bg-background-elevated/50 transition-colors duration-200">
                <td className="py-2 px-3 font-mono text-foreground-muted">#{i + 1}</td>
                <td className="py-2 px-3 font-mono" style={{ color: COLORS[i % COLORS.length] }}>{f.feature}</td>
                <td className="py-2 px-3 font-mono text-foreground">{f.importance.toFixed(6)}</td>
                <td className="py-2 px-3">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 rounded-full bg-background-surface overflow-hidden max-w-[120px]">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }}
                      />
                    </div>
                    <span className="font-mono text-xs text-foreground-secondary">{pct.toFixed(0)}%</span>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
