import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders temperature control', () => {
  render(<App />);
  const temperatureElement = screen.getByText(/°C/i);
  expect(temperatureElement).toBeInTheDocument();
});