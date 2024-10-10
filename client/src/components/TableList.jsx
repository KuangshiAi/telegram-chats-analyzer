import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TableData from './TableData';
import "./components.css"

const TableList = () => {
  const [tables, setTables] = useState([]);
  const navigate = useNavigate();
  const selectRef = useRef(null);
  const [selectedOption, setSelectedOption] = useState('selected');

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get('http://localhost:5000/tables');
        setTables(response.data);
      } catch (error) {
        console.error('Error fetching table names:', error);
      }
    };
    fetchTables();
  }, []);

  function handleChange(event) {
    const selectedTable = event.target.value;
    setSelectedOption(selectedTable);
  }

  function handleSelect() {
    const dbName = selectedOption;
    if (dbName === 'selected') {
      return;
    }
    navigate('/functions/', { state: { dbName: dbName } });
  }

  async function handleDelete() {
    if (selectedOption === 'selected') {
      alert('Please select a table to delete.');
      return;
    }

    if (window.confirm(`Are you sure you want to delete table "${selectedOption}"?`)) {
      try {
        await axios.delete(`http://localhost:5000/table/delete/${selectedOption}`);
        alert(`Table "${selectedOption}" has been deleted.`);
        // 更新表列表
        setTables(tables.filter(table => table !== selectedOption));
        setSelectedOption('selected');
      } catch (error) {
        console.error('Error deleting table:', error);
        alert('Error deleting table. Please check the console for more details.');
      }
    }
  }

  return (
    <div>
      <div className="input-group mb-3 justify-content-center">
        <select
          className="custom-select"
          id="selectDatabase"
          onChange={handleChange}
          ref={selectRef}
          value={selectedOption}
        >
          <option value="selected">Choose...</option>
          {tables.map((table) => (
            <option value={table} key={table}>
              {table}
            </option>
          ))}
        </select>
        <div className="input-group-append">
          <button
            className="input-group-text analyze-button"
            onClick={handleSelect}
          >
            Select
          </button>
        </div>
        <button
          className="btn btn-danger ml-2"
          onClick={handleDelete}
          disabled={selectedOption === 'selected'}
        >
          Delete
        </button>
      </div>
      {selectedOption !== 'selected' && (
        <TableData tableName={selectedOption} />
      )}
    </div>
  );
};

export default TableList;
