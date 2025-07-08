from imaplib import Debug

from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = "super-secret"

LOGIN_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate'
STUDENT_LIST_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentDetailsIndex'
STUDENT_DETAIL_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/student/getAllStudentDetailsData'
WALKIN_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/reports/walkInReportForSingleStudent'

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        payload = {"userName": username, "password": password}

        res = requests.post(LOGIN_API, json=payload)
        print(f"🔁 LOGIN: {res.status_code} | {res.text}")

        if res.status_code == 200 and res.json().get("success"):
            data = res.json().get("data", {})
            session['token'] = data.get("token")
            session['username'] = data.get("userName")
            return redirect(url_for('select_year'))
        else:
            flash("Login xatolik! Parol yoki login noto‘g‘ri!", "danger")
    return render_template("login.html")


# ---------------- ACADEMIC YEAR TANLASH (statik) ----------------
@app.route('/years')
def select_year():
    return render_template('select_year.html')


# ---------------- STUDENT RO‘YXATI ----------------
@app.route('/students')
def students():
    token = session.get("token")
    if not token:
        return redirect(url_for('login'))

    year_id = request.args.get('year_id', '20')  # Default 2024-25
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{STUDENT_LIST_API}?page=0&page_size=100&sort=created_date&ac_year_id={year_id}"

    res = requests.get(url, headers=headers)
    students = []
    if res.status_code == 200:
        students = res.json().get("data", {}).get("Paginated_data", {}).get("content", [])
    else:
        flash("Talabalarni olishda xatolik!", "danger")

    return render_template("students.html", students=students)


# ---------------- STUDENT DETAIL ----------------
@app.route('/student/<int:student_id>')
def student_detail(student_id):
    token = session.get("token")
    if not token:
        return redirect(url_for('login'))

    headers = {"Authorization": f"Bearer {token}"}

    # 1. STUDENT DETAIL
    detail_url = f"{STUDENT_DETAIL_API}/{student_id}"
    detail_res = requests.get(detail_url, headers=headers)
    print(f"🔍 DETAIL: {detail_res.status_code}")

    student_data = {}
    walkin_data = []

    if detail_res.status_code == 200:
        student_data = detail_res.json().get("data", {})
        application_no = student_data.get("application_no_npf")

        # 2. WALKIN DATA
        if application_no:
            walkin_url = f"{WALKIN_API}?application_no_npf={application_no}"
            walkin_res = requests.get(walkin_url, headers=headers)
            print(f"🚶 WALKIN: {walkin_res.status_code}")

            if walkin_res.status_code == 200:
                walkin_data = walkin_res.json().get("data", [])

    return render_template("student_detail.html", student=student_data, walkins=walkin_data)
if __name__ == "__main__":
    app.run(debug=True)