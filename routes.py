from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from models import User, Subject, Question, Exam, ExamType
from openai_integration import generate_questions
import json
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Please check your login details and try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    exam_types = ExamType.query.all()
    return render_template('dashboard.html', exam_types=exam_types)

@app.route('/exam_type/<int:exam_type_id>')
@login_required
def exam_type(exam_type_id):
    exam_type = ExamType.query.get_or_404(exam_type_id)
    subjects = Subject.query.filter_by(exam_type_id=exam_type_id).all()
    return render_template('exam_type.html', exam_type=exam_type, subjects=subjects)

@app.route('/exam/<int:subject_id>')
@login_required
def exam(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    questions = generate_questions(subject.name, "medium")  # Generate 5 medium difficulty questions
    return render_template('exam.html', subject=subject, questions=questions)

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    data = request.form
    subject_id = int(data['subject_id'])
    questions_json = data['questions'].strip()
    print("All attributes and values of data:")
    for key, value in data.items():
        print(f"{key}: {value}")
   
    questions = json.loads(questions_json)
    
    score = 0
    j =1
    for q in questions:
        user_answer = data.get(f"q{j}")
        if user_answer == q['correct_answer']:
            score += 1
        j=j+1

    subject = Subject.query.get(subject_id)
    exam = Exam(user_id=current_user.id, subject_id=subject_id, exam_type_id=subject.exam_type_id, score=score, date_taken=datetime.utcnow())
    db.session.add(exam)
    db.session.commit()

    flash(f'Exam submitted successfully. Your score: {score}/{len(questions)}')
    return redirect(url_for('dashboard'))

@app.route('/admin/exam_types', methods=['GET', 'POST'])
@login_required
def admin_exam_types():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        new_exam_type = ExamType(name=name, description=description)
        db.session.add(new_exam_type)
        db.session.commit()
        flash('New exam type added successfully')
        return redirect(url_for('admin_exam_types'))
    
    exam_types = ExamType.query.all()
    return render_template('admin/exam_types.html', exam_types=exam_types)

@app.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
def admin_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        exam_type_id = request.form.get('exam_type_id')
        new_subject = Subject(name=name, exam_type_id=exam_type_id)
        db.session.add(new_subject)
        db.session.commit()
        flash('New subject added successfully')
        return redirect(url_for('admin_subjects'))
    
    subjects = Subject.query.all()
    exam_types = ExamType.query.all()
    return render_template('admin/subjects.html', subjects=subjects, exam_types=exam_types)

