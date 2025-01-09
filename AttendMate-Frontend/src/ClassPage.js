
import React from 'react';
import { useParams } from 'react-router-dom';
import StudentsTable from './StudentsTable';
import EditAbsenceLimit from './editAbsenceLimit';


function ClassPage({ classData, studentsData }) {
    const { classNumber } = useParams();
    const classItem = classData.find(item => item.number === classNumber);


    console.log(classItem);

    return (
        <div>
            <div className="header-container">
                <button className="back-button" onClick={() => window.history.back()}>&#129144;</button>
                <h1>
                    {classItem.name}
                    <span className="class-type">{classItem.type}</span>
                </h1>
            </div>
            <EditAbsenceLimit absenceLimit={classItem.absenceLimit}/>
            <StudentsTable studentsData={studentsData}/>
        </div>
    );
}

export default ClassPage;