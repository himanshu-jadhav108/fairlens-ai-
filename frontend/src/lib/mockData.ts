import type {
  UploadResult,
  AnalysisResult,
  ShapResult,
  AiExplanation,
  FixResult,
} from "@/context/AppContext";

export const mockUploadResult: UploadResult = {
  filename: "hiring_decisions.csv",
  rows: 4200,
  columns: [
    { name: "age", dtype: "int64" },
    { name: "gender", dtype: "object" },
    { name: "education_level", dtype: "object" },
    { name: "years_experience", dtype: "float64" },
    { name: "interview_score", dtype: "float64" },
    { name: "referral", dtype: "int64" },
    { name: "department", dtype: "object" },
    { name: "hired", dtype: "int64" },
  ],
  preview: [
    { age: 28, gender: "Male", education_level: "Masters", years_experience: 4.2, interview_score: 82, referral: 1, department: "Engineering", hired: 1 },
    { age: 34, gender: "Female", education_level: "PhD", years_experience: 7.1, interview_score: 91, referral: 0, department: "Engineering", hired: 0 },
    { age: 42, gender: "Male", education_level: "Bachelors", years_experience: 12.0, interview_score: 75, referral: 1, department: "Sales", hired: 1 },
    { age: 25, gender: "Female", education_level: "Masters", years_experience: 2.5, interview_score: 88, referral: 0, department: "Marketing", hired: 0 },
    { age: 38, gender: "Male", education_level: "Bachelors", years_experience: 9.3, interview_score: 70, referral: 0, department: "Engineering", hired: 1 },
  ],
};

export const mockTargetCol = "hired";
export const mockSensitiveCol = "gender";

export const mockAnalysisResult: AnalysisResult = {
  dpd: 0.23,
  eod: 0.18,
  accuracy: 0.847,
  group_stats: [
    { group: "Male", count: 2310, positive_rate: 0.64, accuracy: 0.88 },
    { group: "Female", count: 1890, positive_rate: 0.41, accuracy: 0.81 },
  ],
  model_info: {
    model_type: "RandomForestClassifier",
    features_used: 6,
    test_samples: 840,
    groups_found: 2,
  },
};

export const mockShapResult: ShapResult = {
  feature_importance: [
    { feature: "years_experience", importance: 0.32 },
    { feature: "interview_score", importance: 0.25 },
    { feature: "referral", importance: 0.18 },
    { feature: "education_level", importance: 0.12 },
    { feature: "age", importance: 0.08 },
    { feature: "department", importance: 0.05 },
  ],
  method: "TreeSHAP",
};

export const mockAiExplanation: AiExplanation = {
  explanation: `## Bias Analysis Summary

The model shows **significant demographic parity disparity** (DPD = 0.23) between Male and Female applicants in hiring decisions.

### Key Findings

1. **Hiring Rate Gap**: Male candidates are hired at a rate of **64%** compared to **41%** for Female candidates — a 23 percentage point gap that exceeds the commonly accepted threshold of 0.10.

2. **Feature Influence**: The SHAP analysis reveals that \`years_experience\` (0.32) and \`interview_score\` (0.25) are the top predictive features. However, the \`referral\` feature (0.18 importance) may act as a **proxy variable** for gender, since referral networks often reflect existing demographic imbalances.

3. **Equal Opportunity**: The EOD of 0.18 indicates that even among truly qualified candidates, the model's true positive rate differs substantially across groups — Female candidates who *should* be hired are more likely to be missed.

### Risk Assessment

This level of disparity poses **legal and ethical risks** under disparate impact doctrine (80% rule). The Female positive rate (41%) is only 64% of the Male rate, falling below the 80% threshold established by EEOC guidelines.

### Recommendations

- Apply **reweighing** or **threshold adjustment** to reduce DPD while preserving accuracy
- Audit the \`referral\` feature for proxy discrimination
- Consider removing or decorrelating features that encode protected information`,
  summary: {
    verdict: "Significant bias detected — immediate mitigation recommended",
    dpd_severity: "high",
    eod_severity: "medium",
  },
};

export const mockFixResult: FixResult = {
  original_metrics: {
    dpd: 0.23,
    eod: 0.18,
    accuracy: 0.847,
  },
  fixed_metrics: {
    dpd: 0.04,
    eod: 0.03,
    accuracy: 0.831,
  },
  comparison: {
    group_rates_before: { Male: 0.64, Female: 0.41 },
    group_rates_after: { Male: 0.55, Female: 0.51 },
  },
  strategy: "Reweighing + Threshold Optimization",
};
