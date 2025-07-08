from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'secret-key'

# Tokenni shu yerga joylashtiring
TOKEN = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJ1c2VyVHlwZVwiOlwic3RhZmZcIixcInVzZXJOYW1lXCI6XCJIUmFkbWluXCIsXCJ1c2VySWRcIjoxM30iLCJ1c2VyVHlwZSI6InN0YWZmIiwidXNlck5hbWUiOiJIUmFkbWluIiwiZXhwIjoxNzUxNjAyNzkwLCJ1c2VySWQiOjEzLCJpYXQiOjE3NTE1NjY3OTB9.i3Vj4_B5-Xl0fdQ3dqIl7SVVFfiHSnM77mLV6MAQSUM_r4X9yeMDlO9uyHdoHKmVevJXbA_Mq4SSNcjRlXNq-Q'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Iltimos, username (AUID) kiriting", "warning")
            return redirect(url_for('index'))

        headers = {"Authorization": TOKEN}

        # 1. AUID orqali application_no topamiz
        payme_api = "https://acharyajava.uz/AcharyaInstituteUZB/api/reports/paidPaymentReportOfStudentAndCandidate?page=0&pageSize=100000&sort=sign_time"
        payme_response = requests.get(payme_api, headers=headers)

        if payme_response.status_code == 200:
            payments = payme_response.json().get('data', {}).get('paymeTransactionDetails', [])
            for p in payments:
                if p.get('auid') == username:
                    application_no = p.get('application_no_npf')

                    # 2. Endi application_no orqali walkin ma'lumotlarini topamiz
                    walkin_api = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/candidateWalkinDetails?application_no_npf={application_no}"
                    walkin_res = requests.get(walkin_api, headers=headers)

                    if walkin_res.status_code == 200:
                        data = walkin_res.json().get("data", [])
                        if data:
                            return render_template("walkin_details.html", info=data[0])
                        else:
                            flash("Walkin ma'lumot topilmadi", "danger")
                    else:
                        flash("Walkin API xatolik", "danger")
                    break
            else:
                flash("Username topilmadi", "danger")
        else:
            flash("To‘lovlar API xatolik", "danger")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
