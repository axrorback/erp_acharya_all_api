from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = "secret"

# API URLs
LOGIN_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate"
ACADEMIC_YEARS_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/academic/academic_year"
STUDENT_LIST_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentDetailsIndex"


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        res = requests.post(LOGIN_API, json={"username": username, "password": password})

        if res.status_code == 200 and res.json().get("success"):
            token = res.json()['data']['token']
            session['token'] = token
            return redirect(url_for('select_students'))
        else:
            flash("Login muvaffaqiyatsiz!", "danger")

    return render_template('login.html')


@app.route('/select-students', methods=['GET', 'POST'])
def select_students():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: get academic years
    years_res = requests.get(ACADEMIC_YEARS_API, headers=headers)
    academic_years = years_res.json().get("data", []) if years_res.status_code == 200 else []

    selected_year_id = None
    students = []
    page = 0
    total_pages = 0
    total_elements = 0
    page_size = 50

    if request.method == 'POST':
        selected_year_id = request.form.get("ac_year_id")
        page = int(request.form.get("page", 0))

        # Step 2: get students
        params = {
            "page": page,
            "page_size": page_size,
            "sort": "created_date",
            "ac_year_id": selected_year_id
        }
        student_res = requests.get(STUDENT_LIST_API, headers=headers, params=params)

        if student_res.status_code == 200:
            student_data = student_res.json().get("data", {}).get("Paginated_data", {})
            students = student_data.get("content", [])
            total_pages = student_data.get("totalPages", 1)
            total_elements = student_data.get("totalElements", len(students))

    return render_template(
        "select_students.html",
        academic_years=academic_years,
        selected_year_id=selected_year_id,
        students=students,
        total_pages=total_pages,
        total_elements=total_elements,
        page=page,
        page_size=page_size
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
