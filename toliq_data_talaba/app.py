from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests, os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['IMAGE_FOLDER'] = 'static/images'

# Token olish uchun login API
LOGIN_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate'

# Academic year ro'yxati
YEAR_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/common/academicYearList'

# Student list API (pagination bilan)
STUDENT_LIST_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentDetailsIndex'

# Student image path
IMAGE_DOWNLOAD_URL = 'https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentImageDownload?student_image_attachment_path='

# Walk-in API (optional)
WALKIN_API = 'https://acharyajava.uz/AcharyaInstituteUZB/api/reports/paidPaymentReportOfStudentAndCandidate'

# ------------------------ LOGIN PAGE ------------------------
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
            return redirect(url_for('select_year'))
        else:
            error_message = res.json().get("message", "Login muvaffaqiyatsiz!")
            flash(error_message, "danger")
    return render_template('login.html')


# ------------------------ ACADEMIC YEAR ------------------------
@app.route('/years')
def select_year():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    headers = {"Authorization": f"Bearer {token}"}
    print("📡 Academic Year ro'yxatini olish...")

    try:
        res = requests.get(YEAR_API, headers=headers)

        print(f"🔁 Academic Year Request:\nStatus: {res.status_code}\nBody: {res.text}")

        if res.status_code == 200 and res.json().get("success"):
            years = res.json().get("data", [])
            return render_template("select_year.html", years=years)
        else:
            flash("❌ Academic Year ma'lumotlari olinmadi", "danger")

    except Exception as e:
        print(f"🚨 Academic Year olishda xatolik: {e}")
        flash("API xatolik yuz berdi", "danger")

    return redirect(url_for('login'))

# ------------------------ STUDENT LIST ------------------------
@app.route('/students/<int:year_id>')
def student_list(year_id):
    token = session.get('token')
    headers = {"Authorization": f"Bearer {token}"}
    page = int(request.args.get("page", 0))
    print(f"📥 Student list yuklanmoqda. YearID: {year_id}, Page: {page}")
    try:
        response = requests.get(f"{STUDENT_LIST_API}?page={page}&page_size=20&sort=created_date&ac_year_id={year_id}", headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {}).get("Paginated_data", {}).get("content", [])
            print(f"✅ Studentlar topildi: {len(data)} ta")
            return render_template("student_list.html", students=data, page=page, year_id=year_id)
        else:
            print(f"❌ Student list API xatolik: {response.status_code}")
            flash("Talabalar ro‘yxatini olishda xatolik!", "danger")
    except Exception as e:
        print(f"🚨 Student list exception: {e}")
        flash("Xatolik!", "danger")
    return redirect(url_for('select_year'))

# ------------------------ STUDENT DETAIL ------------------------
@app.route('/student/<username>')
def student_detail(username):
    token = session.get('token')
    headers = {"Authorization": f"Bearer {token}"}

    print(f"📥 Talaba ma'lumotlari yuklanmoqda: {username}")
    try:
        # Get all students to find the one with this username
        student_list = requests.get(f"{STUDENT_LIST_API}?page=0&page_size=1000&sort=created_date", headers=headers)
        if student_list.status_code == 200:
            students = student_list.json().get("data", {}).get("Paginated_data", {}).get("content", [])
            student = next((s for s in students if s["auid"] == username), None)

            if student:
                print(f"✅ Talaba topildi: {student['student_name']}")
                # Download image
                image_path = student.get('student_image_path')
                image_url = None
                if image_path:
                    image_name = image_path.split("/")[-1]
                    image_file_path = os.path.join(app.config['IMAGE_FOLDER'], image_name)
                    if not os.path.exists(image_file_path):
                        img_response = requests.get(IMAGE_DOWNLOAD_URL + image_path, headers=headers)
                        if img_response.status_code == 200:
                            with open(image_file_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"📸 Rasm yuklandi: {image_name}")
                    image_url = url_for('static', filename=f'images/{image_name}')

                # Walkin data (optional)
                walkin_data = requests.get(WALKIN_API, headers=headers)
                walkin = None
                if walkin_data.status_code == 200:
                    all_walkin = walkin_data.json().get("data", {}).get("paymeTransactionDetails", [])
                    walkin = next((w for w in all_walkin if w["auid"] == username), None)
                    print("📄 Walkin ma'lumotlari tekshirildi.")

                return render_template("student_detail.html", student=student, image_url=image_url, walkin=walkin)

            else:
                print("❌ Talaba topilmadi.")
                flash("Foydalanuvchi topilmadi!", "danger")
        else:
            print(f"❌ Talabalarni olishda xatolik: {student_list.status_code}")
            flash("Talabalarni olishda xatolik!", "danger")
    except Exception as e:
        print(f"🚨 Detail exception: {e}")
        flash("Xatolik!", "danger")

    return redirect(url_for('select_year'))

# ------------------------ RUNNING ------------------------
if __name__ == '__main__':
    if not os.path.exists(app.config['IMAGE_FOLDER']):
        os.makedirs(app.config['IMAGE_FOLDER'])
        print("📁 static/images papkasi yaratildi.")

    print("🚀 Flask ilova ishga tushdi! http://localhost:5000")
    app.run(debug=True)
