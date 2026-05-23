import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Legend, Tooltip,
} from "recharts";

interface Props {
  before: { dpd: number; eod: number; accuracy: number };
  after: { dpd: number; eod: number; accuracy: number };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-background-elevated border border-border-subtle rounded px-3 py-2">
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((p: any) => (
        <p key={p.dataKey} className="font-mono text-xs" style={{ color: p.color }}>
          {p.name}: {p.value.toFixed(4)}
        </p>
      ))}
    </div>
  );
};

export default function FairnessRadar({ before, after }: Props) {
  const data = [
    { axis: "Accuracy", before: before.accuracy, after: after.accuracy },
    { axis: "DPD Fairness", before: 1 - before.dpd, after: 1 - after.dpd },
    { axis: "EOD Fairness", before: 1 - before.eod, after: 1 - after.eod },
  ];

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data}>
        <PolarGrid stroke="hsl(220 20% 15%)" />
        <PolarAngleAxis
          dataKey="axis"
          tick={{ fill: "hsl(225 30% 93%)", fontSize: 11, fontFamily: "DM Mono" }}
        />
        <PolarRadiusAxis
          domain={[0, 1]}
          tick={{ fill: "hsl(220 25% 63%)", fontSize: 9, fontFamily: "DM Mono" }}
          axisLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Radar name="Before" dataKey="before" stroke="hsl(0 100% 68%)" fill="hsl(0 100% 68%)" fillOpacity={0.15} strokeWidth={2} />
        <Radar name="After" dataKey="after" stroke="hsl(145 63% 55%)" fill="hsl(145 63% 55%)" fillOpacity={0.2} strokeWidth={2} />
        <Legend wrapperStyle={{ fontSize: 11, fontFamily: "DM Mono", color: "hsl(220 25% 63%)" }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
