import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the geolocation API
const mockGeolocation = {
  getCurrentPosition: jest.fn().mockImplementation((successCallback) =>
    successCallback({
      coords: {
        latitude: 40.1164,
        longitude: -88.2434,
      },
    })
  ),
};

global.navigator.geolocation = mockGeolocation;

test('renders Route Planner title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Route Planner/i); // Updated to match "Route Planner"
  expect(titleElement).toBeInTheDocument();
});

test('renders input fields for start and end locations', () => {
  render(<App />);
  const startInput = screen.getByPlaceholderText(/Start Location/i);
  const endInput = screen.getByPlaceholderText(/End Location/i);
  expect(startInput).toBeInTheDocument();
  expect(endInput).toBeInTheDocument();
});
