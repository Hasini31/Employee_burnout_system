"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    department: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const endpoint = isLogin 
        ? "/api/auth/employee/login" 
        : "/api/auth/employee/register";
      
      const body = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Authentication failed");
      }

      // Store token and user info
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Redirect to employee dashboard
      router.push("/employee");
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
          <Link href="/login" className="nav-link active">
            Employee Login
          </Link>
          <Link href="/manager/login" className="nav-link">
            Manager Login
          </Link>
        </div>
      </nav>

      <div className="container-narrow">
        <div className="card-elevated form-card slide-up">
          <div className="form-header">
            <h1 className="form-title">
              Employee <span className="accent">{isLogin ? "Login" : "Register"}</span>
            </h1>
            <p className="form-subtitle">
              {isLogin 
                ? "Sign in to access your burnout assessment dashboard" 
                : "Create an account to track your wellness over time"}
            </p>
          </div>

          <div className="auth-tabs">
            <button 
              className={`auth-tab ${isLogin ? "active" : ""}`}
              onClick={() => setIsLogin(true)}
            >
              Login
            </button>
            <button 
              className={`auth-tab ${!isLogin ? "active" : ""}`}
              onClick={() => setIsLogin(false)}
            >
              Register
            </button>
          </div>

          {error && <div className="error-alert">{error}</div>}

          <form onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Enter your name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required={!isLogin}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Department (Optional)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., Engineering, Marketing"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  />
                </div>
              </>
            )}

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="you@company.com"
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
                placeholder={isLogin ? "Enter your password" : "Min. 6 characters"}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                minLength={6}
              />
            </div>

            {isLogin && (
              <div style={{ textAlign: "right", marginBottom: "1.5rem" }}>
                <Link href="/forgot-password" style={{ color: "#3b82f6", fontSize: "0.85rem", textDecoration: "none" }}>
                  Forgot Password?
                </Link>
              </div>
            )}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <span className="loading">
                  <span className="spinner"></span>
                  {isLogin ? "Signing in..." : "Creating account..."}
                </span>
              ) : (
                isLogin ? "Sign In" : "Create Account"
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>Are you a manager? <Link href="/manager/login" className="auth-link">Login here</Link></p>
          </div>
        </div>
      </div>
    </>
  );
}
