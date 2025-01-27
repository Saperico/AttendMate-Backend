from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime, timedelta
from mail import *
import pandas as pd

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
    return email[0:6].isdigit() and email.endswith('@student.pwr.edu.pl')

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

@app.route('/api/classes', methods=['GET'])
def get_classes():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT classID, subjectName, subjectNumber, year, semester, room, day, time FROM class""")
    results = cursor.fetchall()

    for row in results:
        if isinstance(row['day'], datetime):
            row['day'] = row['day'].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row['time'], timedelta):
            row['time'] = str(row['time'])

    cursor.close()
    connection.close()
    return jsonify(results)
    

@app.route('/api/students/<subject_number>', methods=['GET'])
def get_students_by_class(subject_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT 
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

@app.route('/api/student/<email>', methods=['GET'])
def get_student_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT user.name as name, user.lastName as lastName FROM student
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

@app.route('/api/class/<subject_number>/student/<student_number>/attendance', methods=['GET'])
def get_attendance_by_class_and_student(subject_number, student_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
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
def get_late_time(subject_number, student_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

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
    

#'http://127.0.0.1:5000/api/class/update-absence-limit
@app.route('/api/class/update-absence-limit', methods=['POST'])
def update_absence_limit():
    data = request.get_json()
    print(data) 
    subject_number = data['subjectNumber']
    absence_limit = data['absenceLimit']

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
def update_attendance():
    data = request.get_json()
    print(data)
    subject_number = data['subjectNumber']
    student_number = data ['studentNumber']
    status = data['status']
    time = data['time']
    date = data['date']

    if(status == 'none'):
        return jsonify({"message": "update-attendance called but delete-attendance-record should have been called instead"}), 500
    

    if not subject_number or not student_number or status is None:
        return jsonify({"message": "subjectNumber, studentNumber and status are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

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

    else: # create new entry
        cursor.execute("""
        INSERT INTO attendanceRecords (classID, studentID, date, time, status)
        VALUES (
        (SELECT class.classID from class WHERE class.subjectNumber = %s),
        (SELECT student.studentID from student WHERE student.studentNumber = %s),
        %s,
        %s,
        (SELECT attendanceStatus.attendanceID from attendanceStatus 
            WHERE attendanceStatus.status = %s)
        )
        """, (subject_number, student_number, formatted_date, time, status))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Failed to add row"}), 500
            

    connection.commit()
    cursor.close()
    connection.close()

    if duplicates_found:
        return jsonify({"message": "Duplicate entry in database"}), 409

    return jsonify({"message": "Status updated successfully"}), 200

@app.route('/api/delete-attendance-record', methods=['POST'])
def delete_attendance_record():
    data = request.get_json()
    subject_number = data['subjectNumber']
    student_number = data['studentNumber']
    date = data['date']

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

if __name__ == '__main__':
    app.run(debug=True)