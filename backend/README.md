# Backend – Smart Trip Planner

This is the Flask backend for the Smart Trip Planner project. It provides RESTful APIs for route calculation, AI-powered stop recommendations, and integration with mapping and language model services.

## Features
- Calculate driving routes between locations
- Suggest stops (food, gas, attractions, etc.) along a route or near a location
- Use OpenAI or Llama models for intelligent recommendations
- Integrate with Google Maps and Places APIs

## Main Files
- `app.py` – Main Flask app, API endpoints
- `llm.py` – OpenAI-based recommendation logic
- `llama.py` – Llama-based recommendation logic (optional)
- `googlemapsroute.py` – Google Maps routing and stop search
- `stopLLM.py` – Uses LLM to pick the best stop from a list
- `requirements.txt` – Python dependencies

## Setup & Development
### Prerequisites
- Python 3.8+
- pip
- (For Google Maps features) Google Maps API key (`GOOGLE_MAPS_KEY` in `.env`)
- (For OpenAI features) OpenAI API key (`OPENAI_API_KEY` in `.env`)

### Install & Run
```bash
cd backend
pip install -r requirements.txt
python app.py
```
The API will be available at [http://localhost:5000](http://localhost:5000).

### Environment Variables
- `OPENAI_API_KEY`: For OpenAI GPT-based recommendations
- `GOOGLE_MAPS_KEY`: For Google Maps/Places API

Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_KEY=your_google_maps_key
```

## API Endpoints
- `POST /get_route` – Get route between start, end, and optional stops
- `POST /find_places` – Find places of a given type along a route or near a location
- `POST /llm_chat` – Get AI-powered recommendations for stops (chat interface)
- `POST /get_route2` – Advanced route and stop search (uses Google Maps)

### Example Request: `/get_route`
```json
{
  "start": "Chicago, IL",
  "end": "New York, NY",
  "stops": ["Cleveland, OH"]
}
```

### Example Request: `/find_places`
```json
{
  "place_type": "coffee shop",
  "location": {"lat": 41.8781, "lon": -87.6298}
}
```

## Customization
- You can swap between OpenAI (API) and Llama (Local) models in the code for recommendations.
- Add new endpoints or logic as needed for your use case.
