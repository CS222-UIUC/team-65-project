import os
import googlemaps
from typing import Dict, List, Optional, Union
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class MapsService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_MAPS_KEY")
        if not api_key:
            raise ValueError("Google Maps API key not found in environment variables")
        self.gmaps = googlemaps.Client(key=api_key)
        self.geolocator = Nominatim(user_agent="trip_planner")

    def get_route(
        self,
        start_location: str,
        end_location: str,
        waypoints: Optional[List[str]] = None
    ) -> Dict:
        try:
            # Get directions
            directions_result = self.gmaps.directions(
                start_location,
                end_location,
                waypoints=waypoints,
                mode="driving"
            )

            if not directions_result:
                return {
                    "error": "No route found",
                    "route": None
                }

            # Extract route information
            route = directions_result[0]
            legs = route["legs"]
            
            # Calculate total distance and duration
            total_distance = sum(leg["distance"]["value"] for leg in legs)
            total_duration = sum(leg["duration"]["value"] for leg in legs)

            # Format the response
            return {
                "error": None,
                "route": {
                    "total_distance": total_distance,
                    "total_duration": total_duration,
                    "legs": [
                        {
                            "start_location": leg["start_location"],
                            "end_location": leg["end_location"],
                            "distance": leg["distance"],
                            "duration": leg["duration"],
                            "steps": [
                                {
                                    "instruction": step["html_instructions"],
                                    "distance": step["distance"],
                                    "duration": step["duration"],
                                    "start_location": step["start_location"],
                                    "end_location": step["end_location"]
                                }
                                for step in leg["steps"]
                            ]
                        }
                        for leg in legs
                    ]
                }
            }

        except Exception as e:
            return {
                "error": str(e),
                "route": None
            }

    def _format_location(self, location: Union[str, Dict]) -> str:
        """Convert location to a format suitable for Google Maps API."""
        if isinstance(location, dict):
            if 'lat' in location and 'lng' in location:
                return f"{location['lat']},{location['lng']}"
            elif 'formatted_address' in location:
                return location['formatted_address']
        return str(location)

    def get_route_data(self, itinerary: List[Dict]) -> Dict:
        waypoints = []
        markers = []
        
        # First, geocode all locations to ensure we have coordinates
        for item in itinerary:
            location = item.get("location") or item.get("address")
            if location:
                try:
                    # Try to parse coordinates if they're in lat,lng format
                    if isinstance(location, str) and "," in location:
                        lat, lng = map(float, location.split(","))
                    else:
                        # If not in lat,lng format, geocode the address
                        geocode_result = self.gmaps.geocode(location)
                        if not geocode_result:
                            continue
                        lat = geocode_result[0]["geometry"]["location"]["lat"]
                        lng = geocode_result[0]["geometry"]["location"]["lng"]
                    
                    waypoints.append(f"{lat},{lng}")
                    markers.append({
                        "position": {
                            "lat": lat,
                            "lng": lng
                        },
                        "title": item.get("title", "Stop"),
                        "description": item.get("description", ""),
                        "type": item.get("type", "stop")
                    })
                except Exception as e:
                    print(f"Error processing location {location}: {str(e)}")
                    continue

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
                "markers": markers,
                "bounds": route["bounds"],
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
            print(f"Error generating route: {str(e)}")
            return {"error": str(e)}

    def geocode_address(self, address: str) -> Dict:
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