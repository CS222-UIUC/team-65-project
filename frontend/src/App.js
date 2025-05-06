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
    try {
      const response = await axios.post("http://127.0.0.1:5000/get_route", {
        start,
        end,
        stops,
      });
      setRoute(response.data);

      // Update the state for Google Maps API
      const coordinates = response.data.routes[0].geometry.coordinates; // Assuming GeoJSON format
      const path = coordinates.map(([lng, lat]) => ({ lat, lng })); // Convert to Google Maps format
      setGoogleMapRoute(path); // Update the Google Maps route state
    } catch (error) {
      console.error("Error fetching route:", error);
    }
  };

  const handleFindPlaces = async () => {
    try {
      let requestData = { place_type: placeType };

      if (route) {
        requestData["route"] = route;
      } else if (userLocation) {
        requestData["location"] = userLocation;
      } else {
        alert("Unable to determine location.");
        return;
      }

      const response = await axios.post(
        "http://127.0.0.1:5000/find_places",
        requestData
      );

      console.log("Found Places Response:", response.data); // Debugging

      if (Array.isArray(response.data)) {
        setFoundPlaces(response.data);
      } else {
        console.error("Unexpected response format:", response.data);
        setFoundPlaces([]);
      }
    } catch (error) {
      console.error("Error fetching places:", error);
    }
  };

  const handleLLM2 = async () => {
    try {
      let requestData = { place_type: placeType };

      if (route) {
        requestData["route"] = route;
      } else if (userLocation) {
        requestData["location"] = userLocation;
      } else {
        alert("Unable to determine location.");
        return;
      }

      const response = await axios.post(
        "http://127.0.0.1:5000/find_places",
        requestData
      );
      setFoundPlaces(response.data);
    } catch (error) {
      console.error("Error fetching places:", error);
    }
  };

  const addPlaceToStops = (place) => {
    setStops([...stops, place.name]);
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
        userLocation: userLocation, // Include user location
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
      <div className="app-container" style={{ fontFamily: "Arial, sans-serif", padding: "20px" }}>
        {/* Header Section */}
        <header style={{ textAlign: "center", marginBottom: "20px" }}>
          <h1 style={{ color: "#333" }}>Route Planner</h1>
          <p style={{ color: "#555" }}>Plan your route and explore places along the way!</p>
        </header>
  
        {/* Input Section */}
        <section style={{ marginBottom: "20px" }}>
          <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
            <input
              type="text"
              placeholder="Start Location"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              style={{
                flex: 1,
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
            <input
              type="text"
              placeholder="End Location"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              style={{
                flex: 1,
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <input
              type="text"
              placeholder="Place Type (e.g., restaurants)"
              value={placeType}
              onChange={(e) => setPlaceType(e.target.value)}
              style={{
                flex: 1,
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
            <button
              onClick={() => alert("Find Places Clicked")}
              style={{
                padding: "10px 20px",
                backgroundColor: "#007BFF",
                color: "#FFF",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Find Places
            </button>
          </div>
        </section>
  
        {/* Map Section */}
        <section style={{ marginBottom: "20px" }}>
          <div className="googleMap">
            <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
              <GoogleMap mapContainerStyle={containerStyle} center={userLocation} zoom={10}>
                <Marker position={userLocation} />
                {route && (
                  <Polyline
                    path={route}
                    options={{ strokeColor: "#FF0000", strokeWeight: 4 }}
                  />
                )}
              </GoogleMap>
            </LoadScript>
          </div>
        </section>
  
 
      </div>
    );
  
}

export default App;
