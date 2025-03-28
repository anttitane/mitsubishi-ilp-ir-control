import React, { useState } from "react";
import "./App.css";
import API from "./api";
import { TEMPERATURE, MODES, FAN_SPEEDS, VERTICAL_MODES, HORIZONTAL_MODES, OperatingMode, FanSpeed, VerticalMode, HorizontalMode } from "./constants";
import { ModeSelector, DropdownSelect, TemperatureControl, Notification, Option } from "./components";

/**
 * Interface for notification state
 */
interface NotificationState {
  message: string;
  type: "success" | "error" | "info";
}

/**
 * Main application component for the Mitsubishi Air Pump Control
 */
const AirPumpControl: React.FC = () => {
  // State management with typed state variables
  const [mode, setMode] = useState<OperatingMode>(MODES.HEAT);
  const [temperature, setTemperature] = useState<number>(TEMPERATURE.DEFAULT);
  const [fanSpeed, setFanSpeed] = useState<FanSpeed>(FAN_SPEEDS[0].value);
  const [verticalMode, setVerticalMode] = useState<VerticalMode>(VERTICAL_MODES[2].value);
  const [horizontalMode, setHorizontalMode] = useState<HorizontalMode>(HORIZONTAL_MODES[3].value);
  const [notification, setNotification] = useState<NotificationState | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Create mutable options arrays for the dropdown components
  const fanSpeedOptions = FAN_SPEEDS as readonly Option<FanSpeed>[];
  const verticalModeOptions = VERTICAL_MODES as readonly Option<VerticalMode>[];
  const horizontalModeOptions = HORIZONTAL_MODES as readonly Option<HorizontalMode>[];
  
  const handleTemperatureIncrement = (): void => {
    setTemperature(prev => Math.min(TEMPERATURE.MAX, prev + 1));
  };
  
  const handleTemperatureDecrement = (): void => {
    setTemperature(prev => Math.max(TEMPERATURE.MIN, prev - 1));
  };
  
  const showNotification = (message: string, type: "success" | "error" | "info" = "info"): void => {
    setNotification({ message, type });
    
    // Auto-dismiss notifications after 5 seconds
    setTimeout(() => {
      setNotification(null);
    }, 5000);
  };
  
  const handleModeChange = (newMode: OperatingMode): void => {
    setMode(newMode);
  };
  
  const sendCommand = async (): Promise<void> => {
    setIsLoading(true);
    
    try {
      if (mode === MODES.OFF) {
        const response = await API.turnOff();
        showNotification(response.status, "success");
      } else {
        const settings = {
          temperature: parseInt(temperature.toString(), 10),
          fan_speed: fanSpeed,
          vertical_mode: verticalMode,
          horizontal_mode: horizontalMode
        };
        
        const response = await API.sendCommand(mode, settings);
        showNotification(response.status, "success");
      }
    } catch (error) {
      showNotification(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="control-panel">
      <div className="brand-name top-left">MITSUBISHI</div>
      
      <TemperatureControl 
        temperature={temperature}
        onIncrement={handleTemperatureIncrement}
        onDecrement={handleTemperatureDecrement}
      />
      
      <ModeSelector 
        currentMode={mode} 
        onSelectMode={handleModeChange} 
      />
      
      <div className={`dropdowns ${mode === MODES.OFF ? "disabled" : ""}`}>
        <DropdownSelect<FanSpeed>
          id="fan-speed"
          label="Fan Speed"
          value={fanSpeed}
          options={fanSpeedOptions}
          onChange={setFanSpeed}
          disabled={mode === MODES.OFF}
        />
        
        <DropdownSelect<VerticalMode>
          id="vertical-mode"
          label="Vertical Mode"
          value={verticalMode}
          options={verticalModeOptions}
          onChange={setVerticalMode}
          disabled={mode === MODES.OFF}
        />
        
        <DropdownSelect<HorizontalMode>
          id="horizontal-mode"
          label="Horizontal Mode"
          value={horizontalMode}
          options={horizontalModeOptions}
          onChange={setHorizontalMode}
          disabled={mode === MODES.OFF}
        />
      </div>
      
      <button 
        onClick={sendCommand} 
        className={`send-command-button ${isLoading ? "loading" : ""}`}
        disabled={isLoading}
      >
        {isLoading ? "Sending..." : "Send Command"}
      </button>
      
      <Notification 
        message={notification?.message}
        type={notification?.type}
        onClose={() => setNotification(null)}
      />
    </div>
  );
};

export default AirPumpControl;