# Team 65 Project: Smart Trip Planner

## Overview

This project is a full-stack web application for planning road trips with intelligent stop recommendations. It leverages AI and mapping APIs to suggest optimal places to visit along your route or near your current location. It also allows user the generate itineraries based on user requests and visualize it on a map

- **Frontend:** React.js (see [`frontend/README.md`](frontend/README.md))
- **Backend:** Flask (see [`backend/README.md`](backend/README.md))

## Features

- Plan routes between two locations
- Get AI-powered recommendations for stops (food, gas, attractions, etc.)
- Visualize routes and stops on an interactive map
- Export routes to Google Maps


## Directory Structure

```
.
├── frontend/   # React app (UI, map, user interaction)
├── backend/    # Flask API (routing, AI, LLM)
├── tests/      # Test Scripts
└── README.md
```

## Getting Started

### Prerequisites

- Node.js, Python 3.8+, pip (for manual setup)

### Manual Setup

#### Backend

- Environment Variables
  `OPENAI_API_KEY`: For OpenAI GPT-based recommendations
  `GOOGLE_MAPS_KEY`: For Google Maps/Places API

Create a `.env` file in the backend directory:
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_KEY=your_google_maps_key

- Install & Run

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend

- Install & Run

```bash
cd frontend
npm install
npm start
```

### Environment Variables

- `REACT_APP_GOOGLE_MAPS_API_KEY`: Your Google Maps API key for map rendering

Create a `.env.local` file in frontend directory
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_key

### Scripts

- `npm start` – Start development server
- `npm run build` – Build for production
- `npm test` – Run tests

### Technical 

## Contributors

- Keshav Balaji - Backend 
- Kyle Zhao - Backend 
- Divij Garg - Frontend 
- Jash Nanda - Frontend 
