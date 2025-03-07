import { useState } from "react";

export default function AirPumpControl() {
  const [mode, setMode] = useState("cooling");
  const [temperature, setTemperature] = useState(21);
  const [fanSpeed, setFanSpeed] = useState("auto");
  const [verticalMode, setVerticalMode] = useState("middle");
  const [horizontalMode, setHorizontalMode] = useState("middle");

  const sendCommand = async () => {
    const endpoint = mode === "cooling" ? "/air_pump/cool/" : "/air_pump/heat/";
    const requestBody = {
      temperature: parseInt(temperature, 10),
      fan_speed: fanSpeed,
      vertical_mode: verticalMode,
      horizontal_mode: horizontalMode,
    };

    const response = await fetch(`http://localhost:8000${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    const data = await response.json();
    alert(data.status);
  };

  const turnOff = async () => {
    const response = await fetch("http://localhost:8000/air_pump/off/", {
      method: "POST",
    });
    const data = await response.json();
    alert(data.status);
  };

  return (
    <div className="p-4 max-w-md mx-auto bg-white shadow-lg rounded-lg">
      <h2 className="text-xl font-bold mb-4">Mitsubishi Air Pump Control</h2>

      <label>Mode:</label>
      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="cooling">Cooling</option>
        <option value="heating">Heating</option>
      </select>

      <label>Temperature:</label>
      <input
        type="number"
        value={temperature}
        onChange={(e) => setTemperature(e.target.value)}
        min="16"
        max="30"
      />

      <label>Fan Speed:</label>
      <select value={fanSpeed} onChange={(e) => setFanSpeed(e.target.value)}>
        <option value="auto">Auto</option>
        <option value="low">Low</option>
        <option value="med">Medium</option>
        <option value="high">High</option>
      </select>

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

      <button onClick={sendCommand} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Send Command
      </button>
      <button onClick={turnOff} className="mt-4 bg-red-500 text-white px-4 py-2 rounded">
        Turn Off
      </button>
    </div>
  );
}