import { OperatingMode, FanSpeed, VerticalMode, HorizontalMode } from './constants';

/**
 * Interface for air pump settings
 */
export interface AirPumpSettings {
  temperature: number;
  fan_speed: FanSpeed;
  vertical_mode: VerticalMode;
  horizontal_mode: HorizontalMode;
}

/**
 * Interface for API responses
 */
export interface ApiResponse {
  status: string;
  [key: string]: any;
}

/**
 * API client for interacting with the Air Pump Control API
 */
const API = {
  /**
   * Send a command to turn off the air pump
   * @returns {Promise<ApiResponse>} Response from the server
   */
  turnOff: async (): Promise<ApiResponse> => {
    const response = await fetch('/air_pump/off/', { method: 'POST' });
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    return response.json();
  },

  /**
   * Send a command to control the air pump
   * @param {OperatingMode} mode - Either "heat" or "cool"
   * @param {AirPumpSettings} settings - Settings for the air pump
   * @returns {Promise<ApiResponse>} Response from the server
   */
  sendCommand: async (mode: OperatingMode, settings: AirPumpSettings): Promise<ApiResponse> => {
    const endpoint = mode === "heat" ? "/air_pump/heat/" : "/air_pump/cool/";
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    return response.json();
  }
};

export default API;