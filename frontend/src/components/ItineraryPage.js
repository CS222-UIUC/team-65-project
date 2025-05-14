import React, { useState } from 'react';
import { GoogleMap, LoadScript, Marker, Polyline } from "@react-google-maps/api";
import { Link } from 'react-router-dom';
import './ItineraryPage.css';

function ItineraryPage() {
  const [itineraryItems, setItineraryItems] = useState([]);
  const [llmInput, setLlmInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const containerStyle = {
    width: "100%",
    height: "400px",
  };

  const center = {
    lat: 40.1164,
    lng: -88.2434,
  };

  const handleRemoveItem = (index) => {
    const newItems = [...itineraryItems];
    newItems.splice(index, 1);
    setItineraryItems(newItems);
  };

  const handleModifyItem = (index, newValue) => {
    const newItems = [...itineraryItems];
    newItems[index] = { ...newItems[index], ...newValue };
    setItineraryItems(newItems);
  };

  const handleLLM = async () => {
    if (!llmInput.trim()) return;

    setChatHistory((prev) => [...prev, { sender: "user", message: llmInput }]);

    try {
      // Add your LLM API call here
      const response = "Sample LLM response"; // Replace with actual API call
      setChatHistory((prev) => [
        ...prev,
        { sender: "llm", message: response },
      ]);
    } catch (error) {
      console.error("Error communicating with LLM:", error);
      setChatHistory((prev) => [
        ...prev,
        { sender: "llm", message: "Error: Unable to fetch response." },
      ]);
    }

    setLlmInput("");
  };

  return (
    <div className="itinerary-page">
      <Link to="/" className="back-button">
        ← Back to Trip Planner
      </Link>
      
      <div className="itinerary-content">
        <div className="itinerary-container">
          <h2>Your Itinerary</h2>
          <div className="itinerary-list">
            {itineraryItems.map((item, index) => (
              <div key={index} className="itinerary-item">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <p>Time: {item.time}</p>
                <button onClick={() => handleRemoveItem(index)}>Remove</button>
                <button onClick={() => handleModifyItem(index, { title: "Modified Title" })}>
                  Modify
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="right-panel">
          <div className="map-container">
            <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
              <GoogleMap
                mapContainerStyle={containerStyle}
                center={center}
                zoom={10}
              >
                <Marker position={center} />
              </GoogleMap>
            </LoadScript>
          </div>

          <div className="chat-container">
            <div className="chat-history">
              {chatHistory.map((chat, index) => (
                <div key={index} className={`chat-message ${chat.sender}`}>
                  {chat.message}
                </div>
              ))}
            </div>
            <div className="chat-input">
              <textarea
                value={llmInput}
                onChange={(e) => setLlmInput(e.target.value)}
                placeholder="Ask about your itinerary..."
              />
              <button onClick={handleLLM}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ItineraryPage; 