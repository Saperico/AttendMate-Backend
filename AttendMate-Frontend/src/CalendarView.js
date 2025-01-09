import React, { useState } from 'react';
import Calendar from 'react-calendar';
import './CalendarView.css';

function CalendarView({ attendanceData }) {
    const [date, setDate] = useState(new Date());
    const [attendance, setAttendance] = useState({attendanceData})

    const handleTileClick = (selectedDate) => {
        const dateStr = selectedDate.toLocaleDateString('en-CA').split('T')[0];
        const pair = attendanceData.find(item => item.date === dateStr);
        if (pair == null) {
           return 
        }
        const status = pair.status;
        console.log(
            "Date: " + selectedDate
            + " Attendance: " + status
            + " Date String: " + dateStr
        );
    };

    const getTileClassName = ({ date }) => {
        const dateStr = date.toLocaleDateString('en-CA').split('T')[0];
        const pair = attendanceData.find(item => item.date === dateStr);
        if (pair == null) {
            return "";
        }
        const status = pair.status;
        if (status === "Present") return "tile-present";
        if (status === "Late") return "tile-late";
        if (status === "Absent") return "tile-absent";
        if (status === "Excused") return "tile-excused";
        return "";
    };


    return(
    <div>
            <Calendar
                onChange={setDate}
                value={date}
                onClickDay={handleTileClick}
                tileClassName={getTileClassName}
                showNeighboringMonth={false}
            />
        </div>
    )
}

export default CalendarView;