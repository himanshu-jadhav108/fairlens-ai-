import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHistory } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { ArrowLeft, History as HistoryIcon } from "lucide-react";

export default function HistoryPage() {
  const { currentUser } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentUser) {
      setLoading(false);
      return;
    }

    fetchHistory()
      .then((data) => {
        setHistory(data.history || []);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch history");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [currentUser]);

  if (!currentUser) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-6 bg-background text-center">
        <HistoryIcon className="w-16 h-16 text-foreground-muted mb-4" />
        <h1 className="text-2xl font-display font-bold text-foreground">Sign in required</h1>
        <p className="text-foreground-secondary mt-2 mb-6">You must be signed in to view your session history.</p>
        <Link to="/login" className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-bold transition-opacity hover:opacity-90">Sign In</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center gap-4 border-b border-border pb-4">
          <Link to="/" className="p-2 hover:bg-background-elevated rounded-full transition-colors text-foreground-muted hover:text-foreground">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-display font-bold text-foreground">My Audits</h1>
            <p className="text-xs font-mono text-foreground-muted mt-1">View your past FairLens AI sessions</p>
          </div>
        </div>

        {loading ? (
          <div className="animate-pulse flex flex-col gap-4">
            {[1, 2, 3].map(i => <div key={i} className="h-24 bg-background-surface rounded-xl border border-border" />)}
          </div>
        ) : error ? (
          <div className="bg-danger/10 border border-danger/20 text-danger p-4 rounded-xl">
            {error}
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-20 bg-background-surface border border-border border-dashed rounded-xl">
            <p className="text-foreground-secondary">No audits found.</p>
            <Link to="/" className="inline-block mt-4 text-primary font-bold hover:underline">Start a new audit</Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {history.map((session) => (
              <div key={session.session_id} className="bg-background-surface border border-border p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-primary/40 transition-colors">
                <div>
                  <h3 className="font-bold text-foreground font-display text-lg">{session.dataset?.filename || "Unknown Dataset"}</h3>
                  <div className="flex gap-3 text-xs font-mono text-foreground-muted mt-2">
                    <span>Rows: {session.dataset?.rows || 0}</span>
                    <span>Created: {new Date((session.created_at || 0) * 1000).toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {session.analysis_summary?.verdict ? (
                    <span className="px-3 py-1 rounded-full text-[10px] font-mono bg-background-elevated text-foreground-secondary border border-border-subtle">
                      {session.analysis_summary.verdict}
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full text-[10px] font-mono bg-background-elevated text-foreground-muted border border-border-subtle opacity-50">Incomplete Audit</span>
                  )}
                  {session.fix_strategy && (
                    <span className="px-3 py-1 rounded-full text-[10px] font-mono bg-success/10 text-success border border-success/20">
                      Mitigated
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
