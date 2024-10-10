import React, { useState, useEffect } from 'react'; 
import axios from 'axios';
import { ProgressBar, Button } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faCheckCircle, faTimesCircle, faPlay } from '@fortawesome/free-solid-svg-icons';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState(''); 
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentContactProgress, setCurrentContactProgress] = useState(0);
  const [processedContacts, setProcessedContacts] = useState(0);
  const [totalContacts, setTotalContacts] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploaded, setIsUploaded] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadStatus('');
    setUploadProgress(0);
    setCurrentContactProgress(0);
    setProcessedContacts(0);
    setTotalContacts(0);
    setIsUploaded(false);
    setIsProcessing(false);
    setTableName(''); 
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });
      setIsUploaded(true);
      setUploadStatus('Upload succeeds.');
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Upload error.');
    }
  };

  const handleProcess = async () => {
    if (!tableName) {
      setUploadStatus('Please enter a table name.');
      return;
    }

    try {
      setIsProcessing(true); 
      await axios.post('http://localhost:5000/process', { tableName });
      setUploadStatus('Processing starts.');
      pollProgress();
    } catch (error) {
      console.error('Processing error:', error);
      setUploadStatus('Processing error.');
      setIsProcessing(false);
    }
  };

  const pollProgress = () => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get('http://localhost:5000/progress');
        const data = response.data;

        setCurrentContactProgress(data.current_contact_progress);
        setProcessedContacts(data.processed_contacts);
        setTotalContacts(data.total_contacts);

        if (data.processed_contacts === data.total_contacts) {
          clearInterval(interval); 
          setUploadStatus('Processing succeeds. Refresh to view.');
          setIsProcessing(false);
        }
      } catch (error) {
        console.error('Error:', error);
        clearInterval(interval); 
        setIsProcessing(false); 
      }
    }, 1000); 
  };

  return (
    <div className="container mt-5">
      <div className="card">
        <div className="card-header">
          <h3>Upload Telegram Chats json File</h3>
        </div>
        <div className="card-body">
          <div className="mb-3">
            <input type="file" className="form-control" onChange={handleFileChange} />
          </div>
          <div className="mb-3">
            <Button onClick={handleUpload} variant="primary" disabled={isUploaded}>
              <FontAwesomeIcon icon={faUpload} /> Upload
            </Button>
          </div>
          {uploadProgress > 0 && (
            <div className="mb-3">
              <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} />
            </div>
          )}
          {isUploaded && (
            <>
              <div className="mb-3">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Please enter a table name"
                  value={tableName}
                  onChange={(e) => setTableName(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <Button onClick={handleProcess} variant="success" disabled={isProcessing}>
                  <FontAwesomeIcon icon={faPlay} /> Process Data and Load to Database
                </Button>
              </div>
              {isProcessing && (
                <div className="mb-3">
                  <ProgressBar now={currentContactProgress} label={`${currentContactProgress}%`} />
                  <div>Processing {processedContacts + 1} contacts，in total {totalContacts}.</div>
                </div>
              )}
            </>
          )}
          {uploadStatus && (
            <div className="mb-3">
              <FontAwesomeIcon icon={isUploaded && processedContacts === totalContacts ? faCheckCircle : faTimesCircle} /> {uploadStatus}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
