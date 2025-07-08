from flask import Flask, render_template, request, redirect, url_for, flash
import requests, os

app = Flask(__name__)
app.secret_key = 'secret-key'

# Lokalda saqlanadigan rasm papkasi
IMAGE_FOLDER = 'static/images'
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Tokenni mana bu yerga kiriting
TOKEN = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJ1c2VyVHlwZVwiOlwic3RhZmZcIixcInVzZXJOYW1lXCI6XCJ2aWduZXNod2FyYW4zMVwiLFwidXNlcklkXCI6NTh9IiwidXNlclR5cGUiOiJzdGFmZiIsInVzZXJOYW1lIjoidmlnbmVzaHdhcmFuMzEiLCJleHAiOjE3NTE1OTk5MTIsInVzZXJJZCI6NTgsImlhdCI6MTc1MTU2MzkxMn0.NMlvHNaB_pHVx7NI4gR6b3yBQdUeyqZVbeoBjTW81BpNPMm1TC-QErcM689fSsiV7mXHhDPxrjCmsuux9Bajkw'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        auid = request.form.get('auid')
        headers = {"Authorization": TOKEN}
        api_url = "https://acharyajava.uz/AcharyaInstituteUZB/api/student/fetchAllStudentIdCardHistory?page=0&page_size=1000&sort=created_date"

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            students = response.json().get('data', {}).get('Paginated_data', {}).get('content', [])
            for student in students:
                if student.get('auid') == auid:
                    image_path = student.get('student_image_path')
                    full_url = f"https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentImageDownload?student_image_attachment_path={image_path}"
                    image_name = image_path.split('/')[-1]
                    local_image_path = os.path.join(IMAGE_FOLDER, image_name)

                    if not os.path.exists(local_image_path):
                        img_res = requests.get(full_url, headers=headers)
                        if img_res.status_code == 200:
                            with open(local_image_path, 'wb') as f:
                                f.write(img_res.content)

                    return render_template('show_image.html', student=student,
                                           image_url=url_for('static', filename=f'images/{image_name}'))
            flash("Bunday foydalanuvchi topilmadi", "danger")
        else:
            flash("API muammosi!", "danger")
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)