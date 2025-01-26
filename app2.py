from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import mysql.connector

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
    user = User.query.filter_by(name=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        isTeacher = getWhetherUserIsTeacher(email)
        token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=1))
        return jsonify({'token': token , 'isTeacher': isTeacher})
    return jsonify({'message': 'Invalid credentials'}), 401


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
                    JOIN class ON class.classID = attendanceRecords.classID
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
    cursor.execute("""SELECT subjectNumber, subjectName FROM class""")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(results)

@app.route('/api/students/<subject_number>', methods=['GET'])
def get_students_by_class(subject_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            student.studentNumber,
            student.studentID,
            user.name, 
            user.lastName,
            COALESCE(attendance.absences, 0) AS absences
        FROM student
        JOIN user ON student.userID = user.userID
        JOIN studentsInClasses ON student.studentID = studentsInClasses.studentID
        JOIN class ON studentsInClasses.classID = class.classID
        LEFT JOIN (
            SELECT 
                ar.studentID, 
                COUNT(*) AS absences 
            FROM attendanceRecords ar
            JOIN attendanceStatus ats ON ar.status = ats.attendanceID
            JOIN studentsInClasses ON ar.studentID = studentsInClasses.studentID
            JOIN class ON studentsInClasses.classID = class.classID
            WHERE ats.status = 'absent'
            AND class.subjectNumber = %s
            AND ar.classID = class.classID
            GROUP BY ar.studentID
        ) attendance ON student.studentID = attendance.studentID
        WHERE class.subjectNumber = %s;
        """, (subject_number, subject_number))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(results)

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

@app.route('/api/student/<student_number>', methods=['GET'])
def get_student_by_number(student_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT user.name as name, user.lastName as lastName FROM student
                   JOIN user ON student.userID = user.userID
                   WHERE student.studentNumber = %s""", (student_number,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(result)

@app.route('/api/class/<subject_number>/student/<student_number>/attendance', methods=['GET'])
def get_attendance_by_class_and_student(subject_number, student_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    date_format = '%d.%m.%YT%H:%i'
    cursor.execute("""SELECT DATE_FORMAT(CONCAT(attendanceRecords.date, ' ', attendanceRecords.time), %s)  as date, attendanceStatus.status as status
                   FROM attendanceRecords JOIN attendanceStatus
                   ON attendanceRecords.status = attendanceStatus.attendanceID
                   JOIN class ON attendanceRecords.classID = class.classID
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
        JOIN class ON class.classID = attendanceRecords.classID
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
        JOIN class ON class.classID = attendanceRecords.classID
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
        JOIN class ON attendanceRecords.classID = class.classID
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
            JOIN class ON attendanceRecords.classID = class.classID
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
        JOIN class ON attendanceRecords.classID = class.classID
        JOIN student ON student.studentID = attendanceRecords.studentID
        WHERE student.studentNumber = %s 
        AND class.subjectNumber = %s 
        AND date = %s
    """, (student_number, subject_number, formatted_date))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Status updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)