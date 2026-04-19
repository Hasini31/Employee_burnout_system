import requests

API_URL = "http://127.0.0.1:5000"


def login_employee(email, password):
    res = requests.post(f"{API_URL}/auth/employee/login", json={"email": email, "password": password})
    return res.json(), res.status_code


def register_employee(name, department, email, password):
    res = requests.post(f"{API_URL}/auth/employee/register", json={
        "name": name, "department": department, "email": email, "password": password
    })
    return res.json(), res.status_code


def login_manager(email, password):
    res = requests.post(f"{API_URL}/auth/manager/login", json={"email": email, "password": password})
    return res.json(), res.status_code


def predict_burnout(token, mood, work_hours, fatigue, experience, feedback):
    res = requests.post(f"{API_URL}/predict", headers={"Authorization": f"Bearer {token}"}, json={
        "mood": mood, "work_hours": work_hours, "fatigue": fatigue,
        "experience": experience, "feedback": feedback
    })
    return res.json(), res.status_code


def get_employee_history(token):
    res = requests.get(f"{API_URL}/my-records", headers={"Authorization": f"Bearer {token}"})
    return res.json(), res.status_code


def get_manager_stats(token):
    res = requests.get(f"{API_URL}/stats", headers={"Authorization": f"Bearer {token}"})
    return res.json(), res.status_code


def get_manager_insights(token):
    res = requests.get(f"{API_URL}/api/manager-insights", headers={"Authorization": f"Bearer {token}"})
    return res.json(), res.status_code
