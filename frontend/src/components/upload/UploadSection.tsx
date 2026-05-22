import { useCallback, useRef, useState } from "react";
import { useApp } from "@/context/AppContext";
import { uploadFile, analyzeData, checkHealth, getErrorMessage } from "@/lib/api";
import ScanLineLoader from "@/components/shared/ScanLineLoader";
import ErrorAlert from "@/components/shared/ErrorAlert";
import StaggerItem from "@/components/shared/StaggerItem";
import ColumnChips from "./ColumnChips";
import DataPreviewTable from "./DataPreviewTable";
import ConfigureAnalysis from "./ConfigureAnalysis";
import { X } from "lucide-react";

export default function UploadSection() {
  const { state, dispatch } = useApp();
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      dispatch({ type: "SET_ERROR", payload: { key: "upload", value: "Only .csv files are supported" } });
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      dispatch({ type: "SET_ERROR", payload: { key: "upload", value: "File must be under 10MB" } });
      return;
    }

    dispatch({ type: "SET_LOADING", payload: { key: "upload", value: true } });
    dispatch({ type: "SET_ERROR", payload: { key: "upload", value: null } });

    try {
      const isHealthy = await checkHealth();
      if (!isHealthy) {
        throw new Error("Backend server is unreachable. Please ensure the backend is running on port 8000.");
      }

      const result = await uploadFile(file);
      dispatch({ type: "SET_UPLOAD_RESULT", payload: result });
    } catch (err) {
      const msg = getErrorMessage(err);
      dispatch({ type: "SET_ERROR", payload: { key: "upload", value: msg } });
    } finally {
      dispatch({ type: "SET_LOADING", payload: { key: "upload", value: false } });
    }
  }, [dispatch]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleRemove = () => {
    dispatch({ type: "SET_UPLOAD_RESULT", payload: null });
    dispatch({ type: "SET_TARGET_COL", payload: "" });
    dispatch({ type: "SET_SENSITIVE_COL", payload: "" });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleAnalyze = async () => {
    dispatch({ type: "SET_LOADING", payload: { key: "analyze", value: true } });
    dispatch({ type: "SET_ERROR", payload: { key: "analyze", value: null } });
    try {
      if (!state.sessionId) throw new Error("No session active. Please upload a file again.");
      const result = await analyzeData(state.sessionId, state.targetCol, state.sensitiveCol);
      dispatch({ type: "SET_ANALYSIS_RESULT", payload: result });
    } catch (err) {
      const msg = getErrorMessage(err);
      if (msg.includes("SESSION_EXPIRED")) {
        dispatch({ type: "HANDLE_SESSION_EXPIRED", payload: "Your session has expired or the backend was restarted. Please re-upload your data." });
      } else {
        dispatch({ type: "SET_ERROR", payload: { key: "analyze", value: msg } });
      }
    } finally {
      dispatch({ type: "SET_LOADING", payload: { key: "analyze", value: false } });
    }
  };

  const isUploading = state.loading.upload;
  const uploaded = state.uploadResult !== null;

  return (
    <div className="space-y-6">
      {/* Card 1 — File Upload */}
      <StaggerItem index={0}>
        <div className="card-border card-border-hover rounded-lg bg-background-surface p-4 sm:p-6 transition-all duration-200">
          <div className="flex items-center gap-3 mb-1">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded bg-primary/10 text-primary text-[10px] font-mono font-medium">01</span>
            <h2 className="font-display font-bold text-foreground text-base">Upload Dataset</h2>
          </div>
          <p className="text-foreground-secondary text-xs mb-5 ml-9">Upload a CSV file to begin bias analysis</p>

          {state.errors.upload && (
            <div className="mb-4">
              <ErrorAlert message={state.errors.upload} onDismiss={() => dispatch({ type: "SET_ERROR", payload: { key: "upload", value: null } })} />
            </div>
          )}

          {/* Upload zone */}
          {!uploaded && !isUploading && (
            <>
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`min-h-[200px] border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-3 cursor-pointer transition-all duration-200
                ${dragOver ? "border-primary bg-primary/5" : "border-foreground-muted/30 hover:border-foreground-muted/50"}
              `}
            >
              <span className="text-4xl">📂</span>
              <p className="font-display font-bold text-foreground text-sm">Drag & drop your CSV file</p>
              <p className="text-foreground-secondary text-xs">or click to browse — only .csv supported</p>
              <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-secondary text-foreground-muted text-[10px] font-mono">Max 10MB</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />
            </div>
            
            <div className="mt-4 flex items-center justify-center">
              <button
                onClick={async () => {
                  dispatch({ type: "SET_LOADING", payload: { key: "upload", value: true } });
                  dispatch({ type: "SET_ERROR", payload: { key: "upload", value: null } });
                  try {
                    const { loadDemoData, checkHealth } = await import("@/lib/api");
                    const isHealthy = await checkHealth();
                    if (!isHealthy) throw new Error("Backend not reachable. Ensure it's running on port 8000.");
                    
                    const result = await loadDemoData();
                    dispatch({ type: "SET_UPLOAD_RESULT", payload: result });
                    dispatch({ type: "SET_TARGET_COL", payload: "Hired" });
                    dispatch({ type: "SET_SENSITIVE_COL", payload: "Gender" });
                  } catch (err) {
                    dispatch({ type: "SET_ERROR", payload: { key: "upload", value: err.message || "Failed to load demo data" } });
                  } finally {
                    dispatch({ type: "SET_LOADING", payload: { key: "upload", value: false } });
                  }
                }}
                className="text-xs font-display text-primary hover:text-primary/80 transition-colors underline cursor-pointer"
              >
                No dataset? Click here to load Demo Data instantly.
              </button>
            </div>
          </>
          )}

          {/* Loading state */}
          {isUploading && (
            <div className="min-h-[200px] border-2 border-dashed border-primary/30 rounded-lg flex items-center justify-center p-8">
              <ScanLineLoader text="Parsing CSV…" />
            </div>
          )}

          {/* Success state */}
          {uploaded && !isUploading && (
            <div className="space-y-5">
              <StaggerItem index={1} delay={100}>
                <div className="relative p-4 rounded-lg bg-secondary/50 border border-primary/20">
                  <button
                    onClick={handleRemove}
                    className="absolute top-3 right-3 text-foreground-muted hover:text-foreground transition-colors cursor-pointer"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">✅</span>
                    <div>
                      <p className="font-mono text-foreground text-sm font-medium">{state.uploadResult!.filename}</p>
                      <p className="text-foreground-secondary text-xs mt-0.5">
                        {state.uploadResult!.rows.toLocaleString()} rows · {state.uploadResult!.columns.length} columns
                      </p>
                    </div>
                  </div>
                </div>
              </StaggerItem>

              <StaggerItem index={2} delay={100}>
                <ColumnChips columns={state.uploadResult!.columns} />
              </StaggerItem>

              <StaggerItem index={3} delay={100}>
                <DataPreviewTable columns={state.uploadResult!.columns} rows={state.uploadResult!.preview} />
              </StaggerItem>

              <StaggerItem index={4} delay={100}>
                <div className="flex items-start gap-2 p-3 rounded-md bg-primary/5 border border-primary/10">
                  <span className="text-sm mt-0.5">💡</span>
                  <p className="text-foreground-secondary text-xs">
                    No dataset? Use <span className="font-mono text-primary">backend/sample_data.csv</span> — a hiring bias dataset
                  </p>
                </div>
              </StaggerItem>
            </div>
          )}
        </div>
      </StaggerItem>

      {/* Card 2 — Configure Analysis */}
      {uploaded && (
        <StaggerItem index={5} delay={100}>
          <ConfigureAnalysis
            columns={state.uploadResult!.columns}
            targetCol={state.targetCol}
            sensitiveCol={state.sensitiveCol}
            onTargetChange={(v) => dispatch({ type: "SET_TARGET_COL", payload: v })}
            onSensitiveChange={(v) => dispatch({ type: "SET_SENSITIVE_COL", payload: v })}
            onAnalyze={handleAnalyze}
            loading={!!state.loading.analyze}
            error={state.errors.analyze || null}
            onDismissError={() => dispatch({ type: "SET_ERROR", payload: { key: "analyze", value: null } })}
          />
        </StaggerItem>
      )}
    </div>
  );
}
