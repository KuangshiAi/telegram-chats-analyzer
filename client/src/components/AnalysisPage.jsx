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
  const [resultImage, setResultImage] = useState(null);

  // Parameters for Social Network Graph
  const [minEdgeWeight, setMinEdgeWeight] = useState(3);
  const [topNNodes, setTopNNodes] = useState(100);

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
    { funcName: "Social Network Graph", funcDescription: "Generate a social network graph to visualize user interactions in selected Telegram channels, highlighting key connections" },
  ];

  const handleFunctionSelect = async (funcName) => {
    setSelectedFunction(funcName);
    setError(null);
    setCalendarImages(null);
    setResultImage(null);
    setLoading(true);

    try {
      if (funcName === "Visualize Chat Frequency Calendar") {
        const response = await axios.get('http://127.0.0.1:5000/api/countChatDates', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            db_name: dbName,
            contact_name: contact,
          },
        });
        if (response.data && response.data.images) {
          setCalendarImages(response.data.images);
        } else {
          setError("Image URLs not found in the response.");
        }
      } else if (funcName === "Word Cloud") {
        const response = await axios.get('http://127.0.0.1:5000/api/wordcloud', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            db_name: dbName,
            contact_name: contact,
          },
        });
        if (response.data && response.data.image) {
          setResultImage(response.data.image);
        } else {
          setError("Word Cloud image URL not found in the response.");
        }
      } else if (funcName === "Sentiment Analysis") {
        const response = await axios.get('http://127.0.0.1:5000/api/sentiment', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            db_name: dbName,
            contact_name: contact,
          },
        });
        if (response.data && response.data.image) {
          setResultImage(response.data.image);
        } else {
          setError("Sentiment Analysis image URL not found in the response.");
        }
      } else if (funcName === "Social Network Graph") {
        setLoading(true);
        try {
          const response = await axios.get('http://127.0.0.1:5000/api/social_graph', {
            params: {
              start_date: startDate.toISOString(),
              end_date: endDate.toISOString(),
              db_name: dbName,
              contact_name: contact,
              min_edge_weight: minEdgeWeight,
              top_n_nodes: topNNodes,
            },
          });
          if (response.data && response.data.image) {
            const timestamp = new Date().getTime();
            setResultImage(`${response.data.image}?t=${timestamp}`);
          } else {
            setError("Social Network Graph image URL not found in the response.");
          }
        } catch (err) {
          console.error("Error generating social network graph:", err);
          setError("Failed to generate social network graph.");
        } finally {
          setLoading(false);
        }
      }      
    } catch (err) {
      console.error(`Error performing ${funcName}:`, err);
      setError(`Failed to perform ${funcName.toLowerCase()}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="text-center mt-4">Analysis of Chats with {contact}</h1>
      
      {/* Parameters for Social Network Graph */}
      {selectedFunction === "Social Network Graph" && (
        <div className="row mt-4">
          <div className="col-md-6">
            <label htmlFor="minEdgeWeight" className="form-label">Minimum Edge Weight:</label>
            <input
              type="number"
              id="minEdgeWeight"
              className="form-control"
              value={minEdgeWeight}
              onChange={(e) => setMinEdgeWeight(Number(e.target.value))}
              min="1"
            />
          </div>
          <div className="col-md-6">
            <label htmlFor="topNNodes" className="form-label">Top N Nodes:</label>
            <input
              type="number"
              id="topNNodes"
              className="form-control"
              value={topNNodes}
              onChange={(e) => setTopNNodes(Number(e.target.value))}
              min="1"
            />
          </div>
        </div>
      )}

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
              <div className="row g-3">
                {Object.keys(calendarImages).map((key) => (
                  <div className="col-md-4" key={key}>
                    <div className="card h-100">
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
            ) : null
          ) : selectedFunction === "Word Cloud" || selectedFunction === "Sentiment Analysis" || selectedFunction === "Social Network Graph" ? (
            loading ? (
              <p className="text-center">Generating {selectedFunction.toLowerCase()}...</p>
            ) : error ? (
              <p className="text-center text-danger">{error}</p>
            ) : resultImage ? (
              <div className="text-center">
                <h5>{selectedFunction}</h5>
                <img
                  src={resultImage}
                  alt={`${selectedFunction} Visualization`}
                  className="img-fluid"
                />
              </div>
            ) : null
          ) : (
            <p className="text-center">In progress...</p>
          )
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
