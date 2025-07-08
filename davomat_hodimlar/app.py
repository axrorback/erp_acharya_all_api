import os
import requests
from flask import Flask, render_template, request, session, redirect, flash, url_for
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

LOGIN_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate"
ATTENDANCE_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/employee/employeeAttendance"
WORKING_DAYS_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/hr/getWorkingDaysByMonth"

# LOGIN ROUTE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        res = requests.post(LOGIN_API, json={"username": username, "password": password})

        if res.status_code == 200 and res.json().get("success"):
            token = res.json()['data']['token']
            session['token'] = token
            return redirect(url_for('attendance_view'))
        else:
            flash("Login muvaffaqiyatsiz!", "danger")

    return render_template('login.html')

# ATTENDANCE ROUTE
@app.route('/attendance', methods=['GET', 'POST'])
def attendance_view():
    if 'token' not in session:
        return redirect(url_for('login'))

    token = session['token']
    month = datetime.now().month
    year = datetime.now().year

    if request.method == 'POST':
        month = int(request.form.get("month", month))
        year = int(request.form.get("year", year))

    payload = {
        "month": month,
        "year": year
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(ATTENDANCE_API, json=payload, headers=headers)
        print(f"🔁 Attendance Request: {response.status_code}")
        attendance = response.json().get('data', []) if response.status_code == 200 else []
    except Exception as e:
        print("❌ Attendance xato:", e)
        attendance = []

    return render_template(
        'attendence.html',
        attendance=attendance,
        month=month,
        year=year
    )

@app.route('/logout')
def logout():
    session.clear()  # sessiyani tozalash
    flash("Siz tizimdan chiqdingiz", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    print("🚀 Flask ilova ishga tushdi! http://localhost:5000")
    app.run(debug=True)
