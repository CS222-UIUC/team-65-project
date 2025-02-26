from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import quote
import requests

app = Flask(__name__)
CORS(app)

OSRM_SERVER = "http://router.project-osrm.org"

def get_coordinates(location):
    """
    Convert a location (address or place name) to coordinates using Nominatim API.
    """
    headers = {"User-Agent": "TripPlannerApp"}
    encoded_location = quote(location)
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json"
    response = requests.get(nominatim_url, headers=headers)
    if response.status_code == 200 and response.json():
        location_data = response.json()[0]
        return float(location_data["lat"]), float(location_data["lon"])
    
    print(f"Error fetching coordinates for {location}: {response.text}")
    return None

@app.route("/get_route", methods=["POST"])
def get_route():
    data = request.json
    start_location = data.get("start")
    end_location = data.get("end")
    stop_locations = data.get("stops", [])

    if not start_location or not end_location:
        return jsonify({"error": "Start and End locations are required"}), 400

    start_coords = get_coordinates(start_location)
    end_coords = get_coordinates(end_location)
    if not start_coords or not end_coords:
        return jsonify({"error": "Could not get coordinates for locations"}), 400

    stop_coords = [get_coordinates(stop) for stop in stop_locations if get_coordinates(stop)]
    waypoints = [f"{start_coords[1]},{start_coords[0]}"] + \
                [f"{lon},{lat}" for lat, lon in stop_coords] + \
                [f"{end_coords[1]},{end_coords[0]}"]

    osrm_url = f"{OSRM_SERVER}/route/v1/driving/" + ";".join(waypoints) + "?overview=full&geometries=geojson"
    osrm_response = requests.get(osrm_url)
    route_data = osrm_response.json()
    return jsonify(route_data)

if __name__ == "__main__":
    app.run(debug=True)
