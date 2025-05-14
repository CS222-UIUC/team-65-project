import React, { useState, useEffect } from 'react';
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
  const [mapCenter, setMapCenter] = useState({ lat: 40.1164, lng: -88.2434 });
  const [mapZoom, setMapZoom] = useState(10);
  const [startCoords, setStartCoords] = useState(null);
  const [endCoords, setEndCoords] = useState(null);

  const containerStyle = {
    width: "100%",
    height: "400px",
  };

  // Geocode locations when they change
  useEffect(() => {
    const geocodeLocation = async (address, isStart) => {
      if (!address) return;
      
      try {
        const geocoder = new window.google.maps.Geocoder();
        const result = await geocoder.geocode({ address });
        
        if (result.results[0]) {
          const location = result.results[0].geometry.location;
          const coords = {
            lat: location.lat(),
            lng: location.lng()
          };
          
          if (isStart) {
            setStartCoords(coords);
          } else {
            setEndCoords(coords);
          }
        }
      } catch (error) {
        console.error(`Error geocoding ${isStart ? 'start' : 'end'} location:`, error);
      }
    };

    if (startLocation) {
      geocodeLocation(startLocation, true);
    }
    if (endLocation) {
      geocodeLocation(endLocation, false);
    }
  }, [startLocation, endLocation]);

  // Update map center and zoom when coordinates change
  useEffect(() => {
    if (startCoords && endCoords) {
      // Calculate center point
      const center = {
        lat: (startCoords.lat + endCoords.lat) / 2,
        lng: (startCoords.lng + endCoords.lng) / 2
      };
      setMapCenter(center);

      // Calculate distance between points
      const R = 6371; // Earth's radius in km
      const dLat = (endCoords.lat - startCoords.lat) * Math.PI / 180;
      const dLon = (endCoords.lng - startCoords.lng) * Math.PI / 180;
      const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(startCoords.lat * Math.PI / 180) * Math.cos(endCoords.lat * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      const distance = R * c;

      // Set zoom level based on distance
      // Closer points = higher zoom level
      let zoom = 10;
      if (distance < 1) zoom = 15;
      else if (distance < 5) zoom = 13;
      else if (distance < 20) zoom = 11;
      else if (distance < 50) zoom = 9;
      else zoom = 7;

      setMapZoom(zoom);
    } else if (startCoords) {
      setMapCenter(startCoords);
      setMapZoom(13);
    } else if (endCoords) {
      setMapCenter(endCoords);
      setMapZoom(13);
    }
  }, [startCoords, endCoords]);

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
                center={mapCenter}
                zoom={mapZoom}
              >
                {startCoords && (
                  <Marker
                    position={startCoords}
                    title="Start Location"
                    icon={{
                      url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
                    }}
                  />
                )}
                {endCoords && (
                  <Marker
                    position={endCoords}
                    title="End Location"
                    icon={{
                      url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                    }}
                  />
                )}
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
                      url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
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