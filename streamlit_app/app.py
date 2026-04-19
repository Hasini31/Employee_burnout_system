import streamlit as st
import pandas as pd
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.api import (login_employee, register_employee, login_manager,
                        predict_burnout, get_employee_history, get_manager_insights)

# ─── Page Config ───
st.set_page_config(page_title="Burnout Detection Dashboard", page_icon="🧘", layout="wide", initial_sidebar_state="collapsed")

# ─── Load Custom CSS ───
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ─── Session State Initialization ───
for key in ["token", "user", "auth_tab", "dash_tab", "prediction_result", "mgr_section"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.auth_tab is None:
    st.session_state.auth_tab = "emp_login"
if st.session_state.dash_tab is None:
    st.session_state.dash_tab = "assess"
if st.session_state.mgr_section is None:
    st.session_state.mgr_section = "overview"


# ═══════════════════════════════════════════════
# RENDER: Login / Registration Page
# ═══════════════════════════════════════════════
def render_login_page():
    # Nav
    st.markdown("""
    <nav class="nav">
        <span class="nav-logo">Burnout Detection</span>
        <div class="nav-links">
            <span class="nav-link active">Employee Login</span>
            <span class="nav-link">Manager Login</span>
        </div>
    </nav>
    """, unsafe_allow_html=True)

    # Form Card Container
    st.markdown('<div class="container-narrow">', unsafe_allow_html=True)
    st.markdown('<div class="card-elevated form-card slide-up">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="form-header">
        <h1 class="form-title">Employee <span class="accent">Login</span></h1>
        <p class="form-subtitle">Sign in to access your burnout assessment dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # Auth Tabs
    tab_labels = {"emp_login": "Login", "emp_register": "Register", "mgr_login": "Manager"}
    cols = st.columns(3)
    for i, (key, label) in enumerate(tab_labels.items()):
        with cols[i]:
            if st.button(label, key=f"tab_{key}", use_container_width=True,
                         type="primary" if st.session_state.auth_tab == key else "secondary"):
                st.session_state.auth_tab = key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Employee Login Form ──
    if st.session_state.auth_tab == "emp_login":
        with st.form("emp_login_form"):
            email = st.text_input("Email Address", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In")
            if submitted:
                res, status = login_employee(email.strip(), password.strip())
                if status == 200:
                    st.session_state.token = res["token"]
                    st.session_state.user = res["user"]
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-alert">{res.get("error", "Login failed")}</div>', unsafe_allow_html=True)

    # ── Employee Register Form ──
    elif st.session_state.auth_tab == "emp_register":
        with st.form("emp_reg_form"):
            name = st.text_input("Full Name", placeholder="Enter your name")
            dept = st.text_input("Department (Optional)", placeholder="e.g., Engineering, Marketing")
            email = st.text_input("Email Address", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                res, status = register_employee(name.strip(), dept.strip(), email.strip(), password.strip())
                if status == 200:
                    st.session_state.token = res["token"]
                    st.session_state.user = res["user"]
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-alert">{res.get("error", "Registration failed")}</div>', unsafe_allow_html=True)

    # ── Manager Login Form ──
    elif st.session_state.auth_tab == "mgr_login":
        with st.form("mgr_login_form"):
            email = st.text_input("Manager Email", placeholder="admin@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Manager Sign In")
            if submitted:
                res, status = login_manager(email.strip(), password.strip())
                if status == 200:
                    st.session_state.token = res["token"]
                    st.session_state.user = res["user"]
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-alert">{res.get("error", "Login failed")}</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# RENDER: Employee Dashboard
# ═══════════════════════════════════════════════
def render_employee_dashboard():
    user = st.session_state.user

    # Nav
    st.markdown(f"""
    <nav class="nav">
        <span class="nav-logo">Burnout Detection</span>
        <div class="nav-links">
            <span class="user-greeting">Welcome, {user['name']}</span>
        </div>
    </nav>
    """, unsafe_allow_html=True)

    # Logout button (needs Streamlit interactivity)
    c1, c2 = st.columns([11, 1])
    with c2:
        if st.button("Logout", key="emp_logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.prediction_result = None
            st.rerun()

    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="dashboard-header fade-in">
        <h1 class="dashboard-title">Your <span class="accent">Wellness Dashboard</span></h1>
        <p class="dashboard-subtitle">Track your burnout levels over time with AI-powered pattern analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Trend Insight Banner
    hist_res, hist_status = get_employee_history(st.session_state.token)
    trend_data = None
    records = []
    if hist_status == 200:
        records = hist_res.get("records", [])
        trend_data = hist_res.get("trend")

    if trend_data and trend_data.get("trend") != "No Data":
        t = trend_data
        trend_cls = "trend-decreasing" if t["trend"] == "Decreasing" else ("trend-increasing" if t["trend"] == "Increasing" else "trend-stable")
        st.markdown(f"""
        <div class="trend-insight-banner {trend_cls}">
            <span class="trend-insight-arrow">{t['trend_arrow']}</span>
            <span class="trend-insight-text">{t['insight']}</span>
        </div>
        """, unsafe_allow_html=True)

    # Dashboard Tabs
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("New Assessment", key="tab_assess", use_container_width=True,
                      type="primary" if st.session_state.dash_tab == "assess" else "secondary"):
            st.session_state.dash_tab = "assess"
            st.rerun()
    with tc2:
        if st.button(f"My History ({len(records)})", key="tab_history", use_container_width=True,
                      type="primary" if st.session_state.dash_tab == "history" else "secondary"):
            st.session_state.dash_tab = "history"
            st.rerun()

    # ── Assessment Tab ──
    if st.session_state.dash_tab == "assess":
        if st.session_state.prediction_result is None:
            st.markdown("""
            <div class="card-elevated form-card slide-up" style="max-width: 600px; margin: 2rem auto;">
                <div class="form-header">
                    <h2 class="form-title">Daily <span class="accent">Check-in</span></h2>
                    <p class="form-subtitle">Your data is compared with your recent history for better trend analysis.</p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("assessment_form"):
                mood = st.selectbox("Current Mood", ["Happy", "Okay", "Stressed"], index=1)
                work_hours = st.slider("Work Hours Today", 0.0, 16.0, 8.0, 0.5)
                fatigue = st.slider("Fatigue Level (0 = None, 10 = Extreme)", 0, 10, 5)
                experience = st.number_input("Years of Experience", min_value=0.0, max_value=50.0, value=2.0, step=0.5)
                feedback = st.text_area("How are you feeling today?", placeholder="Share your thoughts about work, stress, or anything else...")

                if st.form_submit_button("Submit Daily Check-in"):
                    with st.spinner("Analyzing..."):
                        res, status = predict_burnout(st.session_state.token, mood, work_hours, fatigue, experience, feedback)
                        if status == 200:
                            st.session_state.prediction_result = res
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-alert">{res.get("error", "API Error")}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # ── Show Result ──
            res = st.session_state.prediction_result
            level = res['burnout_level'].lower()

            st.markdown(f"""
            <div class="card-elevated result-container slide-up" style="max-width: 700px; margin: 2rem auto;">
                <div class="result-header">
                    <div class="result-score {level}">{res['burnout_score']}</div>
                    <span class="result-level {level}">{res['burnout_level']} Burnout Risk</span>
                </div>
            """, unsafe_allow_html=True)

            # Trend Insight
            if res.get('trend_insight'):
                trend_cls = 'improving' if res['trend_arrow'] == '↓' else ('worsening' if res['trend_arrow'] == '↑' else 'stable')
                st.markdown(f"""
                <div class="result-trend-insight {trend_cls}">
                    <span class="trend-insight-arrow">{res['trend_arrow']}</span>
                    <span>{res['trend_insight']}</span>
                </div>
                """, unsafe_allow_html=True)

            # Detected Patterns
            patterns = res.get('patterns', {})
            active_patterns = {k: v for k, v in patterns.items() if v}
            if active_patterns:
                pattern_tags = ""
                pattern_map = {
                    'fatigue_increasing': ('Fatigue Increasing', 'warning'),
                    'work_hours_high': ('High Work Hours', 'warning'),
                    'burnout_spike': ('Burnout Spike', 'danger'),
                    'negative_sentiment': ('Negative Sentiment', 'muted'),
                }
                for k in active_patterns:
                    label, cls = pattern_map.get(k, (k, 'muted'))
                    pattern_tags += f'<span class="pattern-tag {cls}">{label}</span>'
                st.markdown(f"""
                <div class="patterns-panel">
                    <h4 class="patterns-title">Detected Patterns</h4>
                    <div class="patterns-list">{pattern_tags}</div>
                </div>
                """, unsafe_allow_html=True)

            # Weekly Analysis
            wa = res.get('weekly_analysis', {})
            if wa:
                trend_label = {"improving": "Improving", "worsening": "Getting Worse", "stable": "Stable", "baseline": "Baseline"}.get(wa.get('trend', ''), wa.get('trend', ''))
                comp_html = ""
                if wa.get('comparison'):
                    c = wa['comparison']
                    comp_html = f"""
                    <div class="comparison-stats">
                        <div class="comparison-stat"><span class="comparison-label">Today</span><span class="comparison-value">{c['current']:.1f}</span></div>
                        <div class="comparison-stat"><span class="comparison-label">Week Avg</span><span class="comparison-value">{c['average']:.1f}</span></div>
                        <div class="comparison-stat"><span class="comparison-label">Days Analyzed</span><span class="comparison-value">{wa.get('days_analyzed', 0)}</span></div>
                    </div>"""

                st.markdown(f"""
                <div class="weekly-analysis-card">
                    <h3 class="weekly-analysis-title">Weekly Analysis — {wa.get('current_day', '')}</h3>
                    <div class="trend-indicator {wa.get('trend', 'stable')}">{trend_label}</div>
                    <p class="trend-message">{wa.get('trend_message', '')}</p>
                    {comp_html}
                </div>
                """, unsafe_allow_html=True)

            # Analysis Summary
            sentiment_cls = res.get('sentiment', 'Neutral').lower()
            st.markdown(f"""
            <div class="result-body">
                <div class="result-section">
                    <h3 class="result-section-title">Analysis Summary</h3>
                    <div class="result-grid">
                        <div class="result-item"><div class="result-item-label">Current Mood</div><div class="result-item-value">{res['mood']}</div></div>
                        <div class="result-item"><div class="result-item-label">Work Hours</div><div class="result-item-value">{res['work_hours']}h</div></div>
                        <div class="result-item"><div class="result-item-label">Fatigue Level</div><div class="result-item-value">{res['fatigue']}/10</div></div>
                        <div class="result-item"><div class="result-item-label">Feedback Sentiment</div><div class="result-item-value"><span class="sentiment-badge {sentiment_cls}">{res['sentiment']}</span></div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # AI Suggestions
            suggestions_html = ""
            for i, sug in enumerate(res.get('suggestions', [])):
                suggestions_html += f'<li class="suggestion-item"><span class="suggestion-icon">{i+1}</span><span class="suggestion-text">{sug}</span></li>'
            st.markdown(f"""
                <div class="result-section">
                    <h3 class="result-section-title">AI-Powered Recommendations</h3>
                    <ul class="suggestions-list">{suggestions_html}</ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("New Assessment", key="new_assess", use_container_width=True):
                    st.session_state.prediction_result = None
                    st.rerun()
            with bc2:
                if st.button("View History", key="view_hist", use_container_width=True):
                    st.session_state.dash_tab = "history"
                    st.session_state.prediction_result = None
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # ── History Tab ──
    elif st.session_state.dash_tab == "history":
        st.markdown('<div class="card table-card slide-up">', unsafe_allow_html=True)
        st.markdown('<h3 class="table-title">Your Assessment History</h3>', unsafe_allow_html=True)

        if trend_data and trend_data.get("trend") != "No Data":
            t = trend_data
            trend_cls = "trend-decreasing" if t["trend"] == "Decreasing" else ("trend-increasing" if t["trend"] == "Increasing" else "trend-stable")
            pct = f' ({("+" if t["percentage_change"] > 0 else "")}{t["percentage_change"]}%)' if t["percentage_change"] != 0 else ""
            st.markdown(f"""
            <div class="history-trend-summary {trend_cls}">
                <strong>{t['trend_arrow']} {t['trend']}</strong> — {t['insight']}<span class="pct-change">{pct}</span>
            </div>
            """, unsafe_allow_html=True)

        if not records:
            st.markdown('<div style="text-align:center; padding: 3rem; color: var(--text-muted);">No assessments yet. Complete your first daily check-in to start tracking.</div>', unsafe_allow_html=True)
        else:
            # Build HTML table matching original
            rows_html = ""
            for r in records:
                high_cls = ' class="high-risk"' if r.get('burnout_level') == 'High' else ''
                trend = r.get('weekly_trend', 'baseline') or 'baseline'
                trend_arrow = '↑' if trend == 'worsening' else ('↓' if trend == 'improving' else '→')
                date_str = r.get('submission_date', r.get('created_at', ''))[:10]
                rows_html += f"""<tr{high_cls}>
                    <td>{date_str}</td><td>{r.get('mood', '')}</td><td>{r.get('work_hours', '')}h</td>
                    <td>{r.get('fatigue', '')}/10</td><td style="font-weight:600">{r.get('burnout_score', '')}</td>
                    <td><span class="badge {r.get('burnout_level', '').lower()}">{r.get('burnout_level', '')}</span></td>
                    <td><span class="trend-badge {trend}">{trend_arrow} {trend}</span></td>
                </tr>"""
            st.markdown(f"""
            <div class="table-responsive">
                <table class="data-table">
                    <thead><tr><th>Date</th><th>Mood</th><th>Work Hours</th><th>Fatigue</th><th>Burnout Score</th><th>Level</th><th>Trend</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# RENDER: Manager Dashboard
# ═══════════════════════════════════════════════
def render_manager_dashboard():
    user = st.session_state.user

    st.markdown(f"""
    <nav class="nav">
        <span class="nav-logo">Burnout Intelligence</span>
        <div class="nav-links">
            <span class="user-greeting">Manager: {user['name']}</span>
        </div>
    </nav>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([11, 1])
    with c2:
        if st.button("Logout", key="mgr_logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="dashboard-header fade-in">
        <h1 class="dashboard-title">Burnout <span class="accent">Intelligence</span> Dashboard</h1>
        <p class="dashboard-subtitle">Employee-centric wellness monitoring with AI-powered trend analysis and alerts</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch data
    res, status = get_manager_insights(st.session_state.token)
    if status != 200:
        st.markdown(f'<div class="error-alert">Failed to load manager insights: {res.get("error", "Unknown error")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    s = res["summary"]
    alerts = res.get("alerts", [])
    critical_alerts = [a for a in alerts if a["severity"] == "critical"]
    warning_alerts = [a for a in alerts if a["severity"] == "warning"]

    # Section tabs
    sections = ["overview", "employees", "alerts", "analytics"]
    sec_cols = st.columns(4)
    for i, sec in enumerate(sections):
        with sec_cols[i]:
            label = sec.capitalize()
            if sec == "alerts" and alerts:
                label += f" ({len(alerts)})"
            if st.button(label, key=f"mgr_sec_{sec}", use_container_width=True,
                         type="primary" if st.session_state.mgr_section == sec else "secondary"):
                st.session_state.mgr_section = sec
                st.rerun()

    # ═══ OVERVIEW ═══
    if st.session_state.mgr_section == "overview":
        trend_cls = "danger-text" if s['team_trend'] == "Increasing" else ("success-text" if s['team_trend'] == "Decreasing" else "")
        wow = res.get('weekly_analytics', {}).get('burnout_change_pct', 0)
        wow_prefix = "+" if wow > 0 else ""

        st.markdown(f"""
        <div class="modern-stats-grid slide-up">
            <div class="modern-stat-card"><div class="modern-stat-value" style="color:#3b82f6">{s['total_employees']}</div><div class="modern-stat-label">Total Employees</div></div>
            <div class="modern-stat-card"><div class="modern-stat-value danger-text">{s['high_risk_employees']}</div><div class="modern-stat-label">High Risk</div></div>
            <div class="modern-stat-card"><div class="modern-stat-value">{s['avg_burnout']}</div><div class="modern-stat-label">Avg Burnout Score</div></div>
            <div class="modern-stat-card"><div class="modern-stat-value trend-text {trend_cls}">{s['team_trend_arrow']} {s['team_trend']}</div><div class="modern-stat-label">Team Trend</div></div>
            <div class="modern-stat-card"><div class="modern-stat-value warning-text">{len(critical_alerts)}</div><div class="modern-stat-label">Critical Alerts</div></div>
            <div class="modern-stat-card"><div class="modern-stat-value">{wow_prefix}{wow}%</div><div class="modern-stat-label">Week-on-Week Change</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Team Insights
        team_insights = res.get("team_insights", [])
        if team_insights:
            items = "".join(f'<li class="insight-item"><span class="insight-dot"></span>{ins}</li>' for ins in team_insights)
            st.markdown(f'<div class="card slide-up"><h3 class="chart-title" style="margin-bottom:0.75rem">Team Insights</h3><ul class="insights-list">{items}</ul></div>', unsafe_allow_html=True)

        # Recommendations
        recs = res.get("recommendations", [])
        if recs:
            items = "".join(f'<li class="insight-item recommendation"><span class="insight-icon">→</span>{r}</li>' for r in recs)
            st.markdown(f'<div class="card slide-up" style="padding:1.5rem 2rem"><h3 class="chart-title" style="margin-bottom:0.75rem">Manager Recommendations</h3><ul class="insights-list">{items}</ul></div>', unsafe_allow_html=True)

        # Top Risk Employees
        top_risk = res.get("top_risk", [])
        if top_risk:
            cards_html = ""
            for emp in top_risk:
                lvl = emp['burnout_level'].lower()
                trend_map = {"Increasing": "increasing", "Decreasing": "decreasing", "Stable": "stable"}
                t_cls = trend_map.get(emp['trend'], 'stable')
                cards_html += f"""
                <div class="top-risk-card {lvl}">
                    <div class="top-risk-header"><span class="top-risk-name">{emp['name']}</span><span class="trend-arrow {t_cls}">{emp['trend_arrow']} {emp['trend']}</span></div>
                    <div class="top-risk-score">{emp['burnout_score']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center"><span class="badge {lvl}">{emp['burnout_level']}</span><span style="font-size:0.72rem; color:var(--text-muted)">Fatigue {emp['fatigue']}/10</span></div>
                    <p class="top-risk-insight">{emp['trend_insight']}</p>
                </div>"""
            st.markdown(f'<div class="card slide-up"><h3 class="chart-title" style="margin-bottom:1rem">Top 5 Risk Employees</h3><div class="top-risk-grid">{cards_html}</div></div>', unsafe_allow_html=True)

        # Correlation
        corr = res.get("correlation_insight", {})
        if corr.get("insight"):
            st.markdown(f'<div class="card correlation-card slide-up"><h3 class="chart-title" style="margin-bottom:0.5rem">Correlation Insight</h3><p style="color:var(--text-muted);line-height:1.6">{corr["insight"]}</p></div>', unsafe_allow_html=True)

    # ═══ EMPLOYEES ═══
    elif st.session_state.mgr_section == "employees":
        employees = res.get("employees", [])
        st.markdown('<div class="card table-card slide-up">', unsafe_allow_html=True)
        st.markdown('<h3 class="table-title">Employee Status Table</h3>', unsafe_allow_html=True)
        if not employees:
            st.markdown('<div style="text-align:center; padding:3rem; color:var(--text-muted);">No employee data yet</div>', unsafe_allow_html=True)
        else:
            rows_html = ""
            for emp in employees:
                high_cls = ' class="high-risk"' if emp['burnout_level'] == 'High' else ''
                t_cls = {"Increasing": "increasing", "Decreasing": "decreasing"}.get(emp['trend'], "stable")
                pct_cls = "danger-text" if emp['percentage_change'] > 0 else ("success-text" if emp['percentage_change'] < 0 else "")
                pct_prefix = "+" if emp['percentage_change'] > 0 else ""
                date_str = (emp.get('last_updated') or '')[:10]
                rows_html += f"""<tr{high_cls}>
                    <td style="font-weight:500">{emp['name']}</td>
                    <td style="font-weight:700">{emp['burnout_score']}</td>
                    <td><span class="badge {emp['burnout_level'].lower()}">{emp['burnout_level']}</span></td>
                    <td><span class="trend-arrow {t_cls}">{emp['trend_arrow']} {emp['trend']}</span></td>
                    <td class="{pct_cls}">{pct_prefix}{emp['percentage_change']}%</td>
                    <td>{emp['fatigue']}/10</td>
                    <td>{emp['work_hours']}h</td>
                    <td>{date_str}</td>
                </tr>"""
            st.markdown(f"""
            <div class="table-responsive"><table class="data-table">
                <thead><tr><th>Employee</th><th>Latest Score</th><th>Risk</th><th>Trend</th><th>Change %</th><th>Fatigue</th><th>Hours</th><th>Last Updated</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table></div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ ALERTS ═══
    elif st.session_state.mgr_section == "alerts":
        st.markdown(f'<div class="card slide-up"><h3 class="table-title" style="margin-bottom:1rem">Active Alerts ({len(alerts)})</h3>', unsafe_allow_html=True)
        if not alerts:
            st.markdown('<div style="text-align:center; padding:3rem; color:var(--text-muted);">✓ No active alerts — team is stable!</div>', unsafe_allow_html=True)
        else:
            alerts_html = '<div class="alerts-list">'
            if critical_alerts:
                items = "".join(f"""<div class="alert-item critical">
                    <span class="severity-dot critical"></span>
                    <div class="alert-content"><span class="alert-name">{a['employee_name']}</span><span class="alert-message">{a['message']}</span></div>
                    <span class="alert-type-badge">{a['type'].replace('_', ' ')}</span>
                </div>""" for a in critical_alerts)
                alerts_html += f'<div class="alerts-group"><h4 class="alerts-group-title critical">Critical ({len(critical_alerts)})</h4>{items}</div>'
            if warning_alerts:
                items = "".join(f"""<div class="alert-item warning">
                    <span class="severity-dot warning"></span>
                    <div class="alert-content"><span class="alert-name">{a['employee_name']}</span><span class="alert-message">{a['message']}</span></div>
                    <span class="alert-type-badge">{a['type'].replace('_', ' ')}</span>
                </div>""" for a in warning_alerts)
                alerts_html += f'<div class="alerts-group"><h4 class="alerts-group-title warning">Warnings ({len(warning_alerts)})</h4>{items}</div>'
            alerts_html += '</div>'
            st.markdown(alerts_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ ANALYTICS ═══
    elif st.session_state.mgr_section == "analytics":
        wa = res.get("weekly_analytics", {})
        daily = wa.get("daily_data", [])

        if daily:
            import altair as alt
            df = pd.DataFrame(daily)
            df['date'] = pd.to_datetime(df['date'])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card" style="padding:2rem">', unsafe_allow_html=True)
                st.markdown('<h3 class="chart-title">Burnout Trend — Last 7 Days</h3>', unsafe_allow_html=True)
                chart = alt.Chart(df).mark_area(line={'color': '#ef4444'}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(239,68,68,0.1)', offset=1), alt.GradientStop(color='rgba(239,68,68,0.3)', offset=0)])).encode(x=alt.X('date:T', title=None), y=alt.Y('avg_burnout:Q', title=None, scale=alt.Scale(domain=[0, 10]))).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card" style="padding:2rem">', unsafe_allow_html=True)
                st.markdown('<h3 class="chart-title">Fatigue Trend — Last 7 Days</h3>', unsafe_allow_html=True)
                chart = alt.Chart(df).mark_area(line={'color': '#f59e0b'}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(245,158,11,0.1)', offset=1), alt.GradientStop(color='rgba(245,158,11,0.3)', offset=0)])).encode(x=alt.X('date:T', title=None), y=alt.Y('avg_fatigue:Q', title=None, scale=alt.Scale(domain=[0, 10]))).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Week-on-Week Insights
        insights_list = wa.get("insights", [])
        if insights_list:
            items = "".join(f'<li class="insight-item"><span class="insight-dot"></span>{ins}</li>' for ins in insights_list)
            comp_html = ""
            if wa.get("prev_week_avg") is not None:
                pct = wa.get("burnout_change_pct", 0)
                pct_cls = "danger-text" if pct > 0 else "success-text"
                comp_html = f"""<div style="display:flex; gap:2rem; margin-top:1rem">
                    <div class="comparison-stat"><span class="comparison-label">This Week Avg</span><span class="comparison-value">{wa['this_week_avg']}</span></div>
                    <div class="comparison-stat"><span class="comparison-label">Last Week Avg</span><span class="comparison-value">{wa['prev_week_avg']}</span></div>
                    <div class="comparison-stat"><span class="comparison-label">Change</span><span class="comparison-value {pct_cls}">{"+" if pct > 0 else ""}{pct}%</span></div>
                </div>"""
            st.markdown(f'<div class="card slide-up"><h3 class="chart-title" style="margin-bottom:0.75rem">Week-on-Week Insights</h3><ul class="insights-list">{items}</ul>{comp_html}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════
if not st.session_state.token:
    render_login_page()
elif st.session_state.user and st.session_state.user.get("role") == "manager":
    render_manager_dashboard()
elif st.session_state.user and st.session_state.user.get("role") == "employee":
    render_employee_dashboard()
else:
    render_login_page()
