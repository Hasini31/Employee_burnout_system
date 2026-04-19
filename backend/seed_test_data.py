"""
seed_test_data.py
=================
Seed the database with 20 employees and 60 days (2 months) of records.
Includes three distinct behavioral patterns:
  - Pattern A (7 employees): Increasing burnout 
  - Pattern B (6 employees): Decreasing burnout (recovery)
  - Pattern C (7 employees): Stable burnout

Usage:
    python seed_test_data.py
    python seed_test_data.py --reset   # Clears all employees+records first
"""

import sqlite3
import os
import sys
import hashlib
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Exactly 20 employees
EMPLOYEES = [
    # Increasing burnout (7)
    {"name": "Alice Morgan",    "email": "alice@company.com",     "dept": "Engineering", "pattern": "increasing"},
    {"name": "Bob Nguyen",      "email": "bob@company.com",       "dept": "Engineering", "pattern": "increasing"},
    {"name": "Carol Patel",     "email": "carol@company.com",     "dept": "Sales",       "pattern": "increasing"},
    {"name": "David Kim",       "email": "david@company.com",     "dept": "Engineering", "pattern": "increasing"},
    {"name": "Eva Rossi",       "email": "eva@company.com",       "dept": "Marketing",   "pattern": "increasing"},
    {"name": "Frank Okafor",    "email": "frank@company.com",     "dept": "Support",     "pattern": "increasing"},
    {"name": "Grace Chen",      "email": "grace@company.com",     "dept": "Engineering", "pattern": "increasing"},
    # Decreasing burnout (6)
    {"name": "Henry Park",      "email": "henry@company.com",     "dept": "Sales",       "pattern": "decreasing"},
    {"name": "Isla Torres",     "email": "isla@company.com",      "dept": "HR",          "pattern": "decreasing"},
    {"name": "Jack Wilson",     "email": "jack@company.com",      "dept": "Engineering", "pattern": "decreasing"},
    {"name": "Karen Smith",     "email": "karen@company.com",     "dept": "Finance",     "pattern": "decreasing"},
    {"name": "Leo Zhang",       "email": "leo@company.com",       "dept": "Engineering", "pattern": "decreasing"},
    {"name": "Mia Johansen",    "email": "mia@company.com",       "dept": "Marketing",   "pattern": "decreasing"},
    # Stable burnout (7)
    {"name": "Noah Adeyemi",    "email": "noah@company.com",      "dept": "Support",     "pattern": "stable"},
    {"name": "Olivia Brown",    "email": "olivia@company.com",    "dept": "HR",          "pattern": "stable"},
    {"name": "Paul Nakamura",   "email": "paul@company.com",      "dept": "Finance",     "pattern": "stable"},
    {"name": "Quinn Reyes",     "email": "quinn@company.com",     "dept": "Engineering", "pattern": "stable"},
    {"name": "Rachel Santos",   "email": "rachel@company.com",    "dept": "Marketing",   "pattern": "stable"},
    {"name": "Sam Liu",         "email": "sam@company.com",       "dept": "Engineering", "pattern": "stable"},
    {"name": "Tina Bennett",    "email": "tina@company.com",      "dept": "Sales",       "pattern": "stable"},
]

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def get_burnout_level(score):
    if score >= 7: return "High"
    elif score >= 4: return "Medium"
    return "Low"

def get_mood_from_score(score):
    if score >= 7: return random.choice(["Stressed", "Stressed"])
    elif score >= 4: return random.choice(["Stressed", "Okay", "Okay"])
    return random.choice(["Okay", "Happy"])

def generate_score(day_idx, pattern, total_days=60):
    noise = random.uniform(-0.5, 0.5)
    if pattern == "increasing":
        base = 2.5 + (5.5 * day_idx / (total_days - 1))
    elif pattern == "decreasing":
        base = 8.0 - (5.0 * day_idx / (total_days - 1))
    else:
        base = 5.0 + random.uniform(-0.8, 0.8)
    return round(min(max(base + noise, 0.1), 10.0), 1)

def generate_stress_level(burnout_score):
    base = int(burnout_score * 0.9 + random.uniform(-1, 1))
    return max(1, min(10, base))

def generate_sleep_hours(burnout_score):
    if burnout_score >= 7:
        return round(random.uniform(4.0, 6.5), 1)
    elif burnout_score >= 4:
        return round(random.uniform(5.5, 7.5), 1)
    else:
        return round(random.uniform(6.5, 9.0), 1)

def generate_weekly_trend(score, prev_score):
    diff = score - prev_score
    if diff > 0.5: return "worsening"
    elif diff < -0.5: return "improving"
    return "stable"

def seed():
    reset = "--reset" in sys.argv
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if reset:
        print("Resetting all seeded data...")
        seeded_emails = [e["email"] for e in EMPLOYEES]
        placeholders = ','.join('?' * len(seeded_emails))
        # Get IDs
        cursor.execute(f"SELECT id FROM employees WHERE email IN ({placeholders})", seeded_emails)
        ids = [row[0] for row in cursor.fetchall()]
        if ids:
            id_placeholders = ','.join('?' * len(ids))
            cursor.execute(f"DELETE FROM records WHERE employee_id IN ({id_placeholders})", ids)
        cursor.execute(f"DELETE FROM employees WHERE email IN ({placeholders})", seeded_emails)
        conn.commit()

    total_days = 60  # 2 months
    today = datetime.now().date()
    emp_id_map = {}

    print(f"Seeding {len(EMPLOYEES)} employees...")
    for emp in EMPLOYEES:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO employees (email, password, name, department)
                VALUES (?, ?, ?, ?)
            ''', (emp["email"], hash_password("password123"), emp["name"], emp["dept"]))
            conn.commit()
            cursor.execute("SELECT id FROM employees WHERE email = ?", (emp["email"],))
            row = cursor.fetchone()
            if row:
                emp_id_map[emp["email"]] = (row[0], emp)
        except Exception as ex:
            print(f"  Error inserting {emp['name']}: {ex}")

    print(f"Seeding {total_days} days of records per employee...")
    feedbacks = {
        "increasing": [
            "Feeling overwhelmed with the project deadlines.",
            "Can't seem to keep up with everything.",
            "Very tired, struggling to focus.",
            "Too many meetings and no time to work.",
            "Workload is getting out of hand.",
            "Didn't sleep well, stressed about tomorrow.",
        ],
        "decreasing": [
            "Things are getting better this week.",
            "Starting to feel more in control.",
            "Had a good rest over the weekend.",
            "Workload feels more manageable now.",
            "Feeling positive about the current sprint.",
            "Good team support helping me cope.",
        ],
        "stable": [
            "Normal week. Nothing unusual.",
            "Work is steady, feeling okay.",
            "Average day. Keeping up with tasks.",
            "Got some tasks done, feeling decent.",
            "Routine day at the office.",
            "Steady workload, no major issues.",
        ]
    }

    for email, (emp_id, emp) in emp_id_map.items():
        pattern = emp["pattern"]
        prev_score = None

        for day_idx in range(total_days):
            record_date = today - timedelta(days=(total_days - 1 - day_idx))
            date_str = record_date.strftime('%Y-%m-%d')
            created_at = f"{date_str} {random.randint(8,17):02d}:{random.randint(0,59):02d}:00"

            score = generate_score(day_idx, pattern, total_days)
            level = get_burnout_level(score)
            mood = get_mood_from_score(score)
            fatigue = int(min(10, max(1, score * 0.9 + random.uniform(-1, 1))))
            stress_level = generate_stress_level(score)
            sleep_hours = generate_sleep_hours(score)

            work_hours = round(
                random.uniform(8.0, 12.0) if pattern == "increasing" else
                (random.uniform(7.0, 9.0) if pattern == "stable" else
                 random.uniform(6.5, 9.5)), 1)

            experience = round(random.uniform(0.5, 10.0), 1)
            sentiment_score = round(random.uniform(-0.6, 0.0) if score > 6 else random.uniform(-0.3, 0.5), 2)
            feedback = random.choice(feedbacks.get(pattern, feedbacks["stable"]))
            weekly_trend = generate_weekly_trend(score, prev_score if prev_score is not None else score)
            prev_score = score
            week_number = record_date.isocalendar()[1]
            day_of_week = record_date.weekday()

            suggestions = "Stay hydrated.|Take regular breaks.|Maintain work-life balance.|Talk to your manager."

            try:
                cursor.execute('''
                    INSERT INTO records (
                        employee_id, employee_name, mood, work_hours, fatigue, experience,
                        feedback, sentiment, sentiment_score, burnout_score, burnout_level,
                        suggestions, week_number, day_of_week, weekly_trend, submission_date,
                        created_at, sleep_hours, stress_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    emp_id, emp["name"], mood, work_hours, fatigue, experience,
                    feedback,
                    "Negative" if sentiment_score < -0.1 else ("Positive" if sentiment_score > 0.1 else "Neutral"),
                    sentiment_score, score, level, suggestions,
                    week_number, day_of_week, weekly_trend, date_str, created_at,
                    sleep_hours, stress_level
                ))
            except Exception as ex:
                print(f"  Error inserting record for {emp['name']} on {date_str}: {ex}")

        print(f"  Done: {emp['name']} ({pattern}, {total_days} records)")

    conn.commit()
    conn.close()

    print(f"\nSeeding complete!")
    print(f"  Employees: {len(emp_id_map)}")
    print(f"  Days per employee: {total_days}")
    print(f"  Total records: {len(emp_id_map) * total_days}")
    print(f"  Patterns: 7 increasing | 6 decreasing | 7 stable")
    print(f"\n  Employee Login Credentials:")
    print(f"  {'Email':<30} {'Name':<20} {'Pattern'}")
    print(f"  {'-'*70}")
    for emp in EMPLOYEES:
        print(f"  {emp['email']:<30} {emp['name']:<20} {emp['pattern']}")
    print(f"\n  Password for all: password123")
    print(f"  Manager: admin@company.com / admin123")

if __name__ == "__main__":
    seed()
