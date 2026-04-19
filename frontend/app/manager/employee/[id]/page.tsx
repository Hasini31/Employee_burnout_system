"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler,
} from "chart.js";
import { Line, Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

/* ──── Types ──── */
interface DailyRecord {
  id: number; mood: string; work_hours: number; fatigue: number;
  burnout_score: number; burnout_level: string; weekly_trend: string;
  submission_date: string; sentiment: string; feedback: string;
  sleep_hours: number; stress_level: number;
}
interface Overall {
  recommendations: string[];
}
interface AnalysisData {
  employee_id: number; name: string; department: string; email: string;
  records: DailyRecord[];
  overall: Overall;
}

/* ──── Helpers ──── */
function fmtDate(d: string) {
  if (!d) return "—";
  try { const dt = new Date(d + "T00:00:00"); return isNaN(dt.getTime()) ? d : dt.toLocaleDateString(undefined, { month: "short", day: "numeric" }); }
  catch { return d; }
}

/* ──── Chart Defaults ──── */
const defaultOpts = (title: string) => ({
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: true, text: title, color: "#1a1a1a", font: { size: 14, weight: "bold" as const } },
  },
  scales: {
    y: { beginAtZero: true, ticks: { color: "#6b7280" }, grid: { color: "rgba(0,0,0,0.06)" } },
    x: { ticks: { color: "#6b7280", maxRotation: 45 }, grid: { display: false } },
  },
});

/* ──── Main Component ──── */
export default function EmployeeAnalysis() {
  const router = useRouter();
  const params = useParams();
  const empId = Number(params.id);

  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Requirement 1 & 6: Initial state shows ONLY inputs, showAnalysis controls render
  const [showAnalysis, setShowAnalysis] = useState(false);

  // Date range default to last 30 days
  const today = new Date();
  const defaultStart = new Date(today); defaultStart.setDate(today.getDate() - 30);
  const [startDate, setStartDate] = useState(defaultStart.toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(today.toISOString().split("T")[0]);

  // Requirement 2: Fetch data AFTER clicking apply, THEN show charts
  const applyDates = async () => {
    setLoading(true); setError(""); setShowAnalysis(false);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:5000/api/employee/${empId}/history?startDate=${startDate}&endDate=${endDate}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) { 
        if (res.status === 401) { router.push("/manager/login"); return; } 
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to fetch data from server"); 
      }
      const dataJson = await res.json();
      setData(dataJson);
      setShowAnalysis(true);
    } catch (e) { 
      setError(e instanceof Error ? e.message : "Error"); 
    } finally { 
      setLoading(false); 
    }
  };

  const r = data?.records || [];
  const o = data?.overall;

  // Mood Bar Chart Data (Counts frequency of moods)
  const moodCounts = r.reduce((acc, curr) => {
    const m = curr.mood || "Neutral";
    acc[m] = (acc[m] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  /* ──── CHARTS ──── */
  const burnoutDaily = {
    labels: r.map(d => fmtDate(d.submission_date)),
    datasets: [{
      label: "Burnout Score", data: r.map(d => d.burnout_score),
      borderColor: "rgb(239,68,68)", backgroundColor: "rgba(239,68,68,0.08)",
      fill: true, tension: 0.3, pointRadius: 3, pointHoverRadius: 6,
      pointBackgroundColor: r.map(d => d.burnout_score >= 7 ? "#ef4444" : d.burnout_score >= 4 ? "#f59e0b" : "#10b981"),
    }],
  };
  const fatigueDaily = {
    labels: r.map(d => fmtDate(d.submission_date)),
    datasets: [{ label: "Fatigue", data: r.map(d => d.fatigue), borderColor: "#f59e0b", backgroundColor: "rgba(245,158,11,0.08)", fill: true, tension: 0.3, pointRadius: 3 }],
  };
  const moodChart = {
    labels: Object.keys(moodCounts),
    datasets: [{ label: "Days", data: Object.values(moodCounts), backgroundColor: "rgba(139,92,246,0.7)", borderRadius: 6 }],
  };

  return (
    <>
      <nav className="nav">
        <Link href="/manager" className="nav-logo">Burnout Intelligence</Link>
        <div className="nav-links">
          <Link href="/manager" className="nav-link">Dashboard</Link>
        </div>
      </nav>

      <div className="container">
        {/* Requirement 1: Minimal Header and Inputs */}
        <div className="analysis-header fade-in">
          <h1 className="dashboard-title" style={{ marginTop: "0.5rem" }}>
            {data ? data.name : "Employee"} <span className="accent">Analysis</span>
          </h1>
        </div>

        <div className="card compact-date-picker slide-up">
          <div className="date-selection-container">
            <div className="dates-row">
              <div className="compact-field">
                <label className="compact-label">Start Date</label>
                <input 
                  type="date" 
                  className="compact-input" 
                  value={startDate} 
                  onChange={e => setStartDate(e.target.value)} 
                  placeholder="YYYY-MM-DD"
                />
              </div>
              <div className="compact-field">
                <label className="compact-label">End Date</label>
                <input 
                  type="date" 
                  className="compact-input" 
                  value={endDate} 
                  onChange={e => setEndDate(e.target.value)} 
                  placeholder="YYYY-MM-DD"
                />
              </div>
            </div>
            
            <button 
              className="compact-apply-btn" 
              onClick={applyDates} 
              disabled={loading || !startDate || !endDate}
            >
              {loading ? "Loading..." : "Apply Range"}
            </button>

            {showAnalysis && startDate && endDate && (
              <p className="selected-range-text">
                Selected: {fmtDate(startDate)} – {fmtDate(endDate)}
              </p>
            )}
          </div>
        </div>

        {error && <div className="error-alert">{error}</div>}

        {/* Requirement 5 & 6: Loading State / Display analysis ONLY if showAnalysis is true */}
        {loading && (
          <div className="loading-screen" style={{ marginTop: "2rem", background: "transparent" }}>
            <span className="spinner"></span><p>Analyzing employee data...</p>
          </div>
        )}

        {showAnalysis && !loading && (
          <div className="fade-in">
            {r.length === 0 ? (
              <div className="empty-state">
                <p>No data available for the selected dates.</p>
              </div>
            ) : (
              <>
                {/* Requirement 3: Minimal Recommendations (Max 3) */}
                {o?.recommendations && o.recommendations.length > 0 && (
                  <div className="card recommendations-card mb-4">
                    <h3 className="section-title">Actionable Advice</h3>
                    <ul className="recommendations-list">
                      {o.recommendations.slice(0, 3).map((rec, i) => (
                        <li key={i} className="recommendation-item"><span className="rec-icon">→</span>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Requirement 2: Show exactly 3 Graphs */}
                <div className="charts-grid mb-4">
                  {/* A. Burnout Trend Graph */}
                  <div className="card chart-card">
                    <div className="chart-container" style={{ height: "300px" }}>
                      <Line data={burnoutDaily} options={{
                        ...defaultOpts("Burnout Trend"),
                        scales: { ...defaultOpts("").scales, y: { ...defaultOpts("").scales.y, max: 10 } }
                      }} />
                    </div>
                  </div>

                  {/* B. Fatigue Trend Graph */}
                  <div className="card chart-card">
                    <div className="chart-container" style={{ height: "300px" }}>
                      <Line data={fatigueDaily} options={defaultOpts("Fatigue Trend")} />
                    </div>
                  </div>
                </div>

                {/* C. Mood Analysis Graph */}
                <div className="card chart-card mb-4" style={{ maxWidth: "600px", margin: "0 auto" }}>
                  <div className="chart-container" style={{ height: "250px" }}>
                    <Bar data={moodChart} options={defaultOpts("Mood Analysis (Frequency)")} />
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
      <style jsx>{`
        .mb-4 { margin-bottom: 2rem; }
        .recommendations-card { padding: 1.5rem; background: rgba(255, 255, 255, 0.7); }

        /* ──── Date Selection Modern Compact Styling ──── */
        .compact-date-picker {
          padding: 1.5rem;
          max-width: 450px;
          margin: 0 auto 2rem auto;
          background: #ffffff;
          border-radius: 12px;
          border: 1px solid #e5e7eb;
          box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        .date-selection-container {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }
        .dates-row {
          display: flex;
          gap: 1rem;
          justify-content: space-between;
        }
        .compact-field {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          flex: 1;
        }
        .compact-label {
          font-size: 0.75rem;
          font-weight: 600;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .compact-input {
          padding: 0.65rem 0.8rem;
          font-size: 0.95rem;
          color: #1f2937;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          outline: none;
          transition: all 0.2s ease;
          background: #f9fafb;
          font-family: inherit;
        }
        .compact-input:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
          background: white;
        }
        ::-webkit-calendar-picker-indicator {
          cursor: pointer;
          opacity: 0.6;
          transition: 0.2s;
          padding-left: 0.5rem;
        }
        ::-webkit-calendar-picker-indicator:hover {
          opacity: 1;
        }
        .compact-apply-btn {
          padding: 0.75rem;
          font-size: 0.95rem;
          font-weight: 600;
          color: white;
          background: #0f172a;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s ease, transform 0.1s ease;
          width: 100%;
        }
        .compact-apply-btn:hover:not(:disabled) {
          background: #1e293b;
          transform: translateY(-1px);
        }
        .compact-apply-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          background: #9ca3af;
        }
        .selected-range-text {
          font-size: 0.85rem;
          color: #10b981;
          text-align: center;
          font-weight: 500;
          margin-top: 0.25rem;
        }
      `}</style>
    </>
  );
}
