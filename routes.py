from flask import render_template, request, redirect, session, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from models import User, ExamType, Class, Subject, Chapter, Question, Exam
from openai_integration import generate_questions, get_explanation
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
    classes = Class.query.filter_by(exam_type_id=exam_type_id).all()
    return render_template('exam_type.html', exam_type=exam_type, classes=classes)

@app.route('/class/<int:class_id>')
@login_required
def class_view(class_id):
    class_ = Class.query.get_or_404(class_id)
    subjects = Subject.query.filter_by(class_id=class_id).all()
    return render_template('class.html', class_=class_, subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def subject_view(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('subject.html', subject=subject, chapters=chapters)

@app.route('/exam_setup/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def exam_setup(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        difficulty = request.form.get('difficulty', 'medium')
        num_questions = int(request.form.get('num_questions', 10))
        print(chapter_id)
        if chapter_id == 'all':
            questions =generate_questions(f"{subject.name}", difficulty, num_questions,use_ollama=True)
        else:
            chapter = Chapter.query.get(chapter_id)
            questions = generate_questions(f"{subject.name} - {chapter.name}", difficulty, num_questions,use_ollama=True)
        
        return render_template('exam.html', subject=subject, questions=questions, chapter_id=chapter_id)
    
    return render_template('exam_setup.html', subject=subject, chapters=chapters)

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    data = request.form
    subject_id = int(data['subject_id'])
    chapter_id = data.get('chapter_id')
    questions = json.loads(data['questions'])
    total_questions = len(questions)
    correct_answers = 0
    results = []

    for i, q in enumerate(questions, start=1):
        user_answer = data.get(f"q{i}")
        is_correct = user_answer == q['correct_answer']
        if is_correct:
            correct_answers += 1
        results.append({
            'question': q['question'],
            'options': q['options'],
            'user_answer': user_answer,
            'correct_answer': q['correct_answer'],
            'is_correct': is_correct
        })

    mark = (correct_answers / total_questions) * 100
    subject = Subject.query.get(subject_id)
    exam = Exam(
        user_id=current_user.id,
        exam_type_id=subject.class_.exam_type_id,
        class_id=subject.class_.id,
        subject_id=subject_id,
        chapter_id=chapter_id if chapter_id != 'all' else None,
        score=correct_answers,
        date_taken=datetime.utcnow()
    )
    db.session.add(exam)
    db.session.commit()
    session['exam_results'] = results #Added this line to store results in session

    return render_template('exam_result.html', 
                           results=results, 
                           mark=mark, 
                           total_questions=total_questions, 
                           correct_answers=correct_answers)

    
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

@app.route('/admin/classes', methods=['GET', 'POST'])
@login_required
def admin_classes():
    if request.method == 'POST':
        name = request.form.get('name')
        exam_type_id = request.form.get('exam_type_id')
        new_class = Class(name=name, exam_type_id=exam_type_id)
        db.session.add(new_class)
        db.session.commit()
        flash('New class added successfully')
        return redirect(url_for('admin_classes'))
    
    classes = Class.query.all()
    exam_types = ExamType.query.all()
    return render_template('admin/classes.html', classes=classes, exam_types=exam_types)

@app.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
def admin_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        class_id = request.form.get('class_id')
        new_subject = Subject(name=name, class_id=class_id)
        db.session.add(new_subject)
        db.session.commit()
        flash('New subject added successfully')
        return redirect(url_for('admin_subjects'))
    
    subjects = Subject.query.all()
    classes = Class.query.all()
    return render_template('admin/subjects.html', subjects=subjects, classes=classes)

@app.route('/admin/chapters', methods=['GET', 'POST'])
@login_required
def admin_chapters():
    if request.method == 'POST':
        name = request.form.get('name')
        subject_id = request.form.get('subject_id')
        new_chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('New chapter added successfully')
        return redirect(url_for('admin_chapters'))
    
    chapters = Chapter.query.all()
    subjects = Subject.query.all()
    return render_template('admin/chapters.html', chapters=chapters, subjects=subjects)



@app.route('/question_explanation/<int:question_id>')
@login_required
def question_explanation(question_id):
    results = session.get('exam_results', [])
    if question_id < 0 or question_id >= len(results):
        flash('Invalid question ID', 'error')
        return redirect(url_for('dashboard'))
    
    question = results[question_id]
    if 'explanation' not in question:
        explanation = get_explanation(question['question'], question['options'], question['correct_answer'])
        question['explanation'] = explanation
        results[question_id] = question
        session['exam_results'] = results

    return render_template('question_explanation.html', question=question)
