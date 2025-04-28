import os
import openai
from googlemapsroute import find_stops_along_route

openai.api_key = os.getenv("OPENAI_API_KEY")

def choose_best_stop(stops):
    """
    Uses OpenAI's language model to select the best stop for a coffee break out of a list of stops.
    """
    prompt = "I have found the following stops along my route:\n"
    for i, stop in enumerate(stops, start=1):
        prompt += (
            f"{i}. {stop.get('name', 'Unknown')} located at {stop.get('vicinity', 'N/A')}, "
            f"with a rating of {stop.get('rating', 'N/A')} based on {stop.get('user_ratings_total', 'N/A')} reviews.\n"
        )
    prompt += (
        "\nBased on the above details, please choose the best stop. "
        "Please only say the name of the stop you deem to be the best, based on convenience nad ratings."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in travel and local recommendations. Please consider the ratings and reviews of the stops, as well as ease of access and reliability. ."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

def main():
    start_location = "Champaign, IL"
    end_location = "Chicago, IL"
    stop_type = "coffee shop"
    
    # Find stops along the route with a target of 5 samples
    result = find_stops_along_route(start_location, end_location, stop_type, num_samples=5)
    stops = result.get('stops', [])
    
    if not stops:
        print("No stops found along the route.")
        return
    
    print("Found the following stops:")
    for stop in stops:
        print(f"- {stop.get('name', 'Unknown')} at {stop.get('vicinity', 'N/A')}")
    
    # Get the LLM's recommendation for the best stop
    recommendation = choose_best_stop(stops)
    print("\chatgpt's rec:")
    print(recommendation)

if __name__ == '__main__':
    main()
