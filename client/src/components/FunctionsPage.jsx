import React, { useState } from "react";
import ShowChats from "./ShowChats";
import "./components.css";
import { useNavigate, useLocation } from "react-router-dom";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import axios from "axios";

function FunctionsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { dbName } = location.state || {};
  

  return (
    <div>
      <div className="container top-spacing">
        <div className="row bottom-spacing justify-content-between">
          <div className="col-4">
            <button
              onClick={() => navigate("/", { state: { showHeader: false } })}
              className="btn btn-primary d-inline-block w-auto"
              style={{fontSize: ".75rem"}}
            >
              <ArrowBackIosIcon />Go Back to Homepage
            </button>
          </div>
        </div>
      </div>
        <ShowChats dbName={dbName} />
      </div>
  );
}

export default FunctionsPage;
