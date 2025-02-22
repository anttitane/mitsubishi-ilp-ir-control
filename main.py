import time
import datetime
import argparse
import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from ir_sender.ir_sender import LogLevel
from ir_sender.mitsubishi import Mitsubishi, ClimateMode, FanMode, VanneVerticalMode, VanneHorizontalMode, ISeeMode, AreaMode, PowerfulMode

app = FastAPI()

# Load configuration
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Retrieve GPIO pin number from the configuration
gpio_pin = config['gpio']['pin']

# Initialize AirPumpController class with IR sender
AirPumpController = Mitsubishi(gpio_pin, LogLevel.ErrorsOnly)  # (GPIO pin number, Log level)

# Define the request model for the API
class AirPumpRequest(BaseModel):
    mode: str
    temperature: int
    fan_speed: str = "auto"

# Print user inputs (for debugging)
def print_user_inputs(mode, temperature, fan_speed):
    print("---------------------------------------------")
    print("Operation mode is {}".format(mode))
    print("Temperature is {}".format(temperature))
    print("Fan speed is {}".format(fan_speed))
    print("---------------------------------------------")

# Set fan speed mode based on input
def get_fan_speed_selection(fan_speed):
    if fan_speed == "low":
        return FanMode.Speed1
    elif fan_speed == "med":
        return FanMode.Speed2
    elif fan_speed == "high":
        return FanMode.Speed3
    else:
        return FanMode.Auto

# Endpoint to control air pump
@app.post("/control_air_pump/")
def control_air_pump(request: AirPumpRequest):
    mode = request.mode
    temperature = request.temperature
    fan_speed = request.fan_speed

    print_user_inputs(mode, temperature, fan_speed)
    FanSpeedSelection = get_fan_speed_selection(fan_speed)

    if temperature == 0:
        print("Powering off...")
        AirPumpController.power_off()
        return {"status": "Powered off"}

    if mode == "cooling" and temperature > 0:
        print("Sending cooling command...")
        AirPumpController.send_command(
            climate_mode=ClimateMode.Cold,
            temperature=temperature,
            fan_mode=FanSpeedSelection,
            vanne_vertical_mode=VanneVerticalMode.Top,
            vanne_horizontal_mode=VanneHorizontalMode.MiddleRight,
            isee_mode=ISeeMode.ISeeOff,
            area_mode=AreaMode.Full,
            powerful=PowerfulMode.PowerfulOff
        )
        return {"status": "Cooling command sent"}

    if mode == "heating" and temperature > 0:
        print("Sending heating command...")
        AirPumpController.send_command(
            climate_mode=ClimateMode.Hot,
            temperature=temperature,
            fan_mode=FanSpeedSelection,
            vanne_vertical_mode=VanneVerticalMode.MiddleTop,
            vanne_horizontal_mode=VanneHorizontalMode.MiddleRight,
            isee_mode=ISeeMode.ISeeOff,
            area_mode=AreaMode.Full,
            powerful=PowerfulMode.PowerfulOff
        )
        return {"status": "Heating command sent"}

    return {"status": "Invalid command"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
