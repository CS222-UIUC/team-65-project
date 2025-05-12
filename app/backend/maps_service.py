import googlemaps
import os
from typing import List, Dict, Union
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class MapsService:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        self.geolocator = Nominatim(user_agent="trip_planner")

    async def _format_location(self, location: Union[str, Dict]) -> str:
        """Convert location to a format suitable for Google Maps API."""
        if isinstance(location, dict):
            if 'lat' in location and 'lng' in location:
                return f"{location['lat']},{location['lng']}"
            elif 'formatted_address' in location:
                return location['formatted_address']
        return str(location)

    async def get_route_data(self, itinerary: List[Dict]) -> Dict:
        waypoints = []
        for item in itinerary:
            if item.get("location"):
                formatted_location = await self._format_location(item["location"])
                if formatted_location:
                    waypoints.append(formatted_location)

        if len(waypoints) < 2:
            return {"error": "Not enough waypoints to create a route"}

        try:
            # Get directions between waypoints
            directions = self.gmaps.directions(
                waypoints[0],
                waypoints[-1],
                waypoints=waypoints[1:-1] if len(waypoints) > 2 else None,
                mode="driving",
                alternatives=False
            )

            if not directions:
                return {"error": "Could not generate route"}

            # Extract route information
            route = directions[0]
            legs = route["legs"]
            
            # Create a simplified route representation
            simplified_route = {
                "overview_polyline": route["overview_polyline"]["points"],
                "legs": [
                    {
                        "start_location": leg["start_location"],
                        "end_location": leg["end_location"],
                        "distance": leg["distance"],
                        "duration": leg["duration"],
                        "steps": [
                            {
                                "start_location": step["start_location"],
                                "end_location": step["end_location"],
                                "polyline": step["polyline"]["points"]
                            }
                            for step in leg["steps"]
                        ]
                    }
                    for leg in legs
                ]
            }

            return simplified_route

        except Exception as e:
            print(f"Error generating route: {str(e)}")  # Add logging
            return {"error": str(e)}

    async def geocode_address(self, address: str) -> Dict:
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "formatted_address": location.address
                }
            return {"error": "Could not geocode address"}
        except GeocoderTimedOut:
            return {"error": "Geocoding timed out"}
        except Exception as e:
            return {"error": str(e)} 