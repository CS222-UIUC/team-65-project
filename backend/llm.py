from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = """You are a trip assistant helping a traveler find places along their route or near their location. When suggesting places, consider:
- The type of place the user is looking for
- Making sure the location is not too far from the user's specified location, cannot be more than 30 minutes away
- The current location or route
- Relevance to the user's needs
You must return a JSON array of place suggestions. Each place must be a dictionary with exactly these keys:
- "name": string, the name of the place
- "category": string, type of place (e.g., restaurant, landmark, gas station)
- "estimated_time_minutes": integer, estimated travel time in minutes
- "description": string, brief description of the place
- "worth_visiting": string, explanation of why it's worth visiting
Your response must be valid JSON that can be parsed. Do not include any text outside the JSON array.
Example response format:
[
    {
        "name": "Sample Place",
        "category": "restaurant",
        "estimated_time_minutes": 15,
        "description": "A cozy Italian restaurant",
        "worth_visiting": "Known for authentic pasta and great atmosphere"
    }
]
"""

def parse_user_input(data):
    try:
        start = data.get("start", "unknown location")
        end = data.get("end", "unknown location")
        stops = data.get("stops","unknown location")
        message = data.get("message", "")
        system_prompt = """
        You are a trip assistant helping a traveler find places along their route or near their location. When suggesting places, consider:
        - The type of place the user is looking for
        - The maximum travel time if specified
        = type of request if looking for food, gas, etc. look for places that are close by user location for less time relevant requests you can look further
        = if looking for a route, look for places along the route
        - look at places that have good reviews and are popular
        - cost of the place the user want to visit
        - The current location or route
        - Relevance to the user's needs
        You must return a JSON array of place suggestions. Try to find 3 different places. Each place must be a dictionary with exactly these keys:
        - "name": string, the name of the place
        - "category": string, type of place (e.g., restaurant, landmark, gas station)
        - "address": string, address of the place
        - "estimated_time_minutes": integer, estimated travel time in minutes
        - "description": string, brief description of the place
        - "worth_visiting": string, explanation of why it's worth visiting
        Your response must be valid JSON that can be parsed. Do not include any text outside the JSON array.
        Example response format:
        [
            {
                "name": "Sample Place",
                "category": "restaurant",
                "estimated_time_minutes": 15,
                "address": "123 Sample St, Sample City, ST 12345",
                "description": "A cozy Italian restaurant",
                "worth_visiting": "Known for authentic pasta and great atmosphere"
            }
        ]
        """
        prompt = f"I am driving from {start} to {end}, with {stops} on the way. I want to know if {message}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=500
        )
        suggestions = parse_llm_response(response.choices[0].message.content)
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        print(f"Error in suggest_stops: {str(e)}")
        return {"success": False, "error": "Failed to generate suggestions", "details": str(e)}
    

def parse_llm_response(response_text):
    try:
        suggestions = json.loads(response_text)
        required_keys = {"name", "category", "estimated_time_minutes", "address", "description", "worth_visiting"}
        
        if not isinstance(suggestions, list):
            raise ValueError("Response is not a list")
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                raise ValueError("Suggestion is not a dictionary")
            if not all(key in suggestion for key in required_keys):
                raise ValueError(f"Suggestion missing required keys: {required_keys - set(suggestion.keys())}")
        return suggestions
    except json.JSONDecodeError:
        raise ValueError("Failed to parse response as JSON")
    except Exception as e:
        raise ValueError(f"Error parsing response: {str(e)}")

def suggest_stops(data):
    try:
        start = data.get("start", "unknown location")
        end = data.get("end", "unknown location")
        prompt = f"I'm planning a road trip from {start} to {end}. Suggest some interesting stops along the way."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        suggestions = parse_llm_response(response.choices[0].message.content)
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        print(f"Error in suggest_stops: {str(e)}")
        return {"success": False, "error": "Failed to generate suggestions", "details": str(e)}

def suggest_places_by_time(current_location, place_type, max_minutes, additional_preferences=None):
    try:
        # Construct the prompt
        prompt = f"""Find places matching these criteria: - Location: {current_location} - Type: {place_type} - Maximum travel time: {max_minutes} minutes"""
        if additional_preferences:
            prompt += f"- Additional preferences: {additional_preferences}\n"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        suggestions = parse_llm_response(response.choices[0].message.content)
        return {
            "success": True,
            "suggestions": suggestions,
            "search_criteria": {
                "location": current_location,
                "place_type": place_type,
                "max_minutes": max_minutes,
                "preferences": additional_preferences
            }
        }
    except Exception as e:
        print(f"Error in suggest_places_by_time: {str(e)}")
        return {
            "success": False,
            "error": "Failed to generate time-based suggestions",
            "details": str(e)
        }

if __name__ == "__main__":
    # just for testing
    test_route_data = {
        "start": "Chicago, IL",
        "end": "New York, NY"
    }
    route_response = suggest_stops(test_route_data)
    print("\nRoute-based suggestions:")
    print(json.dumps(route_response, indent=2))
    test_time_data = {
        "location": "Chicago, IL",
        "place_type": "coffee shop",
        "max_minutes": 15,
        "preferences": "Quiet atmosphere, good for working"
    }
    time_response = suggest_places_by_time(
        test_time_data["location"],
        test_time_data["place_type"],
        test_time_data["max_minutes"],
        test_time_data["preferences"]
    )
    print("\nTime-based suggestions:")
    print(json.dumps(time_response, indent=2))