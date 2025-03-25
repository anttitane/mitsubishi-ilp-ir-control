import React, { useState } from "react";
import "./App.css";

export default function AirPumpControl() {
  const [mode, setMode] = useState("heat");
  const [temperature, setTemperature] = useState(23);
  const [fanSpeed, setFanSpeed] = useState("Medium");
  const [verticalMode, setVerticalMode] = useState("Middle Top");
  const [horizontalMode, setHorizontalMode] = useState("Middle");

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
    </div>
  );
}