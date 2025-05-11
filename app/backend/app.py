from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from llm_service import LLMService
from maps_service import MapsService

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
maps_service = MapsService()

class TripRequest(BaseModel):
    user_request: str
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    current_location: Optional[dict] = None

class ItineraryItem(BaseModel):
    id: str
    type: str
    description: str
    location: Optional[dict]
    time: Optional[str]
    duration: Optional[str]

@app.post("/api/generate-itinerary")
async def generate_itinerary(request: TripRequest):
    try:
        # Generate itinerary using LLM
        itinerary = await llm_service.generate_itinerary(
            request.user_request,
            request.start_location,
            request.end_location,
            request.current_location
        )
        
        # Get map data for the itinerary
        map_data = await maps_service.get_route_data(itinerary)
        
        return {
            "itinerary": itinerary,
            "map_data": map_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-itinerary")
async def update_itinerary(request: TripRequest):
    try:
        # Update itinerary based on user modifications
        updated_itinerary = await llm_service.update_itinerary(
            request.user_request,
            request.current_location
        )
        
        # Update map data
        map_data = await maps_service.get_route_data(updated_itinerary)
        
        return {
            "itinerary": updated_itinerary,
            "map_data": map_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 