import axios from 'axios';
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
 * Interface for room temperature response
 */
export interface RoomTemperatureResponse {
  temperature: number;
  unit: string;
  display_in_ui: boolean;
}

// Create axios instance with default configs
const axiosInstance = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * API client for interacting with the Air Pump Control API
 */
const API = {
  /**
   * Send a command to turn off the air pump
   * @returns {Promise<ApiResponse>} Response from the server
   */
  turnOff: async (): Promise<ApiResponse> => {
    try {
      const response = await axiosInstance.post('/air_pump/off/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Server responded with ${error.response?.status}: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Send a command to control the air pump
   * @param {OperatingMode} mode - Either "heat" or "cool"
   * @param {AirPumpSettings} settings - Settings for the air pump
   * @returns {Promise<ApiResponse>} Response from the server
   */
  sendCommand: async (mode: OperatingMode, settings: AirPumpSettings): Promise<ApiResponse> => {
    const endpoint = mode === "heat" ? "/air_pump/heat/" : "/air_pump/cool/";
    
    try {
      const response = await axiosInstance.post(endpoint, settings);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Server responded with ${error.response?.status}: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Get the current state of the air pump
   * @returns {Promise<ApiResponse>} Response from the server with current state
   */
  getState: async (): Promise<ApiResponse> => {
    try {
      const response = await axiosInstance.get('/air_pump/state/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Server responded with ${error.response?.status}: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Get the current room temperature
   * @returns {Promise<ApiResponse>} Response from the server with room temperature
   */
  getRoomTemperature: async (): Promise<ApiResponse> => {
    try {
      const response = await axiosInstance.get('/air_pump/room_temperature/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Server responded with ${error.response?.status}: ${error.message}`);
      }
      throw error;
    }
  }
};

export default API;