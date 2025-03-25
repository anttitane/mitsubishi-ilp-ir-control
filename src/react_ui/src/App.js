import React, { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:8000"; // Add base URL for the backend

export default function AirPumpControl() {
  const [mode, setMode] = useState("heat");
  const [temperature, setTemperature] = useState(23);
  const [fanSpeed, setFanSpeed] = useState("Medium");
  const [verticalMode, setVerticalMode] = useState("Middle Top");
  const [horizontalMode, setHorizontalMode] = useState("Middle");

  const sendCommand = async () => {
    if (mode === "off") {
      try {
        const response = await fetch(`${API_BASE_URL}/air_pump/off/`, {
          method: "POST",
        });
        const data = await response.json();
        alert(data.status);
      } catch (error) {
        alert("Error turning off: " + error.message);
      }
      return;
    }

    const endpoint = mode === "heat" ? "/air_pump/heat/" : "/air_pump/cool/";
    const requestBody = {
      temperature: parseInt(temperature, 10),
      fan_speed: fanSpeed.toLowerCase(),
      vertical_mode: verticalMode.replace(" ", ""),
      horizontal_mode: horizontalMode.replace(" ", "")
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      alert(data.status);
    } catch (error) {
      alert("Error sending command: " + error.message);
    }
  };

  return (
    <div className="control-panel">
      <div className="temperature-control">
        <div className="temperature">{temperature}°C</div>
        <div className="temperature-buttons">
          <button onClick={() => setTemperature(prev => Math.max(15, prev - 1))}>-</button>
          <button onClick={() => setTemperature(prev => Math.min(30, prev + 1))}>+</button>
        </div>
      </div>

      <div className="mode-buttons">
        <button className={mode === "heat" ? "active" : ""} onClick={() => setMode("heat")}>Heat</button>
        <button className={mode === "cool" ? "active" : ""} onClick={() => setMode("cool")}>Cool</button>
        <button className={mode === "off" ? "active" : ""} onClick={() => setMode("off")}>Off</button>
      </div>

      <div className="dropdowns">
        <div>
          <label>Fan Speed:</label>
          <select value={fanSpeed} onChange={(e) => setFanSpeed(e.target.value)}>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        <div>
          <label>Vertical Mode:</label>
          <select value={verticalMode} onChange={(e) => setVerticalMode(e.target.value)}>
            <option value="Top">Top</option>
            <option value="Middle Top">Middle Top</option>
            <option value="Middle">Middle</option>
            <option value="Bottom">Bottom</option>
          </select>
        </div>

        <div>
          <label>Horizontal Mode:</label>
          <select value={horizontalMode} onChange={(e) => setHorizontalMode(e.target.value)}>
            <option value="Left">Left</option>
            <option value="Middle Left">Middle Left</option>
            <option value="Middle">Middle</option>
            <option value="Middle Right">Middle Right</option>
            <option value="Right">Right</option>
          </select>
        </div>
      </div>

      <button 
        onClick={sendCommand} 
        className="send-command-button"
      >
        Send Command
      </button>
    </div>
  );
}