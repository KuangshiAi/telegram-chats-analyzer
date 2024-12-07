import React, { useState, useEffect } from "react";
import axios from "axios";
import "./components.css";
import ShowCalendar from "./ShowCalendar";
import Fab from "@mui/material/Fab";

function ShowChats(props) {
  const [error, setError] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [chatDates, setChatDates] = useState([]);
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);

  const dbName = props.dbName;

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5000/api/contacts/${dbName}`
        );
        setContacts(response.data);
        setError(null); 
      } catch (error) {
        setError("There was an error fetching the contacts!");
        console.error(error);
      }
    };

    fetchContacts();
  }, [dbName]);

  const handleButtonClick = async (contact, dbName) => {
    if (contact === selectedContact) {
      return;
    }
    const fetchChatDates = async (contact, dbName) => {
      try {
        const response = await axios.get(
          `http://localhost:5000/api/getChatDates/${dbName}/${contact}`
        );
        return response.data;
      } catch (error) {
        setError("There was an error fetching the chat dates!");
        console.error(error);
      }
    };

    const dates = await fetchChatDates(contact, dbName);
    if (dates) {
      setChatDates(dates);
      console.log(dates);
      setShowCalendar(true);
      setSelectedContact(contact);
    }
  };

  return (
    <div className="container spacing">
      <div className="row d-flex justify-content-center align-items-center">
        <div className="badge bg-primary-subtle border border-primary-subtle text-primary-emphasis pill d-inline-block w-auto">
          <h1 style={{ fontSize: "2rem" }}>Contacts</h1>
        </div>
      </div>
      <div className="row d-flex justify-content-center align-items-center">
        {contacts.map((contact, index) => {
          if (contact) {
            return (
              <div
                key={index}
                className="col-3 d-flex justify-content-center align-items-center"
              >
                <Fab
                  color="success"
                  style={{
                    color: "white",
                    width: "7.5rem",
                    height: "7.5rem",
                    fontSize: ".75rem",
                  }}
                  onClick={() => handleButtonClick(contact, dbName)} 
                >
                  {contact}
                </Fab>
              </div>
            );
          }
        })}
      </div>
      {showCalendar && (
        <ShowCalendar
          dates={chatDates}
          contact={selectedContact}
          dbName={dbName}
        />
      )}
    </div>
  );
}

export default ShowChats;
