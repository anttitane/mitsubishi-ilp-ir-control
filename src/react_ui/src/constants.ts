/**
 * Application constants
 */

// Temperature range
export const TEMPERATURE = {
  MIN: 15,
  MAX: 30,
  DEFAULT: 23
} as const;

// Operating modes
export const MODES = {
  HEAT: "heat",
  COOL: "cool",
  OFF: "off"
} as const;

export type OperatingMode = typeof MODES[keyof typeof MODES];

// Fan speed options
export const FAN_SPEEDS = [
  { value: "auto", label: "Auto" },
  { value: "low", label: "Low" },
  { value: "med", label: "Medium" },
  { value: "high", label: "High" }
] as const;

export type FanSpeed = typeof FAN_SPEEDS[number]['value'];

// Vertical mode options
export const VERTICAL_MODES = [
  { value: "auto", label: "Auto" },
  { value: "top", label: "Top" },
  { value: "middle_top", label: "Middle Top" },
  { value: "middle", label: "Middle" },
  { value: "middle_bottom", label: "Middle Bottom" },
  { value: "bottom", label: "Bottom" },
  { value: "swing", label: "Swing" }
] as const;

export type VerticalMode = typeof VERTICAL_MODES[number]['value'];

// Horizontal mode options
export const HORIZONTAL_MODES = [
  { value: "not_set", label: "Not Set" },
  { value: "left", label: "Left" },
  { value: "middle_left", label: "Middle Left" },
  { value: "middle", label: "Middle" },
  { value: "middle_right", label: "Middle Right" },
  { value: "right", label: "Right" },
  { value: "swing", label: "Swing" }
] as const;

export type HorizontalMode = typeof HORIZONTAL_MODES[number]['value'];