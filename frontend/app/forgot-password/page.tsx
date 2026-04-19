"use client";

import { useState } from "react";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);

    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to send reset email");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <nav className="nav">
        <Link href="/" className="nav-logo">Burnout Detection</Link>
        <div className="nav-links">
          <Link href="/login" className="nav-link">Employee Login</Link>
          <Link href="/manager/login" className="nav-link">Manager Login</Link>
        </div>
      </nav>

      <div className="container-narrow">
        <div className="card-elevated form-card slide-up">
          <div className="form-header">
            <h1 className="form-title">Forgot <span className="accent">Password</span></h1>
            <p className="form-subtitle">
              Enter your email address and we&apos;ll send you a link to reset your password.
            </p>
          </div>

          {error && <div className="error-alert">{error}</div>}

          {success ? (
            <div
              style={{
                background: "linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.15))",
                border: "1px solid rgba(16, 185, 129, 0.25)",
                color: "#065f46",
                padding: "1.25rem 1.5rem",
                borderRadius: "12px",
                marginBottom: "1.5rem",
                fontSize: "0.95rem",
                lineHeight: "1.6",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>✉️</div>
              <strong>Reset link sent!</strong>
              <p style={{ marginTop: "0.5rem", color: "#047857" }}>
                If an account exists with <strong>{email}</strong>, you&apos;ll receive a password reset link shortly. Check your inbox and spam folder.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
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
                {loading ? (
                  <span className="loading">
                    <span className="spinner"></span>
                    Sending...
                  </span>
                ) : (
                  "Send Reset Link"
                )}
              </button>
            </form>
          )}

          <div className="auth-footer">
            <p>Remember your password? <Link href="/login" className="auth-link">Back to Login</Link></p>
          </div>
        </div>
      </div>
    </>
  );
}
