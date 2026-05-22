import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";

const ACCENT_COLORS = ["#63cab7", "#f0a500", "#a78bfa", "#60a5fa", "#f472b6", "#34d399"];

interface GroupBarChartProps {
  title: string;
  subtitle: string;
  data: { group: string; value: number }[];
  formatAsPercent?: boolean;
  colorOffset?: number;
}

export default function GroupBarChart({ title, subtitle, data, formatAsPercent, colorOffset = 0 }: GroupBarChartProps) {
  const avg = data.reduce((s, d) => s + d.value, 0) / data.length;

  return (
    <div className="card-border card-border-hover rounded-lg bg-background-surface p-5 transition-all duration-200">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="font-display font-bold text-foreground text-sm">{title}</h3>
        <span className="text-[10px] font-mono text-foreground-muted px-1.5 py-0.5 rounded bg-secondary">
          {data.length} groups
        </span>
      </div>
      <p className="text-foreground-muted text-xs mb-5">{subtitle}</p>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis
            dataKey="group"
            tick={{ fill: "#8a9ab5", fontSize: 11, fontFamily: "DM Mono" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#8a9ab5", fontSize: 11, fontFamily: "DM Mono" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => formatAsPercent ? `${(v * 100).toFixed(0)}%` : v.toFixed(2)}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0];
              return (
                <div className="bg-background-elevated border border-border rounded-md px-3 py-2 shadow-lg">
                  <p className="text-foreground text-xs font-mono font-medium">{d.payload.group}</p>
                  <p className="text-primary text-sm font-mono mt-0.5">
                    {formatAsPercent ? `${((d.value as number) * 100).toFixed(1)}%` : (d.value as number).toFixed(4)}
                  </p>
                </div>
              );
            }}
          />
          <ReferenceLine
            y={avg}
            stroke="#63cab7"
            strokeDasharray="4 4"
            strokeOpacity={0.6}
            label={{
              value: "avg",
              position: "right",
              fill: "#63cab7",
              fontSize: 10,
              fontFamily: "DM Mono",
            }}
          />
          <Bar dataKey="value" radius={[3, 3, 0, 0]} maxBarSize={48}>
            {data.map((_, i) => (
              <Cell key={i} fill={ACCENT_COLORS[(i + colorOffset) % ACCENT_COLORS.length]} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
