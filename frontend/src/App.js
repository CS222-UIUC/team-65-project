import React, { useState, useEffect } from "react";
import axios from "axios";
import Map from "./components/Map";
import "./App.css";
import { Provider } from "./components/ui/provider";
import { VStack } from "@chakra-ui/react";
function App({ Component, pageProps }) {
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

  return (
    <Provider>
      <VStack spacing={8}>
        <h1 className="title">Trip Planner</h1>

        <div className="input_start_end">
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

        <h3 className="stopsTitle">Stops:</h3>
        <div className="input_start_end">
          {stops.map((stop, index) => (
            <input
              className="stopTextBox"
              key={index}
              type="text"
              placeholder="Stop"
              value={stop}
              onChange={(e) => handleStopChange(index, e.target.value)}
            />
          ))}
          <button onClick={handleAddStop}>+ Add Stop</button>
          <button onClick={handleSubmit}>Get Route</button>
        </div>

        {/* Find Places Feature */}
        <h3 className="stopsTitle">Find Places:</h3>
        <div className="input_start_end">
          <input
            className="textBox"
            type="text"
            placeholder="Search for places (e.g., gas stations, coffee shops)"
            value={placeType}
            onChange={(e) => setPlaceType(e.target.value)}
          />
          <button onClick={handleFindPlaces}>Find Places</button>
        </div>

        {/* Display Found Places */}
        {foundPlaces.length > 0 && (
          <div>
            <h3>Suggested Places:</h3>
            <ul className="found-places-list">
              {foundPlaces.map((place, index) => (
                <li key={index}>
                  {place.name} ({place.lat}, {place.lon})
                  <button onClick={() => addPlaceToStops(place)}>
                    Add to Stops
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <Map route={route} />
      </VStack>
    </Provider>
  );
}

export default App;
