from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Enum, Time, Date, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.mysql import TINYINT
from app import db




class AttendanceStatus(db.Model):
    __tablename__ = 'attendanceStatus'

    attendanceID = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(255), nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    userID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    teacher = relationship("Teacher", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)


class Teacher(db.Model):
    __tablename__ = 'teacher'

    teacherID = Column(Integer, primary_key=True, autoincrement=True)
    userID = Column(Integer, ForeignKey('user.userID', ondelete="CASCADE"), unique=True, nullable=False)

    user = relationship("User", back_populates="teacher")
    classes = relationship("Class", back_populates="teacher")


class Student(db.Model):
    __tablename__ = 'student'

    studentID = Column(Integer, primary_key=True, autoincrement=True)
    userID = Column(Integer, ForeignKey('user.userID', ondelete="CASCADE"), unique=True, nullable=False)
    studentNumber = Column(Integer, unique=True, nullable=False)

    user = relationship("User", back_populates="student")
    images = relationship("Image", back_populates="student")
    classes = relationship("StudentsInClasses", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")


class Image(db.Model):
    __tablename__ = 'images'

    imageID = Column(Integer, primary_key=True, autoincrement=True)
    studentID = Column(Integer, ForeignKey('student.studentID', ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    path = Column(String(255), nullable=False)

    student = relationship("Student", back_populates="images")


class Class(db.Model):
    __tablename__ = 'class'

    classID = Column(Integer, primary_key=True, autoincrement=True)
    subjectName = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(TINYINT, nullable=False)
    room = Column(String(50))
    day = Column(Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'), nullable=False)
    time = Column(Time, nullable=False)
    idTeacher = Column(Integer, ForeignKey('teacher.teacherID', ondelete="CASCADE"), nullable=False)

    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("StudentsInClasses", back_populates="class_")
    attendance_records = relationship("AttendanceRecord", back_populates="class_")


class StudentsInClasses(db.Model):
    __tablename__ = 'studentsInClasses'

    classID = Column(Integer, ForeignKey('class.classID', ondelete="CASCADE"), primary_key=True)
    studentID = Column(Integer, ForeignKey('student.studentID', ondelete="CASCADE"), primary_key=True)

    class_ = relationship("Class", back_populates="students")
    student = relationship("Student", back_populates="classes")


class AttendanceRecord(db.Model):
    __tablename__ = 'attendanceRecords'

    recordID = Column(Integer, primary_key=True, autoincrement=True)
    classID = Column(Integer, ForeignKey('class.classID', ondelete="CASCADE"), nullable=False)
    studentID = Column(Integer, ForeignKey('student.studentID', ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(Integer, ForeignKey('attendanceStatus.attendanceID', ondelete="SET NULL"))

    class_ = relationship("Class", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
    attendance_status = relationship("AttendanceStatus")
