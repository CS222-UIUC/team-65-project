import React, { useState, useEffect } from "react";
import Map from "./components/Map";

function App() {
  const [routeData, setRouteData] = useState(null);
  const [error, setError] = useState(null);
  const startLocation = "Champaign, IL";
  const endLocation = "Chicago, IL";
  const stopType = "coffee shop";

  useEffect(() => {
    const fetchRouteData = async () => {
      try {
        const response = await fetch(
          http://localhost:5000/route?start=${encodeURIComponent(startLocation)}&end=${encodeURIComponent(endLocation)}&stop_type=${encodeURIComponent(stopType)}
        );
        const data = await response.json();
        if (data.error) {
          setError(data.error);
        } else {
          setRouteData(data);
        }
      } catch (err) {
        setError("Failed to fetch route data");
        console.error("Error fetching route data:", err);
      }
    };

    fetchRouteData();
  }, []);

  return (
    <div>
      <h1>Route Map</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {routeData ? <Map route={routeData} /> : <p>Loading route data...</p>}
    </div>
  );
}

export default App;