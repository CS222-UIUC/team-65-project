from ollama import Client
import json

client = Client(host='http://localhost:11434')

system_prompt = """You are a trip assistant helping a traveler find places along their route or near their location. When suggesting places, consider:
- The type of place the user is looking for
- The maximum travel time specified
- The current location or route
- Relevance to the user's needs

CRITICAL INSTRUCTIONS:
1. You must respond with ONLY a JSON array. No other text, no explanations, no markdown.
2. The JSON array must contain place suggestions.
3. Each place must be a dictionary with EXACTLY these keys:
   - "name": string
   - "category": string
   - "estimated_time_minutes": integer
   - "description": string
   - "worth_visiting": string
4. Do not include any text before or after the JSON array.

Example response (this is the ONLY thing you should return):
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

def parse_llm_response(response_text):
    try:
        # Clean the response text to ensure it's valid JSON
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        suggestions = json.loads(cleaned_text)
        required_keys = {"name", "category", "estimated_time_minutes", "description", "worth_visiting"}
        
        if not isinstance(suggestions, list):
            raise ValueError("Response is not a list")
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                raise ValueError("Suggestion is not a dictionary")
            if not all(key in suggestion for key in required_keys):
                raise ValueError(f"Suggestion missing required keys: {required_keys - set(suggestion.keys())}")
        return suggestions
    except json.JSONDecodeError as e:
        print(f"Raw response: {response_text}")
        raise ValueError(f"Failed to parse response as JSON: {str(e)}")
    except Exception as e:
        print(f"Raw response: {response_text}")
        raise ValueError(f"Error parsing response: {str(e)}")

def suggest_stops(data):
    try:
        start = data.get("start", "unknown location")
        end = data.get("end", "unknown location")
        prompt = f"""I'm planning a trip from {start} to {end}. 
Suggest 3-5 interesting stops along the way. 
Return ONLY a JSON array of places with the exact format specified in the system prompt.
Do not include any other text or explanations."""

        response = client.chat(
            model='llama3.2:1b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        suggestions = parse_llm_response(response['message']['content'])
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        print(f"Error in suggest_stops: {str(e)}")
        return {"success": False, "error": "Failed to generate suggestions", "details": str(e)}

def suggest_places_by_time(current_location, place_type, max_minutes, additional_preferences=None):
    try:
        # Construct the prompt
        prompt = f"""Find 3-5 places matching these criteria:
- Location: {current_location}
- Type: {place_type}
- Maximum travel time: {max_minutes} minutes"""
        if additional_preferences:
            prompt += f"\n- Additional preferences: {additional_preferences}"
        prompt += "\nReturn ONLY a JSON array of places with the exact format specified in the system prompt.\nDo not include any other text or explanations."
            
        response = client.chat(
            model='llama3.2:1b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        suggestions = parse_llm_response(response['message']['content'])
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
    # Test the functions
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

