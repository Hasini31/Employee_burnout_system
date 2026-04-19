"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ManagerLoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/auth/manager/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Authentication failed");
      }

      // Store token and user info
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Redirect to manager dashboard
      router.push("/manager");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <nav className="nav">
        <Link href="/" className="nav-logo">
          Burnout Detection
        </Link>
        <div className="nav-links">
          <Link href="/login" className="nav-link">
            Employee Login
          </Link>
          <Link href="/manager/login" className="nav-link active">
            Manager Login
          </Link>
        </div>
      </nav>

      <div className="container-narrow">
        <div className="card-elevated form-card slide-up">
          <div className="form-header">
            <h1 className="form-title">
              Manager <span className="accent">Login</span>
            </h1>
            <p className="form-subtitle">
              Access the management dashboard to monitor team wellness
            </p>
          </div>

          {error && <div className="error-alert">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="admin@company.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div className="form-group" style={{ marginBottom: "0.5rem" }}>
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>

            <div style={{ textAlign: "right", marginBottom: "1.5rem" }}>
              <Link href="/manager/forgot-password" style={{ color: "#3b82f6", fontSize: "0.85rem", textDecoration: "none" }}>
                Forgot Password?
              </Link>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <span className="loading">
                  <span className="spinner"></span>
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>Are you an employee? <Link href="/login" className="auth-link">Login here</Link></p>
          </div>

          <div className="demo-credentials">
            <p className="demo-title">Demo Credentials</p>
            <p>Email: admin@company.com</p>
            <p>Password: admin123</p>
          </div>
        </div>
      </div>
    </>
  );
}
