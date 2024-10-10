import React, { useState, useEffect } from 'react';
import axios from 'axios';

function TableData({ tableName }) {
  const [data, setData] = useState([]);
  

  useEffect(() => {
    const fetchTableData = async () => {
      try {
        if (tableName === "selected") {
          return;
        }
        const response = await axios.get(`http://localhost:5000/table/${tableName}`);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching table data:', error);
      }
    };
    if (tableName) {
      fetchTableData();
    }
  }, [tableName]);

  if (!tableName || tableName === "selected") return null;

  return (
    <div className="container">
    <h3 className="text-center">Data for Table: {tableName}</h3>
    <div className="row justify-content-center">
      <div className="col-auto">
        <table className="table table-bordered">
          <thead>
            <tr>
              {data.length > 0 && Object.keys(data[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index}>
                {Object.values(row).map((value, idx) => (
                  <td key={idx}>{value}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    <h3 className="text-center">...</h3>
  </div>
  );
};

export default TableData;
