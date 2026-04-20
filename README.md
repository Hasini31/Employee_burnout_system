# 🧘 Employee Burnout Detection System

> An AI-powered full-stack web application that monitors employee wellness, detects burnout patterns using machine learning, and provides personalized recommendations — helping managers and HR teams take proactive action before burnout becomes critical.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup (Python / Flask)](#2-backend-setup-python--flask)
  - [3. Frontend Setup (Next.js)](#3-frontend-setup-nextjs)
  - [4. Streamlit Dashboard (Optional)](#4-streamlit-dashboard-optional)
- [Environment Variables](#environment-variables)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Employee Burnout Detection System** is a dual-interface platform (Next.js web app + optional Streamlit dashboard) backed by a Flask REST API. Every day employees fill in a short wellness check — stress level, working hours, fatigue, sleep, and mood — and the system uses a **pre-trained Random Forest model** to predict their burnout score in real time.

Key differentiators:
- **Time-based analysis**: Each daily entry is compared to all previous entries in the same week, so predictions improve as the week progresses.
- **Sentiment analysis**: Open-ended text feedback is processed with **TextBlob** for emotional scoring.
- **Gemini AI integration**: Google Generative AI generates personalized, context-aware recommendations.
- **Manager dashboard**: Aggregated team burnout trends, heatmaps, and alerts.

---

## Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Separate login / registration flows for employees and managers |
| 📊 Daily Assessment | Employees submit stress, working hours, fatigue, sleep hours, and mood |
| 🤖 ML Prediction | Random Forest Regressor predicts burnout score (0 – 10) |
| 📈 Weekly Trends | Day-over-day comparisons reveal patterns (Mon → Fri context builds up) |
| 💬 Sentiment Analysis | TextBlob NLP scores free-text feedback for positive/negative tone |
| 🧠 AI Recommendations | Google Gemini generates personalised wellness advice |
| 📉 Manager Dashboard | Team overview, burnout heatmap, high-risk employee alerts |
| 📧 Email Alerts | Automated email notifications for critical burnout scores |
| 📱 Responsive UI | Fully responsive Next.js frontend with dark / light theme |
| 🐍 Streamlit Alt UI | Optional Streamlit-based dashboard as an alternative front-end |

---

## Tech Stack

### Frontend
- **Next.js 15** (React 19, TypeScript)
- **Chart.js / react-chartjs-2** — data visualizations
- **SQLite3** (via Node.js) — local session storage
- **Nodemailer** — email notifications
- **bcryptjs / jsonwebtoken** — auth utilities

### Backend
- **Python 3.11+**
- **Flask 3** + **Flask-CORS**
- **scikit-learn** — Random Forest model
- **TextBlob** — sentiment analysis
- **Google Generative AI (Gemini)** — AI recommendations
- **pandas / numpy / matplotlib / seaborn** — data processing & charts
- **SQLite** — persistent database

### ML
- **Random Forest Regressor** trained on the included `employee_data.csv`
- Features: stress level, working hours, fatigue score, sleep hours, mood
- Target: burnout score (0 – 10)

---

## Project Structure

```
Employee_burnout_system/
├── frontend/                  # Next.js application
│   ├── app/
│   │   ├── page.tsx           # Landing / home page
│   │   ├── login/             # Employee login
│   │   ├── employee/          # Employee dashboard
│   │   ├── manager/           # Manager login & dashboard
│   │   ├── forgot-password/
│   │   ├── reset-password/
│   │   └── api/               # Next.js API routes
│   ├── components/            # Reusable UI components
│   ├── styles/                # Global CSS
│   ├── package.json
│   └── next.config.ts         # API proxy → Flask :5000
│
├── backend/                   # Flask REST API
│   ├── main.py                # All endpoints
│   ├── train_model.py         # Model training script
│   ├── seed_test_data.py      # Seed sample data
│   ├── database.db            # SQLite database (auto-created)
│   ├── burnout_model.pkl      # Trained ML model (auto-generated)
│   ├── pyproject.toml
│   └── .env                   # Environment variables (not committed)
│
├── streamlit_app/             # Optional Streamlit front-end
│   ├── app.py
│   ├── utils/api.py
│   └── styles/custom.css
│
├── employee_data.csv          # Training dataset
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel deployment config
└── README.md
```

---

## Screenshots

> Screenshots below illustrate the key pages of the working application.

### 🏠 Home / Landing Page
![Home Page](public/placeholder.jpg)
*The landing page introduces the system, explains the time-based analysis workflow, and provides quick access to the Employee and Manager portals.*

### 🔐 Employee Login & Registration
![Employee Login](public/placeholder-logo.png)
*Employees log in with their email and password. New users can register directly from this page.*

### 📊 Employee Daily Assessment
*Employees fill in five daily metrics — stress level (0-10), working hours, fatigue score (0-10), sleep hours, and current mood — and receive an instant burnout score with a risk classification.*

### 📈 Employee History & Weekly Trends
*The history page shows a chart of burnout scores over time, highlighting upward trends that may indicate sustained overload.*

### 🧠 AI Recommendations
*After each assessment Google Gemini generates three to five personalised wellness tips based on the employee's specific scores and patterns.*

### 👔 Manager Dashboard — Team Overview
*Managers see the aggregated burnout score for their entire team, plus individual-level breakdowns to identify high-risk employees.*

### 🔥 Manager Burnout Heatmap
*A seaborn-generated heatmap (served as a base64 PNG from Flask) visualises each employee's burnout score across the working week.*

### 🐍 Streamlit Alternative Dashboard
*The optional Streamlit interface offers the same functionality in a Python-native UI, useful for data-science or internal-tool contexts.*

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Git | any | For cloning |
| Node.js | ≥ 18.x | Required for frontend |
| npm | ≥ 9.x | Comes with Node.js |
| Python | ≥ 3.11 | Required for backend |
| pip | latest | Comes with Python |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Hasini31/Employee_burnout_system.git
cd Employee_burnout_system
```

---

### 2. Backend Setup (Python / Flask)

#### a) Create a virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

#### b) Install Python dependencies

```bash
pip install -r ../requirements.txt
```

#### c) Configure environment variables

```bash
cp .env.example .env   # or create .env manually
```

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

#### d) Train the ML model

```bash
python train_model.py
```

This reads `employee_data.csv`, trains a Random Forest Regressor, and saves `burnout_model.pkl`.

#### e) (Optional) Seed sample data

```bash
python seed_test_data.py
```

#### f) Start the Flask server

```bash
python main.py
```

The API will be available at **http://localhost:5000**.

---

### 3. Frontend Setup (Next.js)

Open a **new terminal** and run:

```bash
cd frontend

# Install all dependencies
npm install

# Start the development server
npm run dev
```

The web application will be available at **http://localhost:3000**.

> The Next.js config proxies all `/api/*` calls to `http://localhost:5000`, so both services must be running simultaneously.

#### Production build

```bash
npm run build
npm run start
```

---

### 4. Streamlit Dashboard (Optional)

```bash
# From the repo root (with the Python venv active)
streamlit run streamlit_app/app.py
```

The Streamlit UI will open at **http://localhost:8501**.

> Ensure the Flask backend (`python backend/main.py`) is already running before launching Streamlit.

---

## Environment Variables

| Variable | Location | Description |
|---|---|---|
| `GEMINI_API_KEY` | `backend/.env` | Google Generative AI (Gemini) API key |
| `EMAIL_HOST` | `backend/.env` | SMTP host (e.g. `smtp.gmail.com`) |
| `EMAIL_PORT` | `backend/.env` | SMTP port (e.g. `587`) |
| `EMAIL_USER` | `backend/.env` | Sender email address |
| `EMAIL_PASS` | `backend/.env` | App-specific email password |

Get a free Gemini API key at [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey).

---

## How It Works

```
Employee submits daily form
         │
         ▼
Flask /predict endpoint
         │
         ├─► Feature extraction (stress, hours, fatigue, sleep, mood)
         ├─► Random Forest Regressor → burnout score (0–10)
         ├─► TextBlob sentiment analysis on feedback text
         ├─► Compare with this week's previous entries (trend detection)
         └─► Google Gemini → personalised recommendations
         │
         ▼
Score + risk level + AI tips returned to frontend
         │
         ▼
Manager dashboard aggregates all team scores
+ heatmap generated server-side (matplotlib/seaborn)
+ email alert if score > threshold
```

### Risk Classification

| Score Range | Risk Level | Action |
|---|---|---|
| 0 – 3.4 | 🟢 Low | Monitor normally |
| 3.5 – 6.4 | 🟡 Moderate | Check in with employee |
| 6.5 – 10 | 🔴 High | Immediate manager intervention |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register new employee |
| POST | `/login` | Employee login |
| POST | `/manager/login` | Manager login |
| POST | `/predict` | Submit daily assessment & get burnout score |
| GET | `/history` | Get employee's weekly history |
| GET | `/manager/insights` | Team overview for managers |
| GET | `/manager/heatmap` | Burnout heatmap (base64 PNG) |
| POST | `/forgot-password` | Send password reset email |
| POST | `/reset-password` | Reset password with token |

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ for healthier workplaces
</div>
