#routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from models import db, User, Student, Course, Grade
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask import jsonify

import json

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id)) if user_id else None



bcrypt = Bcrypt()

home = Blueprint('home', __name__)
login = Blueprint('login', __name__)
register = Blueprint('register', __name__)
dashboard = Blueprint('dashboard', __name__)
logout = Blueprint('logout', __name__)
student_management = Blueprint('student_management', __name__)
course_management = Blueprint('course_management', __name__)
grade_management = Blueprint('grade_management', __name__)

# Home page route
@home.route('/')
def home_page():
    if 'loggedin' in session:
        username = session['username']
        role = session['role']

        if role == 'admin':
            greeting_message = "Welcome, Administrator " + username
        else:
            greeting_message = "Welcome, Student " + username

        return render_template('home.html', greeting_message=greeting_message, profile_photo_url='static/images/home.jpg')
    else:
        return render_template('home.html', greeting_message="Welcome to Mkurugenzi School", profile_photo_url='static/images/home.jpg')


# Login page route
@login.route('/login', methods=['GET', 'POST'])
def login_page():
    registration_enabled = True  # Set this variable based on your logic (e.g., check if registration is allowed)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['loggedin'] = True
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'student':
                # Redirect students to the home page
                return redirect(url_for('home.home_page'))
            elif user.role == 'admin':
                # Redirect admins to the dashboard page
                return redirect(url_for('home.home_page'))

        # If the login is unsuccessful, show an error message
        return render_template('login.html', error='Invalid username or password', registration_enabled=registration_enabled)

    return render_template('login.html', registration_enabled=registration_enabled)


# Logout page route
@logout.route('/logout')
def logout_page():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home.home_page'))


@register.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role = request.form.get('role', 'student')  # Default role is 'student'

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password=hashed_password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()

        # Log in the newly registered user
        user = User.query.filter_by(username=username).first()
        login_user(user)

        flash('Registration successful!', 'success')

        return redirect(url_for('home.home_page'))

    return render_template('register.html')


@dashboard.route('/dashboard')
def dashboard_page():
    if 'loggedin' in session and session['role'] == 'admin':
        # Fetch data from the database
        students = Student.query.all()
        courses = Course.query.all()
        grades = Grade.query.all()

        # Pass the students list to the template context
        return render_template('dashboard.html', students=students, courses=courses, grades=grades)
    else:
        flash('You need to log in as an admin.')
        return redirect(url_for('login.login_page'))


# ...


# Add, update, and delete student routes
@student_management.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            # Add a new student based on the form data
            student_id = request.form.get('student_id')  # Make sure 'student_id' is the correct field name in your form
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            major = request.form.get('major')

            # Create a new student object
            new_student = Student(student_id=student_id, first_name=first_name, last_name=last_name, major=major)

            # Add the student to the session
            db.session.add(new_student)

            # Commit the changes to the database
            db.session.commit()

            # Return a JSON response indicating success
            return jsonify(success=True, message='Student added successfully')

        return render_template('add_student.html')
    else:
        return redirect(url_for('login.login_page'))


@student_management.route('/update-student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    if 'loggedin' in session and session['role'] == 'admin':
        student = Student.query.get(student_id)

        if request.method == 'POST':
            # Update the student information based on the form data
            student.first_name = request.form.get('first_name')
            student.last_name = request.form.get('last_name')
            student.major = request.form.get('major')

            # Commit the updated student to the database
            db.session.commit()

            return redirect(url_for('student_management.student_management_page'))

        return render_template('update_student.html', student=student)
    else:
        return redirect(url_for('login.login_page'))

@student_management.route('/delete-student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'loggedin' in session and session['role'] == 'admin':
        student = Student.query.get(student_id)

        # Delete the student from the database
        db.session.delete(student)
        db.session.commit()

        return redirect(url_for('student_management.student_management_page'))
    else:
        return redirect(url_for('login.login_page'))

# Student management page route
@student_management.route('/student-management')
def student_management_page():
    if 'loggedin' in session and session['role'] == 'admin':
        students = Student.query.all()

        return render_template('student_management.html', students=students)
    else:
        return redirect(url_for('login.login_page'))

# Add, update, and delete course routes
@course_management.route('/course-management', methods=['GET'])
def course_management_page():
    if 'loggedin' in session and session['role'] == 'admin':
        courses = Course.query.all()

        return render_template('course_management.html', courses=courses)
    else:
        return redirect(url_for('login.login_page'))

@course_management.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            # Add a new course based on the form data
            course_code = request.form.get('course_code')
            course_name = request.form.get('course_name')

            existing_course = Course.query.filter_by(course_code=course_code).first()

            if existing_course:
                return render_template('add_course.html', error='Course code already exists')

            new_course = Course(course_code=course_code, course_name=course_name)

            # Commit the new course to the database
            db.session.add(new_course)
            db.session.commit()

            return redirect(url_for('course_management.course_management_page'))

        return render_template('add_course.html')
    else:
        return redirect(url_for('login.login_page'))

@course_management.route('/update-course/<string:course_code>', methods=['GET', 'POST'])
def update_course(course_code):
    if 'loggedin' in session and session['role'] == 'admin':
        course = Course.query.filter_by(course_code=course_code).first()

        if request.method == 'POST':
            # Update the course information based on the form data
            course.course_name = request.form.get('course_name')

            # Commit the updated course to the database
            db.session.commit()

            return redirect(url_for('course_management.course_management_page'))

        return render_template('update_course.html', course=course)
    else:
        return redirect(url_for('login.login_page'))

@course_management.route('/delete-course/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    if 'loggedin' in session and session['role'] == 'admin':
        course = Course.query.filter_by(course_code=course_code).first()

        # Delete the course from the database
        db.session.delete(course)
        db.session.commit()

        return redirect(url_for('course_management.course_management_page'))
    else:
        return redirect(url_for('login.login_page'))

# Grade management page route
@grade_management.route('/grade-management')
def grade_management_page():
    if 'loggedin' in session and session['role'] == 'admin':
        # Get filter criteria from the request (if provided)
        student_id = request.args.get('student_id')
        course_code = request.args.get('course_code')

        # Filter grades based on criteria
        if student_id and course_code:
            grades = Grade.query.filter_by(student_id=student_id, course_code=course_code).all()
        elif student_id:
            grades = Grade.query.filter_by(student_id=student_id).all()
        elif course_code:
            grades = Grade.query.filter_by(course_code=course_code).all()
        else:
            # If no filter criteria, get all grades
            grades = Grade.query.all()

        return render_template('grade_management.html', grades=grades)
    else:
        return redirect(url_for('login.login_page'))

# Add grade route
# In your add_grade route
@grade_management.route('/add-grade', methods=['GET', 'POST'])
def add_grade():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            # Add a new grade based on the form data
            student_id = request.form.get('student_id')
            course_code = request.form.get('course_code')
            grade_value = request.form.get('grade')
            semester = request.form.get('semester')
            year = request.form.get('year')  # Retrieve year from the form

            # Check if the student exists
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                return render_template('add_grade.html', error='Student not found')

            # Check if the course exists
            course = Course.query.filter_by(course_code=course_code).first()
            if not course:
                return render_template('add_grade.html', error='Course not found')

            # Check if the grade for the given student and course already exists
            existing_grade = Grade.query.filter_by(student_id=student_id, course_code=course_code).first()
            if existing_grade:
                return render_template('add_grade.html', error='Grade already exists for this student and course')

            # Create a new Grade instance with the year
            new_grade = Grade(student_id=student_id, course_code=course_code, grade=grade_value, semester=semester, year=year)

            # Commit the new grade to the database
            db.session.add(new_grade)
            db.session.commit()

            return redirect(url_for('grade_management.grade_management_page'))

        return render_template('add_grade.html')
    else:
        return redirect(url_for('login.login_page'))
@grade_management.route('/update-grade/<int:grade_id>', methods=['GET', 'POST'])
def update_grade(grade_id):
    if 'loggedin' in session and session['role'] == 'admin':
        # Get the grade based on the provided grade_id
        grade = Grade.query.get_or_404(grade_id)

        if request.method == 'POST':
            # Update grade based on the form data
            grade.student_id = request.form.get('student_id')
            grade.course_code = request.form.get('course_code')
            grade.grade = request.form.get('grade')

            # Commit the updated grade to the database
            db.session.commit()

            return redirect(url_for('grade_management.grade_management_page'))

        # Render the update grade form with the current grade details
        return render_template('update_grade.html', grade=grade)
    else:
        return redirect(url_for('login.login_page'))
    

# Add the delete_grade route
@grade_management.route('/delete-grade/<int:grade_id>', methods=['POST'])
def delete_grade(grade_id):
    if 'loggedin' in session and session['role'] == 'admin':
        # Get the grade based on the provided grade_id
        grade = Grade.query.get_or_404(grade_id)

        # Delete the grade from the database
        db.session.delete(grade)
        db.session.commit()

        return redirect(url_for('grade_management.grade_management_page'))
    else:
        return redirect(url_for('login.login_page'))
