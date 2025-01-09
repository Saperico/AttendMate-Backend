import React, { useState } from 'react';
import ClassPage from './ClassPage';
import HomePage from './HomePage';
import StudentPage from './StudentPage';
import './HomePage.css';
import './ClassPage.css';
import './StudentPage.css';
import './StudentsTable.css';
import './editAbsenceLimit.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';


function App() {
    const classData =[
        { id: 1, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 2, name: "Physics 202", type: "Laboratory", number: "PHYS202", absenceLimit: 2 },
        { id: 3, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 4, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 5, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 6, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 7, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 8, name: "Mathematics 101", type: "Lecture", number: "MATH101", absenceLimit: 3 },
        { id: 9, name: "Mathematics - Probability and Statistics", type: "Lecture", number: "MATHPS", absenceLimit: 4 },
    ];

    const studentsData = [
        { id: 1, firstName: "John", lastName: "Doe", number: "S1001", absences: 2 },
        { id: 2, firstName: "Jane", lastName: "Smith", number: "S1002", absences: 1 },
        { id: 3, firstName: "Michael", lastName: "Brown", number: "S1003", absences: 0 },
        { id: 4, firstName: "Emily", lastName: "Davis", number: "S1004", absences: 3 },
        { id: 5, firstName: "David", lastName: "Wilson", number: "S1005", absences: 4 },
        { id: 6, firstName: "Sarah", lastName: "Taylor", number: "S1006", absences: 1 },
        { id: 7, firstName: "Chris", lastName: "Martinez", number: "S1007", absences: 0 },
        { id: 8, firstName: "Laura", lastName: "Garcia", number: "S1008", absences: 2 },
        { id: 9, firstName: "Matthew", lastName: "Anderson", number: "S1009", absences: 3 },
        { id: 10, firstName: "Sophia", lastName: "Thomas", number: "S1010", absences: 0 },
        { id: 11, firstName: "Daniel", lastName: "Moore", number: "S1011", absences: 2 },
        { id: 12, firstName: "Olivia", lastName: "Jackson", number: "S1012", absences: 1 },
        { id: 13, firstName: "James", lastName: "Lee", number: "S1013", absences: 4 },
        { id: 14, firstName: "Ava", lastName: "Harris", number: "S1014", absences: 0 },
        { id: 15, firstName: "Benjamin", lastName: "Clark", number: "S1015", absences: 3 },
        { id: 16, firstName: "Mia", lastName: "Walker", number: "S1016", absences: 2 },
        { id: 17, firstName: "Ethan", lastName: "Young", number: "S1017", absences: 1 },
        { id: 18, firstName: "Isabella", lastName: "Allen", number: "S1018", absences: 0 },
        { id: 19, firstName: "Liam", lastName: "Scott", number: "S1019", absences: 4 },
        { id: 20, firstName: "Emma", lastName: "Adams", number: "S1020", absences: 3 },
    ];

    const attendanceData = [
        { date: "2025-01-03", status: "Present" },
        { date: "2025-01-07", status: "Late" },
        { date: "2025-01-10", status: "Absent" },
        { date: "2025-01-14", status: "Present" },
        { date: "2025-01-17", status: "Present" },
        { date: "2025-01-21", status: "Late" },
        { date: "2025-01-24", status: "Excused" },
        { date: "2025-01-28", status: "Present" },
        { date: "2025-01-31", status: "Late" },
    ];


    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage classData={classData} />} />
                <Route path="/class/:classNumber" element={<ClassPage classData={classData} studentsData={studentsData} />} />
                <Route
                    path="/class/:classNumber/student/:studentNumber"
                    element={<StudentPage classData={classData} studentsData={studentsData} attendanceData={attendanceData} />}
                />
            </Routes>
        </Router>
    );
}

export default App;
