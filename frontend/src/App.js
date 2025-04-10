import React, { useState, useEffect } from "react";
import axios from "axios";
import Map from "./components/Map";
import './App.css';

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
    name: "Champaign, IL (Default)"
  });

  // Get User's Current Location
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude
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

      const response = await axios.post("http://127.0.0.1:5000/find_places", requestData);
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

    const waypoints = stops.map(stop => encodeURIComponent(stop)).join('|');
    const startLocation = encodeURIComponent(start);
    const endLocation = encodeURIComponent(end);

    const googleMapsUrl = `https://www.google.com/maps/dir/${startLocation}/${waypoints}/${endLocation}/@${route.lat},${route.lon},12z`;

    window.open(googleMapsUrl, '_blank');
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title">Trip Planner</h1>
      </header>

      <main className="main-content">


      <div class = "box1">
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
                <button className="button" onClick={handleAddStop}>+ Add Stop</button>
                <button className="button primary" onClick={handleSubmit}>Get Route</button>
                <button className="button secondary" onClick={exportToGoogleMaps}>Export to Google Maps</button>
              </div>
            </div>
          </section>
    
          {/* Find Places */}
          <section className="section">
            <h2 className="section-title">Find Places</h2>
            <div className="input-group">
              <input
                className="textBox"
                type="text"
                placeholder="Search for places (e.g., gas stations, coffee shops)"
                value={placeType}
                onChange={(e) => setPlaceType(e.target.value)}
              />
              <button className="button primary" onClick={handleFindPlaces}>Find Places</button>
            </div>
          </section>
    
          {/* Display Found Places */}
          {foundPlaces.length > 0 && (
            <section className="section">
              <h2 className="section-title">Suggested Places</h2>
              <ul className="found-places-list">
                {foundPlaces.map((place, index) => (
                  <li key={index} className="place-item">
                    <span>{place.name} ({place.lat}, {place.lon})</span>
                    <button className="button small" onClick={() => addPlaceToStops(place)}>Add to Stops</button>
                  </li>
                ))}
              </ul>
            </section>
          )}

    </div>
  
        {/* Map */}
        <div class = "box2">
          <section className="section">
            <h2 className="section-title">Route Map</h2>
            <Map className = "map-section" route={route} />
          </section>
        </div>

      </main>
    </div>
  );
}

export default App;