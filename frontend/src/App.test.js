import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the geolocation API
const mockGeolocation = {
  getCurrentPosition: jest.fn()
    .mockImplementation((successCallback) => 
      successCallback({
        coords: {
          latitude: 40.1164,
          longitude: -88.2434
        }
      })
    )
};

global.navigator.geolocation = mockGeolocation;

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
