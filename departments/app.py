from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# API URL
LOGIN_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate"
DEPT_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/fetchdept1/1"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        payload = {"username": username, "password": password}

        res = requests.post(LOGIN_API, json=payload)

        if res.status_code == 200 and res.json().get("success"):
            data = res.json().get("data", {})
            session['token'] = data.get("token")
            session['username'] = data.get("userName")
            flash("Muvaffaqiyatli tizimga kirildi!", "success")
            return redirect(url_for('departments'))
        else:
            error_message = res.json().get("message", "Login muvaffaqiyatsiz!")
            flash(error_message, "danger")
    return render_template('login.html')

@app.route('/departments')
def departments():
    if 'token' not in session:
        flash("Iltimos, tizimga kiring", "warning")
        return redirect(url_for('login'))

    headers = {"Authorization": f"Bearer {session['token']}"}
    try:
        res = requests.get(DEPT_API, headers=headers)
        if res.status_code == 200:
            departments = res.json().get("data", [])
        else:
            departments = []
            flash("Bo‘limlar ma'lumotini olishda xatolik yuz berdi.", "danger")
    except Exception as e:
        departments = []
        flash(f"Server bilan bog‘lanishda xatolik: {e}", "danger")

    return render_template('departments.html', departments=departments)

@app.route('/logout')
def logout():
    session.clear()
    flash("Tizimdan chiqdingiz.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
