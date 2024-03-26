from flask import Flask, render_template, request, redirect, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import tempfile


uri = "mongodb+srv://Ostap:zoloto@cluster0.qnbbr3y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

myclient = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

mydb = myclient['project']
collection = mydb['tasks']
vacancies = mydb['vacancies']

app = Flask(__name__)
app.secret_key = 'zoloto'

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'

PARENT_FOLDER_ID = '1pYZe55TA7d6x1mXR24CSwypWtesxfj5s'

CREDS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
service = build('drive', 'v3', credentials=CREDS)

@app.route('/')
def index():
    user_data = session.get('user_data')
    is_student = False
    if user_data and user_data['type'] == 'student':
        is_student = True
    return render_template('afterentr.html', user=user_data, is_student=is_student)

@app.route('/submit_employer', methods=['POST'])
def register_employer():
    if request.method == 'POST':

        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        company_name = request.form['company_name']
        if 'image' in request.files:
            image_data = request.files['image']
            file_metadata = {
                'name': image_data.filename,
                'parents': [PARENT_FOLDER_ID]
            }
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                image_data.save(temp_file)
                temp_file.seek(0)
                file = service.files().create(
                    body=file_metadata,
                    media_body=MediaFileUpload(temp_file.name, mimetype=image_data.content_type),
                ).execute()
                file_id = file.get('id')
            

        for field in [name, surname, company_name, password, email]:
            if not field:
                return "Please fill in all fields."

        existing_user = collection.find_one({'email': email})
        if existing_user:
            return 'Email already exists'

        if file_id:
            image_link = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
        data = {
            'name': name.strip().title(),
            'surname': surname.strip().title(),
            'email': email.strip().lower(),
            'password': password,
            'company_name': company_name,
            'profile_image': image_link,
            'type': 'employer'
        }
        collection.insert_one(data)
        session['user_data'] = data
        print(session['user_data'])
        if '_id' in session['user_data']:
            data['_id'] = str(session['user_data']['_id'])
        return redirect('/')

@app.route('/submit_student1', methods=['POST'])
def register_student1():
    if request.method == 'POST':

        name = request.form['name']
        session['name'] = name.strip().title()
        surname = request.form['surname']
        session['surname'] = surname.strip().title()
        session['age'] = request.form['age']
        session['password'] = request.form['password']
        mail = request.form['email']
        session['email'] = mail.lower()
        file_id = None  # Set a default value for file_id

        if 'image' in request.files:
            image_data = request.files['image']
            file_metadata = {
                'name': image_data.filename,
                'parents': [PARENT_FOLDER_ID]
            }
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                image_data.save(temp_file)
                temp_file.seek(0)
                file = service.files().create(
                    body=file_metadata,
                    media_body=MediaFileUpload(temp_file.name, mimetype=image_data.content_type),
                ).execute()
                file_id = file.get('id')

        if file_id:
            image_link = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
            session['profile_image'] = image_link

        existing_user = collection.find_one({'email': session['email']})
        if existing_user:
            email_error = "Email already exists. Please choose a different email address or sign in."
            return render_template('sign_up_student.html', email_error=email_error)

        if session['email'] and not session['email'].endswith('ucu.edu.ua'):
            email_ucu_error = "You cannot register here. You are not an UCU student!"
            return render_template('sign_up_student.html', email_ucu_error=email_ucu_error)

        for field in ['name', 'surname', 'age', 'password', 'email']:
            if not session[field]:
                null_error = "Please fill in all fields."
                return render_template('sign_up_student.html', null_error=null_error)

        if not 16 < int(session['age']) < 120:
            age_error = 'Please fill the correct information about your age.'
            return render_template('sign_up_student.html', age_error=age_error)

        return redirect('/sign_up_next')
    return render_template('sign_up_student.html')

@app.route('/submit_student2', methods=['POST'])
def register_student2():
    if request.method == 'POST':
        experience_it = "yes" if request.form.get('experience_it') else "no"
        session['experience_it'] = experience_it
        session['academic_degree'] = request.form.get('academic_degree')

        data = {
            'name': session.get('name'),
            'surname': session.get('surname'),
            'email': session.get('email'),
            'age': session.get('age'),
            'password': session.get('password'),
            'experience_it': session.get('experience_it'),
            'academic_degree': session.get('academic_degree'),
            'profile_image': session.get('profile_image'),
            'type': 'student'
        }

        collection.insert_one(data)
        session['user_data'] = data
        if '_id' in session['user_data']:
            data['_id'] = str(session['user_data']['_id'])
        return redirect('/')
    return render_template('sign_up_next.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = collection.find_one({'email': email, 'password': password})

        if user:
            session['user_data'] = user
            if '_id' in session['user_data']:
                user['_id'] = str(session['user_data']['_id'])
            if user['type'] == 'student':
                return redirect('/')
            if user['type'] == 'employer':
                return redirect('/')
        invalid_error = "Invalid email or password"
        return render_template('login.html', invalid_error=invalid_error)

    if request.method == 'GET':
        return render_template('login.html')

@app.route('/add_job_offer', methods=['POST', 'GET'])
def add_job_offer():
    if request.method == 'POST':

        job_name = request.form['jobName']
        skills = request.form['skills']
        employment = request.form['employment']
        description = request.form['description']

        job_offer_data = {
            'email': session['user_data']['email'],
            'company_name': collection.find_one({'email': session['user_data']['email']})['company_name'],
            'job_name': job_name,
            'skills': skills,
            'employment': employment,
            'description': description
        }
        vacancies.insert_one(job_offer_data)

        return redirect('/profile_employer.html')

@app.route('/sign_out')
def sign_out():
    session.clear()
    return redirect('/')

@app.route('/delete_account')
def deleter():
    user_data = session.get('user_data')
    email = user_data['email']
    collection.delete_one({'email': email})
    session.clear()
    return redirect('/')

@app.route('/login.html')
def login_route():
    return render_template('login.html')

@app.route('/sign_up_student.html')
def register_st():
    return render_template('sign_up_student.html')

@app.route('/sign_up_em.html')
def register_em():
    return render_template('sign_up_em.html')

@app.route('/as_student.html')
def as_student_clear():
    session.clear()
    return redirect('/sign_up_student.html')

@app.route('/as_employer.html')
def as_employer_clear():
    session.clear()
    return redirect('/sign_up_em.html')

@app.route('/profile_student.html')
def profile_st():
    user_email = session['user_data']['email']
    user_data = collection.find_one({'email': user_email})
    return render_template('profile_student.html', user_data=user_data)

@app.route('/profile_employer.html')
def profile_em():
    user_email = session['user_data']['email']
    user_data = collection.find_one({'email': user_email})
    return render_template('profile_employer.html', user_data=user_data, vacancies=vacancies)

@app.route('/main_page')
def main_page():
    return render_template('main_page.html', vacancies=list(vacancies.find()))

@app.route('/main_page_employer')
def main_page_employer():
    students = collection.find({'type': 'student'})
    students = list(students)
    return render_template('main_page_employer.html', students=students)

@app.route('/sign_up_next')
def student_next():
    return render_template('sign_up_next.html')

@app.route('/update_profile_personal', methods=['POST', "GET"])
def update_profile_personal():
    # Retrieve updated data from the form
    name = request.form['name'].title()
    surname = request.form['surname'].title()
    age = request.form['age'] if request.form['age'] in range(16, 120) else \
collection.find_one({'email': session['user_data']['email']})['age']
    phone = request.form['phone-number']

    session['user_data']['name'] = name
    session['user_data']['surname'] = surname
    session['user_data']['age'] = age
    session['user_data']['phone'] = phone

    email = session['user_data']['email']
    collection.update_one({'email': email}, {'$set': {'name': name, 'surname': surname, 'age': age, 'phone': phone}})

    return redirect('profile_student.html')

@app.route('/update_profile_skills', methods=['POST', "GET"])
def update_profile_skills():
    # Retrieve updated data from the form
    skills = request.form['skills']
    experience = request.form['experience']
    english = request.form['english']
    degree = request.form['degree']
    description = request.form['description']

    session['user_data']['skills'] = skills
    session['user_data']['experience'] = experience
    session['user_data']['english'] = english
    session['user_data']['degree'] = degree
    session['user_data']['description'] = description

    email = session['user_data']['email']
    collection.update_one({'email': email}, {'$set': {'skills': skills, 'experience_it': experience, \
'english': english, 'academic_degree': degree, 'description': description}})

    # Update profile in the database with the new data

    # Return a response (e.g., success message or updated profile data)
    return redirect('profile_student.html')

@app.route('/update_profile_employer', methods=['POST', "GET"])
def update_profile_employer():
    # Retrieve updated data from the form
    name = request.form['name'].title()
    surname = request.form['surname'].title()
    age = request.form['company-name']
    phone = request.form['phone-number']

    session['user_data']['name'] = name
    session['user_data']['surname'] = surname
    session['user_data']['company-name'] = age
    session['user_data']['phone'] = phone

    email = session['user_data']['email']
    collection.update_one({'email': email}, {'$set': {'name': name, 'surname': surname, 'company_name': age, 'phone': phone}})

    return redirect('profile_employer.html')

if __name__ == '__main__':
    app.run(debug=True)
