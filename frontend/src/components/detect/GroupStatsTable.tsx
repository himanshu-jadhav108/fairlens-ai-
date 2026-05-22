import type { GroupStat } from "@/context/AppContext";
import SeverityBadge from "@/components/shared/SeverityBadge";

interface GroupStatsTableProps {
  stats: GroupStat[];
}

export default function GroupStatsTable({ stats }: GroupStatsTableProps) {
  const avgRate = stats.reduce((s, g) => s + g.positive_rate, 0) / stats.length;

  return (
    <div className="card-border card-border-hover rounded-lg bg-background-surface p-5 transition-all duration-200">
      <h3 className="font-display font-bold text-foreground text-sm mb-4">Group Statistics</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-foreground-muted font-medium">Group</th>
              <th className="text-right py-2 px-3 text-foreground-muted font-medium">Sample Count</th>
              <th className="text-right py-2 px-3 text-foreground-muted font-medium">Positive Rate</th>
              <th className="text-right py-2 px-3 text-foreground-muted font-medium">Accuracy</th>
              <th className="text-right py-2 px-3 text-foreground-muted font-medium">Bias Risk</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((g) => {
              const deviation = Math.abs(g.positive_rate - avgRate);
              return (
                <tr key={g.group} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                  <td className="py-2.5 px-3 text-primary font-medium">{g.group}</td>
                  <td className="py-2.5 px-3 text-foreground-secondary text-right">{g.count.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-foreground-secondary text-right">{(g.positive_rate * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-foreground-secondary text-right">{(g.accuracy * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-right">
                    <SeverityBadge value={deviation} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
