// pages/index.tsx

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import axios from 'axios'
import { FiTrash2, FiEdit2 } from 'react-icons/fi'

// Dynamically load TripMap only on the client
const TripMap = dynamic(() => import('../components/TripMap'), {
  ssr: false,
})

interface ItineraryItem {
  id: string
  type: string
  description: string
  location?:
    | string
    | {
        lat: number
        lng: number
      }
  time?: string
  duration?: string
}

interface MapData {
  overview_polyline: string
  legs: Array<{
    start_location: { lat: number; lng: number }
    end_location: { lat: number; lng: number }
    steps: Array<{ polyline: string }>
  }>
}

export default function Home() {
  const [itinerary, setItinerary] = useState<ItineraryItem[]>([])
  const [mapData, setMapData] = useState<MapData | null>(null)
  const [userInput, setUserInput] = useState('')
  const [currentLocation, setCurrentLocation] = useState<{
    lat: number
    lng: number
  } | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)

  // get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        ({ coords }) =>
          setCurrentLocation({ lat: coords.latitude, lng: coords.longitude }),
        (err) => console.error('Location error', err)
      )
    }
  }, [])

  const handleGenerateItinerary = async () => {
    try {
      setMapError(null)
      const res = await axios.post(
        'http://localhost:8000/api/generate-itinerary',
        { user_request: userInput, current_location: currentLocation }
      )
      const data = res.data
      if (!data?.itinerary) return console.error('Invalid response', data)
      setItinerary(data.itinerary)

      if (data.map_data && !data.map_data.error) {
        setMapData(data.map_data)
      } else {
        setMapData(null)
        setMapError('Unable to load route map. Please try again.')
      }
    } catch (e) {
      console.error(e)
      setMapError('Failed to generate itinerary. Please try again.')
    }
  }

  const handleUpdateItinerary = async (req: string) => {
    try {
      const res = await axios.post(
        'http://localhost:8000/api/update-itinerary',
        { user_request: req, current_itinerary: itinerary }
      )
      setItinerary(res.data.itinerary)
      setMapData(res.data.map_data)
    } catch (e) {
      console.error(e)
    }
  }

  const removeItem = (id: string) => {
    setItinerary((it) => it.filter((i) => i.id !== id))
    handleUpdateItinerary(`Remove item ${id} from itinerary`)
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left panel: Itinerary */}
      <div className="w-1/3 p-4 overflow-y-auto">
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h2 className="text-2xl font-bold mb-4">Your Itinerary</h2>
          <div className="space-y-4">
            {itinerary.map((item, idx) => (
              <div
                key={item.id}
                className="bg-gray-50 p-4 rounded-lg flex justify-between items-start"
              >
                <div>
                  <h3 className="font-semibold">{item.type}</h3>
                  <p className="text-gray-600">{item.description}</p>
                  {item.time && (
                    <p className="text-sm text-gray-500">Time: {item.time}</p>
                  )}
                  {item.duration && (
                    <p className="text-sm text-gray-500">
                      Duration: {item.duration}
                    </p>
                  )}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <FiTrash2 />
                  </button>
                  <button className="text-blue-500 hover:text-blue-700">
                    <FiEdit2 />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel: Map & Chat */}
      <div className="w-2/3 flex flex-col">
        {/* Map */}
        <div className="h-1/2 p-4">
          <div className="bg-white rounded-lg shadow-lg h-full">
            <TripMap
              currentLocation={currentLocation}
              itinerary={itinerary}
              mapData={mapData}
              mapError={mapError}
              setMapError={setMapError}
            />
          </div>
        </div>
        {/* Chat */}
        <div className="h-1/2 p-4">
          <div className="bg-white rounded-lg shadow-lg h-full flex flex-col">
            <div className="flex-1 p-4 overflow-y-auto">
              {/* …your chat */}
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
  )
}
