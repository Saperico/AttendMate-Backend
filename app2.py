from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
from flask_cors import CORS
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import send_from_directory
import mysql.connector
from datetime import datetime, timedelta
from mail import *
import pandas as pd
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://appuser:apppassword@localhost:3306/AttendMate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

USER = "appuser"
PASSWORD = "apppassword"
DATABASE_NAME = "AttendMate"

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

 
jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# defines for file upload (doctors note)
DN_UPLOAD_FOLDER = os.path.abspath('doctors_notes')
DN_ALLOWED_EXTENSIONS = {'pdf', 'png'}
app.config['DN_UPLOAD_FOLDER'] = DN_UPLOAD_FOLDER

if not os.path.exists(DN_UPLOAD_FOLDER):
    os.makedirs(DN_UPLOAD_FOLDER)


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

def getWhetherUserIsTeacher(email):
    return Teacher.query.join(User).filter(User.email == email).first() is not None

def is_teacher_of_class(subject_number):
    verify_jwt_in_request()
    email = get_jwt_identity()  # Get the user's email

    isTeacher = getWhetherUserIsTeacher(email)
    if not isTeacher:
        return False  # User is not a teacher

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT class.subjectName FROM class
    JOIN teachersInClasses ON teachersInClasses.classID = class.classID
    JOIN teacher ON teacher.teacherId = teachersInClasses.teacherID
    JOIN user ON user.userID = teacher.userID
    WHERE user.email = %s
    AND class.subjectNumber = %s
    """, (email, subject_number))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return bool(result)  # True if the user teaches the class, False otherwise


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        isTeacher = getWhetherUserIsTeacher(email)
        token = create_access_token(identity=email, expires_delta=timedelta(days=1))
        return jsonify({'token': token , 'isTeacher': isTeacher})
    return jsonify({'message': 'Invalid credentials'}), 401

def checkIfStudentEmail(email):
    return email[0:6].isdigit() and email.endswith('@student.pwr.edu.pl') or email in ['emilydavis@example.com','michaelwilson@example.com',
'davidmiller@example.com',
'emmajohnson@example.com',
'oliviabrown@example.com',
'liamsmith@example.com',
'sophiadavis@example.com',
'noahwilson@example.com',
'isabellagarcia@example.com']

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if user and user.password == "NULL":
        password = generate_password()
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        send_email(email, password)
        return jsonify({'message': 'Password has been sent to your email'})
    else :
        return jsonify({'message': 'User already has a password, check your email'}), 400
    
@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Password has been updated'})
    return jsonify({'message': 'User not found'}), 404
    
    
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='appuser',
        password='apppassword',
        database='AttendMate'
    )
    return connection

@app.route('/api/debug/<date_input>', methods=['GET'])
def debug(date_input):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT classID, studentID FROM attendanceRecords WHERE attendanceRecords.date = %s"""
                    ,(date_input,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    date_format = '%d.%m.%YT%H:%i'
    cursor.execute("""SELECT DATE_FORMAT(CONCAT(attendanceRecords.date, ' ', attendanceRecords.time), %s)  as formattedDate,
                    class.subjectName, student.studentNumber, attendanceRecords.status, attendanceRecords.date
                    FROM attendanceRecords
                    join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
                    JOIN class ON class.classID = ClassSession.classID
                    JOIN student ON student.studentID = attendanceRecords.studentID""", (date_format,))
    results = cursor.fetchall()

    for row in results:
        if isinstance(row['date'], datetime):
            row['date'] = row['date'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['date'], timedelta):
            row['date'] = str(row['date'])

    cursor.close()
    connection.close()
    return results

@app.route('/api/class-sessions', methods=['GET'])
def get_class_sessions():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    date_format = '%d.%m.%YT%H:%i'
    cursor.execute("""SELECT DATE_FORMAT(CONCAT(ClassSession.sessionDate, ' ', ClassSession.sessionStartTime), %s) as formattedStartDate,
                    DATE_FORMAT(CONCAT(ClassSession.sessionDate, ' ', ClassSession.sessionEndTime), %s) as formattedEndDate,
                    ClassSession.sessionDate, class.subjectName
                    FROM ClassSession 
                    JOIN class ON class.classID = ClassSession.classID""", (date_format,date_format))
    results = cursor.fetchall()

    for row in results:
        if isinstance(row['formattedStartDate'], datetime):
            row['formattedStartDate'] = row['formattedStartDate'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['formattedEndDate'], datetime):
            row['formattedEndDate'] = row['formattedEndDate'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['sessionDate'], timedelta):
            row['sessionDate'] = str(row['sessionDate'])

    cursor.close()
    connection.close()
    return results

@app.route('/api/excuses', methods=['GET'])
def get_excuses():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM Excuse""")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(results)

@app.route('/api/classes', methods=['GET'])
def get_classes():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT classID, subjectName, subjectNumber, year, semester, room, day, time FROM class""")
    results = cursor.fetchall()

    for row in results:
        print(row)
        if isinstance(row['day'], datetime):
            row['day'] = row['day'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['time'], timedelta):
            row['time'] = str(row['time'])

    cursor.close()
    connection.close()
    return jsonify(results)
    
@app.route('/api/classes/<is_teacher>/<email>', methods=['GET'])
def get_classes_by_email(is_teacher, email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    print("is_teacher: " + is_teacher)

    if(is_teacher.lower() == "true"): # is_teacher is a string of value true, not a boolean (!)
        cursor.execute("""
        SELECT class.* FROM class 
        JOIN teachersInClasses ON class.classID = teachersInClasses.classID
        JOIN teacher ON teacher.teacherID = teachersInClasses.teacherID
        JOIN user ON teacher.userID = user.userID
        WHERE user.email = %s
        """, (email,))
        results = cursor.fetchall()
    else:
        print("starting query")
        cursor.execute("""
        SELECT class.* FROM class
        JOIN studentsInClasses ON class.classID = studentsInClasses.classID
        JOIN student ON student.studentID = studentsInClasses.studentID
        JOIN user ON student.userID = user.userID
        WHERE user.email = %s
        """, (email,))
        results = cursor.fetchall()

    print(email)
    print(results)

    for row in results:
        print(row)
        if isinstance(row['day'], datetime):
            row['day'] = row['day'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['time'], timedelta):
            row['time'] = str(row['time'])

    cursor.close()
    connection.close()
    return jsonify(results)


@app.route('/api/students/<subject_number>', methods=['GET'])
@jwt_required()
def get_students_by_class(subject_number):
    email = get_jwt_identity() # logged in user's email

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    # check if teacher teaches selected class
    cursor.execute("""
    SELECT class.subjectName FROM class
    JOIN teachersInClasses ON teachersInClasses.classID = class.classID
    JOIN teacher ON teacher.teacherId = teachersInClasses.teacherID
    JOIN user ON user.userID = teacher.userID
    WHERE user.email = %s
    AND class.subjectNumber = %s
    """, (email, subject_number))

    result = cursor.fetchone();
    print(result)

    if not result:  # if teacher doesn't teach subject, return empty list
        cursor.close()
        connection.close()
        return jsonify([])

    # if teacher teaches subject, return all students in it
    cursor.execute("""SELECT
    student.studentID,
    student.studentNumber, 
    user.name, 
    user.lastName, 
    COUNT(CASE WHEN attendanceRecords.status = 2 THEN 1 END) AS absences
    FROM student 
    JOIN user ON student.userID = user.userID
    JOIN studentsInClasses ON student.studentID = studentsInClasses.studentID
    JOIN class ON studentsInClasses.classID = class.classID
    LEFT JOIN attendanceRecords ON student.studentID = attendanceRecords.studentID 
        AND class.classID = attendanceRecords.classSessionID
    WHERE class.subjectNumber = %s
    GROUP BY student.studentNumber, user.name, user.lastName;""", (subject_number,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(results)

@app.route('/api/students_table/<subject_number>', methods=['GET'])
def get_students_table(subject_number):
    query = """
    SELECT 
        student.studentNumber,
        ClassSession.sessionDate,
    COALESCE(attendanceStatus.status, "absent") as "status"
    FROM student
    JOIN studentsInClasses ON student.studentID = studentsInClasses.studentID
    JOIN class ON studentsInClasses.classID = class.classID
    JOIN ClassSession ON class.classID = ClassSession.classID
    LEFT JOIN attendanceRecords ON student.studentID = attendanceRecords.studentID 
        AND ClassSession.sessionID = attendanceRecords.classSessionID
    LEFT JOIN attendanceStatus ON attendanceRecords.status = attendanceStatus.attendanceID
    WHERE class.subjectNumber = %s
    """
    # Use parameterized query to safely pass subject_number
    df = pd.read_sql(query, engine, params=(subject_number,))
    
    # Pivot the data
    pivot_table = df.pivot(index='studentNumber', columns='sessionDate', values='status')
    
    # Convert the pivot table to JSON and return
    return pivot_table.to_json()


@app.route('/api/students/current-class', methods=['GET'])
def get_students_by_current_class():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    curr_date = datetime.today().strftime('%Y-%m-%d')
    curr_time = datetime.now().strftime('%H:%M:%S')

    # get currently happening class
    cursor.execute("""
    SELECT ClassSession.sessionID AS sessionID FROM ClassSession
    WHERE ClassSession.sessionDate = %s
    AND ClassSession.sessionStartTime <= %s
    AND ClassSession.sessionEndTime >= %s
    LIMIT 1
    """,(curr_date, curr_time, curr_time) )
    result = cursor.fetchone()

    if result is None:
        return jsonify(result)

    # get students and status from that class
    cursor.execute("""
    SELECT 
        class.subjectName,
        student.studentNumber, 
        user.name, 
        user.lastName, 
        COALESCE(attendanceStatus.status, 'absent') AS status
    FROM studentsInClasses 
    JOIN student ON studentsInClasses.studentId = student.studentID
    JOIN user ON user.userId = student.userID
    JOIN class ON studentsInClasses.classID = class.classID
    JOIN ClassSession ON class.classID = ClassSession.classID
    LEFT JOIN attendanceRecords 
        ON ClassSession.sessionID = attendanceRecords.classSessionID 
        AND attendanceRecords.studentID = student.studentID
    LEFT JOIN attendanceStatus ON attendanceStatus.attendanceId = attendanceRecords.status
    WHERE ClassSession.sessionID = %s
    """, (result['sessionID'],))


    students = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(students)

    
@app.route('/api/class/<subject_number>', methods=['GET'])
def get_class_by_number(subject_number):
    print(f"ClassPage: Received subject_number: {subject_number}")
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT classID, subjectName, subjectType, absenceLimit,
        year, semester, room, day, time
        FROM class WHERE subjectNumber = %s""", (subject_number,))
    result = cursor.fetchone()

    if isinstance(result['day'], datetime):
        result['day'] = result['day'].strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(result['time'], timedelta):
            result['time'] = str(result['time'])

    cursor.close()
    connection.close()
    return jsonify(result)



@app.route('/api/student/by-number/<student_number>', methods=['GET'])
@jwt_required()  # Requires a valid JWT token
def get_student_by_number(student_number):
    # Get the logged-in user's email from the token
    email = get_jwt_identity()

    # Fetch student data based on email
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if(checkIfStudentEmail(email)):
        cursor.execute("""SELECT student.studentNumber FROM student 
                        JOIN user ON student.userID = user.userID 
                        WHERE user.email = %s""", (email,))
        student = cursor.fetchone()

        # Ensure the logged-in student can only access their own data
        if not student or str(student["studentNumber"]) != str(student_number):
            cursor.close()
            connection.close()
            return jsonify({"error": "Unauthorized access"}), 403
    
    cursor.close()
    connection.close()

    # Fetch and return student details
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT user.name, user.lastName FROM student
                      JOIN user ON student.userID = user.userID
                      WHERE student.studentNumber = %s""", (student_number,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(result)



@app.route('/api/student/<email>', methods=['GET'])
def get_student_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT user.name as name, user.lastName as lastName,
                   student.studentNumber as studentNumber FROM student
                   JOIN user ON student.userID = user.userID
                   WHERE user.email = %s""", (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(result)

@app.route('/api/teacher/<email>', methods=['GET'])
def get_teacher_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT user.name as name, user.lastName as lastName FROM teacher
                   JOIN user ON teacher.userID = user.userID
                   WHERE user.email = %s""", (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return jsonify({"error": "Teacher not found"}), 404
    return jsonify(result)

@app.route('/api/is-teacher-of-class/<subject_number>', methods=['GET'])
@jwt_required()
def get_is_valid_teacher(subject_number):
    is_teacher = is_teacher_of_class(subject_number)
    return jsonify(is_teacher)

@app.route('/api/class/<subject_number>/student/<student_number>/attendance', methods=['GET'])
@jwt_required()
def get_attendance_by_class_and_student(subject_number, student_number):
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    email = get_jwt_identity()
    #check if its a teacher

    if(checkIfStudentEmail(email)): # check if student has access
        cursor.execute("""SELECT student.studentNumber FROM student 
                        JOIN user ON student.userID = user.userID 
                        WHERE user.email = %s""", (email,))
        student = cursor.fetchone()
        

        if not student or str(student["studentNumber"]) != str(student_number):
            cursor.close()
            connection.close()
            return jsonify({"error": "Unauthorized access"}), 403

    else: # check if teacher has access
        valid_teacher = is_teacher_of_class(subject_number)
        if not valid_teacher:
            return jsonify({'message': 'Not allowed: You do not teach this class'}), 403

    date_format = '%d.%m.%YT%H:%i'
    cursor.execute("""SELECT DATE_FORMAT(CONCAT(attendanceRecords.date, ' ', attendanceRecords.time), %s)  as date, attendanceStatus.status as status
                   FROM attendanceRecords JOIN attendanceStatus
                   ON attendanceRecords.status = attendanceStatus.attendanceID
                   join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
                   JOIN class ON class.classID = ClassSession.classID
                   JOIN student ON attendanceRecords.studentID = student.studentID
                   WHERE student.studentNumber = %s
                   AND class.subjectNumber = %s""", (date_format, student_number, subject_number))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(results)

@app.route('/api/class/<subject_number>/student/<student_number>/statistics', methods=['GET'])
@jwt_required()
def get_late_time(subject_number, student_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    email = get_jwt_identity()
    #check if its a teacher

    if(checkIfStudentEmail(email)):
        cursor.execute("""SELECT student.studentNumber FROM student 
                        JOIN user ON student.userID = user.userID 
                        WHERE user.email = %s""", (email,))
        student = cursor.fetchone()
        

        if not student or str(student["studentNumber"]) != str(student_number):
            cursor.close()
            connection.close()
            return jsonify({"error": "Unauthorized access"}), 403

    else: # check if teacher has access
        valid_teacher = is_teacher_of_class(subject_number)
        if not valid_teacher:
            return jsonify({'message': 'Not allowed: You do not teach this class'}), 403

    # total late time in seconds
    # exclude negative times from the addition (if student was too early)
    cursor.execute("""
        SELECT SUM(
            CASE 
                WHEN TIME_TO_SEC(SUBTIME(attendanceRecords.time, class.time)) >= 0 
                THEN TIME_TO_SEC(SUBTIME(attendanceRecords.time, class.time))
                ELSE 0
            END
        ) AS lateTime
        FROM attendanceRecords
        join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
        JOIN class ON class.classID = ClassSession.classID
        JOIN student ON student.studentID = attendanceRecords.studentID
        JOIN attendanceStatus ON attendanceStatus.attendanceID = attendanceRecords.status
        WHERE class.subjectNumber = %s AND student.studentNumber = %s
        AND attendanceStatus.status = %s
    """, (subject_number, student_number, 'late'))
    late_time = cursor.fetchone()


    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN attendanceStatus.status IN ('late', 'present') THEN 1 END) AS timesInClass,
            COUNT(CASE WHEN attendanceStatus.status = 'late' THEN 1 END) AS timesLate,
            COUNT(CASE WHEN attendanceStatus.status IN ('absent', 'excused') THEN 1 END) AS missedClasses,
            COUNT(CASE WHEN attendanceStatus.status = 'absent' THEN 1 END) As timesUnexcused
        FROM attendanceRecords
        join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
        JOIN class ON class.classID = ClassSession.classID
        JOIN student ON student.studentID = attendanceRecords.studentID
        JOIN attendanceStatus 
        ON attendanceStatus.attendanceID = attendanceRecords.status
        WHERE class.subjectNumber = %s AND student.studentNumber = %s
        """, (subject_number, student_number,))
    attendance_times = cursor.fetchone()

    result = {
        'lateTime': late_time['lateTime'],
        'timesInClass': attendance_times['timesInClass'],
        'timesLate': attendance_times['timesLate'],
        'missedClasses': attendance_times['missedClasses'],
        'timesUnexcused': attendance_times['timesUnexcused']
    }

    cursor.close()
    connection.close()
    return jsonify(result)
    

@app.route('/api/class/update-absence-limit', methods=['POST'])
@jwt_required()
def update_absence_limit():
    data = request.get_json()
    print(data) 
    subject_number = data['subjectNumber']
    absence_limit = data['absenceLimit']

    is_valid_teacher = is_teacher_of_class(subject_number)

    if not is_valid_teacher:
        return jsonify({"message": "action not allowed"}), 403

    if not subject_number or absence_limit is None:
        return jsonify({"message": "subjectNumber and absenceLimit are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE class 
        SET absenceLimit = %s
        WHERE subjectNumber = %s
    """, (absence_limit, subject_number))

    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({"message": "Absence limit updated successfully"}), 200


@app.route('/api/update-attendance', methods=['POST'])
@jwt_required()
def update_attendance():

    data = request.get_json()
    print(data)
    subject_number = data['subjectNumber']
    student_number = data ['studentNumber']
    status = data['status']
    time = data['time']
    date = data['date']

    if time == "0:0:00" or time == "00:00:00":
        return jsonify({"message" : "Time is null"}), 400

    is_valid_teacher = is_teacher_of_class(subject_number)
    if not is_valid_teacher:
        return jsonify({"message": "not allowed"}), 403

    if(status == 'none'):
        return jsonify({"message": "update-attendance called but delete-attendance-record should have been called instead"}), 500
    

    if not subject_number or not student_number or status is None:
        return jsonify({"message": "subjectNumber, studentNumber and status are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # convert date back
    date_obj = datetime.strptime(date, '%d.%m.%Y')
    formatted_date = date_obj.strftime('%Y-%m-%d')

    print(formatted_date)

    # check if row for this class, student and day already exists
    cursor.execute("""
        SELECT * FROM attendanceRecords
        join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
        JOIN class ON class.classID = ClassSession.classID
        JOIN student ON attendanceRecords.studentID = student.studentID
        WHERE class.subjectNumber = %s
        AND student.studentNumber = %s
        AND attendanceRecords.date = %s
    """, (subject_number, student_number, formatted_date))
    rows = cursor.fetchall()
    duplicates_found = False
    if len(rows) > 1:
        duplicates_found = True

    if len(rows) == 1: # update row
        cursor.execute("""
            UPDATE attendanceRecords
            join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
            JOIN class ON class.classID = ClassSession.classID
            JOIN student ON attendanceRecords.studentID = student.studentID
            JOIN attendanceStatus ON attendanceStatus.status = %s
            SET attendanceRecords.status = attendanceStatus.attendanceID,
                attendanceRecords.time = %s
            WHERE student.studentNumber = %s 
            AND class.subjectNumber = %s
            AND attendanceRecords.date = %s
        """, (status, time, student_number, subject_number, formatted_date))

    else:  # create new entry

        # check if there is a session on this day
        cursor.execute("""
            SELECT sessionID, sessionStartTime, sessionEndTime
            FROM ClassSession
            WHERE classID = (SELECT classID FROM class WHERE subjectNumber = %s)
              AND sessionDate = %s
        """, (subject_number, formatted_date))  
        sessions = cursor.fetchall()

        session_id = None
        time_obj = datetime.strptime(time, '%H:%M:%S').time()
        time_delta = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)


        # check if a session exists at this time
        for session in sessions:
            print(session['sessionStartTime'])
            print("<=")
            print(time_delta)
            print("<=")
            print(session['sessionEndTime'])
            if session['sessionStartTime'] <= time_delta <= session['sessionEndTime']:
                print("time within session")
                session_id = session['sessionID']
                break

        # if no session at this time, create one
        if not session_id:
            cursor.execute("""
                INSERT INTO ClassSession (classID, sessionDate, sessionStartTime, sessionEndTime)
                VALUES (
                    (SELECT classID FROM class WHERE subjectNumber = %s),
                    %s,
                    %s,
                    ADDTIME(%s, '01:00:00')
                )
            """, (subject_number, formatted_date, time, time))
            session_id = cursor.lastrowid # lastrowid gives primary key id of last inserted row


        # Step 3: Insert the attendance record
        cursor.execute("""
        INSERT INTO attendanceRecords (classSessionID, studentID, date, time, status)
        VALUES (
            %s,
            (SELECT studentID FROM student WHERE studentNumber = %s),
            %s,
            %s,
            (SELECT attendanceID FROM attendanceStatus WHERE status = %s)
        )
        """, (session_id, student_number, formatted_date, time, status))
            

        if cursor.rowcount == 0:
            return jsonify({"message": "Failed to add row"}), 500
            

    connection.commit()
    cursor.close()
    connection.close()

    if duplicates_found:
        return jsonify({"message": "Duplicate entry in database"}), 409

    return jsonify({"message": "Status updated successfully"}), 200

@app.route('/api/delete-attendance-record', methods=['POST'])
@jwt_required()
def delete_attendance_record():
    data = request.get_json()
    subject_number = data['subjectNumber']
    student_number = data['studentNumber']
    date = data['date']

    is_valid_teacher = is_teacher_of_class(subject_number)
    if not is_valid_teacher:
        return jsonify({"message": "not allowed"}), 403

    date_obj = datetime.strptime(date, '%d.%m.%Y')
    formatted_date = date_obj.strftime('%Y-%m-%d')

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE attendanceRecords FROM attendanceRecords
        join ClassSession on attendanceRecords.classSessionID = ClassSession.sessionID
        JOIN class ON class.classID = ClassSession.classID
        JOIN student ON student.studentID = attendanceRecords.studentID
        WHERE student.studentNumber = %s 
        AND class.subjectNumber = %s 
        AND date = %s
    """, (student_number, subject_number, formatted_date))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Status updated successfully"}), 200

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


# doctors notes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in DN_ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    extension = filename.rsplit('.', 1)[1].lower()  # Get file extension
    unique_id = uuid.uuid4().hex
    new_filename = f"{unique_id}_{filename}"
    return new_filename

@app.route('/upload-file', methods=['POST'])
@jwt_required()
def upload_file():
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    file = request.files['file']
    subject_number = request.form['subjectNumber']
    student_number = request.form['studentNumber']
    date = request.form['date']

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    # check if user has access to this operation
    email = get_jwt_identity()
    if(checkIfStudentEmail(email)):
        cursor.execute("""SELECT student.studentNumber FROM student 
                        JOIN user ON student.userID = user.userID 
                        WHERE user.email = %s""", (email,))
        student = cursor.fetchone()
        

        if not student or str(student["studentNumber"]) != str(student_number): # student is trying to upload file for someone else
            cursor.close()
            connection.close()
            return jsonify({"error": "Unauthorized access"}), 403

    else: # not a student
        return jsonify({"error": "Unauthorized access"}), 403
    

    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        filepath = os.path.join(app.config['DN_UPLOAD_FOLDER'], unique_filename)

        print(f"Saving file to: {filepath}")
        
        file.save(filepath)
        
        # Insert the file path into the database
       

        # check if attendance Record for given date, student and class exists
        cursor.execute("""SELECT attendanceRecords.recordID FROM attendanceRecords 
            JOIN ClassSession on ClassSession.sessionID = attendanceRecords.classSessionID
            JOIN class on class.classID = ClassSession.classID
            JOIN student on student.studentID = attendanceRecords.studentID
            WHERE student.studentNumber = %s
            AND class.subjectNumber = %s
            AND attendanceRecords.date = %s
        """, (student_number, subject_number, date ))

        result = cursor.fetchone()
        if result is None:
            return jsonify({'message': 'Invalid date'}), 400
            

        cursor.execute("""
            INSERT INTO Excuse(recordID, status, filePath)
            VALUES (
            (SELECT attendanceRecords.recordID FROM attendanceRecords 
            JOIN ClassSession on ClassSession.sessionID = attendanceRecords.classSessionID
            JOIN class on class.classID = ClassSession.classID
            JOIN student on student.studentID = attendanceRecords.studentID
            WHERE student.studentNumber = %s
            AND class.subjectNumber = %s
            AND attendanceRecords.date = %s),
            'sent',
            %s)
        """, (student_number, subject_number, date, unique_filename ))

        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'File uploaded and recorded successfully!'}), 200
    
    return jsonify({'message': 'Invalid file type'}), 400


@app.route('/list-files', methods=['GET'])
@jwt_required()
def list_files():
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # if user is student, return null
    user_mail = get_jwt_identity()
    if getWhetherUserIsTeacher(user_mail) == False:
        return jsonify(None)

    # select excuses with status = sent and from classes this teacher has
    cursor.execute("""
        SELECT 
            Excuse.excuseID,
            COALESCE(class.subjectName, 'Unknown') AS subjectName, 
            COALESCE(user_student.name, 'Unknown') AS name, 
            COALESCE(user_student.lastName, 'Unknown') AS lastName, 
            COALESCE(attendanceRecords.date, 'Unknown') AS date,
            Excuse.filePath
        FROM Excuse
        JOIN attendanceRecords ON attendanceRecords.recordID = Excuse.recordID
        JOIN ClassSession ON ClassSession.sessionID = attendanceRecords.classSessionID
        JOIN class ON class.classID = ClassSession.classID
        JOIN student ON student.studentID = attendanceRecords.studentID
        JOIN user AS user_student ON user_student.userID = student.userID
        JOIN teachersInClasses ON teachersInClasses.classID = class.classID
        JOIN teacher ON teachersInClasses.teacherId = teacher.teacherID
        JOIN user AS user_teacher ON user_teacher.userID = teacher.userID
        WHERE Excuse.status = %s
        AND user_teacher.email = %s
    """, ('sent', user_mail))
        

    results = cursor.fetchall()
    print(results)

    filtered_results = []
    for row in results:
        excuseId, subjectName, name, lastName, date, filePath = row

        if filePath and os.path.exists(os.path.join(app.config['DN_UPLOAD_FOLDER'], filePath)):  # Only include if file exists
            filtered_results.append({
                "excuseId": excuseId,
                "subjectName": subjectName,
                "name": name,
                "lastName": lastName,
                "date": date,
                "filePath": filePath
            })

    
    cursor.close()
    connection.close()
    
    return jsonify(filtered_results)


@app.route('/doctors_note/decide/<operation>', methods=['POST'])
@jwt_required()
def accept_reject_note(operation):

    connection = get_db_connection()
    cursor = connection.cursor()
    data = request.get_json()
    excuseId = data['excuseId']

    cursor.execute("SELECT status FROM Excuse WHERE Excuse.excuseId = %s", (excuseId,))
    result = cursor.fetchone();
    if result is None or result[0] != 'sent':
        print("Doctors note state != 'sent'")  
        return jsonify({'message': 'State of doctors note is not equal to sent'}), 400

    if operation == 'accept':
        cursor.execute("""
        UPDATE Excuse
        SET status = 'accepted'
        WHERE excuseId = %s;
        """, (excuseId,))

        cursor.execute("""
        UPDATE attendanceRecords SET attendanceRecords.status = (
        SELECT attendanceID FROM attendanceStatus WHERE attendanceStatus.status = %s
        )
        WHERE attendanceRecords.recordID = (
        SELECT recordID 
        FROM Excuse 
        WHERE Excuse.excuseId = %s
        )""", ('excused', excuseId))
        
    elif operation == 'reject':
        cursor.execute("""
        UPDATE Excuse
        SET status = 'rejected'
        WHERE excuseId = %s;
        """, (excuseId,))

    else:
        print("[accept_reject_note] unknown operation: " + operation)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Unknown operation'}), 400

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Excuse status updated successfully'}), 200


@app.route('/doctors_notes/<filename>', methods=['GET'])
@jwt_required()
def serve_file(filename):
    return send_from_directory(app.config['DN_UPLOAD_FOLDER'], filename)




if __name__ == '__main__':
    app.run(debug=True)