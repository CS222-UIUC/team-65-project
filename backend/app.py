from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import quote
import requests
import json
from googlemapsroute import find_stops_along_route


from dotenv import load_dotenv
import os
import openai
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Corrected syntax
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))




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

from llm import suggest_stops, parse_user_input

@app.route("/llm_chat", methods=["POST"])
def llm_chat():
    data = request.json
    user_message = data.get("message", "")
    start_location = data.get("start")
    end_location = data.get("end")
    stops = data.get("stops")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    try:
        # Use start_location, end_location, and user_location in your LLM logic
        response = parse_user_input({
            "start": start_location,
            "end": end_location,
            "stops":stops,
            "message": user_message,
        })
        print(response["suggestions"])
        if response["success"]:
            return jsonify({"response": response["suggestions"]}) # Return the first suggestion
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