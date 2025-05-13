import React, { useState, useEffect } from "react";
import axios from "axios";
// import Map from "./components/Map";
import "./App.css";
import {
  GoogleMap,
  LoadScript,
  Marker,
  Polyline,
} from "@react-google-maps/api";

function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [stops, setStops] = useState([]);
  const [route, setRoute] = useState(null);
  const [placeType, setPlaceType] = useState("");
  const [foundPlaces, setFoundPlaces] = useState([]);

  const clearMap = () => {
    setGoogleMapRoute([]);
    setRoute(null);
    setMapKey((prevKey) => prevKey + 1); // Update the map key to force re-render
  };

  const [mapKey, setMapKey] = useState(0);

  // const getSegmentColor = (index, total) =>
  //   `hsl(${Math.round((index / total) * 360)}, 80%, 50%)`;
  // const [googleMapSegments, setGoogleMapSegments] = useState([]);
  const [userLocation, setUserLocation] = useState({
    lat: 40.1164,
    lon: -88.2434,
    name: "Champaign, IL (Default)",
  });

  const containerStyle = {
    width: "100%",
    height: "400px",
  };

  const center = {
    lat: 40.1164, // Replace with your lat
    lng: -88.2434, // Replace with your lng
  };

  const [googleMapRoute, setGoogleMapRoute] = useState([]); // For Google Maps API

  // Get User's Current Location
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      (error) => {
        console.error("Error getting location:", error);
      }
    );
  }, []);

  const handleAddStop = () => {
    setStops([...stops, ""]);
  };

  const [llmInput, setLlmInput] = useState("");

  const handleStopChange = (index, value) => {
    const newStops = [...stops];
    newStops[index] = value;
    setStops(newStops);
  };

  const handleSubmit = async () => {
    // Clear the map and route data before fetching a new route
    clearMap();
    try {
      console.log("Route data:", "hi");
      const response = await axios.post("http://127.0.0.1:5000/get_route", {
        start,
        end,
        stops,
      });
      console.log("Route data:", "hi");
      setRoute(response.data);
      // // Update the state for Google Maps API

      const coordinates = response.data.routes[0].geometry.coordinates; // Assuming GeoJSON format
      const path = coordinates.map(([lng, lat]) => ({ lat, lng })); // Convert to Google Maps format
      setGoogleMapRoute(path); // Update the Google Maps route state
    } catch (error) {
      console.error("Error fetching route:", error);
    }
  };

  const addPlaceToStops = (place) => {
    setStops([...stops, place.address]);
  };

  // export the route to a google maps link
  const exportToGoogleMaps = () => {
    if (!route) {
      alert("No route to export.");
      return;
    }

    const waypoints = stops.map((stop) => encodeURIComponent(stop)).join("|");
    const startLocation = encodeURIComponent(start);
    const endLocation = encodeURIComponent(end);

    const googleMapsUrl = `https://www.google.com/maps/dir/${startLocation}/${waypoints}/${endLocation}/@${route.lat},${route.lon},12z`;

    window.open(googleMapsUrl, "_blank");
  };

  const [chatHistory, setChatHistory] = useState([]); // State to store chat history
  const [llmRecommendations, setLlmRecommendations] = useState([]);

  const handleLLM = async () => {
    if (!llmInput.trim()) return; // Prevent empty messages

    // Add user input to chat history
    setChatHistory((prev) => [...prev, { sender: "user", message: llmInput }]);

    try {
      const response = await axios.post("http://127.0.0.1:5000/llm_chat", {
        message: llmInput,
        start: start, // Include start location
        end: end, // Include end location
        stops: stops, // Include stops
      });

      const llmResponse = response.data.response;

      // Add LLM response to chat history
      setChatHistory((prev) => [
        ...prev,
        { sender: "llm", message: "Here are the top recommendations:" },
      ]);

      // Update the recommendations state
      setLlmRecommendations(llmResponse);
    } catch (error) {
      console.error("Error communicating with LLM:", error);
      setChatHistory((prev) => [
        ...prev,
        { sender: "llm", message: "Error: Unable to fetch response." },
      ]);
    }

    setLlmInput(""); // Clear input field
  };

  const saveRouteToLocalStorage = () => {
    if (googleMapRoute.length > 0) {
      localStorage.setItem("googleMapRoute", JSON.stringify(googleMapRoute));
      alert("Route saved to local storage!");
    } else {
      alert("No route to save!");
    }
  };
  const restoreRouteFromLocalStorage = () => {
    const savedRoute = localStorage.getItem("googleMapRoute");
    if (savedRoute) {
      setGoogleMapRoute(JSON.parse(savedRoute));
      alert("Route restored from local storage!");
    } else {
      alert("No saved route found in local storage!");
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title">Trip Planner</h1>
      </header>

      <main className="main-content">
        <div class="box1">
          {/* Start and End Locations */}
          <section className="section">
            <h2 className="section-title">Plan Your Trip</h2>
            <div className="input-group">
              <input
                className="textBox"
                type="text"
                placeholder="Start Location"
                value={start}
                onChange={(e) => setStart(e.target.value)}
              />
              <input
                className="textBox"
                type="text"
                placeholder="End Location"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
              />
            </div>
          </section>

          {/* Stops */}
          <section className="section">
            <h2 className="section-title">Stops</h2>
            <div className="stops-container">
              {stops.map((stop, index) => (
                <input
                  className="stopTextBox"
                  key={index}
                  type="text"
                  placeholder={`Stop ${index + 1}`}
                  value={stop}
                  onChange={(e) => handleStopChange(index, e.target.value)}
                />
              ))}
              <div className="button-group">
                <button className="button" onClick={handleAddStop}>
                  + Add Stop
                </button>
                <button className="button primary" onClick={handleSubmit}>
                  Get Route
                </button>
                <button
                  className="button secondary"
                  onClick={exportToGoogleMaps}
                >
                  Export to Google Maps
                </button>
              </div>
            </div>
          </section>

          <section className="section">
            <h2 className="section-title">LLM Chat</h2>
            <div className="input-group">
              <textarea
                className="llmTextBox"
                placeholder="Enter places you wish to visit on your route."
                value={llmInput}
                onChange={(e) => setLlmInput(e.target.value)}
              />
              <button className="button primary" onClick={handleLLM}>
                Send
              </button>
            </div>
             <section className="section">
            <h2 className="section-title">Top Recommendations</h2>
            {llmRecommendations.length > 0 ? (
              <ul className="recommendations-list">
                {llmRecommendations.map((place, index) => (
                  <li key={index} className="recommendation-item">
                    <h3>{place.name}</h3>
                    <p>
                      <strong>Category:</strong> {place.category}
                    </p>
                    <p>
                      <strong>Estimated Time:</strong>{" "}
                      {place.estimated_time_minutes} minutes
                    </p>
                    <p>
                      <strong>Description:</strong> {place.description}
                    </p>
                    <p>
                      <strong>Address:</strong> {place.address}
                    </p>
                    <p>
                      <strong>Worth Visiting:</strong> {place.worth_visiting}
                    </p>
                    <button
                      className="button small"
                      onClick={() => addPlaceToStops(place)}
                    >
                      Add to Stops
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p>
                No recommendations yet. Use the LLM chat to get suggestions.
              </p>
            )}
          </section>
        
          </section>

          {/* Display Found Places */}
          {foundPlaces.length > 0 && (
            <section className="section">
              <h2 className="section-title">Suggested Places</h2>
              <ul className="found-places-list">
                {foundPlaces.map((place, index) => (
                  <li key={index} className="place-item">
                    <h3>{place.name}</h3>
                    <p>
                      <strong>Latitude:</strong> {place.lat}
                    </p>
                    <p>
                      <strong>Longitude:</strong> {place.lon}
                    </p>
                    <p>
                      <strong>Description:</strong> {place.description}
                    </p>
                    <p>
                      <strong>Estimated Time:</strong>{" "}
                      {place.estimated_time_minutes} minutes
                    </p>
                    <button
                      className="button small"
                      onClick={() => addPlaceToStops(place)}
                    >
                      Add to Stops
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* Map */}
        <div className="box2">
          <section className="section">
            <div className="googleMap">
              <LoadScript
                googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}
              >
                <GoogleMap
                  key={mapKey} // Adding key to force re-render
                  mapContainerStyle={containerStyle}
                  center={center}
                  zoom={10}
                >
                  <Marker position={center} />
                  {googleMapRoute.length > 0 && (
                    <Polyline
                      path={googleMapRoute}
                      options={{
                        strokeColor: "#FF0000",
                        strokeOpacity: 1.0,
                        strokeWeight: 4,
                      }}
                    />
                  )}
                </GoogleMap>
              </LoadScript>
            </div>

            {/* <button
              onClick={saveRouteToLocalStorage}
              style={{ marginTop: "10px" }}
            >
              Save Route */}
            {/* </button>
            <button
              onClick={restoreRouteFromLocalStorage}
              style={{ marginTop: "10px" }}
            >
              Restore Route
            </button> */}
          </section>

          {/* Recommendations Section */}
         
        </div>
      </main>
    </div>
  );
}

export default App;
