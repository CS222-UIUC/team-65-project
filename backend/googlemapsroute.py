import os
import math
import logging
from dotenv import load_dotenv
import requests
import polyline

load_dotenv()  # loads GOOGLE_MAPS_KEY

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_KEY")


def haversine(lat1, lng1, lat2, lng2):
    """
    Compute the great-circle distance between two points on the Earth (in meters).
    """
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_route(start, end):
    """
    Fetches the polyline route between start and end (strings or "lat,lng").
    Returns a list of (lat, lng) points.
    """
    url = (
        "https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={start}&destination={end}&key={GOOGLE_MAPS_API_KEY}"
    )
    try:
        resp = requests.get(url)
        data = resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching directions: {e}")
        return []

    if data.get("status") != "OK":
        logging.error(f"Directions API error: {data.get('status')}")
        return []

    points_str = data["routes"][0]["overview_polyline"]["points"]
    return polyline.decode(points_str)


def sample_route_points(route_points, num_samples):
    """
    Uniformly sample up to num_samples points along the route.
    """
    if not route_points:
        return []

    step = max(1, len(route_points) // num_samples)
    return route_points[::step]


def score_place(place, origin_lat, origin_lng, radius=500, max_reviews=500):
    """
    Example custom score combining rating, review count, and proximity.
    Normalize each component to roughly [0,1] before weighting.
    """
    rating = place.get("rating", 0) / 5.0
    reviews = place.get("user_ratings_total", 0)
    reviews_norm = min(reviews, max_reviews) / max_reviews
    plat = place["geometry"]["location"]["lat"]
    plng = place["geometry"]["location"]["lng"]
    dist = haversine(origin_lat, origin_lng, plat, plng) / radius  # >1 if outside
    # weights: rating 60%, reviews 30%, penalty for distance 10%
    return 0.6 * rating + 0.3 * reviews_norm - 0.1 * dist


def get_stop_nearby(lat, lng, stop_type, radius=500,
                    mode="prominence", custom_score_fn=None):
    """
    Finds one “best” stop near (lat,lng) of keyword type.

    mode:
      - "prominence" (default): API’s default sort within radius
      - "distance":    nearest (requires omitting radius)
      - "custom":      use custom_score_fn on top N candidates
    """
    base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "keyword": stop_type,
        "key": GOOGLE_MAPS_API_KEY,
    }

    if mode == "distance":
        params["rankby"] = "distance"
    else:
        # prominence or custom both need a radius
        params["radius"] = radius

    try:
        resp = requests.get(base, params=params)
        data = resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Places API error: {e}")
        return None

    results = data.get("results", [])
    if not results:
        return None

    if mode == "custom" and custom_score_fn:
        # score top 10 candidates by your function
        candidates = results[:10]
        best = max(candidates, key=lambda p: custom_score_fn(p, lat, lng))
    elif mode in ("distance", "prominence"):
        best = results[0]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return {
        "place_id": best.get("place_id"),
        "name": best.get("name"),
        "location": best.get("geometry", {}).get("location"),
        "rating": best.get("rating", "N/A"),
        "user_ratings_total": best.get("user_ratings_total", "N/A"),
        "vicinity": best.get("vicinity"),
    }


def find_stops_along_route(start, end, stop_type,
                           num_samples=10, radius=500,
                           mode="prominence", custom_score_fn=None):
    """
    Sample points along the route and find unique stops of stop_type.
    Returns:
      { "route": [...points...],
        "stops": [...stop dicts...] }
    """
    route = get_route(start, end)
    sampled = sample_route_points(route, num_samples)

    stops = {}
    for lat, lng in sampled:
        stop = get_stop_nearby(lat, lng, stop_type, radius,
                               mode=mode, custom_score_fn=custom_score_fn)
        if stop and stop["place_id"] not in stops:
            stops[stop["place_id"]] = stop

    return {"route": route, "stops": list(stops.values())}


if __name__ == "__main__":
    # Example usage:
    start_location = "Champaign, IL"
    end_location = "Chicago, IL"
    stop_type = "gas station"

    # Choose mode: "prominence", "distance", or "custom"
    mode = "custom"

    result = find_stops_along_route(
        start=start_location,
        end=end_location,
        stop_type=stop_type,
        num_samples=8,
        radius=800,
        mode=mode,
        custom_score_fn=score_place  # only used if mode=="custom"
    )

    print(f"Found {len(result['stops'])} stops along the route ({mode} mode):\n")
    for stop in result["stops"]:
        print(f"- {stop['name']} ({stop['vicinity']}): "
              f"{stop['rating']}⭐️ from {stop['user_ratings_total']} reviews")
