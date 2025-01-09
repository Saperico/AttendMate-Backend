
import React from 'react';
import { useParams } from 'react-router-dom';
import CalendarView from './CalendarView';


function StudentPage({ classData, studentsData, attendanceData }) {
    const { classNumber } = useParams();
    const { studentNumber } = useParams();
    const classItem = classData.find(item => item.number === classNumber);
    const student = studentsData.find(item => item.number === studentNumber);

    console.log(student);



    return (
        <><div className="header-container">
            <button className="back-button" onClick={() => window.history.back()}>&#129144;</button>
            <h1>
                {student.firstName} {student.lastName}
                <span className="student-number">{student.number}</span>
            </h1>
        </div>
            <div className="main-body">
                <CalendarView attendanceData={attendanceData} />
        </div></>
    );
}

export default StudentPage;