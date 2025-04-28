import pytest
import requests_mock as requests_mock_module
from backend import googlemapsroute as core


def test_sample_route_points():
    points = [(1, 1), (2, 2), (3, 3), (4, 4)]
    sampled = core.sample_route_points(points, 2)
    assert sampled == [(1, 1), (3, 3)]


def test_get_route(requests_mock):
    fake_response = {
        'status': 'OK',
        'routes': [{
            'overview_polyline': {
                'points': '}_ilFtwvpOwK_A'
            }
        }]
    }
    # ANY from the real module, not the fixture
    requests_mock.get(requests_mock_module.ANY, json=fake_response)
    result = core.get_route("Start", "End")
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_stop_nearby(requests_mock):
    mock_data = {
        'status': 'OK',
        'results': [{
            'place_id': 'abc123',
            'name': 'Mock Stop',
            'geometry': {'location': {'lat': 40.0, 'lng': -88.0}},
            'rating': 4.5,
            'user_ratings_total': 200,
            'vicinity': '123 Mock St'
        }]
    }
    requests_mock.get(requests_mock_module.ANY, json=mock_data)
    stop = core.get_stop_nearby(40.0, -88.0, "gas station")
    assert stop['name'] == 'Mock Stop'