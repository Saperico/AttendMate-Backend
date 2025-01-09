import React from 'react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';


function StudentsTable({ studentsData }) {

    const { classNumber } = useParams();

    const navigate = useNavigate();

    const handleTableClick = (studentNumber) => {
        navigate(`/class/${classNumber}/student/${studentNumber}`)
    }

    return (
        <div className="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Number</th>
                        <th>Last Name</th>
                        <th>First Name</th>
                        <th>Absences</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {studentsData.map(student => (
                        <tr key={student.id} onClick={() => handleTableClick(student.number) }>
                            <td>{student.number}</td>
                            <td>{student.lastName}</td>
                            <td>{student.firstName}</td>
                            <td className="absence">{student.absences}</td>
                            <td className="student-arrow">&#129146;</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default StudentsTable;