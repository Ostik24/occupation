from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import random
import string
import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import certifi
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import tempfile
import os


uri = "mongodb+srv://Sofia:cfvgfhf1601@cluster0.zw63kf1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

myclient = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

mydb = myclient['ucupation']
collection = mydb['users']
vacancies = mydb['vacancies']

app = Flask(__name__)

app.secret_key = 'zoloto'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ucupation@gmail.com'
app.config['MAIL_PASSWORD'] = 'ykyv mxib gixw gebz'
app.config['MAIL_DEFAULT_SENDER'] = 'ucupation@gmail.com'
mail = Mail(app)

SCOPES = ['https://www.googleapis.com/auth/drive']
# SERVICE_ACCOUNT_FILE = 'service_account.json'
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')

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

@app.route('/reset_password', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['new-password']
        new_password = request.form['new-again-password']

        session.clear()
        session['email'] = email

        if password and password == new_password and collection.find_one({'email': email}):

            pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
            regex = re.compile(pattern)
            match = regex.match(password)
            if not match:
                regex_password_error = ["Your password must contain at least 8 characters,", "including at least one uppercase and lowercase letter, and one digit."]
                return render_template('reset-password.html', regex_password_error=regex_password_error)

            session['password'] = password

            session['verification_code'] = generate_verification_code()
            
            msg = Message('Email Verification', recipients=[email], body = f'Your verification code is: {session["verification_code"]}')
            mail.send(msg)

            session['types'] = "reset"

            return render_template('check-email.html', types=session['types'])
        existing_email_error = "The email is not found or passwords do not match."
        return render_template('reset-password.html', existing_email_error=existing_email_error)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_code = request.form['code']
        if entered_code == session.get('verification_code'):

            if session['types'] == "reset":
                user = collection.find_one({'email': session['email']})
                if user:
                    collection.update_one({'_id': user['_id']}, {'$set': {'password': session["password"]}})
                    session['user_data'] = user
                    data = session['user_data']
                    if '_id' in session['user_data']:
                        data['_id'] = str(session['user_data']['_id'])
                    return redirect('/')

            if session['types'] == 'employer':
                data = {
                'name': session['name'],
                'surname': session['surname'],
                'email': session['email'],
                'password': session['password'],
                'company_name': session['company_name'],
                'profile_image': session.get('profile_image'),
                'type': 'employer'
                }

                collection.insert_one(data)
                session['user_data'] = data
                if '_id' in session['user_data']:
                    data['_id'] = str(session['user_data']['_id'])
                return redirect('/')
            if session['types'] == 'student':
                return redirect('/sign_up_next')
    invalid_code_error = "Your code doesn't match. Try again!"
    return render_template('check-email.html', invalid_code_error=invalid_code_error)

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/reset-password')
def res():
    return render_template('reset-password.html')

@app.route('/submit_employer', methods=['POST'])
def register_employer():
    if request.method == 'POST':

        session['name'] = request.form['name'].strip().title()
        session['surname'] = request.form['surname'].strip().title()
        session['email'] = request.form['email'].strip().lower()
        session['password'] = request.form['password']
        session['company_name'] = request.form['company_name']
        file_id = None

        image_data = request.files['image']
        if image_data.filename:
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
            session['profile_image'] = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"

        for field in [session['name'], session['surname'], session['company_name'], session['email']]:
            if not field:
                null_error = "Please fill in all fields."
                return render_template('sign_up_em.html', null_error=null_error)

        existing_user = collection.find_one({'email': session['email']})
        if existing_user:
            email_error = "Email already exists. Please choose a different email address or sign in."
            return render_template('sign_up_em.html', email_error=email_error)
        
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
        regex = re.compile(pattern)
        match = regex.match(session['password'])
        if not match or not session['password']:
            regex_password_error = ["Your password must contain at least 8 characters,", "including at least one uppercase and lowercase letter, and one digit."]
            return render_template('sign_up_em.html', regex_password_error=regex_password_error)


        session['verification_code'] = generate_verification_code()
        
        msg = Message('Email Verification', recipients=[session['email']], body = f'Your verification code is: {session["verification_code"]}')
        mail.send(msg)

        session['types'] = "employer"

        return render_template('check-email.html', types=session['types'])

@app.route('/submit_student1', methods=['POST'])
def register_student1():
    if request.method == 'POST':

        name = request.form['name']
        session['name'] = name.strip().title()
        surname = request.form['surname']
        session['surname'] = surname.strip().title()
        session['age'] = request.form['age']
        session['password'] = request.form['password']
        email = request.form['email']
        session['email'] = email.lower()
        file_id = None

        image_data = request.files['image']
        if image_data.filename:
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

        for field in ['name', 'surname', 'age', 'email']:
            if not session[field]:
                null_error = "Please fill in all fields."
                return render_template('sign_up_student.html', null_error=null_error)
        
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
        regex = re.compile(pattern)
        match = regex.match(session['password'])
        if not match or not session['password']:
            regex_password_error = ["Your password must contain at least 8 characters,", "including at least one uppercase and lowercase letter, and one digit."]
            return render_template('sign_up_student.html', regex_password_error=regex_password_error)

        if not 16 < int(session['age']) < 120:
            age_error = 'Please fill the correct information about your age.'
            return render_template('sign_up_student.html', age_error=age_error)
        
        session['verification_code'] = generate_verification_code()
        
        msg = Message('Email Verification', recipients=[session['email']], body = f'Your verification code is: {session["verification_code"]}')
        mail.send(msg)

        session['types'] = "student"
        return render_template('check-email.html', types=session['types'])
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

        user = collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user_data'] = user
            if '_id' in session['user_data']:
                user['_id'] = str(session['user_data']['_id'])
            if user['type'] == 'student':
                return redirect('/')
            if user['type'] == 'employer':
                return redirect('/')
        if user:
            incorrect_error = "Incorrect password"
            return render_template('login.html', invalid_error=incorrect_error, mail=email)
        invalid_error = "Invalid email or password"
        return render_template('login.html', invalid_error=invalid_error)

    if request.method == 'GET':
        session.clear()
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
    vacancies.delete_many({'email': email})
    collection.delete_one({'email': email})
    session.clear()
    return redirect('/')

@app.route('/delete_vacancy')
def delete_vacancy():
    vacancy_id = request.args.get('vacancy_id')
    vacancies.delete_one({'_id': ObjectId(vacancy_id)})

    return redirect('/profile_employer.html')

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
    user_email = session['user_data']['email']
    user_data = collection.find_one({'email': user_email})
    return render_template('main_page.html', vacancies=list(vacancies.find()), user_data=user_data, collection=collection)

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
    age = request.form['age']
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

@app.route('/edit_job_offer', methods=['POST', "GET"])
def edit_job_offer():
    # Retrieve updated data from the form
    job_name = request.form['jobName']
    skills = request.form['skills']
    employment = request.form['employment']
    description = request.form['description']

    session['user_data']['job_name'] = job_name
    session['user_data']['skills'] = skills
    session['user_data']['employment'] = employment
    session['user_data']['description'] = description

    vacancy_id = request.args.get('id')
    vacancies.update_one({'_id': ObjectId(vacancy_id)}, {'$set': {'job_name': job_name, \
'skills': skills, 'employment': employment, 'description': description}})

    return redirect('profile_employer.html')

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
