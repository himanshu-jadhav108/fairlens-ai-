import axios from "axios";
import { auth } from "./firebase";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60s timeout for long-running SHAP tasks
});

api.interceptors.request.use(async (config) => {
  if (auth.currentUser) {
    const token = await auth.currentUser.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Handle API errors consistently.
 */
export const getErrorMessage = (err: unknown): string => {
  const error = err as import("axios").AxiosError;
  if (error.response) {
    return err.response.data?.detail || `Server error (${err.response.status})`;
  } else if (err.request) {
    return "No response from server. Is the backend running?";
  } else {
    return err.message || "An unexpected error occurred";
  }
};

/**
 * Check if the backend is reachable.
 */
export const checkHealth = async () => {
  try {
    const response = await api.get("/health");
    return response.status === 200;
  } catch (err) {
    return false;
  }
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toAnalysisResult = (payload: any) => {
  const metrics = payload?.metrics || {};
  const modelInfo = payload?.model_info || {};
  const groups = metrics?.group_stats || [];

  return {
    dpd: Number(metrics?.demographic_parity_difference || 0),
    eod: Number(metrics?.equalized_odds_difference || 0),
    accuracy: Number(metrics?.accuracy || 0),
    disparate_impact_ratio: Number(metrics?.disparate_impact_ratio || 1),
    fairness_score: metrics?.fairness_score,
    fairness_label: metrics?.fairness_label,
    group_stats: groups,
    model_info: {
      model_type: modelInfo?.type || "Logistic Regression",
      features_used: Number(modelInfo?.features_used || 0),
      test_samples: Number(modelInfo?.test_samples || 0),
      groups_found: groups.length,
    },
  };
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toAiExplanation = (payload: any) => ({
  explanation: payload?.explanation || "No explanation available.",
  summary: {
    verdict: payload?.summary?.verdict || "unknown",
    dpd_severity: payload?.summary?.dpd_severity || "unknown",
    eod_severity: payload?.summary?.eod_severity || "unknown",
  },
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toFixResult = (payload: any) => {
  const before = payload?.original_metrics || {};
  const after = payload?.fixed_metrics || {};

  const beforeGroups = before?.group_stats || [];
  const afterGroups = after?.group_stats || [];

   
  const group_rates_before = Object.fromEntries(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    beforeGroups.map((g: any) => [String(g.group), Number(g.positive_rate || 0)])
  );
   
  const group_rates_after = Object.fromEntries(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    afterGroups.map((g: any) => [String(g.group), Number(g.positive_rate || 0)])
  );

  return {
    strategy: payload?.strategy || "Reweighting + Drop Sensitive Feature",
    original_metrics: {
      dpd: Number(before?.demographic_parity_difference || 0),
      eod: Number(before?.equalized_odds_difference || 0),
      accuracy: Number(before?.accuracy || 0),
      disparate_impact_ratio: Number(before?.disparate_impact_ratio || 1),
    },
    fixed_metrics: {
      dpd: Number(after?.demographic_parity_difference || 0),
      eod: Number(after?.equalized_odds_difference || 0),
      accuracy: Number(after?.accuracy || 0),
      disparate_impact_ratio: Number(after?.disparate_impact_ratio || 1),
    },
    comparison: {
      group_rates_before,
      group_rates_after,
    },
  };
};

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const loadDemoData = async () => {
  const response = await api.post("/api/demo");
  return response.data;
};

export const analyzeData = async (sessionId: string, targetCol: string, sensitiveCol: string) => {
  const response = await api.post("/api/analyze", {
    session_id: sessionId,
    target_col: targetCol,
    sensitive_col: sensitiveCol,
  });
  return toAnalysisResult(response.data);
};

export const explainShap = async (sessionId: string) => {
  const response = await api.post("/api/explain", { session_id: sessionId });
  return response.data;
};

export const aiExplain = async (sessionId: string) => {
  const response = await api.post("/api/ai-explain", { session_id: sessionId });
  return toAiExplanation(response.data);
};

export const applyFix = async (sessionId: string) => {
  const response = await api.post("/api/fix", { session_id: sessionId });
  return toFixResult(response.data);
};

export const fetchHistory = async () => {
  const response = await api.get("/api/history");
  return response.data;
};

export default api;
