import time
import pytest

from backend import googlemapsroute as core

# Disable the 2 s sleep in _paginate_places
@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)

# Stub out polyline.decode to a known fixed route
@pytest.fixture(autouse=True)
def fake_decode(monkeypatch):
    # pretend every polyline decodes to these four points
    monkeypatch.setattr(core.polyline, "decode", lambda pts: [(0, 0), (0, 1), (0, 2), (0, 3)])

# Provide a fake directions() that always returns our dummy encoded polyline
@pytest.fixture(autouse=True)
def fake_directions(monkeypatch):
    monkeypatch.setattr(
        core.gmaps,
        "directions",
        lambda origin, destination, departure_time=None: [
            { "overview_polyline": { "points": "irrelevant" } }
        ],
    )

# Provide a fake places_nearby that returns two pages
@pytest.fixture(autouse=True)
def fake_places(monkeypatch):
    page1 = {
        "results": [
            {
                "place_id": "stop1",
                "name": "Coffee A",
                "geometry": {"location": {"lat": 0.0, "lng": 0.0}},
                "rating": 4.2,
                "user_ratings_total": 50,
                "vicinity": "123 A St",
            }
        ],
        "next_page_token": "token123",
    }
    page2 = {
        "results": [
            {
                "place_id": "stop2",
                "name": "Coffee B",
                "geometry": {"location": {"lat": 0.0, "lng": 1.0}},
                "rating": 4.8,
                "user_ratings_total": 30,
                "vicinity": "456 B Ave",
            }
        ]
    }

    def places_nearby(location=None, radius=None, keyword=None, page_token=None):
        return page2 if page_token else page1

    monkeypatch.setattr(core.gmaps, "places_nearby", places_nearby)


def test_sample_route_points_by_distance():
    route = [(0, 0), (0, 1), (0, 2), (0, 3)]
    # 4-point route, asking for 3 samples → should pick roughly start, mid, end
    samples = core.sample_route_points_by_distance(route, num_samples=3)
    assert samples == [(0, 0), (0, 2), (0, 3)]


def test_paginate_places_collects_both_pages():
    # call paginate on our fake first page
    first = core.gmaps.places_nearby()
    pages = core._paginate_places(first)
    # should have exactly two pages returned
    assert len(pages) == 2
    # verify the place_ids from each page
    ids = [p["results"][0]["place_id"] for p in pages]
    assert ids == ["stop1", "stop2"]


def test_find_stops_along_route_happy_path():
    result = core.find_stops_along_route(
        start="X",
        end="Y",
        stop_type="coffee",
        num_samples=2,
        radius=100,
    )

    # The route should come back with the four points from fake_decode
    assert result["route"] == [(0, 0), (0, 1), (0, 2), (0, 3)]

    stops = result["stops"]
    # We stubbed two pages with distinct place_ids → 2 stops
    assert len(stops) == 2

    by_id = {s["place_id"]: s for s in stops}
    assert "stop1" in by_id
    assert "stop2" in by_id

    # Check some fields carried through
    assert by_id["stop1"]["name"] == "Coffee A"
    assert by_id["stop2"]["vicinity"] == "456 B Ave"
