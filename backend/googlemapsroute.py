import requests
import polyline
import logging
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY")



def get_route(start, end):
    directions_url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={start}&destination={end}&key={GOOGLE_MAPS_API_KEY}"
    )
    print(directions_url)
    response = requests.get(directions_url)
    data = response.json()
    if data.get('status') != 'OK':
        print("Could not find route.")
    route_polyline = data['routes'][0]['overview_polyline']['points']
    return polyline.decode(route_polyline)

def sample_route_points(route_points, num_samples):
    # might want to do distance between points
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


    return route_points[::sample_interval]

def get_stop_nearby(lat, lng, stop_type, radius=500):
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={lat},{lng}&radius={radius}&keyword={stop_type}&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(places_url)
    data = response.json()
    if data.get('status') != 'OK' or not data.get('results'):
        return None
    best_result = max(
        data['results'],
        key=lambda result: (result.get('rating', 0), result.get('user_ratings_total', 0))
    )
    return {
        'place_id': best_result.get('place_id'),
        'name': best_result.get('name'),
        'location': best_result.get('geometry', {}).get('location'),
        'rating': best_result.get('rating', 'N/A'),
        'user_ratings_total': best_result.get('user_ratings_total', 'N/A'),
        'vicinity': best_result.get('vicinity')
    }

def find_stops_along_route(start, end, stop_type, num_samples=10, radius=500):
    """
    Finds stops of a given type along the route from start to end.
    """
    route_points = get_route(start, end)
    sample_points = sample_route_points(route_points, num_samples)
    
    stops = {}
    for lat, lng in sample_points:
        stop = get_stop_nearby(lat, lng, stop_type, radius)
        if stop and stop['place_id'] not in stops:
            stops[stop['place_id']] = stop
    return {'route': route_points, 'stops': list(stops.values())}

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

