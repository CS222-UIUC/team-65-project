import { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, Polyline } from '@react-google-maps/api';
import axios from 'axios';
import { FiTrash2, FiEdit2 } from 'react-icons/fi';

interface ItineraryItem {
  id: string;
  type: string;
  description: string;
  location?: {
    lat: number;
    lng: number;
  };
  time?: string;
  duration?: string;
}

interface MapData {
  overview_polyline: string;
  legs: Array<{
    start_location: { lat: number; lng: number };
    end_location: { lat: number; lng: number };
    steps: Array<{
      polyline: string;
    }>;
  }>;
}

export default function Home() {
  const [itinerary, setItinerary] = useState<ItineraryItem[]>([]);
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [userInput, setUserInput] = useState('');
  const [currentLocation, setCurrentLocation] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    // Get user's current location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);

  const handleGenerateItinerary = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/generate-itinerary', {
        user_request: userInput,
        current_location: currentLocation,
      });
      setItinerary(response.data.itinerary);
      setMapData(response.data.map_data);
    } catch (error) {
      console.error('Error generating itinerary:', error);
    }
  };

  const handleUpdateItinerary = async (request: string) => {
    try {
      const response = await axios.post('http://localhost:8000/api/update-itinerary', {
        user_request: request,
        current_itinerary: itinerary,
      });
      setItinerary(response.data.itinerary);
      setMapData(response.data.map_data);
    } catch (error) {
      console.error('Error updating itinerary:', error);
    }
  };

  const removeItem = (id: string) => {
    const updatedItinerary = itinerary.filter(item => item.id !== id);
    setItinerary(updatedItinerary);
    handleUpdateItinerary(`Remove item ${id} from itinerary`);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left side - Itinerary */}
      <div className="w-1/3 p-4 overflow-y-auto">
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h2 className="text-2xl font-bold mb-4">Your Itinerary</h2>
          <div className="space-y-4">
            {itinerary.map((item) => (
              <div key={item.id} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{item.type}</h3>
                    <p className="text-gray-600">{item.description}</p>
                    {item.time && <p className="text-sm text-gray-500">Time: {item.time}</p>}
                    {item.duration && <p className="text-sm text-gray-500">Duration: {item.duration}</p>}
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <FiTrash2 />
                    </button>
                    <button
                      className="text-blue-500 hover:text-blue-700"
                    >
                      <FiEdit2 />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side - Map and Chat */}
      <div className="w-2/3 flex flex-col">
        {/* Map */}
        <div className="h-1/2 p-4">
          <div className="bg-white rounded-lg shadow-lg h-full">
            <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}
              libraries={['geometry']}
            >
              <GoogleMap
                mapContainerStyle={{ width: '100%', height: '100%' }}
                center={currentLocation || { lat: 0, lng: 0 }}
                zoom={12}
              >
                {mapData && (
                  <Polyline
                    path={google.maps.geometry.encoding.decodePath(mapData.overview_polyline)}
                    options={{
                      strokeColor: '#FF0000',
                      strokeOpacity: 1.0,
                      strokeWeight: 2,
                    }}
                  />
                )}
              </GoogleMap>
            </LoadScript>
          </div>
        </div>

        {/* Chat */}
        <div className="h-1/2 p-4">
          <div className="bg-white rounded-lg shadow-lg h-full flex flex-col">
            <div className="flex-1 p-4 overflow-y-auto">
              {/* Chat messages will go here */}
            </div>
            <div className="p-4 border-t">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your request..."
                  className="flex-1 p-2 border rounded-lg"
                />
                <button
                  onClick={handleGenerateItinerary}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 