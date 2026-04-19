"use client";

import Link from "next/link";

export default function HomePage() {
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
          <Link href="/manager/login" className="nav-link">
            Manager Login
          </Link>
        </div>
      </nav>

      <div className="hero-container">
        <div className="hero-content fade-in">
          <h1 className="hero-title">
            Employee <span className="accent">Burnout Detection</span>
          </h1>
          <p className="hero-subtitle">
            AI-powered wellness tracking with time-based pattern analysis. 
            Monitor burnout levels, detect weekly trends, and get personalized recommendations.
          </p>
          
          <div className="hero-features">
            <div className="hero-feature">
              <div className="hero-feature-icon">1</div>
              <div className="hero-feature-text">
                <strong>Time-Based Analysis</strong>
                <span>Each day compares with previous days for better insights</span>
              </div>
            </div>
            <div className="hero-feature">
              <div className="hero-feature-icon">2</div>
              <div className="hero-feature-text">
                <strong>Pattern Detection</strong>
                <span>Identifies trends like increasing fatigue or high work hours</span>
              </div>
            </div>
            <div className="hero-feature">
              <div className="hero-feature-icon">3</div>
              <div className="hero-feature-text">
                <strong>Sentiment Analysis</strong>
                <span>AI analyzes feedback text for emotional insights</span>
              </div>
            </div>
          </div>

          <div className="hero-actions">
            <Link href="/login" className="btn btn-primary">
              Employee Portal
            </Link>
            <Link href="/manager/login" className="btn btn-secondary">
              Manager Dashboard
            </Link>
          </div>
        </div>

        <div className="hero-cards slide-up">
          <div className="info-card">
            <h3 className="info-card-title">How It Works</h3>
            <div className="info-card-content">
              <div className="day-item">
                <span className="day-label">Monday</span>
                <span className="day-desc">Baseline assessment - no past data</span>
              </div>
              <div className="day-item">
                <span className="day-label">Tuesday</span>
                <span className="day-desc">Compare with Monday</span>
              </div>
              <div className="day-item">
                <span className="day-label">Wednesday</span>
                <span className="day-desc">Use Mon + Tue for better analysis</span>
              </div>
              <div className="day-item">
                <span className="day-label">Thursday</span>
                <span className="day-desc">Use Mon + Tue + Wed</span>
              </div>
              <div className="day-item">
                <span className="day-label">Friday</span>
                <span className="day-desc">Full week data - strongest analysis</span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h3 className="info-card-title">Key Features</h3>
            <ul className="feature-list">
              <li>Pre-trained ML model for accurate predictions</li>
              <li>Weekly trend tracking and pattern detection</li>
              <li>TextBlob sentiment analysis on feedback</li>
              <li>Personalized recommendations based on trends</li>
              <li>Manager dashboard with team overview</li>
              <li>SQLite database for persistent storage</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
