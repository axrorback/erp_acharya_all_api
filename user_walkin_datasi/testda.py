from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ⬇️ Login sahifasi
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        payload = {"username": username, "password": password}

        login_url = "https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate"
        response = requests.post(login_url, json=payload)

        if response.status_code == 200 and response.json().get("success"):
            token = response.json()["data"]["token"]
            session['token'] = token
            flash("Tizimga muvaffaqiyatli kirdingiz!", "success")
            return redirect(url_for('candidate_form'))
        else:
            flash("Login xatoligi: " + response.json().get("message", "Noma'lum xato"), "danger")
    return render_template("login.html")


# ⬇️ Form sahifasi (username kiritish)
@app.route('/candidate-form')
def candidate_form():
    return render_template("candidate_form.html")


# ⬇️ Candidate ma'lumotlarini ko‘rish
@app.route('/candidate-details', methods=['POST'])
def candidate_details():
    username = request.form.get('username')
    token = session.get('token')

    if not username:
        flash("Username kiritilmadi", "warning")
        return redirect(url_for("candidate_form"))

    api_url = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/candidateWalkinDetails?auid={username}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200 and response.json().get("success"):
        data = response.json().get("data")
        if data:
            return render_template("details.html", data=data[0])
        else:
            flash("Foydalanuvchi topilmadi", "warning")
    else:
        flash("API xatoligi: " + response.text, "danger")

    return redirect(url_for("candidate_form"))


if __name__ == '__main__':
    app.run(debug=True)
