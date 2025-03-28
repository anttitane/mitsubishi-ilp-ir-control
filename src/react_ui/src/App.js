import React, { useState } from "react";
import "./App.css";

export default function AirPumpControl() {
  const [mode, setMode] = useState("heat");
  const [temperature, setTemperature] = useState(23);
  const [fanSpeed, setFanSpeed] = useState("auto");
  const [verticalMode, setVerticalMode] = useState("middle_top");
  const [horizontalMode, setHorizontalMode] = useState("middle");

  const sendCommand = async () => {
    if (mode === "off") {
      try {
        const response = await fetch(`/air_pump/off/`, { method: "POST" });
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
      horizontal_mode: horizontalMode.replace(" ", ""),
    };

    try {
      const response = await fetch(endpoint, {
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
    <>
    <div className="control-panel">
      <div className="brand-name top-left">MITSUBISHI</div>
      <div className="temperature-control">
        <div className="temperature">{temperature}°C</div>
        <div className="temperature-buttons">
          <button onClick={() => setTemperature((prev) => Math.max(15, prev - 1))}>-</button>
          <button onClick={() => setTemperature((prev) => Math.min(30, prev + 1))}>+</button>
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
            <option value="auto">Auto</option>
            <option value="low">Low</option>
            <option value="med">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label>Vertical Mode:</label>
          <select value={verticalMode} onChange={(e) => setVerticalMode(e.target.value)}>
            <option value="auto">Auto</option>
            <option value="top">Top</option>
            <option value="middle_top">Middle Top</option>
            <option value="middle">Middle</option>
            <option value="middle_bottom">Middle Bottom</option>
            <option value="bottom">Bottom</option>
            <option value="swing">Swing</option>
          </select>
        </div>

        <div>
          <label>Horizontal Mode:</label>
          <select value={horizontalMode} onChange={(e) => setHorizontalMode(e.target.value)}>
            <option value="not_set">Not Set</option>
            <option value="left">Left</option>
            <option value="middle_left">Middle Left</option>
            <option value="middle">Middle</option>
            <option value="middle_right">Middle Right</option>
            <option value="right">Right</option>
            <option value="swing">Swing</option>
          </select>
          </div>
        </div>
        <button onClick={sendCommand} className="send-command-button">Send Command</button>
      </div>
    </>
  );
}