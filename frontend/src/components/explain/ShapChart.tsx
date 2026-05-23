import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import type { FeatureImportance } from "@/context/AppContext";

const COLORS = [
  "hsl(168 47% 52%)", "hsl(38 90% 47%)", "hsl(270 60% 60%)",
  "hsl(210 70% 55%)", "hsl(145 63% 55%)", "hsl(0 100% 68%)",
  "hsl(50 80% 55%)", "hsl(190 70% 50%)", "hsl(330 60% 55%)",
  "hsl(120 50% 50%)", "hsl(20 80% 55%)", "hsl(250 50% 60%)",
];

function truncate(s: string, n = 18) {
  return s.length > n ? s.slice(0, n) + "…" : s;
}

interface Props {
  data: FeatureImportance[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as FeatureImportance;
  return (
    <div className="bg-background-elevated border border-border-subtle rounded px-3 py-2">
      <p className="font-display text-xs text-foreground mb-1">{d.feature}</p>
      <p className="font-mono text-sm text-primary">{d.importance.toFixed(6)}</p>
    </div>
  );
};

export default function ShapChart({ data }: Props) {
  const top12 = data.slice(0, 12);
  const maxVal = Math.max(...top12.map(d => d.importance));

  return (
    <ResponsiveContainer width="100%" height={top12.length * 36 + 40}>
      <BarChart data={top12} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 20% 15%)" horizontal={false} />
        <XAxis type="number" tick={{ fill: "hsl(220 25% 63%)", fontSize: 11, fontFamily: "DM Mono" }} axisLine={false} tickLine={false} />
        <YAxis
          type="category"
          dataKey="feature"
          tick={{ fill: "hsl(225 30% 93%)", fontSize: 11, fontFamily: "DM Mono" }}
          tickFormatter={(v: string) => truncate(v)}
          width={140}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={false} />
        <Bar dataKey="importance" radius={[0, 4, 4, 0]} barSize={20}>
          {top12.map((entry, i) => {
            const opacity = 0.4 + 0.6 * (entry.importance / maxVal);
            return <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={opacity} />;
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
