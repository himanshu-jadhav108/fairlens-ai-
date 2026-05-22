import type { ColumnInfo } from "@/context/AppContext";

interface ColumnChipsProps {
  columns: ColumnInfo[];
}

function isNumeric(dtype: string): boolean {
  return ["int64", "float64", "int32", "float32", "number", "int", "float"].some(t => dtype.toLowerCase().includes(t));
}

export default function ColumnChips({ columns }: ColumnChipsProps) {
  return (
    <div className="space-y-2">
      <p className="text-foreground-muted text-[10px] uppercase tracking-widest font-mono">Columns</p>
      <div className="flex flex-wrap gap-2">
        {columns.map((col) => {
          const numeric = isNumeric(col.dtype);
          return (
            <span
              key={col.name}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-secondary text-foreground-secondary text-[11px] font-mono"
            >
              <span className={numeric ? "text-primary font-medium" : "text-warning font-medium"}>
                {numeric ? "#" : "Aa"}
              </span>
              {col.name}
            </span>
          );
        })}
      </div>
    </div>
  );
}
