from dotenv import load_dotenv
import os

import logging
import time
from datetime import datetime
from typing import List, Tuple, Dict, Any

import googlemaps
import polyline
from geopy.distance import geodesic

load_dotenv()  # Load environment variables from .env

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def sample_route_points_by_distance(
    route: List[Tuple[float, float]],
    num_samples: int
) -> List[Tuple[float, float]]:
    """
    Sample 'num_samples' points evenly spaced by distance along a polyline route.
    """
    # Compute cumulative distances along the route
    cum_distances: List[float] = [0.0]
    for (lat1, lng1), (lat2, lng2) in zip(route, route[1:]):
        segment = geodesic((lat1, lng1), (lat2, lng2)).meters
        cum_distances.append(cum_distances[-1] + segment)

    total_distance = cum_distances[-1]
    if num_samples < 2 or total_distance == 0:
        return route

    # Target distances for each sample
    targets = [i * total_distance / (num_samples - 1) for i in range(num_samples)]
    samples: List[Tuple[float, float]] = []
    idx = 0
    for t in targets:
        # Advance index to the segment containing target distance
        while idx < len(cum_distances) - 1 and cum_distances[idx] < t:
            idx += 1
        samples.append(route[idx])
    return samples


def _paginate_places(first_page: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Yield all pages of a Places API nearby search, handling next_page_token delays.
    """
    pages = [first_page]
    while 'next_page_token' in pages[-1]:
        time.sleep(2)  # Required delay before requesting next page
        next_token = pages[-1]['next_page_token']
        page = gmaps.places_nearby(page_token=next_token)
        pages.append(page)
    return pages


def find_stops_along_route(
    start: str,
    end: str,
    stop_type: str,
    num_samples: int = 10,
    radius: int = 500
) -> Dict[str, Any]:
    """
    Fetches a route from 'start' to 'end'.
    Samples points evenly by distance, then searches for the highest-rated stop within `radius`
    meters of each point.

    Returns a dict with:
      - 'route': List of (lat, lng) tuples
      - 'stops': List of stop info dicts (place_id, name, location, rating, user_ratings_total, vicinity)
    """
    try:
        directions = gmaps.directions(start, end, departure_time=datetime.now())
    except Exception:
        logging.exception("Failed to fetch directions from %s to %s", start, end)
        return {'route': [], 'stops': []}

    if not directions:
        logging.warning("No route found from %s to %s", start, end)
        return {'route': [], 'stops': []}

    # Decode overview polyline
    raw_poly = directions[0]['overview_polyline']['points']
    route: List[Tuple[float, float]] = polyline.decode(raw_poly)

    # Sample points along the route
    sample_points = sample_route_points_by_distance(route, num_samples)

    seen: Dict[str, Dict[str, Any]] = {}
    # Search for places around each sample point
    for lat, lng in sample_points:
        first_page = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            keyword=stop_type
        )
        for page in _paginate_places(first_page):
            for p in page.get('results', []):
                pid = p['place_id']
                score = (p.get('rating', 0), p.get('user_ratings_total', 0))
                # Keep the highest scored result per place_id
                if pid not in seen or score > seen[pid]['_score']:
                    seen[pid] = {
                        'place_id': pid,
                        'name': p.get('name'),
                        'location': p.get('geometry', {}).get('location'),
                        'rating': p.get('rating'),
                        'user_ratings_total': p.get('user_ratings_total'),
                        'vicinity': p.get('vicinity'),
                        '_score': score
                    }

    # Strip internal scoring fields
    stops = [
        {k: v for k, v in info.items() if k != '_score'}
        for info in seen.values()
    ]

    return {'route': route, 'stops': stops}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Example usage:
    start_address = 'Saratoga, CA'
    end_address = 'Champaign, IL'
    results = find_stops_along_route(
        start_address,
        end_address,
        stop_type='coffee',
        num_samples=10,
        radius=500
    )
    print(results)
if __name__ == '__main__':
    start_location = "Champaign, IL"
    end_location = "Chicago, IL"
    stop_type = "gas station"

    result = find_stops_along_route(start_location, end_location, stop_type)
    print("Route points:")
    print(result['route'])
    print("\nStops along the route:")
    for stop in result['stops']:
        print(stop)

