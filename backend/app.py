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

    start_coords = get_coordinates(start_location)
    end_coords = get_coordinates(end_location)
    if not start_coords or not end_coords:
        return jsonify({"error": "Could not get coordinates for locations"}), 400

    stop_coords = []
    for stop in stop_locations:
        coords = get_coordinates(stop)
        if coords:
            stop_coords.append(coords)
    waypoints = [f"{start_coords[1]},{start_coords[0]}"] + \
                [f"{lon},{lat}" for lat, lon in stop_coords] + \
                [f"{end_coords[1]},{end_coords[0]}"]

    try:
        osrm_url = f"{OSRM_SERVER}/route/v1/driving/" + ";".join(waypoints) + "?overview=full&geometries=geojson"
        osrm_response = requests.get(osrm_url)
        
        # Check if the response is successful
        if osrm_response.status_code != 200:
            return jsonify({
                "error": f"OSRM server returned status code {osrm_response.status_code}",
                "details": osrm_response.text
            }), 500

        # Try to parse the JSON response
        try:
            route_data = osrm_response.json()
            return jsonify(route_data)
        except json.JSONDecodeError as e:
            return jsonify({
                "error": "Invalid response from OSRM server",
                "details": str(e),
                "response_text": osrm_response.text[:200]  # Include first 200 chars of response
            }), 500

    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to connect to OSRM server",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)