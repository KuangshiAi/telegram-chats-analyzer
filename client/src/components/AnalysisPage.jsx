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
  const [wordCloudImage, setWordCloudImage] = useState(null);

  // Mapping of image keys to their respective titles
  const imageTitles = {
    both: "Overall Chat Frequency",
    from_contact: "Chats from Contact",
    from_me: "Chats from Me",
  };

  const functions = [
    { funcName: "Visualize Chat Frequency Calendar", funcDescription: "Generate a calendar heatmap of chat frequency to identify active and inactive periods" },
    { funcName: "Word Cloud", funcDescription: "Create a word cloud to visualize the most frequently used words in chat messages" },
    { funcName: "Sentiment Analysis", funcDescription: "Perform sentiment analysis on chat messages and use t-SNE to cluster examples based on emotional tone" },
    { funcName: "Social Network Graph", funcDescription: "Generate a social network graph to visualize user interactions in selected Telegram channels, highlighting key connections" }
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
    else if (funcName === "Word Cloud") {
      setLoading(true);
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/wordcloud', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            db_name: dbName,
            contact_name: contact 
          }
        });
  
        if (response.data && response.data.image) {
          setWordCloudImage(response.data.image);
        } else {
          setError("Word Cloud image URL not found in the response.");
        }
      } catch (err) {
        console.error("Error generating word cloud:", err);
        setError("Failed to generate word cloud.");
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
          ) : selectedFunction === "Word Cloud" ? (
            loading ? (
              <p className="text-center">Generating word cloud...</p>
            ) : error ? (
              <p className="text-center text-danger">{error}</p>
            ) : wordCloudImage ? (
              <div className="text-center">
                <h5>Word Cloud</h5>
                <img
                  src={wordCloudImage}
                  alt="Word Cloud Visualization"
                  className="img-fluid"
                />
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
