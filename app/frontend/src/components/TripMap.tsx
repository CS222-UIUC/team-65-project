// components/TripMap.tsx
'use client'  // ensure it's client-only in Next 13+/app dir; harmless in pages dir

import { useMemo, useEffect } from 'react'
import {
  LoadScript,
  GoogleMap,
  Marker,
  Polyline,
} from '@react-google-maps/api'

const libraries: ('geometry' | 'places' | 'drawing' | 'visualization')[] = [
  'geometry',
]

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

interface Props {
  currentLocation: { lat: number; lng: number } | null
  itinerary: ItineraryItem[]
  mapData: MapData | null
  mapError: string | null
  setMapError: (e: string | null) => void
}

export default function TripMap({
  currentLocation,
  itinerary,
  mapData,
  mapError,
  setMapError,
}: Props) {
  useEffect(() => {
    console.log('Map component mounted')
    console.log('API Key available:', !!process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY)
    console.log('Current location:', currentLocation)
    console.log('Map data:', mapData)
  }, [currentLocation, mapData])

  // decode overview_polyline
  const path = useMemo<google.maps.LatLngLiteral[]>(() => {
    if (!mapData?.overview_polyline) return []
    try {
      return google.maps.geometry
        .encoding.decodePath(mapData.overview_polyline)
        .map((pt) => ({ lat: pt.lat(), lng: pt.lng() }))
    } catch (e) {
      console.error('Polyline decode error', e)
      setMapError('Error decoding route.')
      return []
    }
  }, [mapData, setMapError])

  // Colors for different legs
  const legColors = [
    '#4285F4', // Google Blue
    '#EA4335', // Google Red
    '#FBBC05', // Google Yellow
    '#34A853', // Google Green
    '#9C27B0', // Purple
    '#FF9800', // Orange
    '#00BCD4', // Cyan
    '#E91E63', // Pink
  ]

  return (
    <div className="h-full w-full relative" style={{ minHeight: '400px' }}>
      <LoadScript
        googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}
        libraries={libraries}
        loadingElement={
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            Loading map...
          </div>
        }
        onError={(error) => {
          console.error('Google Maps loading error:', error)
          setMapError('Error loading Google Maps')
        }}
      >
        <GoogleMap
          mapContainerStyle={{ width: '100%', height: '100%', minHeight: '400px' }}
          center={currentLocation ?? { lat: 0, lng: 0 }}
          zoom={12}
          onLoad={() => console.log('Map loaded successfully')}
        >
          {currentLocation && (
            <Marker
              position={currentLocation}
              title="Your current location"
            />
          )}
          {itinerary.map((item, idx) => {
            if (!item.location) return null
            const pos =
              typeof item.location === 'string'
                ? (() => {
                    const [lat, lng] = item.location
                      .split(',')
                      .map(Number)
                    return { lat, lng }
                  })()
                : item.location

            return (
              <Marker
                key={item.id}
                position={pos}
                label={{ text: `${idx + 1}`, color: 'white' }}
                title={item.description}
              />
            )
          })}
          {mapData?.legs.map((leg, idx) => (
            <>
              <Marker
                key={`start-${idx}`}
                position={leg.start_location}
                icon={{
                  path: google.maps.SymbolPath.CIRCLE,
                  scale: 8,
                  fillColor: '#4CAF50',
                  fillOpacity: 1,
                  strokeColor: '#FFFFFF',
                  strokeWeight: 2,
                }}
                title={`Start of leg ${idx + 1}`}
              />
              <Marker
                key={`end-${idx}`}
                position={leg.end_location}
                icon={{
                  path: google.maps.SymbolPath.CIRCLE,
                  scale: 8,
                  fillColor: '#F44336',
                  fillOpacity: 1,
                  strokeColor: '#FFFFFF',
                  strokeWeight: 2,
                }}
                title={`End of leg ${idx + 1}`}
              />
              {leg.steps.map((step, stepIdx) => {
                try {
                  const stepPath = google.maps.geometry.encoding
                    .decodePath(step.polyline)
                    .map((pt) => ({ lat: pt.lat(), lng: pt.lng() }))
                  return (
                    <Polyline
                      key={`leg-${idx}-step-${stepIdx}`}
                      path={stepPath}
                      options={{
                        strokeColor: legColors[idx % legColors.length],
                        strokeOpacity: 1.0,
                        strokeWeight: 3,
                        geodesic: true,
                      }}
                    />
                  )
                } catch (e) {
                  console.error('Error decoding step polyline:', e)
                  return null
                }
              })}
            </>
          ))}
        </GoogleMap>
      </LoadScript>

      {mapError && (
        <div className="absolute top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {mapError}
        </div>
      )}
    </div>
  )
}
