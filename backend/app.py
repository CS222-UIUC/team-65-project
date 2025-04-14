from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import quote
import requests
import json

app = Flask(__name__)
CORS(app)

OSRM_SERVER = "http://router.project-osrm.org"

def get_coordinates(location):
    headers = {"User-Agent": "TripPlannerApp"}
    encoded_location = quote(location)
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json"
    response = requests.get(nominatim_url, headers=headers)
    if response.status_code == 200 and response.json():
        location_data = response.json()[0]
        return float(location_data["lat"]), float(location_data["lon"])
    
    return None

@app.route("/find_places", methods=["POST"])
def find_places():
    data = request.json
    place_type = data.get("place_type")
    user_location = data.get("location")
    route = data.get("route")

    if not place_type:
        return jsonify({"error": "Place type is required"}), 400

    headers = {"User-Agent": "TripPlannerApp"}

    if route:
        # Find places along the route by taking midpoints
        waypoints = route.get("routes", [])[0].get("geometry", {}).get("coordinates", [])
        midpoints = waypoints[:: max(1, len(waypoints) // 5)]  # Get every 1/5th point along route
        places = []
        for lon, lat in midpoints:
            encoded_query = quote(f"{place_type} near {lat},{lon}")
            nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json"
            response = requests.get(nominatim_url, headers=headers)
            if response.status_code == 200 and response.json():
                places.extend([{"name": p["display_name"], "lat": float(p["lat"]), "lon": float(p["lon"])}
                               for p in response.json()[:3]])  # Limit to 3 per location
        return jsonify(places)

    elif user_location:
        lat, lon = user_location["lat"], user_location["lon"]
        encoded_query = quote(f"{place_type} near {lat},{lon}")
        nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json"
        response = requests.get(nominatim_url, headers=headers)

        if response.status_code == 200 and response.json():
            places = [{"name": p["display_name"], "lat": float(p["lat"]), "lon": float(p["lon"])}
                      for p in response.json()]
            return jsonify(places)

    return jsonify({"error": "No results found"}), 404

from llm import suggest_stops  

@app.route("/llm_chat", methods=["POST"])
def llm_chat():
    # data = request.json
    # user_message = data.get("message", "")
    user_message = {
        "start": "Chicago, IL",
        "end": "New York, NY"
    }

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Use the LLM function to generate a response
        #response = suggest_stops({"start": user_message, "end": ""})
        response = suggest_stops(user_message)
        if response["success"]:
            return jsonify({"response": response["suggestions"][0]["name"]}) # Return the first suggestion
        else:
            return jsonify({"response": "Sorry, I couldn't process your request."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
