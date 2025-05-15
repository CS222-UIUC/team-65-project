from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import quote
import requests
import json
from urllib.parse import urljoin, urlencode
from dotenv import load_dotenv
import os
import openai
from openai import OpenAI
from it_llm import LLMService
from maps_service import MapsService
from llm import suggest_stops, parse_user_input

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verify environment variables are loaded
if not os.getenv("GOOGLE_MAPS_KEY"):
    raise ValueError("GOOGLE_MAPS_KEY environment variable is not set")

app = Flask(__name__)
CORS(app)

# Initialize services
llm_service = LLMService()
maps_service = MapsService()

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

@app.route("/generate_itinerary", methods=["POST"])
def generate_itinerary():
    data = request.json
    user_request = data.get("user_request", "")
    start_location = data.get("start_location")
    end_location = data.get("end_location")
    current_location = data.get("current_location")

    print(f"Received request: {user_request}")
    print(f"Start: {start_location}, End: {end_location}")
    print(f"Current location: {current_location}")

    if not user_request:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Generate itinerary using LLM
        print("Calling LLM service to generate itinerary...")
        itinerary = llm_service.generate_itinerary(
            user_request=user_request,
            start_location=start_location,
            end_location=end_location,
            current_location=current_location
        )
        print(f"Generated itinerary: {itinerary}")

        # Get route data for the itinerary
        print("Getting route data...")
        route_data = maps_service.get_route_data(itinerary)
        print(f"Route data: {route_data}")
        
        if "error" in route_data:
            return jsonify({
                "itinerary": itinerary,
                "route": None,
                "error": route_data["error"]
            })

        return jsonify({
            "itinerary": itinerary,
            "route": route_data
        })
    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Failed to generate itinerary: {str(e)}",
            "details": traceback.format_exc()
        }), 500

@app.route("/update_itinerary", methods=["POST"])
def update_itinerary():
    data = request.json
    user_request = data.get("user_request", "")
    current_itinerary = data.get("current_itinerary", [])

    if not user_request or not current_itinerary:
        return jsonify({"error": "Message and current itinerary are required"}), 400

    try:
        # Update itinerary using LLM
        updated_itinerary = llm_service.update_itinerary(
            user_request=user_request,
            current_itinerary=current_itinerary
        )

        # Get updated route data
        route_data = maps_service.get_route_data(updated_itinerary)
        
        if "error" in route_data:
            return jsonify({
                "itinerary": updated_itinerary,
                "route": None,
                "error": route_data["error"]
            })

        return jsonify({
            "itinerary": updated_itinerary,
            "route": route_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        response = parse_user_input({
            "start": start_location,
            "end": end_location,
            "stops": stops,
            "message": user_message,
        })
        print(response["suggestions"])
        if response["success"]:
            return jsonify({"response": response["suggestions"]})
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
    api_key = os.getenv("GOOGLE_MAPS_KEY")

   
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
@app.route("/clear_itinerary", methods=["POST"])
def clear_itinerary():
    try:
        llm_service.clear_itinerary()
        return jsonify({"message": "Itinerary cleared successfully"})
    except Exception as e:
        print(f"Error clearing itinerary: {str(e)}")
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)