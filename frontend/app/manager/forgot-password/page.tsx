"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to process request");
      }

      setMessage(data.message || "Reset link sent to your email");
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <nav className="nav">
        <Link href="/" className="nav-logo">Burnout Intelligence</Link>
        <div className="nav-links">
          <Link href="/manager/login" className="nav-link">Return to Login</Link>
        </div>
      </nav>

      <div className="container-narrow">
        <div className="card-elevated form-card slide-up">
          <div className="form-header">
            <h1 className="form-title">Reset <span className="accent">Password</span></h1>
            <p className="form-subtitle">Enter your email and we'll send you a link to reset your password.</p>
          </div>

          {error && <div className="error-alert">{error}</div>}
          {message && <div style={{ background: "#d1fae5", color: "#065f46", padding: "0.75rem", borderRadius: "8px", marginBottom: "1.5rem", fontSize: "0.9rem" }}>{message}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group" style={{ marginBottom: "1.5rem" }}>
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
          
          <div className="auth-footer" style={{ marginTop: "2rem" }}>
            <Link href="/manager/login" className="auth-link">← Back to Login</Link>
          </div>
        </div>
      </div>
    </>
  );
}
