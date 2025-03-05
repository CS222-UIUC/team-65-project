from flask import Flask, jsonify, request
import requests
import polyline
import os
# from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
app = Flask(__name__)
# CORS(app)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY")

def find_stops_along_route(start, end, stop_type='coffee shop', num_samples=10):
    """
    Finds stops of a given type along the route from start to end.
    Returns a tuple: (route_points, stops)
    - route_points: list of (lat, lng) tuples.
    - stops: list of stop details.
    """
    # 1. Get route from the Directions API.
    directions_url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={start}&destination={end}&key={GOOGLE_MAPS_API_KEY}"
    )
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    if directions_data.get('status') != 'OK':
        raise ValueError("Could not find route. Check your input or API key.")

    # 2. Decode the polyline into coordinates.
    route_polyline = directions_data['routes'][0]['overview_polyline']['points']
    route_points = polyline.decode(route_polyline)

    # 3. Sample points along the route.
    sample_interval = max(1, int(len(route_points) / num_samples))
    sample_points = route_points[::sample_interval]

    stops = {}
    # 4. For each sample point, search for one nearby stop using the Places API.
    for lat, lng in sample_points:
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
            f"location={lat},{lng}&radius=500&keyword={stop_type}&key={GOOGLE_MAPS_API_KEY}"
        )
        places_response = requests.get(places_url)
        places_data = places_response.json()
        if places_data.get('status') == 'OK' and places_data.get('results'):
            result = places_data['results'][0]  # Only take the first result.
            place_id = result.get('place_id')
            if place_id not in stops:
                stops[place_id] = {
                    'name': result.get('name'),
                    'location': result.get('geometry', {}).get('location'),
                    'rating': result.get('rating', 'N/A'),
                    'vicinity': result.get('vicinity')
                }

    return route_points, list(stops.values())

@app.route("/route", methods=["GET"])
def route():
    # Get query parameters.
    start = request.args.get("start")
    end = request.args.get("end")
    stop_type = request.args.get("stop_type", "coffee shop")
    
    if not start or not end:
        return jsonify({"error": "Please provide start and end locations"}), 400

    try:
        route_points, stops = find_stops_along_route(start, end, stop_type)
        # Convert each (lat, lng) tuple into [lng, lat] to match the front end's expected format.
        coordinates = [[lng, lat] for lat, lng in route_points]
        response = {
            "routes": [
                {
                    "geometry": {
                        "coordinates": coordinates
                    }
                }
            ],
            "stops": stops
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/")
def index():
    return "Welcome to the Route Finder API. Use the /route endpoint to get started."
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0')
