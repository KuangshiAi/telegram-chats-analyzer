import React, { useState } from "react";
import { useLocation } from 'react-router-dom';
import Header from "./Header.jsx";
import FileUpload from "./FileUpload.jsx";
import TableList from "./TableList.jsx";

function StartPage() {
  const location = useLocation();
  const { showHeaderProp } = location.state || { showHeaderProp: true };
  const [showHeader, setShowHeader] = useState(showHeaderProp);

  function handleStart() {
    setShowHeader(false);
  }

  

  return (
    <div className="App">
      {showHeader ? (
        <Header onClick={handleStart} />
      ) : (
        <div>
          <FileUpload />
          <div className="container mt-5">
            <div className="card">
              <div className="card-header">
                <h3>Current Databases</h3>
              </div>
              <div className="card-body">
                <TableList />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StartPage;
