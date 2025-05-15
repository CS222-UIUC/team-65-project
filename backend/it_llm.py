# from langchain_community.chat_models import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationChain
# from langchain.prompts import PromptTemplate

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import os
import json
from typing import List, Dict, Optional


class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.output_parser = StrOutputParser()

        self.itinerary_template = """
        You are a travel planning assistant. Create a detailed itinerary based on the following request:
        User Request: {user_request}
        
        Start Location: {start_location}
        End Location: {end_location}
        Current Location: {current_location}
        
        Generate a JSON array of itinerary items. Each item should have:
        - id: unique identifier
        - type: activity type (e.g., "transportation", "attraction", "food", "accommodation")
        - description: detailed description
        - address: MUST be a string containing the full address (e.g., "123 Main St, City, State, Country")
        - location: MUST be a string containing the latitude and longitude (e.g., "40.7128,-74.0060")
        - time: suggested time
        - duration: estimated duration
        
        Important: The location field MUST be a complete address string that can be geocoded.
        Do not use coordinates or partial addresses.
        
        Format the response as a valid JSON array.
        """

        self.update_template = """
        Based on the following request, modify the existing itinerary:
        User Request: {user_request}
        Current Itinerary: {current_itinerary}
        
        Return the updated itinerary as a JSON array with the same structure.
        """

    def generate_itinerary(
        self,
        user_request: str,
        start_location: Optional[str] = None,
        end_location: Optional[str] = None,
        current_location: Optional[Dict] = None
    ) -> List[Dict]:
        prompt = ChatPromptTemplate.from_template(self.itinerary_template)
        messages = prompt.format_messages(
            user_request=user_request,
            start_location=start_location or "Not specified",
            end_location=end_location or "Not specified",
            current_location=json.dumps(current_location) if current_location else "Not specified"
        )
        response = self.llm.invoke(messages)
        # Extract the content from AIMessage
        text = response.content if hasattr(response, 'content') else str(response)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {text}")
            # Return a default itinerary if parsing fails
            return [
                {
                    "id": "1",
                    "type": "attraction",
                    "title": "Sample Activity",
                    "description": "A sample activity for your trip",
                    "location": "Times Square, New York, NY",
                    "time": "10:00 AM",
                    "duration": "2 hours"
                }
            ]

    def update_itinerary(
        self,
        user_request: str,
        current_itinerary: List[Dict]
    ) -> List[Dict]:
        prompt = ChatPromptTemplate.from_template(self.update_template)
        messages = prompt.format_messages(
            user_request=user_request,
            current_itinerary=json.dumps(current_itinerary)
        )
        response = self.llm.invoke(messages)
        # Extract the content from AIMessage
        text = response.content if hasattr(response, 'content') else str(response)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {text}")
            return current_itinerary
        
    def clear_itinerary(self):
        """Clear the current itinerary and memory"""
        #self._update_vector_store(None)
        #self.memory.clear()
        return []


# from langchain_openai import ChatOpenAI
# import os
# from typing import List, Dict, Optional
# import json

# class LLMService:
#     def __init__(self):
#         # Initialize with dummy data for testing
#         self.dummy_itinerary = [
#             {
#                 "id": "1",
#                 "type": "transportation",
#                 "title": "Start Journey",
#                 "description": "Begin your trip from Times Square",
#                 "location": "Times Square, New York, NY",
#                 "time": "9:00 AM",
#                 "duration": "30 minutes"
#             },
#             {
#                 "id": "2",
#                 "type": "attraction",
#                 "title": "Visit Central Park",
#                 "description": "Explore the beautiful park and its attractions",
#                 "location": "Central Park, New York, NY",
#                 "time": "10:00 AM",
#                 "duration": "2 hours"
#             },
#             {
#                 "id": "3",
#                 "type": "food",
#                 "title": "Lunch at Empire State Building",
#                 "description": "Enjoy lunch with a view at the Empire State Building",
#                 "location": "Empire State Building, New York, NY",
#                 "time": "12:30 PM",
#                 "duration": "1 hour"
#             },
#             {
#                 "id": "4",
#                 "type": "attraction",
#                 "title": "Visit Museum of Modern Art",
#                 "description": "Explore the world-renowned art museum",
#                 "location": "Museum of Modern Art, New York, NY",
#                 "time": "2:00 PM",
#                 "duration": "1.5 hours"
#             },
#             {
#                 "id": "5",
#                 "type": "transportation",
#                 "title": "Return Journey",
#                 "description": "Head back to Times Square",
#                 "location": "Times Square, New York, NY",
#                 "time": "4:00 PM",
#                 "duration": "30 minutes"
#             }
#         ]

#     def generate_itinerary(
#         self,
#         user_request: str,
#         start_location: Optional[str] = None,
#         end_location: Optional[str] = None,
#         current_location: Optional[Dict] = None
#     ) -> List[Dict]:
#         # Return dummy itinerary for testing
#         print(f"Generating itinerary for request: {user_request}")
#         return self.dummy_itinerary

#     def update_itinerary(
#         self,
#         user_request: str,
#         current_itinerary: List[Dict]
#     ) -> List[Dict]:
#         # For testing, just return the current itinerary
#         print(f"Updating itinerary for request: {user_request}")
#         return current_itinerary