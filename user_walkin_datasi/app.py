from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'secret-key'  # Xavfsizlik uchun o'zgartiring

@app.route('/')
def home():
    return redirect(url_for('candidate_details'))

@app.route('/candidate', methods=['GET', 'POST'])
def candidate_details():
    if request.method == 'POST':
        application_no = request.form.get('application_no')
        if not application_no:
            flash('Iltimos, application raqamini kiriting.', 'danger')
            return redirect(url_for('candidate_details'))

        # API so'rovi
        api_url = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/candidateWalkinDetails?application_no_npf={application_no}"
        try:
            res = requests.get(api_url)
            res.raise_for_status()
            result = res.json()

            if result.get("success") and result.get("data"):
                data = result["data"][0]  # Faqat birinchi element
                return render_template("details.html", data=data)
            else:
                flash("Maʼlumot topilmadi yoki noto'g'ri application no.", "warning")
                return redirect(url_for("candidate_details"))
        except Exception as e:
            flash(f"Xatolik yuz berdi: {str(e)}", "danger")
            return redirect(url_for("candidate_details"))

    return render_template("candidate_form.html")

if __name__ == '__main__':
    app.run(debug=True)
