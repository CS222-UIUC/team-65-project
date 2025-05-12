# Frontend – Smart Trip Planner

This is the React.js frontend for the Smart Trip Planner project. It provides an interactive UI for planning road trips, visualizing routes, and getting AI-powered recommendations for stops along your journey.

## Features
- Search for routes between two locations
- Add custom stops or get AI-suggested stops (food, gas, attractions, etc.)
- Visualize your route and stops on a Google Map
- Export your trip to Google Maps for navigation
- Chat with an AI assistant for personalized recommendations

## Project Structure
```
frontend/
├── src/
│   ├── App.js         # Main app logic and UI
│   ├── index.js       # Entry point
│   └── components/
│       └── Map.js     # Map rendering and route visualization
├── public/            # Static assets
├── package.json       # Dependencies and scripts
└── dockerfile         # For containerized builds
```

## Setup & Development
### Prerequisites
- Node.js (v16+ recommended)
- npm or yarn
- (For map features) Google Maps API key (set as `REACT_APP_GOOGLE_MAPS_API_KEY` in a `.env` file)

### Install & Run
```bash
cd frontend
npm install
npm start
```
The app will be available at [http://localhost:3000](http://localhost:3000).

### Environment Variables
- `REACT_APP_GOOGLE_MAPS_API_KEY`: Your Google Maps API key for map rendering

### Scripts
- `npm start` – Start development server
- `npm run build` – Build for production
- `npm test` – Run tests

## How it Works
- **App.js**: Handles user input, communicates with the Flask backend for route and stop suggestions, and manages state.
- **Map.js**: Renders the route and stops using Google Maps.
- **API Calls**: Interacts with backend endpoints (`/get_route`, `/find_places`, `/llm_chat`) for trip planning and recommendations.

## Backend
See [../backend/README.md](../backend/README.md) for backend API details and setup.

## Customization
- You can adjust the map style, add new features, or change the UI by editing components in `src/`.

## License
MIT (or specify your license)
