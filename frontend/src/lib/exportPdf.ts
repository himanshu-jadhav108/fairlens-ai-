import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { FixResult, AnalysisResult, ShapResult, AiExplanation } from "@/context/AppContext";

interface ExportData {
  analysisResult: AnalysisResult;
  fixResult: FixResult;
  shapResult: ShapResult | null;
  aiExplanation: AiExplanation | null;
  filename: string;
}

export function exportAuditPdf(data: ExportData) {
  const { analysisResult, fixResult, shapResult, aiExplanation, filename } = data;
  const doc = new jsPDF();
  const pageW = doc.internal.pageSize.getWidth();
  let y = 20;

  // Title
  doc.setFontSize(22);
  doc.setTextColor(40, 40, 40);
  doc.text("FairLens AI — Bias Audit Report", pageW / 2, y, { align: "center" });
  y += 10;
  doc.setFontSize(10);
  doc.setTextColor(120, 120, 120);
  doc.text(`Generated ${new Date().toLocaleDateString()} • Dataset: ${filename}`, pageW / 2, y, { align: "center" });
  y += 12;

  // Divider
  doc.setDrawColor(200);
  doc.line(14, y, pageW - 14, y);
  y += 10;

  // Section: Model Info
  doc.setFontSize(14);
  doc.setTextColor(40, 40, 40);
  doc.text("1. Model Information", 14, y);
  y += 8;
  const mi = analysisResult.model_info;
  autoTable(doc, {
    startY: y,
    head: [["Property", "Value"]],
    body: [
      ["Model Type", mi.model_type],
      ["Features Used", String(mi.features_used)],
      ["Test Samples", String(mi.test_samples)],
      ["Groups Found", String(mi.groups_found)],
    ],
    theme: "grid",
    headStyles: { fillColor: [63, 181, 160] },
    margin: { left: 14, right: 14 },
  });
  y = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 12;

  // Section: Bias Detection
  doc.setFontSize(14);
  doc.text("2. Bias Detection Results", 14, y);
  y += 8;
  const before = fixResult.original_metrics;
  const after = fixResult.fixed_metrics;
  autoTable(doc, {
    startY: y,
    head: [["Metric", "Before", "After", "Change"]],
    body: [
      ["Demographic Parity (DPD)", before.dpd.toFixed(4), after.dpd.toFixed(4), `${(((before.dpd - after.dpd) / (before.dpd || 1)) * 100).toFixed(1)}%`],
      ["Equalized Odds (EOD)", before.eod.toFixed(4), after.eod.toFixed(4), `${(((before.eod - after.eod) / (before.eod || 1)) * 100).toFixed(1)}%`],
      ["Accuracy", before.accuracy.toFixed(4), after.accuracy.toFixed(4), `${(((after.accuracy - before.accuracy) / (before.accuracy || 1)) * 100).toFixed(1)}%`],
    ],
    theme: "grid",
    headStyles: { fillColor: [63, 181, 160] },
    margin: { left: 14, right: 14 },
  });
  y = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 12;

  // Section: Group Stats
  doc.setFontSize(14);
  doc.text("3. Group Statistics", 14, y);
  y += 8;
  autoTable(doc, {
    startY: y,
    head: [["Group", "Count", "Positive Rate", "Accuracy"]],
    body: analysisResult.group_stats.map(g => [
      g.group, String(g.count), `${(g.positive_rate * 100).toFixed(1)}%`, `${(g.accuracy * 100).toFixed(1)}%`,
    ]),
    theme: "grid",
    headStyles: { fillColor: [63, 181, 160] },
    margin: { left: 14, right: 14 },
  });
  y = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 12;

  // Section: Mitigation
  doc.setFontSize(14);
  doc.text(`4. Mitigation Strategy: ${fixResult.strategy}`, 14, y);
  y += 8;
  autoTable(doc, {
    startY: y,
    head: [["Group", "Rate Before", "Rate After"]],
    body: Object.keys(fixResult.comparison.group_rates_after).map(g => [
      g,
      `${((fixResult.comparison.group_rates_before[g] || 0) * 100).toFixed(1)}%`,
      `${((fixResult.comparison.group_rates_after[g] || 0) * 100).toFixed(1)}%`,
    ]),
    theme: "grid",
    headStyles: { fillColor: [63, 181, 160] },
    margin: { left: 14, right: 14 },
  });
  y = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 12;

  // Check for page break
  if (y > 240) {
    doc.addPage();
    y = 20;
  }

  // Feature Importance
  if (shapResult && shapResult.global_importance) {
    doc.setFontSize(14);
    doc.text("5. Feature Importance (SHAP)", 14, y);
    y += 8;
    autoTable(doc, {
      startY: y,
      head: [["Rank", "Feature", "Importance"]],
      body: shapResult.global_importance.slice(0, 10).map((f, i) => [
        String(i + 1), f.feature, f.importance.toFixed(4),
      ]),
      theme: "grid",
      headStyles: { fillColor: [63, 181, 160] },
      margin: { left: 14, right: 14 },
    });
    y = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 12;
  }

  // AI Verdict
  if (aiExplanation) {
    if (y > 240) {
      doc.addPage();
      y = 20;
    }
    doc.setFontSize(14);
    doc.text(`${shapResult ? "6" : "5"}. AI Verdict`, 14, y);
    y += 8;
    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    const verdict = aiExplanation.summary;
    doc.text(`Verdict: ${verdict.verdict}`, 14, y); y += 6;
    doc.text(`DPD Severity: ${verdict.dpd_severity}`, 14, y); y += 6;
    doc.text(`EOD Severity: ${verdict.eod_severity}`, 14, y); y += 10;
  }

  // Footer
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(150);
    doc.text(`FairLens AI Audit Report — Page ${i} of ${totalPages}`, pageW / 2, doc.internal.pageSize.getHeight() - 10, { align: "center" });
  }

  doc.save(`FairLens_Audit_${filename.replace(/\.[^.]+$/, "")}_${new Date().toISOString().slice(0, 10)}.pdf`);
}
