from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
from typing import List, Dict, Optional
import json

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
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
        - location: coordinates or address
        - time: suggested time
        - duration: estimated duration
        
        Format the response as a valid JSON array.
        """
        
        self.update_template = """
        Based on the following request, modify the existing itinerary:
        User Request: {user_request}
        Current Itinerary: {current_itinerary}
        
        Return the updated itinerary as a JSON array with the same structure.
        """

    async def generate_itinerary(
        self,
        user_request: str,
        start_location: Optional[str] = None,
        end_location: Optional[str] = None,
        current_location: Optional[Dict] = None
    ) -> List[Dict]:
        # 1) Format the prompt exactly as before
        formatted_prompt = PromptTemplate(
            template=self.itinerary_template,
            input_variables=["user_request", "start_location", "end_location", "current_location"]
        ).format(
            user_request=user_request,
            start_location=start_location or "Not specified",
            end_location=end_location or "Not specified",
            current_location=json.dumps(current_location) if current_location else "Not specified"
        )

        # 2) Call apredict instead of agenerate
        response_text = await self.llm.apredict(formatted_prompt)
        print(response_text)

        # 3) Parse the JSON response
        itinerary = json.loads(response_text)

        # 4) Save to memory
        self.memory.save_context(
            {"input": user_request},
            {"output": json.dumps(itinerary)}
        )

        return itinerary

    async def update_itinerary(
        self,
        user_request: str,
        current_itinerary: List[Dict]
    ) -> List[Dict]:
        prompt = PromptTemplate(
            template=self.update_template,
            input_variables=["user_request", "current_itinerary"]
        )
        
        formatted_prompt = prompt.format(
            user_request=user_request,
            current_itinerary=json.dumps(current_itinerary)
        )
        
        response = await self.llm.agenerate([formatted_prompt])
        updated_itinerary = json.loads(response.generations[0][0].text)
        
        # Update memory with the new request and response
        self.memory.save_context(
            {"input": user_request},
            {"output": json.dumps(updated_itinerary)}
        )
        
        return updated_itinerary 