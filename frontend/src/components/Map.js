import React, { useMemo } from "react";
import {
  GoogleMap,
  LoadScript,
  Polyline,
  Marker,
  InfoWindow,
} from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "500px",
};

const defaultCenter = { lat: 40.1164, lng: -88.2434 };

const Map = ({ route }) => {
  // Convert OSRM [lon, lat] pairs into Google’s {lat, lng} objects
  const path = useMemo(() => {
    if (!route?.routes?.length) return [];
    return route.routes[0].geometry.coordinates.map(([lon, lat]) => ({
      lat,
      lng: lon,
    }));
  }, [route]);

  // Center on the first point if available, otherwise default
  const center = path.length > 0 ? path[0] : defaultCenter;

  return (
    <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={10}
      >
        {path.length > 0 && (
          <>
            <Polyline
              path={path}
              options={{
                strokeColor: "#0000FF",
                strokeOpacity: 1,
                strokeWeight: 3,
              }}
            />

            {/* Start marker */}
            <Marker position={path[0]}>
              <InfoWindow>
                <div>Start</div>
              </InfoWindow>
            </Marker>

            {/* End marker */}
            <Marker position={path[path.length - 1]}>
              <InfoWindow>
                <div>End</div>
              </InfoWindow>
            </Marker>
          </>
        )}
      </GoogleMap>
    </LoadScript>
  );
};

export default React.memo(Map);
