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
    subjectType VARCHAR(50),
    subjectNumber VARCHAR(50),
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
VALUES ('Alice', 'Johnson', 'alicejohnson@example.com', SHA2('password789', 256));

INSERT INTO teacher (userID) 
VALUES (LAST_INSERT_ID());

INSERT INTO user (name, lastName, email, password) 
VALUES ('Robert', 'Brown', 'robertbrown@example.com', SHA2('password101', 256));

INSERT INTO teacher (userID) 
VALUES (LAST_INSERT_ID());

-- Insert more students
INSERT INTO user (name, lastName, email, password) 
VALUES ('Emily', 'Davis', 'emilydavis@example.com', SHA2('password111', 256));

INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230002);

INSERT INTO images (studentID, number, path) 
VALUES (LAST_INSERT_ID(), 1, '/images/students/emilydavis1.jpg');

INSERT INTO user (name, lastName, email, password) 
VALUES ('Michael', 'Wilson', 'michaelwilson@example.com', SHA2('password222', 256));

INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230003);

INSERT INTO images (studentID, number, path) 
VALUES (LAST_INSERT_ID(), 1, '/images/students/michaelwilson1.jpg');

INSERT INTO user (name, lastName, email, password) 
VALUES ('David', 'Miller', 'davidmiller@example.com', SHA2('password333', 256));

INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230004);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Emma', 'Johnson', 'emmajohnson@example.com', SHA2('password123', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230005);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Olivia', 'Brown', 'oliviabrown@example.com', SHA2('password456', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230006);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Liam', 'Smith', 'liamsmith@example.com', SHA2('password789', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230007);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Sophia', 'Davis', 'sophiadavis@example.com', SHA2('password101', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230008);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Noah', 'Wilson', 'noahwilson@example.com', SHA2('password202', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230009);

INSERT INTO user (name, lastName, email, password) 
VALUES ('Isabella', 'Garcia', 'isabellagarcia@example.com', SHA2('password303', 256));
INSERT INTO student (userID, studentNumber) 
VALUES (LAST_INSERT_ID(), 20230010);


INSERT INTO class (subjectName, subjectType, subjectNumber, year, semester, room, day, time, absenceLimit) 
VALUES 
('Data Structures', 'Lecture', 'W04IST-SI1020L', 2024, 1, '205a', 'tuesday', '09:00', 2),
('Machine Learning', 'Seminar', 'W04IST-SI4052S', 2024, 2, '312b', 'wednesday', '13:00', 3),
('Software Engineering', 'Lecture', 'W04IST-SI4023L', 2024, 1, '101c', 'friday', '10:00', 3),
('Artificial Intelligence', 'Project', 'W04IST-SI3060P', 2024, 1, '201b', 'monday', '15:00', 2),
('Operating Systems', 'Lecture', 'W04IST-SI3030L', 2024, 2, '102a', 'thursday', '11:00', 3),
('Web Development', 'Lab', 'W04IST-SI1074B', 2024, 1, '110c', 'wednesday', '14:00', 1),
('Computer Networks', 'Lecture', 'W04IST-SI4054L', 2024, 2, '202a', 'friday', '08:00', 3),
('Database Systems', 'Seminar', 'W04IST-SI2010S', 2024, 1, '303b', 'tuesday', '16:00', 3),
('Cloud Computing', 'Lecture', 'W04IST-SI5023L', 2024, 2, '305a', 'thursday', '09:00', 2),
('Cybersecurity', 'Project', 'W04IST-SI4090P', 2024, 2, '307b', 'monday', '17:00', 3);

-- Enroll students into multiple classes
INSERT INTO studentsInClasses (classID, studentID) 
VALUES 
(4, 3), (3, 1), (5, 1), (2, 2), (10, 3), (4, 2), (3, 3), (8, 2), (9, 1), (10, 2),
(1, 2), (2, 1), (6, 1), (7, 3), (5, 2), (9, 3), (8, 1), (1, 1), (7, 2), (6, 3),
(10, 5), (10, 9), (2, 5), (5, 8), (6, 8), (1, 4), (1, 7), (10, 4), (7, 4), (3, 7),
 (6, 5), (5, 7), (2, 3), (3, 4), (4, 1), (6, 7),
(8, 9), (5, 5), (8, 8), (9, 2), (4, 5), (2, 8), (10, 1), (8, 6),
(9, 9), (5, 6), (9, 4), (8, 7), (5, 3);

-- Assign more teachers to classes
INSERT INTO teachersInClasses (classID, teacherID) 
VALUES 
(1, 1), (2, 2), (3, 1), (4, 2), (5, 1), (6, 2), (7, 1), (8, 2), (9, 1), (10, 2);



-- Add attendance records
INSERT INTO attendanceRecords (classID, studentID, date, time, status) 
VALUES 
(1, 1, '2024-12-10', '09:05:00', 1), (1, 2, '2024-12-10', '09:05:00', 2),
(2, 1, '2024-12-11', '13:00:00', 3), (2, 2, '2024-12-11', '13:00:00', 1),
(3, 1, '2024-12-12', '10:05:00', 4), (3, 3, '2024-12-12', '10:05:00', 1),
(4, 2, '2025-01-13', '15:05:00', 1), (4, 3, '2024-12-13', '15:10:00', 2),
(5, 1, '2024-12-14', '11:00:00', 3), (5, 2, '2024-12-14', '11:00:00', 1),
(6, 1, '2024-12-15', '14:10:00', 1), (6, 3, '2024-12-15', '14:00:00', 4),
(7, 2, '2024-12-16', '08:00:00', 2), (7, 3, '2024-12-16', '08:05:00', 3),
(8, 1, '2024-12-17', '16:00:00', 1), (8, 2, '2024-12-17', '16:05:00', 4),
(9, 1, '2024-12-18', '09:10:00', 2), (9, 3, '2024-12-18', '09:00:00', 1),
(10, 2, '2024-12-19', '17:00:00', 1), (10, 3, '2024-12-19', '17:05:00', 3),
(1, 1, '2025-01-10', '09:05:00', 1), (1, 2, '2025-01-10', '09:05:00', 2),
(2, 1, '2025-01-11', '13:00:00', 3), (2, 2, '2025-01-11', '13:00:00', 1),
(3, 1, '2025-01-12', '10:05:00', 4), (3, 3, '2025-01-12', '10:05:00', 1),
(4, 2, '2025-01-13', '15:05:00', 1), (4, 3, '2025-01-13', '15:10:00', 2),
(5, 1, '2025-01-14', '11:00:00', 3), (5, 2, '2025-01-14', '11:00:00', 1),
(6, 1, '2025-01-15', '14:10:00', 1), (6, 3, '2025-01-15', '14:00:00', 4),
(7, 2, '2025-01-16', '08:00:00', 2), (7, 3, '2025-01-16', '08:05:00', 3),
(8, 1, '2025-01-17', '16:00:00', 1), (8, 2, '2025-01-17', '16:05:00', 4),
(9, 1, '2025-01-18', '09:10:00', 2), (9, 3, '2025-01-18', '09:00:00', 1),
(10, 2, '2025-01-19', '17:00:00', 1), (10, 3, '2025-01-19', '17:05:00', 3);

-- Add excuses for some attendance records
INSERT INTO Excuse (recordID, status, filePath) 
VALUES 
(2, 'sent', '/excuses/record2.pdf'),
(4, 'accepted', '/excuses/record4.pdf'),
(6, 'rejected', '/excuses/record6.pdf'),
(8, 'accepted', '/excuses/record8.pdf'),
(10, 'sent', '/excuses/record10.pdf');
