import React from 'react';
import './HomePage.css';
import { useNavigate } from 'react-router-dom';



function ClassCard({ name, number, type, onClick }) {

    const navigate = useNavigate();

    const handleCardClick = (classNumber) => {
        navigate(`/class/${classNumber}`);
    };


    return (
        <div className="class-card" onClick={() => handleCardClick(number)}>
          <h2>{name}</h2>
          <p>Type: {type}</p>
          <p>Number: {number}</p>
        </div>
  );
}

export default ClassCard;
