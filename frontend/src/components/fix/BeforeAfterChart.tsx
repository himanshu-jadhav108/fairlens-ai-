import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

interface Props {
  before: Record<string, number>;
  after: Record<string, number>;
  sensitiveCol: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-background-elevated border border-border-subtle rounded px-3 py-2">
      <p className="font-display text-xs text-foreground mb-1">{label}</p>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((p: any) => (
        <p key={p.dataKey} className="font-mono text-xs" style={{ color: p.color }}>
          {p.name}: {(p.value * 100).toFixed(1)}%
        </p>
      ))}
    </div>
  );
};

export default function BeforeAfterChart({ before, after, sensitiveCol }: Props) {
  const groups = Object.keys(before);
  const data = groups.map((g) => ({
    group: g,
    before: before[g],
    after: after[g],
  }));

  return (
    <div className="card-border rounded-lg bg-background-surface overflow-hidden">
      <div className="p-5 border-b border-border">
        <h2 className="font-display font-bold text-foreground text-lg">
          👥 Group Positive Rates: Before vs After
        </h2>
        <p className="text-foreground-muted text-xs font-mono mt-1">
          Bars closer in height = more equitable prediction rates across {sensitiveCol} groups
        </p>
      </div>
      <div className="p-5">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 20% 15%)" vertical={false} />
            <XAxis
              dataKey="group"
              tick={{ fill: "hsl(225 30% 93%)", fontSize: 12, fontFamily: "DM Mono" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "hsl(220 25% 63%)", fontSize: 11, fontFamily: "DM Mono" }}
              tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={false} />
            <Legend
              wrapperStyle={{ fontSize: 11, fontFamily: "DM Mono", color: "hsl(220 25% 63%)" }}
            />
            <Bar dataKey="before" name="Before Fix" fill="hsl(0 100% 68%)" fillOpacity={0.7} radius={[4, 4, 0, 0]} barSize={28} />
            <Bar dataKey="after" name="After Fix" fill="hsl(145 63% 55%)" fillOpacity={0.8} radius={[4, 4, 0, 0]} barSize={28} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
