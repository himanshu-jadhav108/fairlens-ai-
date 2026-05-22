import type { ColumnInfo } from "@/context/AppContext";

interface DataPreviewTableProps {
  columns: ColumnInfo[];
  rows: Record<string, unknown>[];
}

export default function DataPreviewTable({ columns, rows }: DataPreviewTableProps) {
  const previewRows = rows.slice(0, 5);

  return (
    <div className="space-y-2">
      <p className="text-foreground-muted text-[10px] uppercase tracking-widest font-mono">Data Preview</p>
      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="bg-secondary/70 sticky top-0">
              {columns.map((col) => (
                <th key={col.name} className="text-left px-3 py-2 text-foreground-secondary font-medium whitespace-nowrap">
                  {col.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previewRows.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? "bg-transparent" : "bg-secondary/20"}>
                {columns.map((col) => (
                  <td key={col.name} className="px-3 py-2 text-foreground-secondary whitespace-nowrap">
                    {String(row[col.name] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
