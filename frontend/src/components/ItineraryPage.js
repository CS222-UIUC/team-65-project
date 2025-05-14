import React, { useState } from 'react';
import { GoogleMap, LoadScript, Marker, Polyline } from "@react-google-maps/api";
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ItineraryPage.css';

function ItineraryPage() {
  const [itineraryItems, setItineraryItems] = useState([]);
  const [routeData, setRouteData] = useState(null);
  const [llmInput, setLlmInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [mapError, setMapError] = useState(null);
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");

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
    updateRoute(newItems);
  };

  const handleModifyItem = (index, newValue) => {
    const newItems = [...itineraryItems];
    newItems[index] = { ...newItems[index], ...newValue };
    setItineraryItems(newItems);
    updateRoute(newItems);
  };

  const updateRoute = async (items) => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/update_itinerary", {
        user_request: "Update route based on modified itinerary",
        current_itinerary: items
      });
      
      if (response.data.route && !response.data.route.error) {
        setRouteData(response.data.route);
        setMapError(null);
      } else {
        const errorMsg = response.data.route?.error || "Failed to update route";
        console.error("Route update error:", errorMsg);
        setMapError(errorMsg);
      }
    } catch (error) {
      console.error("Error updating route:", error);
      setMapError("Failed to update route");
    }
  };

  const handleLLM = async () => {
    if (!llmInput.trim()) return;

    setChatHistory((prev) => [...prev, { sender: "user", message: llmInput }]);
    setMapError(null);

    try {
      console.log("Sending request to backend with:", {
        user_request: llmInput,
        start_location: startLocation || "Times Square, New York, NY",
        end_location: endLocation || startLocation || "Times Square, New York, NY"
      });

      const response = await axios.post("http://127.0.0.1:5000/generate_itinerary", {
        user_request: llmInput,
        start_location: startLocation || "Times Square, New York, NY",
        end_location: endLocation || startLocation || "Times Square, New York, NY",
        current_location: { lat: 40.7580, lng: -73.9855 }
      });

      console.log("Backend response:", response.data);

      if (response.data.itinerary) {
        // Update itinerary items
        setItineraryItems(response.data.itinerary);
        
        // Update route if available
        if (response.data.route && !response.data.route.error) {
          setRouteData(response.data.route);
          setChatHistory((prev) => [
            ...prev,
            { sender: "llm", message: "I've created an itinerary for your trip!" },
          ]);
        } else {
          const errorMsg = response.data.route?.error || "Failed to generate route";
          console.error("Route generation error:", errorMsg);
          setMapError(errorMsg);
          setChatHistory((prev) => [
            ...prev,
            { sender: "llm", message: "I've created an itinerary, but couldn't generate the route map." },
          ]);
        }
      } else {
        console.error("No itinerary in response:", response.data);
        setMapError("No itinerary data received from server");
        setChatHistory((prev) => [
          ...prev,
          { sender: "llm", message: "Error: No itinerary data received." },
        ]);
      }
    } catch (error) {
      console.error("Error communicating with LLM:", error);
      console.error("Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setMapError(`Failed to generate itinerary: ${error.message}`);
      setChatHistory((prev) => [
        ...prev,
        { sender: "llm", message: `Error: ${error.message || "Unable to process your request."}` },
      ]);
    }

    setLlmInput("");
  };

  // Helper function to decode Google Maps polyline
  const decodePolyline = (encoded) => {
    if (!encoded) return [];
    const poly = [];
    let index = 0;
    let lat = 0;
    let lng = 0;

    while (index < encoded.length) {
      let shift = 0;
      let result = 0;

      do {
        let b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (result >= 0x20);

      let dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
      lat += dlat;

      shift = 0;
      result = 0;

      do {
        let b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (result >= 0x20);

      let dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
      lng += dlng;

      poly.push({ lat: lat / 1e5, lng: lng / 1e5 });
    }

    return poly;
  };

  return (
    <div className="itinerary-page">
      <Link to="/" className="back-button">
        Back to Home
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
                <p>Duration: {item.duration}</p>
                <p>Location: {item.location}</p>
                <button onClick={() => handleRemoveItem(index)}>Remove</button>
                <button onClick={() => handleModifyItem(index, { title: "Modified Title" })}>
                  Modify
                </button>
              </div>
            ))}
          </div>
        </div>
        <div className="right-panel">
          <div className="location-inputs">
            <div className="location-input-group">
              <label htmlFor="start-location">Start Location</label>
              <input
                id="start-location"
                type="text"
                className="location-input"
                placeholder="Enter start location"
                value={startLocation}
                onChange={(e) => setStartLocation(e.target.value)}
              />
            </div>
            <div className="location-input-group">
              <label htmlFor="end-location">End Location</label>
              <input
                id="end-location"
                type="text"
                className="location-input"
                placeholder="Enter end location (optional)"
                value={endLocation}
                onChange={(e) => setEndLocation(e.target.value)}
              />
            </div>
          </div>
          <div className="map-container">
            <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
              <GoogleMap
                mapContainerStyle={containerStyle}
                center={center}
                zoom={10}
              >
                {routeData?.markers?.map((marker, index) => (
                  <Marker
                    key={index}
                    position={marker.position}
                    title={marker.title}
                    label={{
                      text: `${index + 1}`,
                      color: "white",
                    }}
                    icon={{
                      url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                    }}
                  />
                ))}

                {routeData?.overview_polyline && (
                  <Polyline
                    path={decodePolyline(routeData.overview_polyline)}
                    options={{
                      strokeColor: "#4285F4",
                      strokeOpacity: 1.0,
                      strokeWeight: 4,
                    }}
                  />
                )}
              </GoogleMap>
            </LoadScript>
            {mapError && (
              <div className="map-error">
                {mapError}
              </div>
            )}
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
                placeholder="Describe your trip or ask for modifications..."
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