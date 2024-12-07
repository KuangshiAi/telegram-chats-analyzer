import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ShowFunctions from './ShowFunctions';
import axios from 'axios';

const AnalysisPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Destructure state passed through location
  const { startDate, endDate, dbName, contact } = location.state || {};

  const [selectedFunction, setSelectedFunction] = useState(null);
  const [calendarImages, setCalendarImages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resultImage, setResultImage] = useState(null);

  // Parameters for Social Network Graph
  const [minEdgeWeight, setMinEdgeWeight] = useState(3);
  const [topNNodes, setTopNNodes] = useState(100);

  // Image titles mapping
  const imageTitles = {
    both: "Overall Chat Frequency",
    from_contact: "Chats from Contact",
    from_me: "Chats from Me",
    pie_chart: "Chat Numbers by User",
    radar_chart: "Chat Time Distribution",
  };

  const functions = [
    {
      funcName: "Visualize Chat Frequency Calendar",
      funcDescription:
        "Generate a calendar heatmap of chat frequency to identify active and inactive periods",
    },
    {
      funcName: "Word Cloud",
      funcDescription:
        "Create a word cloud to visualize the most frequently used words in chat messages",
    },
    {
      funcName: "Sentiment Analysis",
      funcDescription:
        "Perform sentiment analysis on chat messages and use t-SNE to cluster examples based on emotional tone",
    },
    {
      funcName: "Social Network Graph",
      funcDescription:
        "Generate a social network graph to visualize user interactions in selected Telegram channels, highlighting key connections",
    },
    {
      funcName: "Pie Chart of Chat Numbers by User",
      funcDescription:
        "Generate a pie chart representing the distribution of chat numbers among different users",
    },
    {
      funcName: "Radar Chart of Activity by Time of Day",
      funcDescription:
        "Create a radar chart to visualize chat activity distribution across different times of the day",
    },
  ];

  // Navigate back function
  const handleBack = () => {
    console.log(window.history.length, "Navigating back");
    if (window.history.length > 1) {
      navigate(-1); // Go back in history if possible
    } else {
      navigate('/'); // Fallback to the home page
    }
  };

  // Function selection handler
  const handleFunctionSelect = async (funcName) => {
    setSelectedFunction(funcName);
    setError(null);
    setCalendarImages(null);
    setResultImage(null);
    setLoading(true);

    try {
      // Add appropriate API calls based on function name
      const apiMap = {
        "Visualize Chat Frequency Calendar": "countChatDates",
        "Word Cloud": "wordcloud",
        "Sentiment Analysis": "sentiment",
        "Social Network Graph": "social_graph",
        "Pie Chart of Chat Numbers by User": "pie_chart_chat_numbers",
        "Radar Chart of Activity by Time of Day": "radar_chat_time",
      };

      const response = await axios.get(`http://127.0.0.1:5000/api/${apiMap[funcName]}`, {
        params: {
          start_date: startDate?.toISOString(),
          end_date: endDate?.toISOString(),
          db_name: dbName,
          contact_name: contact,
          ...(funcName === "Social Network Graph" && {
            min_edge_weight: minEdgeWeight,
            top_n_nodes: topNNodes,
          }),
        },
      });

      if (response.data) {
        const data = response.data;
        if (data.images) setCalendarImages(data.images);
        if (data.image) setResultImage(data.image);
      } else {
        setError(`Data not found for ${funcName}`);
      }
    } catch (err) {
      console.error(`Error performing ${funcName}:`, err);
      setError(`Failed to perform ${funcName}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* Header with Back Button and Centered Title */}
      <div className="d-flex align-items-center mb-3 mt-5">
        <button
          className="btn btn-primary"
          onClick={handleBack}
          style={{ marginLeft: '20px' }}
        >
          Back
        </button>
        <h1 className="w-100 text-center">Analysis of Chats with {contact}</h1>
      </div>

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
          loading ? (
            <p className="text-center">Loading {selectedFunction}...</p>
          ) : error ? (
            <p className="text-center text-danger">{error}</p>
          ) : calendarImages ? (
            <div className="row g-3">
              {Object.keys(calendarImages).map((key) => (
                <div className="col-md-12" key={key}>
                  <div className="card h-100">
                    <div className="card-body text-center">
                      <h5 className="card-title">{imageTitles[key]}</h5>
                      <img
                        src={calendarImages[key]}
                        alt={`${imageTitles[key]} Visualization`}
                        className="img-fluid"
                        style={{ maxWidth: '70%', maxHeight: '400px' }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : resultImage ? (
            <div className="text-center">
              <img
                src={resultImage}
                alt={`${selectedFunction} Visualization`}
                className="img-fluid"
                style={{ maxWidth: '70%', maxHeight: '400px' }}
              />
            </div>
          ) : null
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
