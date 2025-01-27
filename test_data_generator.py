from sqlalchemy import create_engine, text
import datetime

import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='appuser',
        password='apppassword',
        database='AttendMate'
    )
    return connection

#get the class for subject number = W04IST-SI1020L

def get_subject_class(subject_number):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM class WHERE subjectNumber = %s"
    cursor.execute(query, (subject_number,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

#for a class insert new classSession items for fridays from 01.10.2024 - 20.01.2025

def insert_class_sessions(class_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    dates = []
    current_date = datetime.date(2024, 10, 8)
    end_date = datetime.date(2025, 1, 2)
    delta = datetime.timedelta(days=7)  # 1 week

    while current_date <= end_date:
        dates.append(current_date)
        current_date += delta
        print(str(current_date))

    query = """
        INSERT INTO ClassSession (classId, sessionDate, sessionStartTime, sessionEndTime) 
        VALUES (%s, %s, %s, %s)
    """
    for date in dates:
        cursor.execute(query, (class_id, date, '08:00:00', '10:00:00'))
    
    connection.commit()  # Commit the changes to the database
    cursor.close()
    connection.close()

insert_class_sessions(1)