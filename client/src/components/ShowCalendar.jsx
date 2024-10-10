import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useNavigate } from 'react-router-dom';
import "./components.css";
import axios from 'axios';

const ShowCalendar = ({ dates, contact, dbName }) => {
  const [value, setValue] = useState([new Date(), new Date()]);
  const [tempStartDate, setTempStartDate] = useState("to be selected");
  const [tempEndDate, setTempEndDate] = useState("to be selected");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const navigate = useNavigate();

  // Convert date strings to Date objects
  const parsedDates = dates.map(dateStr => new Date(dateStr));

  const [prevContact, setPrevContact] = useState(null);

useEffect(() => {
  if (contact !== prevContact) {
    setValue([new Date(), new Date()]); 
    setPrevContact(contact);
  }
}, [contact, prevContact]);


  const onChange = (value) => {
    setValue(value);
    if (value.length === 1) {
      setTempStartDate(value[0]);
      setTempEndDate("to be selected");
      setIsButtonDisabled(true);
    } else if (value.length === 2) {
      setTempStartDate(value[0]);
      setTempEndDate(value[1]);
      setIsButtonDisabled(false);
    }
  };

  const handleButtonClick = async () => {
    if (tempStartDate !== "to be selected" && tempEndDate !== "to be selected") {
      setStartDate(tempStartDate);
      setEndDate(tempEndDate);
      // Send the dates to the backend
      await axios.post('http://127.0.0.1:5000/api/dates', {
        startDate: tempStartDate,
        endDate: tempEndDate,
      });
      navigate('/analysis', { state: { startDate: tempStartDate, endDate: tempEndDate, dbName: dbName, contact: contact, } });
    }
  };

  const tileDisabled = ({ date, view }) => {
    if (view === 'month') {
      return !parsedDates.some(d => 
        d.getFullYear() === date.getFullYear() &&
        d.getMonth() === date.getMonth() &&
        d.getDate() === date.getDate()
      );
    }
    if (view === 'year') {
      return !parsedDates.some(d => 
        d.getFullYear() === date.getFullYear() &&
        d.getMonth() === date.getMonth()
      );
    }
    if (view === 'decade') {
      return !parsedDates.some(d => 
        d.getFullYear() === date.getFullYear()
      );
    }
    return false;
  };

  const tileClassName = ({ date, view }) => {
    if (view === 'month') {
      return parsedDates.some(d => 
        d.getFullYear() === date.getFullYear() &&
        d.getMonth() === date.getMonth()
      ) ? 'highlight-month' : null;
    }
    if (view === 'decade') {
      return parsedDates.some(d => 
        d.getFullYear() === date.getFullYear()
      ) ? 'highlight-year' : null;
    }
    return null;
  };

  return (
    <div className="calendar-container">
      <div className="badge bg-primary-subtle border border-primary-subtle text-primary-emphasis pill d-inline-block w-auto bottom-spacing-sm">
        <h1 style={{fontSize: "2rem"}}>Select Dates</h1>
      </div>
      <Calendar
        onChange={onChange}
        value={value}
        selectRange={true}
        tileDisabled={tileDisabled}
        tileClassName={tileClassName}
        locale='en-US'
      />
      <div className="text-center mt-3">
        <p>Start Date: {tempStartDate !== "to be selected" ? tempStartDate.toDateString() : tempStartDate}</p>
        <p>End Date: {tempEndDate !== "to be selected" ? tempEndDate.toDateString() : tempEndDate}</p>
        <button className="btn btn-primary bottom-spacing-sm" onClick={handleButtonClick} disabled={isButtonDisabled}>Confirm and Analyze</button>
      </div>
      {startDate && endDate && (
        <div className="text-center mt-3">
          <p>Confirmed Start Date: {startDate.toDateString()}</p>
          <p>Confirmed End Date: {endDate.toDateString()}</p>
        </div>
      )}
    </div>
  );
};

export default ShowCalendar;