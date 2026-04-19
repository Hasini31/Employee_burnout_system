import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train():
    print("Loading dataset...")
    # Load the provided dataset
    df = pd.read_csv('../employee_data.csv')
    
    # Drop missing values
    df = df.dropna(subset=['Mental Fatigue Score', 'Burn Rate', 'Resource Allocation'])
    
    print("Extracting features...")
    # Engineer the requested features from the original dataset
    # fatigue = Mental Fatigue Score (0-10)
    fatigue = df['Mental Fatigue Score']
    
    # workingHours = Derived from Resource Allocation (1-10 mapped to 4-12 hours)
    workingHours = df['Resource Allocation'] * 0.8 + 4
    
    # stressLevel = Derived from Mental Fatigue Score with some noise
    np.random.seed(42)
    stressLevel = df['Mental Fatigue Score'] + np.random.normal(0, 1, size=len(df))
    stressLevel = np.clip(stressLevel, 0, 10)
    
    # sleepHours = Inversely proportional to fatigue
    sleepHours = 10 - df['Mental Fatigue Score'] * 0.5 + np.random.normal(0, 0.5, size=len(df))
    sleepHours = np.clip(sleepHours, 4, 10)
    
    # burnoutScore = Burn Rate (0.0-1.0 mapped to 0-10)
    burnoutScore = df['Burn Rate'] * 10
    
    # mood = 0 (Happy), 1 (Okay), 2 (Stressed) based on Burn Rate thresholds
    mood = np.where(burnoutScore < 3.5, 0, np.where(burnoutScore < 6.5, 1, 2))
    
    X = pd.DataFrame({
        'stressLevel': stressLevel,
        'workingHours': workingHours,
        'fatigue': fatigue,
        'sleepHours': sleepHours,
        'mood': mood
    })
    y = burnoutScore
    
    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print("Evaluating model...")
    score = model.score(X, y)
    print(f"R^2 Score: {score:.4f}")
    
    model_path = os.path.join(os.path.dirname(__file__), 'burnout_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved successfully to {model_path}")

if __name__ == '__main__':
    train()
