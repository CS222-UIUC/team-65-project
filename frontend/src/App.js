import React, { useState } from "react";
import axios from "axios";
import Map from "./components/Map";

import './App.css';

function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [stops, setStops] = useState([]);
  const [route, setRoute] = useState(null);

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

  return (
    <div>
      <h1 className = "title">Trip Planner</h1>
      
      <div className = 'input_start_end'>
      <input className = 'textBox' type="text" placeholder="Start Location" value={start} onChange={(e) => setStart(e.target.value)} />
      <input className = 'textBox' type="text" placeholder="End Location" value={end} onChange={(e) => setEnd(e.target.value)} />
      </div>
  
      <h3 className = 'stopsTitle'>Stops:</h3>

      <div className = 'input_start_end'>

      {stops.map((stop, index) => (
        <input
          className = 'stopTextBox'
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

      <Map route={route} />
    </div>
  );
}

export default App;