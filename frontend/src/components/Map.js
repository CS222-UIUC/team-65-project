import React from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const Map = ({ route }) => {
    const defaultPosition = [40.1164, -88.2434];

    const getPolylineCoordinates = () => {
        if (!route || !route.routes || route.routes.length === 0) return [];
        const coordinates = route.routes[0].geometry.coordinates;
        return coordinates.map(([lon, lat]) => [lat, lon]);
    };

    const polylineCoordinates = getPolylineCoordinates();

    return (
        <MapContainer
            center={polylineCoordinates.length > 0 ? polylineCoordinates[0] : defaultPosition}
            zoom={10}
            style={{ height: "500px", width: "100%" }}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
            />
            {polylineCoordinates.length > 0 && (
                <>
                    <Polyline positions={polylineCoordinates} color="blue" />
                    <Marker position={polylineCoordinates[0]}>
                        <Popup>Start</Popup>
                    </Marker>
                    <Marker position={polylineCoordinates.slice(-1)[0]}>
                        <Popup>End</Popup>
                    </Marker>
                </>
            )}
        </MapContainer>
    );
};

export default Map;
