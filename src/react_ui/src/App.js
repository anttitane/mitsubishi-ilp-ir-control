import React, { useState, useRef, useEffect } from "react";
import "./App.css";

export default function AirPumpControl() {
  const [mode, setMode] = useState("heat");
  const [temperature, setTemperature] = useState(23);
  const [fanSpeed, setFanSpeed] = useState("Medium");
  const [verticalMode, setVerticalMode] = useState("Middle Top");
  const [horizontalMode, setHorizontalMode] = useState("Middle");
  const [isDragging, setIsDragging] = useState(false);
  const circleRef = useRef(null);

  const updateTemperatureFromMouse = (e) => {
    if (!circleRef.current) return;

    const circle = circleRef.current;
    const rect = circle.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.bottom;

    // Calculate angle based on mouse position relative to the bottom center
    const deltaX = e.clientX - centerX;
    const deltaY = centerY - e.clientY;
    let angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
    
    // Normalize angle to 0-180 degrees
    if (angle < 0) {
      angle = 0;
    } else if (angle > 180) {
      angle = 180;
    }
    
    // Map 0-180 degrees to temperature range (15-30)
    const newTemp = Math.round(15 + (angle / 180) * (30 - 15));
    setTemperature(Math.min(30, Math.max(15, newTemp)));
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    updateTemperatureFromMouse(e);
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      updateTemperatureFromMouse(e);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div className="control-panel">
      <div className="temperature-control">
        <div 
          className="circle" 
          ref={circleRef}
          onMouseDown={handleMouseDown}
        >
          <div className="temperature">{temperature}°C</div>
          <div 
            className="temperature-indicator"
            style={{
              transform: `rotate(${((temperature - 15) / (30 - 15)) * 180}deg)`
            }}
          />
        </div>
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