from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import datetime
from functools import wraps
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from mail import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://appuser:apppassword@localhost:3306/AttendMate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

USER = "appuser"
PASSWORD = "apppassword"
DATABASE_NAME = "AttendMate"

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User (db.Model):
    __tablename__ = 'user'

    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class Student(db.Model):
    __tablename__ = 'student'

    studentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID', ondelete="CASCADE"), unique=True, nullable=False)
    studentNumber = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"Student('{self.studentID}', '{self.userID}', '{self.studentNumber}')"
    
class Teacher(db.Model):
    __tablename__ = 'teacher'

    teacherID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID', ondelete="CASCADE"), unique=True, nullable=False)

    def __repr__(self):
        return f"Teacher('{self.teacherID}', '{self.userID}')"

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(name=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        isTeacher = getWhetherUserIsTeacher(email)
        token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=1))
        return jsonify({'token': token , 'isTeacher': isTeacher})
    return jsonify({'message': 'Invalid credentials'}), 401

def getWhetherUserIsTeacher(email):
    return Teacher.query.join(User).filter(User.email == email).first() is not None

def checkIfStudentEmail(email):
    return email[0:6].isdigit() and email.endswith('@student.pwr.edu.pl')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    if not checkIfStudentEmail(email):
        return jsonify({'message': 'Invalid email'}), 400
    user = User.query.filter_by(email=email).first()
    if user and user.password == "NULL":
        password = generate_password()
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        send_email(email, password)
        return jsonify({'message': 'Password has been sent to your email'})
    else :
        return jsonify({'message': 'User already has a password'}), 400


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'This is a protected route'})

@app.route('/user-details' , methods=['GET'])
@jwt_required()
def user_details():
    current_user = get_jwt_identity()
    user = User.query.filter_by(name=current_user).first()
    return jsonify({'name': user.name, 'email': user.email})

if __name__ == '__main__':
    app.run(debug=True)