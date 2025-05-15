from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import quote
import requests
import json
from googlemapsroute import find_stops_along_route
from urllib.parse import urljoin, urlencode


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

    # Construct the Directions API request
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        return jsonify({"error": "Google Maps API key not found in environment variables"}), 500

    params = {
        "origin": start_location,
        "destination": end_location,
        "key": api_key,
    }

    if stop_locations:
        # Format stops as a pipe-separated list
        params["waypoints"] = "|".join(stop_locations)

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch route from Google Maps API"}), 500

    return jsonify(response.json())


def build_osrm_url(waypoints):
    base_path = f"/route/v1/driving/{';'.join(waypoints)}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    query_string = urlencode(params)
    return urljoin(OSRM_SERVER, base_path) + "?" + query_string


if __name__ == "__main__":
    app.run(debug=True)