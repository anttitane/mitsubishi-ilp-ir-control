import React from "react";
import { OperatingMode } from "./constants";

/**
 * Interface for ModeSelector props
 */
interface ModeSelectorProps {
  currentMode: OperatingMode;
  onSelectMode: (mode: OperatingMode) => void;
}

/**
 * ModeSelector - Component for selecting the air pump operation mode
 */
export function ModeSelector({ currentMode, onSelectMode }: ModeSelectorProps): React.ReactElement {
  const modes = [
    { value: "heat" as OperatingMode, label: "Heat" },
    { value: "cool" as OperatingMode, label: "Cool" },
    { value: "off" as OperatingMode, label: "Off" }
  ];

  return (
    <div className="mode-buttons">
      {modes.map(mode => (
        <button
          key={mode.value}
          className={currentMode === mode.value ? "active" : ""}
          onClick={() => onSelectMode(mode.value)}
        >
          {mode.label}
        </button>
      ))}
    </div>
  );
}

/**
 * Option interface for dropdown options
 */
export interface Option<T> {
  value: T;
  label: string;
}

/**
 * Interface for DropdownSelect props
 */
interface DropdownSelectProps<T> {
  id: string;
  label: string;
  value: T;
  options: readonly Option<T>[] | Option<T>[];
  onChange: (value: T) => void;
  disabled?: boolean;
}

/**
 * DropdownSelect - Reusable dropdown component
 */
export function DropdownSelect<T extends string>({ 
  id, 
  label, 
  value, 
  options, 
  onChange, 
  disabled 
}: DropdownSelectProps<T>): React.ReactElement {
  return (
    <div className="dropdown-item">
      <label htmlFor={id}>{label}:</label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        disabled={disabled}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

/**
 * Interface for TemperatureControl props
 */
interface TemperatureControlProps {
  temperature: number;
  onIncrement: () => void;
  onDecrement: () => void;
}

/**
 * TemperatureControl - Component for displaying and controlling temperature
 */
export function TemperatureControl({ 
  temperature, 
  onIncrement, 
  onDecrement 
}: TemperatureControlProps): React.ReactElement {
  return (
    <div className="temperature-control">
      <div className="temperature">{temperature}°C</div>
      <div className="temperature-buttons">
        <button onClick={onDecrement}>-</button>
        <button onClick={onIncrement}>+</button>
      </div>
    </div>
  );
}

/**
 * Interface for Notification props
 */
interface NotificationProps {
  message?: string;
  type?: "success" | "error" | "info";
  onClose?: () => void;
}

/**
 * Notification - Component for displaying feedback messages
 */
export function Notification({ 
  message, 
  type = "info", 
  onClose 
}: NotificationProps): React.ReactElement | null {
  if (!message) return null;
  
  return (
    <div className={`notification ${type}`}>
      <span>{message}</span>
      {onClose && (
        <button className="close-button" onClick={onClose}>
          ×
        </button>
      )}
    </div>
  );
}