# Trip Planner Application

A modern trip planning application that uses AI to generate and modify travel itineraries, with Google Maps integration for route visualization.

## Project Structure

```
app/
├── backend/           # FastAPI backend
│   ├── app.py        # Main FastAPI application
│   ├── llm_service.py # LLM integration service
│   ├── maps_service.py # Google Maps integration service
│   └── requirements.txt
└── frontend/         # Next.js frontend
    ├── src/
    │   ├── pages/   # Next.js pages
    │   └── styles/  # Global styles
    ├── package.json
    └── tsconfig.json
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
   ```bash
   cd app/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

4. Run the backend server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd app/frontend
   npm install
   ```

2. Create a `.env.local` file in the frontend directory with:
   ```
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Features

- AI-powered trip itinerary generation
- Interactive Google Maps integration
- Real-time itinerary modifications
- User location detection
- Modern UI with Tailwind CSS
- Responsive design

## API Endpoints

- `POST /api/generate-itinerary`: Generate a new itinerary
- `POST /api/update-itinerary`: Update an existing itinerary

## Technologies Used

- Frontend:
  - Next.js
  - TypeScript
  - Tailwind CSS
  - Google Maps API
  - React Icons

- Backend:
  - FastAPI
  - LangChain
  - OpenAI
  - Google Maps API
  - Python 3.8+ 