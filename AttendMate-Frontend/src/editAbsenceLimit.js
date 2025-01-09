
import React, { useState } from 'react';

const EditAbsenceLimit = ({ absenceLimit }) => {
    const [maxAbsences, setMaxAbsences] = useState(absenceLimit);
    const [isEditMenuOpen, setIsEditMenuOpen] = useState(false);
    const [newMaxAbsences, setNewMaxAbsences] = useState(maxAbsences);

    const handleEditClick = () => {
        setNewMaxAbsences("");
        setIsEditMenuOpen(true);
    }

    const handleSave = () => {
        if (newMaxAbsences < 0) {
            alert("Please enter a valid number");
            return;
        }
        if (newMaxAbsences === "") {
            setIsEditMenuOpen(false);
            return;
        }
        setMaxAbsences(newMaxAbsences);
        setIsEditMenuOpen(false);
    }

    const handleCancel = () => {
        setIsEditMenuOpen(false);
    }

    return (
        <div>
            {!isEditMenuOpen && (

                <button className="attendance-limit-button" onClick={() => handleEditClick()}>
                    Absence Limit: {maxAbsences} &#x1F589;
                </button>
            )}
            {isEditMenuOpen && (
                <div className="popup">
                    <h3>Edit Max Absences</h3>
                    <input
                        type="number"
                        value={newMaxAbsences}
                        onChange={(e) => {
                            if (e.target.value === "") {
                                setNewMaxAbsences("");
                            }
                            else {
                                setNewMaxAbsences(Number(e.target.value))
                            }
                        }}
                    />
                    <div>
                        <button onClick={handleSave}>Save</button>
                        <button onClick={handleCancel}>Cancel</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EditAbsenceLimit;