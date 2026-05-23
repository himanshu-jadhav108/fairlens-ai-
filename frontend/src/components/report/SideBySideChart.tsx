import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

interface Props {
  before: { dpd: number; eod: number; accuracy: number };
  after: { dpd: number; eod: number; accuracy: number };
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
          {p.name}: {p.value.toFixed(4)}
        </p>
      ))}
    </div>
  );
};

export default function SideBySideChart({ before, after }: Props) {
  const data = [
    { metric: "DPD", before: before.dpd, after: after.dpd },
    { metric: "EOD", before: before.eod, after: after.eod },
    { metric: "Accuracy", before: before.accuracy, after: after.accuracy },
  ];

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 20% 15%)" vertical={false} />
        <XAxis
          dataKey="metric"
          tick={{ fill: "hsl(225 30% 93%)", fontSize: 12, fontFamily: "DM Mono" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "hsl(220 25% 63%)", fontSize: 11, fontFamily: "DM Mono" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={false} />
        <Legend wrapperStyle={{ fontSize: 11, fontFamily: "DM Mono", color: "hsl(220 25% 63%)" }} />
        <Bar dataKey="before" name="Before" fill="hsl(0 100% 68%)" fillOpacity={0.7} radius={[4, 4, 0, 0]} barSize={32} />
        <Bar dataKey="after" name="After" fill="hsl(145 63% 55%)" fillOpacity={0.8} radius={[4, 4, 0, 0]} barSize={32} />
      </BarChart>
    </ResponsiveContainer>
  );
}
