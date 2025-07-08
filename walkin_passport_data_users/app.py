from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'

TOKEN = 'Bearer sizning-tokeningiz-bu-yerda'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        ac_year_id = request.form.get('ac_year_id')

        headers = {
            "Authorization": TOKEN
        }

        # Step 1: Get student data by academic year
        student_api = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentDetailsIndex?page=0&page_size=1000&sort=created_date&ac_year_id={ac_year_id}"
        res = requests.get(student_api, headers=headers)

        if res.status_code == 200:
            students = res.json().get('data', {}).get('Paginated_data', {}).get('content', [])
            student = next((s for s in students if s.get('auid') == username), None)

            if student:
                # Step 2: Get walk-in data using application_no_npf
                app_no = student.get('application_no_npf')
                walkin_api = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/candidateWalkinDetails?application_no_npf={app_no}"
                walkin_res = requests.get(walkin_api, headers=headers)
                walkin_data = {}
                if walkin_res.status_code == 200:
                    walkin_data = walkin_res.json().get('data', [])[0] if walkin_res.json().get('data') else {}

                return render_template('details.html', student=student, walkin=walkin_data)

            else:
                flash("Foydalanuvchi topilmadi!", "danger")
        else:
            flash("Talabalar ro‘yxatini olishda xatolik!", "danger")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
