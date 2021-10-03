from flask_login import UserMixin
from .extensions import db 

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)

class UserSessions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(50))
    session_init_timestamp = db.Column(db.Integer)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.String(50))
    question_category = db.Column(db.String(50))
    question_score = db.Column(db.Integer)

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    option_text = db.Column(db.String(100))
    option_point = db.Column(db.Integer)
    option_is_correct = db.Column(db.Boolean)
    option_is_answer = db.Column(db.Boolean)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

class UserAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), unique=True)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'))
    category = db.Column(db.String(50), db.ForeignKey('questions.question_category'))
    is_correct = db.Column(db.Boolean,db.ForeignKey('options.option_is_correct'))
    score = db.Column(db.Integer,db.ForeignKey('questions.question_score'))
