
import React from 'react';
import { useParams } from 'react-router-dom';
import ClassCard from './ClassCard';
function HomePage({ classData }) {

    return (
        <div className="App">
            <h1>My Classes</h1>
            <div className="class-list">
                {classData.map(cls => (
                    <ClassCard
                        key={cls.id}
                        name={cls.name}
                        type={cls.type}
                        number={cls.number}
                    />
                ))}
            </div>
        </div>
    );
}

export default HomePage;

