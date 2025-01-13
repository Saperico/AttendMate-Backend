CREATE DATABASE IF NOT EXISTS AttendMate;
USE AttendMate;

-- Table definitions
CREATE TABLE attendanceStatus (
    attendanceID INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(255) NOT NULL
);

CREATE TABLE user (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE teacher (
    teacherID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT UNIQUE NOT NULL,
    FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

CREATE TABLE student (
    studentID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT UNIQUE NOT NULL,
    studentNumber INT UNIQUE NOT NULL,
    FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

CREATE TABLE images (
    imageID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    number INT NOT NULL,
    path VARCHAR(255) NOT NULL,
    FOREIGN KEY (studentID) REFERENCES student(studentID) ON DELETE CASCADE
);

CREATE TABLE class (
    classID INT AUTO_INCREMENT PRIMARY KEY,
    subjectName VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    semester TINYINT CHECK (semester IN (1, 2)) NOT NULL,
    room VARCHAR(50),
    day ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday') NOT NULL,
    time TIME NOT NULL,
    absenceLimit INT DEFAULT 3
);

CREATE TABLE studentsInClasses (
    classID INT NOT NULL,
    studentID INT NOT NULL,
    PRIMARY KEY (classID, studentID),
    FOREIGN KEY (classID) REFERENCES class(classID) ON DELETE CASCADE,
    FOREIGN KEY (studentID) REFERENCES student(studentID) ON DELETE CASCADE
);

CREATE TABLE teachersInClasses (
    classID INT NOT NULL,
    teacherID INT NOT NULL,
    PRIMARY KEY (classID, teacherID),
    FOREIGN KEY (classID) REFERENCES class(classID) ON DELETE CASCADE,
    FOREIGN KEY (teacherID) REFERENCES teacher(teacherID) ON DELETE CASCADE
);

CREATE TABLE attendanceRecords (
    recordID INT AUTO_INCREMENT PRIMARY KEY,
    classID INT NOT NULL,
    studentID INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status INT,
    FOREIGN KEY (classID) REFERENCES class(classID) ON DELETE CASCADE,
    FOREIGN KEY (studentID) REFERENCES student(studentID) ON DELETE CASCADE,
    FOREIGN KEY (status) REFERENCES attendanceStatus(attendanceID) ON DELETE SET NULL
);

CREATE TABLE Excuse (
    excuseID INT AUTO_INCREMENT PRIMARY KEY,
    recordID INT NOT NULL,
    status ENUM('sent', 'accepted', 'rejected') NOT NULL,
    filePath VARCHAR(255) NOT NULL,
    FOREIGN KEY (recordID) REFERENCES attendanceRecords(recordID) ON DELETE CASCADE
);

-- This are just examples how to insert data into tables

INSERT INTO attendanceStatus (status) 
VALUES
    ('present'), 
    ('absent'), 
    ('late'), 
    ('excused');

INSERT INTO user (name, lastName, email, password) 
VALUES('John', 'Doe', 'johndoe@example.com', SHA2('securepassword123', 256));

INSERT INTO teacher (userID) 
VALUES (1);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Jane', 'Smith', 'janesmith@example.com', SHA2('securepassword456', 256)); 

INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230001);

INSERT INTO images (studentID, number, path) 
VALUES (LAST_INSERT_ID(), 1, '/images/students/janesmith1.jpg');

INSERT INTO class (subjectName, year, semester, room, day, time, absenceLimit) 
VALUES ('Software Engineering Project', 2024, 2, '127c', 'monday', '17:05', 3);

insert into teachersInClasses (classID, teacherID)
values (1, 1);

INSERT INTO studentsInClasses (classID, studentID) 
VALUES (1, 1);

INSERT INTO attendanceRecords (classID, studentID, date, time, status) 
VALUES (1, 1, '2024-12-13', '17:10:23', 1);

