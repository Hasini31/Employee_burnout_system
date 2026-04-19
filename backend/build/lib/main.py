from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pickle
import os
from textblob import TextBlob
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            mood TEXT,
            work_hours REAL,
            fatigue INTEGER,
            experience REAL,
            feedback TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            burnout_score REAL,
            burnout_level TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Load ML model
def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

# Analyze sentiment using TextBlob
def analyze_sentiment(text):
    if not text or text.strip() == '':
        return 'Neutral', 0.0
    
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return 'Positive', polarity
    elif polarity < -0.1:
        return 'Negative', polarity
    else:
        return 'Neutral', polarity

# Generate suggestions based on burnout level and sentiment
def generate_suggestions(burnout_level, sentiment):
    suggestions = []
    
    if burnout_level == 'High':
        suggestions.extend([
            "Take immediate rest and consider taking time off",
            "Speak with your manager about workload reduction",
            "Consider professional counseling or therapy",
            "Practice stress-relief techniques like meditation"
        ])
    elif burnout_level == 'Medium':
        suggestions.extend([
            "Schedule regular breaks throughout the day",
            "Set clear boundaries between work and personal time",
            "Engage in physical activities or exercise",
            "Connect with colleagues for support"
        ])
    else:
        suggestions.extend([
            "Maintain your current work-life balance",
            "Continue practicing healthy habits",
            "Stay connected with your team"
        ])
    
    if sentiment == 'Negative':
        suggestions.extend([
            "Consider talking to HR about your concerns",
            "Explore mental wellness resources",
            "Practice gratitude and positive thinking"
        ])
    
    return suggestions

# Encode mood for model prediction
def encode_mood(mood):
    mood_map = {'Happy': 0, 'Okay': 1, 'Stressed': 2}
    return mood_map.get(mood, 1)

# Calculate burnout score
def calculate_burnout(mood, work_hours, fatigue, experience, sentiment_score, model=None):
    # Encode features
    mood_encoded = encode_mood(mood)
    
    # If model exists, use it for prediction
    if model is not None:
        try:
            features = np.array([[mood_encoded, work_hours, fatigue, experience]])
            prediction = model.predict(features)[0]
            # Normalize prediction to 0-100 scale
            burnout_score = min(max(float(prediction) * 100, 0), 100)
        except Exception as e:
            print(f"Model prediction error: {e}")
            burnout_score = calculate_rule_based_burnout(mood_encoded, work_hours, fatigue, experience, sentiment_score)
    else:
        burnout_score = calculate_rule_based_burnout(mood_encoded, work_hours, fatigue, experience, sentiment_score)
    
    return burnout_score

def calculate_rule_based_burnout(mood_encoded, work_hours, fatigue, experience, sentiment_score):
    # Rule-based calculation when model is not available
    base_score = 0
    
    # Mood contribution (0-25 points)
    base_score += mood_encoded * 12.5
    
    # Work hours contribution (0-25 points)
    if work_hours > 10:
        base_score += 25
    elif work_hours > 8:
        base_score += (work_hours - 8) * 12.5
    
    # Fatigue contribution (0-30 points)
    base_score += fatigue * 3
    
    # Experience adjustment (-10 to +10 points)
    if experience < 1:
        base_score += 10
    elif experience > 5:
        base_score -= 5
    
    # Sentiment adjustment (-10 to +10 points)
    base_score -= sentiment_score * 10
    
    return min(max(base_score, 0), 100)

# Determine burnout level
def get_burnout_level(score):
    if score >= 70:
        return 'High'
    elif score >= 40:
        return 'Medium'
    else:
        return 'Low'

# Initialize database on startup
init_db()

# Load model
model = load_model()

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Extract input features
        employee_name = data.get('employee_name', 'Anonymous')
        mood = data.get('mood', 'Okay')
        work_hours = float(data.get('work_hours', 8))
        fatigue = int(data.get('fatigue', 5))
        experience = float(data.get('experience', 1))
        feedback = data.get('feedback', '')
        
        # Validate inputs
        if fatigue < 0 or fatigue > 10:
            return jsonify({'error': 'Fatigue must be between 0 and 10'}), 400
        if work_hours < 0 or work_hours > 24:
            return jsonify({'error': 'Work hours must be between 0 and 24'}), 400
        if experience < 0:
            return jsonify({'error': 'Experience cannot be negative'}), 400
        
        # Analyze sentiment
        sentiment, sentiment_score = analyze_sentiment(feedback)
        
        # Calculate burnout score
        burnout_score = calculate_burnout(mood, work_hours, fatigue, experience, sentiment_score, model)
        burnout_level = get_burnout_level(burnout_score)
        
        # Generate suggestions
        suggestions = generate_suggestions(burnout_level, sentiment)
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (employee_name, mood, work_hours, fatigue, experience, feedback, 
                               sentiment, sentiment_score, burnout_score, burnout_level, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_name, mood, work_hours, fatigue, experience, feedback, 
              sentiment, sentiment_score, burnout_score, burnout_level, '|'.join(suggestions)))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'id': record_id,
            'employee_name': employee_name,
            'mood': mood,
            'work_hours': work_hours,
            'fatigue': fatigue,
            'experience': experience,
            'feedback': feedback,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'burnout_score': round(burnout_score, 1),
            'burnout_level': burnout_level,
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/records')
def get_records():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM records ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'employee_name': row[1],
                'mood': row[2],
                'work_hours': row[3],
                'fatigue': row[4],
                'experience': row[5],
                'feedback': row[6],
                'sentiment': row[7],
                'sentiment_score': row[8],
                'burnout_score': row[9],
                'burnout_level': row[10],
                'suggestions': row[11].split('|') if row[11] else [],
                'created_at': row[12]
            })
        
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total employees
        cursor.execute('SELECT COUNT(*) FROM records')
        total_employees = cursor.fetchone()[0]
        
        # High burnout cases
        cursor.execute("SELECT COUNT(*) FROM records WHERE burnout_level = 'High'")
        high_burnout = cursor.fetchone()[0]
        
        # Medium burnout cases
        cursor.execute("SELECT COUNT(*) FROM records WHERE burnout_level = 'Medium'")
        medium_burnout = cursor.fetchone()[0]
        
        # Low burnout cases
        cursor.execute("SELECT COUNT(*) FROM records WHERE burnout_level = 'Low'")
        low_burnout = cursor.fetchone()[0]
        
        # Average burnout score
        cursor.execute('SELECT AVG(burnout_score) FROM records')
        avg_burnout = cursor.fetchone()[0] or 0
        
        # Work hours vs fatigue data for scatter plot
        cursor.execute('SELECT work_hours, fatigue, burnout_level FROM records')
        scatter_data = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'total_employees': total_employees,
            'high_burnout': high_burnout,
            'medium_burnout': medium_burnout,
            'low_burnout': low_burnout,
            'avg_burnout': round(avg_burnout, 1),
            'scatter_data': [{'work_hours': r[0], 'fatigue': r[1], 'burnout_level': r[2]} for r in scatter_data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
