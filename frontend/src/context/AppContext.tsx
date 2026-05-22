import React, { createContext, useContext, useReducer, type ReactNode } from "react";

export interface ColumnInfo {
  name: string;
  dtype: string;
}

export interface UploadResult {
  session_id: string;
  filename: string;
  rows: number;
  columns: ColumnInfo[];
  preview: Record<string, unknown>[];
}

export interface GroupStat {
  group: string;
  count: number;
  positive_rate: number;
  accuracy: number;
}

export interface ModelInfo {
  model_type: string;
  features_used: number;
  test_samples: number;
  groups_found: number;
}

export interface AnalysisResult {
  dpd: number;
  eod: number;
  accuracy: number;
  disparate_impact_ratio: number;
  fairness_score?: number;
  fairness_label?: string;
  group_stats: GroupStat[];
  model_info: ModelInfo;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface Disparity {
  feature: string;
  disparity: number;
}

export interface LocalExplanation {
  row_index_in_sample: number;
  prediction_probability: number;
  true_label: number | null;
  demographic_group: string;
  feature_contributions: { feature: string; value: number | string; shap_impact: number }[];
}

export interface ShapResult {
  method: string;
  global_importance: FeatureImportance[];
  demographic_analysis: {
    group_importance: Record<string, Record<string, number>>;
    top_disparities: Disparity[];
  };
  local_explanation: LocalExplanation;
}

export interface AiExplanation {
  explanation: string;
  summary: {
    verdict: string;
    dpd_severity: string;
    eod_severity: string;
  };
}

export interface FixMetrics {
  dpd: number;
  eod: number;
  accuracy: number;
  disparate_impact_ratio: number;
}

export interface FixResult {
  original_metrics: FixMetrics;
  fixed_metrics: FixMetrics;
  comparison: {
    group_rates_before: Record<string, number>;
    group_rates_after: Record<string, number>;
  };
  strategy: string;
}

export type StepId = "upload" | "analyze" | "explain" | "fix" | "compare";

export interface AppState {
  uploadResult: UploadResult | null;
  targetCol: string;
  sensitiveCol: string;
  analysisResult: AnalysisResult | null;
  shapResult: ShapResult | null;
  aiExplanation: AiExplanation | null;
  fixResult: FixResult | null;
  loading: Record<string, boolean>;
  errors: Record<string, string | null>;
  activeStep: StepId;
  sessionId: string | null;
}

const initialState: AppState = {
  uploadResult: null,
  targetCol: "",
  sensitiveCol: "",
  analysisResult: null,
  shapResult: null,
  aiExplanation: null,
  fixResult: null,
  loading: {},
  errors: {},
  activeStep: "upload",
  sessionId: null,
};

type Action =
  | { type: "SET_UPLOAD_RESULT"; payload: UploadResult | null }
  | { type: "SET_TARGET_COL"; payload: string }
  | { type: "SET_SENSITIVE_COL"; payload: string }
  | { type: "SET_ANALYSIS_RESULT"; payload: AnalysisResult }
  | { type: "SET_SHAP_RESULT"; payload: ShapResult }
  | { type: "SET_AI_EXPLANATION"; payload: AiExplanation }
  | { type: "SET_FIX_RESULT"; payload: FixResult }
  | { type: "SET_LOADING"; payload: { key: string; value: boolean } }
  | { type: "SET_ERROR"; payload: { key: string; value: string | null } }
  | { type: "LOAD_DEMO"; payload: Omit<AppState, "loading" | "errors" | "activeStep"> }
  | { type: "HANDLE_SESSION_EXPIRED"; payload: string }
  | { type: "RESET" };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "SET_UPLOAD_RESULT":
      return { 
        ...state, 
        uploadResult: action.payload,
        sessionId: action.payload ? action.payload.session_id : null 
      };
    case "SET_TARGET_COL":
      return { ...state, targetCol: action.payload };
    case "SET_SENSITIVE_COL":
      return { ...state, sensitiveCol: action.payload };
    case "SET_ANALYSIS_RESULT":
      return { ...state, analysisResult: action.payload, activeStep: "analyze" };
    case "SET_SHAP_RESULT":
      return { ...state, shapResult: action.payload };
    case "SET_AI_EXPLANATION":
      return { ...state, aiExplanation: action.payload };
    case "SET_FIX_RESULT":
      return { ...state, fixResult: action.payload, activeStep: "compare" };
    case "SET_LOADING":
      return { ...state, loading: { ...state.loading, [action.payload.key]: action.payload.value } };
    case "SET_ERROR":
      return { ...state, errors: { ...state.errors, [action.payload.key]: action.payload.value } };
    case "SET_ACTIVE_STEP":
      return { ...state, activeStep: action.payload };
    case "LOAD_DEMO":
      return { ...state, ...action.payload, loading: {}, errors: {}, activeStep: "upload" };
    case "HANDLE_SESSION_EXPIRED":
      return {
        ...initialState,
        activeStep: "upload",
        errors: { upload: action.payload },
      };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<Action>;
}>({ state: initialState, dispatch: () => null });

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
