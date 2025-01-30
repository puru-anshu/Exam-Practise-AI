from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class ExamType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_type.id'), nullable=False)
    exam_type = db.relationship('ExamType', backref=db.backref('subjects', lazy=True))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('questions', lazy=True))

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_type.id'), nullable=False)
    score = db.Column(db.Integer)
    date_taken = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('exams', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('exams', lazy=True))
    exam_type = db.relationship('ExamType', backref=db.backref('exams', lazy=True))

