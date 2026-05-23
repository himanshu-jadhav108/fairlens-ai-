import { LocalExplanation } from "@/context/AppContext";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function LocalExplanationCard({ data }: { data: LocalExplanation }) {
  const isApproved = data.prediction_probability >= 0.5;
  const isFalseNegative = data.true_label === 1 && !isApproved;

  return (
    <Card className="border-border bg-background-surface">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="font-display text-lg text-foreground flex items-center gap-2">
              Case Study: Profile #{data.row_index_in_sample}
            </CardTitle>
            <CardDescription className="font-mono mt-1 text-xs">
              Demographic Group: <span className="text-foreground font-bold">{data.demographic_group}</span>
            </CardDescription>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge variant={isApproved ? "default" : "destructive"}>
              {isApproved ? "Approved" : "Rejected"} ({(data.prediction_probability * 100).toFixed(1)}%)
            </Badge>
            {isFalseNegative && (
              <Badge variant="outline" className="text-warning border-warning/50">
                ⚠️ False Negative
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-border mt-4">
          <Table>
            <TableHeader className="bg-background-elevated">
              <TableRow>
                <TableHead className="font-display">Feature</TableHead>
                <TableHead className="font-display">Value</TableHead>
                <TableHead className="font-display text-right">SHAP Impact</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.feature_contributions.map((feat, idx) => {
                const impactClass = feat.shap_impact > 0 ? "text-success" : "text-danger";
                const impactSign = feat.shap_impact > 0 ? "+" : "";
                return (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-xs">{feat.feature}</TableCell>
                    <TableCell className="font-mono text-xs text-foreground-muted">
                      {typeof feat.value === 'number' && feat.value % 1 !== 0 
                        ? feat.value.toFixed(4) 
                        : feat.value}
                    </TableCell>
                    <TableCell className={`font-mono text-xs text-right font-bold ${impactClass}`}>
                      {impactSign}{feat.shap_impact.toFixed(6)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
        <p className="text-xs text-foreground-muted mt-4">
          <strong className="text-foreground">Interpretation:</strong> Positive SHAP values pushed this individual towards approval. Negative SHAP values dragged their probability down. If this is a False Negative, look at the largest negative values to see exactly *why* the model unfairly rejected them.
        </p>
      </CardContent>
    </Card>
  );
}
