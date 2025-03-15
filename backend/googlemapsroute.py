import requests
import polyline
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY")

def find_stops_along_route(start, end, stop_type, num_samples=10):
    """
    Finds stops of a given type along the route from start to end.

    Parameters:
        start (str): start location.
        end (str): destination location.
        stop_type (str): Type of stop to look for.
        num_samples (int): Number of stops to sample along the route.

    Returns:
        dict: A dictionary containing the route (list of (lat, lng) tuples)
              and stops (list of dictionaries with details about each stop).
    """
    # Get route
    directions_url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={start}&destination={end}&key={GOOGLE_MAPS_API_KEY}"
    )
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    if directions_data.get('status') != 'OK':
        raise ValueError("Could not find route. Check your input or API key.")

    # Decode polyline into coordinates
    route_polyline = directions_data['routes'][0]['overview_polyline']['points']
    route_points = polyline.decode(route_polyline)

    # Sample points along the route - make distance based eventually
    sample_interval = max(1, int(len(route_points) / num_samples))
    sample_points = route_points[::sample_interval]

    stops = {}
    # Search for nearby stops for each sampled point using the Places API.
    for lat, lng in sample_points:
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
            f"location={lat},{lng}&radius=500&keyword={stop_type}&key={GOOGLE_MAPS_API_KEY}"
        )
        places_response = requests.get(places_url)
        places_data = places_response.json()

        if places_data.get('status') == 'OK' and places_data.get('results'):
            # Sort the results by rating (use 0 if rating is missing) 
            sorted_results = sorted(
                places_data['results'], 
                key=lambda x: x.get('rating', 0), 
                reverse=True
            )
            best_result = sorted_results[0]
            place_id = best_result.get('place_id')
            if place_id not in stops:
                stops[place_id] = {
                    'name': best_result.get('name'),
                    'location': best_result.get('geometry', {}).get('location'),
                    'rating': best_result.get('rating', 'N/A'),
                    'vicinity': best_result.get('vicinity')
                }


    return {
        'route': route_points,
        'stops': list(stops.values())
    }

# Example usage for testing the function.
if __name__ == '__main__':
    start_location = "Champaign, IL"
    end_location = "Chicago, IL"
    stop_type = "coffee shop"

    try:
        result = find_stops_along_route(start_location, end_location, stop_type)
        print("Route points:")
        print(result['route'])
        print("\nStops along the route:")
        for stop in result['stops']:
            print(stop)
    except Exception as e:
        print("Error:", e)