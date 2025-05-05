from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from twilio.rest import Client
import json
from datetime import datetime
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartgrade.db'

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '11229a045@kanchiuniv.ac.in'
app.config['MAIL_PASSWORD'] = 'nzzp adnu vkmr trri'
app.config['MAIL_DEFAULT_SENDER'] = '11229a045@kanchiuniv.ac.in'

# Twilio Configuration
TWILIO_ACCOUNT_SID = 'your-account-sid'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = 'your-auth-token'    # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = '+1234567890'      # Replace with your Twilio phone number
TWILIO_WHATSAPP_NUMBER = '+14155238886'  # Twilio WhatsApp sandbox number

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Flask-Mail
mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120))
    role = db.Column(db.String(20))  # student, class_incharge, hod, vc
    department = db.Column(db.String(20))
    year = db.Column(db.Integer)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    department = db.Column(db.String(20))
    year = db.Column(db.Integer)
    subject1 = db.Column(db.Float)
    subject2 = db.Column(db.Float)
    subject3 = db.Column(db.Float)
    subject4 = db.Column(db.Float)
    subject5 = db.Column(db.Float)
    attendance = db.Column(db.Float)
    assignment_score = db.Column(db.Float)
    predicted_grade = db.Column(db.String(2))
    parent_phone = db.Column(db.String(15))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Create sample data
    create_sample_data()
    
    return render_template('index.html')

def generate_random_name():
    first_names = ['Aarav', 'Aditya', 'Akshay', 'Ananya', 'Arjun', 'Bhavya', 'Dhruv', 'Ishaan', 'Kavya', 'Krishna',
                  'Maya', 'Neha', 'Pranav', 'Priya', 'Rahul', 'Riya', 'Rohan', 'Saanvi', 'Sahil', 'Sanjana',
                  'Shreya', 'Siddharth', 'Tanvi', 'Varun', 'Vihaan', 'Yash', 'Zara', 'Aarushi', 'Advait', 'Anika',
                  'Arnav', 'Diya', 'Ishita', 'Kabir', 'Meera', 'Navya', 'Parth', 'Riyaan', 'Saanvi', 'Samaira',
                  'Shiv', 'Sneha', 'Tara', 'Ved', 'Vivaan', 'Yuvraj', 'Zoya']
    
    last_names = ['Agarwal', 'Bansal', 'Chauhan', 'Desai', 'Gupta', 'Jain', 'Kapoor', 'Malhotra', 'Mehta', 'Patel',
                 'Reddy', 'Shah', 'Sharma', 'Singh', 'Verma', 'Yadav', 'Arora', 'Bhatia', 'Choudhary', 'Dixit',
                 'Goyal', 'Joshi', 'Kumar', 'Mishra', 'Pandey', 'Rao', 'Saxena', 'Srivastava', 'Tiwari', 'Trivedi']
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def create_sample_data():
    # Create sample users
    users = [
        # Class incharge users
        User(username='cse1_incharge', password_hash=generate_password_hash('cse1teacher'), role='class_incharge', department='CSE', year=1),
        User(username='cse2_incharge', password_hash=generate_password_hash('cse2teacher'), role='class_incharge', department='CSE', year=2),
        User(username='cse3_incharge', password_hash=generate_password_hash('cse3teacher'), role='class_incharge', department='CSE', year=3),
        User(username='cse4_incharge', password_hash=generate_password_hash('cse4teacher'), role='class_incharge', department='CSE', year=4),
        
        User(username='ece1_incharge', password_hash=generate_password_hash('ece1teacher'), role='class_incharge', department='ECE', year=1),
        User(username='ece2_incharge', password_hash=generate_password_hash('ece2teacher'), role='class_incharge', department='ECE', year=2),
        User(username='ece3_incharge', password_hash=generate_password_hash('ece3teacher'), role='class_incharge', department='ECE', year=3),
        User(username='ece4_incharge', password_hash=generate_password_hash('ece4teacher'), role='class_incharge', department='ECE', year=4),
        
        User(username='eee1_incharge', password_hash=generate_password_hash('eee1teacher'), role='class_incharge', department='EEE', year=1),
        User(username='eee2_incharge', password_hash=generate_password_hash('eee2teacher'), role='class_incharge', department='EEE', year=2),
        User(username='eee3_incharge', password_hash=generate_password_hash('eee3teacher'), role='class_incharge', department='EEE', year=3),
        User(username='eee4_incharge', password_hash=generate_password_hash('eee4teacher'), role='class_incharge', department='EEE', year=4),
        
        # HOD users
        User(username='cse_hod', password_hash=generate_password_hash('csehod123'), role='hod', department='CSE'),
        User(username='ece_hod', password_hash=generate_password_hash('ecehod123'), role='hod', department='ECE'),
        User(username='eee_hod', password_hash=generate_password_hash('eeehod123'), role='hod', department='EEE'),
        
        # Dean user
        User(username='dean', password_hash=generate_password_hash('dean123'), role='dean')
    ]
    
    for user in users:
        db.session.add(user)
    
    def calculate_grade(avg_marks):
        if avg_marks >= 90:
            return 'A+'
        elif avg_marks >= 80:
            return 'A'
        elif avg_marks >= 70:
            return 'B'
        elif avg_marks >= 60:
            return 'C'
        elif avg_marks >= 50:
            return 'D'
        else:
            return 'F'
    
    # Create sample students for each department
    departments = ['CSE', 'ECE', 'EEE']
    years = [1, 2, 3, 4]
    
    for dept in departments:
        for year in years:
            # First 12 years will have 13 students, last year will have 12 to make it 50
            num_students = 13 if year < 4 else 12
            for i in range(1, num_students + 1):
                # Fix student ID format to ensure uniqueness
                student_id = f"{dept}{year}{i:03d}"  # Using 3-digit padding for student number
                # Generate random marks between 50 and 100
                subject1 = round(random.uniform(50, 100), 2)
                subject2 = round(random.uniform(50, 100), 2)
                subject3 = round(random.uniform(50, 100), 2)
                subject4 = round(random.uniform(50, 100), 2)
                subject5 = round(random.uniform(50, 100), 2)
                attendance = round(random.uniform(75, 100), 2)
                assignment_score = round(random.uniform(60, 100), 2)
                
                # Calculate average marks and grade
                avg_marks = (subject1 + subject2 + subject3 + subject4 + subject5) / 5
                grade = calculate_grade(avg_marks)
                
                # Generate random name for student
                student_name = generate_random_name()
                
                # Create student record
                student = Student(
                    student_id=student_id,
                    name=student_name,
                    department=dept,
                    year=year,
                    subject1=subject1,
                    subject2=subject2,
                    subject3=subject3,
                    subject4=subject4,
                    subject5=subject5,
                    attendance=attendance,
                    assignment_score=assignment_score,
                    predicted_grade=grade,
                    parent_phone=f"+9198765432{i:02d}"
                )
                db.session.add(student)
                
                # Create student user
                user = User(
                    username=student_id,
                    password_hash=generate_password_hash('student123'),
                    role='student',
                    department=dept,
                    year=year
                )
                db.session.add(user)
    
    db.session.commit()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        year = request.form.get('year')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        # Validate required fields based on role
        if role == 'student':
            if not all([request.form.get('name'), department, year, request.form.get('parent_phone')]):
                flash('Please fill in all required fields for student registration')
                return redirect(url_for('register'))
        elif role == 'class_incharge':
            if not all([department, year]):
                flash('Please fill in all required fields for class incharge registration')
                return redirect(url_for('register'))
        elif role == 'hod':
            if not department:
                flash('Please fill in all required fields for HOD registration')
                return redirect(url_for('register'))

        # Create new user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            department=department if role in ['class_incharge', 'hod'] else None,
            year=int(year) if role == 'class_incharge' else None
        )
        
        db.session.add(user)
        
        # If registering as a student, create student record with random marks
        if role == 'student':
            # Generate random marks between 70 and 100
            subject1 = round(random.uniform(70, 100), 2)
            subject2 = round(random.uniform(70, 100), 2)
            subject3 = round(random.uniform(70, 100), 2)
            subject4 = round(random.uniform(70, 100), 2)
            subject5 = round(random.uniform(70, 100), 2)
            attendance = round(random.uniform(75, 100), 2)
            assignment_score = round(random.uniform(70, 100), 2)
            
            # Calculate predicted grade based on average marks
            avg_marks = (subject1 + subject2 + subject3 + subject4 + subject5) / 5
            if avg_marks >= 90:
                predicted_grade = 'A+'
            elif avg_marks >= 80:
                predicted_grade = 'A'
            elif avg_marks >= 70:
                predicted_grade = 'B'
            elif avg_marks >= 60:
                predicted_grade = 'C'
            elif avg_marks >= 50:
                predicted_grade = 'D'
            else:
                predicted_grade = 'F'

            student = Student(
                student_id=username,
                name=request.form.get('name'),
                department=department,
                year=int(year),
                subject1=subject1,
                subject2=subject2,
                subject3=subject3,
                subject4=subject4,
                subject5=subject5,
                attendance=attendance,
                assignment_score=assignment_score,
                predicted_grade=predicted_grade,
                parent_phone=request.form.get('parent_phone')
            )
            db.session.add(student)
        
        try:
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        year = request.form.get('year')

        if not all([username, password, role]):
            flash('Please fill in all required fields')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if role == 'student' and user.role == 'student':
                login_user(user)
                return redirect(url_for('student_dashboard'))
            elif role == 'class_incharge' and user.role == 'class_incharge':
                if user.department == department and str(user.year) == year:
                    login_user(user)
                    return redirect(url_for('class_dashboard'))
                else:
                    flash('Invalid department or year for class incharge')
            elif role == 'hod' and user.role == 'hod':
                if user.department == department:
                    login_user(user)
                    return redirect(url_for('department_dashboard'))
                else:
                    flash('Invalid department for HOD')
            elif role == 'dean' and user.role == 'dean':
                login_user(user)
                return redirect(url_for('dean_dashboard'))
            else:
                flash('Invalid role or role mismatch')
        else:
            flash('Invalid username or password')
        
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    # Get the current user's student record
    student = Student.query.filter_by(student_id=current_user.username).first()
    
    if not student:
        flash('Student record not found')
        return redirect(url_for('logout'))
    
    # Calculate average marks
    total_marks = sum([student.subject1, student.subject2, student.subject3, student.subject4, student.subject5])
    avg_marks = total_marks / 5
    
    # Calculate grade based on average marks
    if avg_marks >= 90:
        grade = 'A+'
    elif avg_marks >= 80:
        grade = 'A'
    elif avg_marks >= 70:
        grade = 'B'
    elif avg_marks >= 60:
        grade = 'C'
    elif avg_marks >= 50:
        grade = 'D'
    else:
        grade = 'F'
    
    # Update the predicted grade
    student.predicted_grade = grade
    db.session.commit()
    
    # Create a dictionary of subject marks for easier access in template
    subject_marks = {
        'subject1': student.subject1,
        'subject2': student.subject2,
        'subject3': student.subject3,
        'subject4': student.subject4,
        'subject5': student.subject5
    }
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         subject_marks=subject_marks,
                         avg_marks=avg_marks)

@app.route('/predict_grade', methods=['POST'])
@login_required
def predict_grade():
    student = Student.query.filter_by(student_id=current_user.username).first()
    # Load and train model
    model = RandomForestClassifier()
    # Add your model training code here
    return redirect(url_for('student_dashboard'))

@app.route('/download_marksheet')
@login_required
def download_marksheet():
    student = Student.query.filter_by(student_id=current_user.username).first()
    
    # Generate PDF
    filename = f"marksheet_{student.student_id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add content to PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "SmartGrade - Marksheet")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Student ID: {student.student_id}")
    c.drawString(100, 680, f"Name: {student.name}")
    c.drawString(100, 660, f"Department: {student.department}")
    c.drawString(100, 640, f"Year: {student.year}")
    
    # Draw table header
    c.drawString(100, 600, "Subject")
    c.drawString(300, 600, "Marks")
    
    # Draw subject marks
    y = 580
    subjects = [
        ("Subject 1", student.subject1),
        ("Subject 2", student.subject2),
        ("Subject 3", student.subject3),
        ("Subject 4", student.subject4),
        ("Subject 5", student.subject5)
    ]
    
    for subject, marks in subjects:
        c.drawString(100, y, subject)
        c.drawString(300, y, f"{marks:.2f}")
        y -= 20
    
    # Draw additional metrics
    c.drawString(100, y-20, f"Attendance: {student.attendance:.2f}%")
    c.drawString(100, y-40, f"Assignment Score: {student.assignment_score:.2f}%")
    c.drawString(100, y-60, f"Predicted Grade: {student.predicted_grade}")
    
    # Save the PDF
    c.save()
    
    # Send the file
    return send_file(filename, as_attachment=True)

@app.route('/share_marksheet', methods=['POST'])
@login_required
def share_marksheet():
    method = request.form.get('method')
    student = Student.query.filter_by(student_id=current_user.username).first()
    
    # Generate PDF first
    filename = f"marksheet_{student.student_id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add content to PDF (same as download_marksheet)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "SmartGrade - Marksheet")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Student ID: {student.student_id}")
    c.drawString(100, 680, f"Name: {student.name}")
    c.drawString(100, 660, f"Department: {student.department}")
    c.drawString(100, 640, f"Year: {student.year}")
    
    # Draw table header
    c.drawString(100, 600, "Subject")
    c.drawString(300, 600, "Marks")
    
    # Draw subject marks
    y = 580
    subjects = [
        ("Subject 1", student.subject1),
        ("Subject 2", student.subject2),
        ("Subject 3", student.subject3),
        ("Subject 4", student.subject4),
        ("Subject 5", student.subject5)
    ]
    
    for subject, marks in subjects:
        c.drawString(100, y, subject)
        c.drawString(300, y, f"{marks:.2f}")
        y -= 20
    
    # Draw additional metrics
    c.drawString(100, y-20, f"Attendance: {student.attendance:.2f}%")
    c.drawString(100, y-40, f"Assignment Score: {student.assignment_score:.2f}%")
    c.drawString(100, y-60, f"Predicted Grade: {student.predicted_grade}")
    
    c.save()
    
    if method == 'whatsapp':
        try:
            # Send WhatsApp message with PDF
            message = twilio_client.messages.create(
                from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
                body=f"Here is your marksheet for {student.name}",
                to=f"whatsapp:{student.parent_phone}",
                media_url=[f"file://{os.path.abspath(filename)}"]
            )
            flash('Marksheet shared successfully on WhatsApp!')
        except Exception as e:
            flash(f'Error sharing on WhatsApp: {str(e)}')
    
    elif method == 'email':
        try:
            recipient_email = request.form.get('email', '')
            if not recipient_email:
                flash('Please provide an email address')
                return redirect(url_for('student_dashboard'))
            
            # Create email message using Flask-Mail
            msg = Message(
                subject=f'Marksheet for {student.name}',
                recipients=[recipient_email],
                sender=(f"{student.name} via SmartGrade", app.config['MAIL_USERNAME']),
                body=f"Dear Parent/Guardian,\n\nI am writing to share the marksheet of your ward, {student.name} (Student ID: {student.student_id}).\n\nPlease find the detailed marksheet attached with this email.\n\nBest regards,\n{student.name}\nSmartGrade Team"
            )
            
            # Add PDF attachment
            with open(filename, 'rb') as fp:
                msg.attach(
                    filename,
                    'application/pdf',
                    fp.read()
                )
            
            # Send email
            mail.send(msg)
            flash('Marksheet sent successfully via email!')
        except Exception as e:
            flash(f'Error sending email: {str(e)}')
    
    elif method == 'sms' and student.parent_phone:
        try:
            # Send SMS with Twilio
            message = twilio_client.messages.create(
                body=f"Your child {student.name}'s marksheet is ready. Please check your email or WhatsApp.",
                from_=TWILIO_PHONE_NUMBER,
                to=student.parent_phone
            )
            flash('SMS notification sent successfully!')
        except Exception as e:
            flash(f'Error sending SMS: {str(e)}')
    
    # Clean up the PDF file
    if os.path.exists(filename):
        os.remove(filename)
    
    return redirect(url_for('student_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/class_dashboard')
@login_required
def class_dashboard():
    if current_user.role != 'class_incharge':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get students in the same department and year as the class incharge
    students = Student.query.filter_by(
        department=current_user.department,
        year=current_user.year
    ).all()
    
    return render_template('class_dashboard.html', students=students)

@app.route('/department_dashboard')
@login_required
def department_dashboard():
    if current_user.role != 'hod':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get selected year from query parameter
    selected_year = request.args.get('year')
    
    # Get all students in the department or filter by year
    if selected_year:
        students = Student.query.filter_by(
            department=current_user.department,
            year=int(selected_year)
        ).all()
    else:
        students = Student.query.filter_by(department=current_user.department).all()
    
    # Calculate department statistics
    total_students = len(students)
    avg_attendance = sum(student.attendance for student in students) / total_students if total_students > 0 else 0
    avg_assignment = sum(student.assignment_score for student in students) / total_students if total_students > 0 else 0
    
    # Count students by grade
    grade_counts = {
        'A+': sum(1 for s in students if s.predicted_grade == 'A+'),
        'A': sum(1 for s in students if s.predicted_grade == 'A'),
        'B': sum(1 for s in students if s.predicted_grade == 'B'),
        'C': sum(1 for s in students if s.predicted_grade == 'C'),
        'D': sum(1 for s in students if s.predicted_grade == 'D'),
        'F': sum(1 for s in students if s.predicted_grade == 'F')
    }
    
    return render_template('department_dashboard.html',
                         students=students,
                         total_students=total_students,
                         avg_attendance=avg_attendance,
                         avg_assignment=avg_assignment,
                         grade_counts=grade_counts,
                         selected_year=selected_year)

@app.route('/dean_dashboard')
@login_required
def dean_dashboard():
    if current_user.role != 'dean':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get selected department from query parameter
    selected_department = request.args.get('department')
    
    # Get all students or filter by department
    if selected_department:
        students = Student.query.filter_by(department=selected_department).all()
    else:
        students = Student.query.all()
    
    # Calculate university statistics
    total_students = len(students)
    avg_attendance = sum(student.attendance for student in students) / total_students if total_students > 0 else 0
    avg_assignment = sum(student.assignment_score for student in students) / total_students if total_students > 0 else 0
    
    # Count students by department
    department_counts = {}
    for student in students:
        if student.department not in department_counts:
            department_counts[student.department] = 0
        department_counts[student.department] += 1
    
    # Count students by grade
    grade_counts = {
        'A+': sum(1 for s in students if s.predicted_grade == 'A+'),
        'A': sum(1 for s in students if s.predicted_grade == 'A'),
        'B': sum(1 for s in students if s.predicted_grade == 'B'),
        'C': sum(1 for s in students if s.predicted_grade == 'C'),
        'D': sum(1 for s in students if s.predicted_grade == 'D'),
        'F': sum(1 for s in students if s.predicted_grade == 'F')
    }
    
    return render_template('dean_dashboard.html',
                         students=students,
                         total_students=total_students,
                         avg_attendance=avg_attendance,
                         avg_assignment=avg_assignment,
                         department_counts=department_counts,
                         grade_counts=grade_counts,
                         selected_department=selected_department)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True) 