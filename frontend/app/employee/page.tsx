"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface User {
  id: number;
  email: string;
  name: string;
  department: string;
  role: string;
}

interface PredictionResult {
  id: number;
  employee_name: string;
  mood: string;
  work_hours: number;
  fatigue: number;
  experience: number;
  feedback: string;
  sentiment: string;
  sentiment_score: number;
  burnout_score: number;
  burnout_level: string;
  suggestions: string[];
  trend_insight: string;
  trend_arrow: string;
  patterns: {
    fatigue_increasing: boolean;
    work_hours_high: boolean;
    burnout_spike: boolean;
    negative_sentiment: boolean;
  };
  weekly_analysis: {
    current_day: string;
    week_number: number;
    trend: string;
    trend_message: string;
    pattern: string;
    days_analyzed: number;
    comparison: {
      current: number;
      average: number;
      difference: number;
    } | null;
  };
}

interface HistoryRecord {
  id: number;
  mood: string;
  work_hours: number;
  fatigue: number;
  burnout_score: number;
  burnout_level: string;
  weekly_trend: string;
  submission_date: string;
  created_at: string;
}

interface TrendData {
  trend: string;
  trend_arrow: string;
  percentage_change: number;
  insight: string;
  scores: number[];
  record_count: number;
}

function safeFormatDate(raw: string | undefined | null): string {
  if (!raw) return "—";
  try {
    const clean = raw.split("T")[0];
    if (!clean || clean === "Invalid Date") return "—";
    const d = new Date(clean + "T00:00:00");
    if (isNaN(d.getTime())) return raw.slice(0, 10);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return raw.slice(0, 10) || "—";
  }
}

function TrendArrowBadge({ trend, arrow }: { trend: string; arrow: string }) {
  const colorMap: Record<string, string> = {
    Increasing: "trend-arrow increasing",
    Decreasing: "trend-arrow decreasing",
    Stable: "trend-arrow stable",
    "No Data": "trend-arrow no-data",
  };
  return (
    <span className={colorMap[trend] || "trend-arrow no-data"} title={trend}>
      {arrow} {trend}
    </span>
  );
}

function MiniSparkline({ scores }: { scores: number[] }) {
  if (!scores || scores.length < 2) return null;
  const max = Math.max(...scores);
  const min = Math.min(...scores);
  const range = max - min || 1;
  const w = 80, h = 28, pad = 3;

  const points = scores
    .map((s, i) => {
      const x = pad + (i / (scores.length - 1)) * (w - pad * 2);
      const y = h - pad - ((s - min) / range) * (h - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const lastScore = scores[scores.length - 1];
  const firstScore = scores[0];
  const strokeColor = lastScore > firstScore ? "#ef4444" : lastScore < firstScore ? "#10b981" : "#6b7280";

  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.8"
        strokeLinejoin="round"
        strokeLinecap="round"
        points={points}
      />
    </svg>
  );
}

export default function EmployeeDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [activeTab, setActiveTab] = useState<"assess" | "history">("assess");

  const [formData, setFormData] = useState({
    mood: "Okay",
    work_hours: "8",
    fatigue: "5",
    experience: "2",
    feedback: "",
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    if (!token || !userData) { router.push("/login"); return; }
    const parsedUser = JSON.parse(userData);
    if (parsedUser.role !== "employee") { router.push("/login"); return; }
    setUser(parsedUser);
    fetchHistory(token);
    setLoading(false);
  }, [router]);

  const fetchHistory = async (token: string) => {
    try {
      const response = await fetch("/api/my-records", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        // New API returns {records, trend}; old API returns []
        if (Array.isArray(data)) {
          setHistory(data);
        } else {
          setHistory(data.records || []);
          setTrendData(data.trend || null);
        }
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          mood: formData.mood,
          work_hours: parseFloat(formData.work_hours),
          fatigue: parseInt(formData.fatigue),
          experience: parseFloat(formData.experience),
          feedback: formData.feedback,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to get prediction");
      }
      const data = await response.json();
      setResult(data);
      fetchHistory(token || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setFormData({ mood: "Okay", work_hours: "8", fatigue: "5", experience: "2", feedback: "" });
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <span className="spinner"></span>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <>
      <nav className="nav">
        <Link href="/employee" className="nav-logo">Burnout Detection</Link>
        <div className="nav-links">
          <span className="user-greeting">Welcome, {user?.name}</span>
          <button onClick={handleLogout} className="nav-link logout-btn">Logout</button>
        </div>
      </nav>

      <div className="container">
        <div className="dashboard-header fade-in">
          <h1 className="dashboard-title">
            Your <span className="accent">Wellness Dashboard</span>
          </h1>
          <p className="dashboard-subtitle">
            Track your burnout levels over time with AI-powered pattern analysis
          </p>
        </div>

        {/* Trend Insight Banner */}
        {trendData && trendData.trend !== "No Data" && (
          <div className={`trend-insight-banner trend-${trendData.trend.toLowerCase()}`}>
            <span className="trend-insight-arrow">{trendData.trend_arrow}</span>
            <span className="trend-insight-text">{trendData.insight}</span>
            {trendData.scores.length > 1 && (
              <div className="trend-sparkline">
                <MiniSparkline scores={trendData.scores} />
              </div>
            )}
          </div>
        )}

        <div className="dashboard-tabs">
          <button
            className={`dashboard-tab ${activeTab === "assess" ? "active" : ""}`}
            onClick={() => setActiveTab("assess")}
          >
            New Assessment
          </button>
          <button
            className={`dashboard-tab ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            My History ({history.length})
          </button>
        </div>

        {activeTab === "assess" && !result && (
          <div className="card-elevated form-card slide-up" style={{ maxWidth: "600px", margin: "0 auto" }}>
            <div className="form-header">
              <h2 className="form-title">Daily <span className="accent">Check-in</span></h2>
              <p className="form-subtitle">
                Your data is compared with your recent history for better trend analysis.
              </p>
            </div>
            {error && <div className="error-alert">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Current Mood</label>
                <select className="form-select" value={formData.mood}
                  onChange={(e) => setFormData({ ...formData, mood: e.target.value })}>
                  <option value="Happy">Happy</option>
                  <option value="Okay">Okay</option>
                  <option value="Stressed">Stressed</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Work Hours Today: {formData.work_hours}h</label>
                <input type="range" className="form-range" min="0" max="16" step="0.5"
                  value={formData.work_hours}
                  onChange={(e) => setFormData({ ...formData, work_hours: e.target.value })} />
                <div className="range-labels"><span>0h</span><span>8h</span><span>16h</span></div>
              </div>
              <div className="form-group">
                <label className="form-label">Fatigue Level: {formData.fatigue}/10</label>
                <input type="range" className="form-range" min="0" max="10"
                  value={formData.fatigue}
                  onChange={(e) => setFormData({ ...formData, fatigue: e.target.value })} />
                <div className="range-labels"><span>None</span><span>Moderate</span><span>Extreme</span></div>
              </div>
              <div className="form-group">
                <label className="form-label">Years of Experience</label>
                <input type="number" className="form-input" min="0" max="50" step="0.5"
                  value={formData.experience}
                  onChange={(e) => setFormData({ ...formData, experience: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">How are you feeling today?</label>
                <textarea className="form-textarea"
                  placeholder="Share your thoughts about work, stress, or anything else..."
                  value={formData.feedback}
                  onChange={(e) => setFormData({ ...formData, feedback: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? (
                  <span className="loading"><span className="spinner"></span>Analyzing...</span>
                ) : ("Submit Daily Check-in")}
              </button>
            </form>
          </div>
        )}

        {activeTab === "assess" && result && (
          <div className="card-elevated result-container slide-up" style={{ maxWidth: "700px", margin: "0 auto" }}>
            <div className="result-header">
              <div className={`result-score ${result.burnout_level.toLowerCase()}`}>
                {result.burnout_score}
              </div>
              <span className={`result-level ${result.burnout_level.toLowerCase()}`}>
                {result.burnout_level} Burnout Risk
              </span>
            </div>

            {/* Trend Insight from new engine */}
            {result.trend_insight && (
              <div className={`result-trend-insight ${result.trend_arrow === "↑" ? "worsening" : result.trend_arrow === "↓" ? "improving" : "stable"}`}>
                <span className="trend-insight-arrow">{result.trend_arrow}</span>
                <span>{result.trend_insight}</span>
              </div>
            )}

            {/* Detected Patterns */}
            {result.patterns && Object.values(result.patterns).some(Boolean) && (
              <div className="patterns-panel">
                <h4 className="patterns-title">Detected Patterns</h4>
                <div className="patterns-list">
                  {result.patterns.fatigue_increasing && (
                    <span className="pattern-tag warning">Fatigue Increasing</span>
                  )}
                  {result.patterns.work_hours_high && (
                    <span className="pattern-tag warning">High Work Hours</span>
                  )}
                  {result.patterns.burnout_spike && (
                    <span className="pattern-tag danger">Burnout Spike</span>
                  )}
                  {result.patterns.negative_sentiment && (
                    <span className="pattern-tag muted">Negative Sentiment</span>
                  )}
                </div>
              </div>
            )}

            {/* Weekly Analysis */}
            <div className="weekly-analysis-card">
              <h3 className="weekly-analysis-title">
                Weekly Analysis — {result.weekly_analysis.current_day}
              </h3>
              <div className={`trend-indicator ${result.weekly_analysis.trend}`}>
                {result.weekly_analysis.trend === "improving" && "Improving"}
                {result.weekly_analysis.trend === "worsening" && "Getting Worse"}
                {result.weekly_analysis.trend === "stable" && "Stable"}
                {result.weekly_analysis.trend === "baseline" && "Baseline"}
              </div>
              <p className="trend-message">{result.weekly_analysis.trend_message}</p>
              {result.weekly_analysis.comparison && (
                <div className="comparison-stats">
                  <div className="comparison-stat">
                    <span className="comparison-label">Today</span>
                    <span className="comparison-value">{result.weekly_analysis.comparison.current.toFixed(1)}</span>
                  </div>
                  <div className="comparison-stat">
                    <span className="comparison-label">Week Avg</span>
                    <span className="comparison-value">{result.weekly_analysis.comparison.average.toFixed(1)}</span>
                  </div>
                  <div className="comparison-stat">
                    <span className="comparison-label">Days Analyzed</span>
                    <span className="comparison-value">{result.weekly_analysis.days_analyzed}</span>
                  </div>
                </div>
              )}
              {result.weekly_analysis.pattern !== "No pattern yet" && (
                <p className="pattern-info">Pattern: {result.weekly_analysis.pattern}</p>
              )}
            </div>

            <div className="result-body">
              <div className="result-section">
                <h3 className="result-section-title">Analysis Summary</h3>
                <div className="result-grid">
                  <div className="result-item">
                    <div className="result-item-label">Current Mood</div>
                    <div className="result-item-value">{result.mood}</div>
                  </div>
                  <div className="result-item">
                    <div className="result-item-label">Work Hours</div>
                    <div className="result-item-value">{result.work_hours}h</div>
                  </div>
                  <div className="result-item">
                    <div className="result-item-label">Fatigue Level</div>
                    <div className="result-item-value">{result.fatigue}/10</div>
                  </div>
                  <div className="result-item">
                    <div className="result-item-label">Feedback Sentiment</div>
                    <div className="result-item-value">
                      <span className={`sentiment-badge ${result.sentiment.toLowerCase()}`}>
                        {result.sentiment}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="result-section">
                <h3 className="result-section-title">AI-Powered Recommendations</h3>
                <ul className="suggestions-list">
                  {result.suggestions.map((suggestion, index) => (
                    <li key={index} className="suggestion-item">
                      <span className="suggestion-icon">{index + 1}</span>
                      <span className="suggestion-text">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="result-actions">
              <button onClick={handleReset} className="btn btn-secondary">New Assessment</button>
              <button onClick={() => setActiveTab("history")} className="btn btn-primary">View History</button>
            </div>
          </div>
        )}

        {activeTab === "history" && (
          <div className="card table-card slide-up">
            <h3 className="table-title">Your Assessment History</h3>
            {trendData && trendData.trend !== "No Data" && (
              <div className={`history-trend-summary trend-${trendData.trend.toLowerCase()}`}>
                <strong>{trendData.trend_arrow} {trendData.trend}</strong> — {trendData.insight}
                {trendData.percentage_change !== 0 && (
                  <span className="pct-change"> ({trendData.percentage_change > 0 ? "+" : ""}{trendData.percentage_change}%)</span>
                )}
              </div>
            )}
            {history.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">--</div>
                <p>No assessments yet</p>
                <p style={{ fontSize: "0.875rem", marginTop: "0.5rem", opacity: 0.7 }}>
                  Complete your first daily check-in to start tracking
                </p>
                <button onClick={() => setActiveTab("assess")} className="btn btn-primary" style={{ marginTop: "1rem" }}>
                  Start Assessment
                </button>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Mood</th>
                      <th>Work Hours</th>
                      <th>Fatigue</th>
                      <th>Burnout Score</th>
                      <th>Level</th>
                      <th>Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((record) => (
                      <tr key={record.id} className={record.burnout_level === "High" ? "high-risk" : ""}>
                        <td>{safeFormatDate(record.submission_date || record.created_at)}</td>
                        <td>{record.mood}</td>
                        <td>{record.work_hours}h</td>
                        <td>{record.fatigue}/10</td>
                        <td style={{ fontWeight: 600 }}>{record.burnout_score}</td>
                        <td>
                          <span className={`badge ${record.burnout_level.toLowerCase()}`}>
                            {record.burnout_level}
                          </span>
                        </td>
                        <td>
                          <span className={`trend-badge ${record.weekly_trend || "baseline"}`}>
                            {record.weekly_trend === "worsening" ? "↑" : record.weekly_trend === "improving" ? "↓" : "→"} {record.weekly_trend || "baseline"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
