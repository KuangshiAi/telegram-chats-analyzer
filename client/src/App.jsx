import React from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import "./App.css";
import StartPage from "./components/StartPage";
import AnalysisPage from "./components/AnalysisPage";
import FunctionsPage from "./components/FunctionsPage";

function App() {
  return (
    <Router>
    <Routes>
        <Route path="/" element={<StartPage />} />
        <Route path="/functions" element={<FunctionsPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
    </Routes>
</Router>
  );
}


export default App;
