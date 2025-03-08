import os
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ir_sender.ir_sender import LogLevel
from ir_sender.mitsubishi import (
    Mitsubishi, ClimateMode, FanMode, VanneVerticalMode, VanneHorizontalMode,
    ISeeMode, AreaMode, PowerfulMode
)

app = FastAPI()

# Load configuration
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Get path to the React build folder
CURRENT_DIR = os.path.dirname(__file__)
UI_BUILD_DIR = os.path.join(CURRENT_DIR, "react_ui", "build")

# Mount the 'build' folder at the root path
app.mount("/", StaticFiles(directory=UI_BUILD_DIR, html=True), name="static")

# Retrieve GPIO pin number from the configuration
gpio_pin = config['gpio']['pin']

# Initialize AirPumpController class with IR sender
AirPumpController = Mitsubishi(gpio_pin, LogLevel.ErrorsOnly)

# Define the request model for controlling the air pump
class AirPumpRequest(BaseModel):
    temperature: int
    fan_speed: str = "auto"
    vertical_mode: str = "middle"
    horizontal_mode: str = "middle"

# Helper function to map fan speed
def get_fan_speed_selection(fan_speed):
    fan_speed_map = {
        "low": FanMode.Speed1,
        "med": FanMode.Speed2,
        "high": FanMode.Speed3,
        "auto": FanMode.Auto
    }
    return fan_speed_map.get(fan_speed.lower(), FanMode.Auto)

# Helper function to map vertical mode
def get_vertical_mode(mode):
    vertical_map = {
        "auto": VanneVerticalMode.Auto,
        "top": VanneVerticalMode.Top,
        "middle_top": VanneVerticalMode.MiddleTop,
        "middle": VanneVerticalMode.Middle,
        "middle_bottom": VanneVerticalMode.MiddleBottom,
        "bottom": VanneVerticalMode.Bottom,
        "swing": VanneVerticalMode.Swing
    }
    return vertical_map.get(mode.lower(), VanneVerticalMode.Middle)

# Helper function to map horizontal mode
def get_horizontal_mode(mode):
    horizontal_map = {
        "not_set": VanneHorizontalMode.NotSet,
        "left": VanneHorizontalMode.Left,
        "middle_left": VanneHorizontalMode.MiddleLeft,
        "middle": VanneHorizontalMode.Middle,
        "middle_right": VanneHorizontalMode.MiddleRight,
        "right": VanneHorizontalMode.Right,
        "swing": VanneHorizontalMode.Swing
    }
    return horizontal_map.get(mode.lower(), VanneHorizontalMode.Middle)

# Endpoint to turn off the air pump
@app.post("/air_pump/off/")
def turn_off_air_pump():
    AirPumpController.power_off()
    return {"status": "Powered off"}

# Endpoint for cooling
@app.post("/air_pump/cool/")
def cool_air_pump(request: AirPumpRequest):
    FanSpeedSelection = get_fan_speed_selection(request.fan_speed)
    VerticalSelection = get_vertical_mode(request.vertical_mode)
    HorizontalSelection = get_horizontal_mode(request.horizontal_mode)

    AirPumpController.send_command(
        climate_mode=ClimateMode.Cold,
        temperature=request.temperature,
        fan_mode=FanSpeedSelection,
        vanne_vertical_mode=VerticalSelection,
        vanne_horizontal_mode=HorizontalSelection,
        isee_mode=ISeeMode.ISeeOff,
        area_mode=AreaMode.Full,
        powerful=PowerfulMode.PowerfulOff
    )
    return {"status": "Cooling command sent"}

# Endpoint for heating
@app.post("/air_pump/heat/")
def heat_air_pump(request: AirPumpRequest):
    FanSpeedSelection = get_fan_speed_selection(request.fan_speed)
    VerticalSelection = get_vertical_mode(request.vertical_mode)
    HorizontalSelection = get_horizontal_mode(request.horizontal_mode)

    AirPumpController.send_command(
        climate_mode=ClimateMode.Hot,
        temperature=request.temperature,
        fan_mode=FanSpeedSelection,
        vanne_vertical_mode=VerticalSelection,
        vanne_horizontal_mode=HorizontalSelection,
        isee_mode=ISeeMode.ISeeOff,
        area_mode=AreaMode.Full,
        powerful=PowerfulMode.PowerfulOff
    )
    return {"status": "Heating command sent"}
