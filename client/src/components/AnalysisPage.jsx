// AnalysisPage.jsx

import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import ShowFunctions from './ShowFunctions';
import axios from 'axios';

const AnalysisPage = () => {
  const location = useLocation();
  const { startDate, endDate, dbName, contact } = location.state;

  const [selectedFunction, setSelectedFunction] = useState(null);
  const [calendarImages, setCalendarImages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mapping of image keys to their respective titles
  const imageTitles = {
    both: "Overall Chat Frequency",
    from_contact: "Chats from Contact",
    from_me: "Chats from Me",
  };

  const functions = [
    { funcName: "Visualize Chat Frequency Calendar", funcDescription: "Generate a calendar heatmap of chat frequency" },
    { funcName: "Function 2", funcDescription: "Description for function 2" },
    { funcName: "Function 3", funcDescription: "Description for function 3" },
    { funcName: "Function 4", funcDescription: "Description for function 4" }
  ];

  const handleFunctionSelect = async (funcName) => {
    setSelectedFunction(funcName);
    setError(null);
    setCalendarImages(null); // Reset previous images

    if (funcName === "Visualize Chat Frequency Calendar") {
      setLoading(true);
      try {
        // Make the API call to generate the calendar images
        console.log("contact", contact);
        const response = await axios.get('http://127.0.0.1:5000/api/countChatDates', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            db_name: dbName,
            contact_name: contact 
          }
        });

        if (response.data && response.data.images) {
          // Set the entire images object
          setCalendarImages(response.data.images);
        } else {
          setError("Image URLs not found in the response.");
        }
      } catch (err) {
        console.error("Error fetching calendar data:", err);
        setError("Failed to generate calendar.");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="container">
      <h1 className="text-center mt-4">Analysis of Chats with {contact}</h1>
      <div className="row mt-5">
        {functions.map((func, index) => (
          <div className="col-md-6 mb-4" key={index}>
            <ShowFunctions
              funcName={func.funcName}
              funcDescription={func.funcDescription}
              onClick={() => handleFunctionSelect(func.funcName)}
            />
          </div>
        ))}
      </div>
      <div className="mt-5">
        {selectedFunction && (
          selectedFunction === "Visualize Chat Frequency Calendar" ? (
            loading ? (
              <p className="text-center">Generating calendar...</p>
            ) : error ? (
              <p className="text-center text-danger">{error}</p>
            ) : calendarImages ? (
              <div>
                <div className="row g-3"> {/* Adjust gutter size as needed */}
                  {Object.keys(calendarImages).map((key) => (
                    <div className="col-md-4" key={key}>
                      <div className="card h-100"> {/* Ensure cards have equal height */}
                        <div className="card-body text-center">
                          <h5 className="card-title">{imageTitles[key]}</h5>
                          <img
                            src={calendarImages[key]}
                            alt={`${imageTitles[key]} Visualization`}
                            className="img-fluid"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null
          ) : (
            <p className="text-center">In progress</p>
          )
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
