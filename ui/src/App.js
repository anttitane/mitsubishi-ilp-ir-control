import { useState } from "react";

export default function AirPumpControl() {
  const [mode, setMode] = useState("cooling");
  const [temperature, setTemperature] = useState(21);
  const [fanSpeed, setFanSpeed] = useState("auto");
  const [verticalMode, setVerticalMode] = useState("Auto");
  const [horizontalMode, setHorizontalMode] = useState("Middle");

  const sendCommand = async () => {
    const requestBody = {
      mode,
      temperature: parseInt(temperature, 10),
      fan_speed: fanSpeed,
      vertical_mode: verticalMode,
      horizontal_mode: horizontalMode,
    };

    const response = await fetch("http://192.168.4.52:8000/control_air_pump/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
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
        <option value="Auto">Auto</option>
        <option value="Top">Top</option>
        <option value="MiddleTop">Middle Top</option>
        <option value="Middle">Middle</option>
        <option value="MiddleBottom">Middle Bottom</option>
        <option value="Bottom">Bottom</option>
        <option value="Swing">Swing</option>
      </select>

      <label>Horizontal Mode:</label>
      <select value={horizontalMode} onChange={(e) => setHorizontalMode(e.target.value)}>
        <option value="NotSet">Not Set</option>
        <option value="Left">Left</option>
        <option value="MiddleLeft">Middle Left</option>
        <option value="Middle">Middle</option>
        <option value="MiddleRight">Middle Right</option>
        <option value="Right">Right</option>
        <option value="Swing">Swing</option>
      </select>

      <button onClick={sendCommand} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Send Command
      </button>
    </div>
  );
}
