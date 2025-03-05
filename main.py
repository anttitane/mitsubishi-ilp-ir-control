import time
import datetime
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
AirPumpController = Mitsubishi(gpio_pin, LogLevel.ErrorsOnly)

# Define the request model for the API
class AirPumpSettings(BaseModel):
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

# Endpoint to turn off the air pump
@app.post("/air_pump/off/")
def turn_off_air_pump():
    print("Powering off...")
    AirPumpController.power_off()
    return {"status": "Powered off"}

# Endpoint to activate cooling mode
@app.post("/air_pump/cool/")
def cool_air_pump(settings: AirPumpSettings):
    print_user_inputs("cooling", settings.temperature, settings.fan_speed)
    fan_speed = get_fan_speed_selection(settings.fan_speed)
    AirPumpController.send_command(
        climate_mode=ClimateMode.Cold,
        temperature=settings.temperature,
        fan_mode=fan_speed,
        vanne_vertical_mode=VanneVerticalMode.Top,
        vanne_horizontal_mode=VanneHorizontalMode.MiddleRight,
        isee_mode=ISeeMode.ISeeOff,
        area_mode=AreaMode.Full,
        powerful=PowerfulMode.PowerfulOff
    )
    return {"status": "Cooling command sent"}

# Endpoint to activate heating mode
@app.post("/air_pump/heat/")
def heat_air_pump(settings: AirPumpSettings):
    print_user_inputs("heating", settings.temperature, settings.fan_speed)
    fan_speed = get_fan_speed_selection(settings.fan_speed)
    AirPumpController.send_command(
        climate_mode=ClimateMode.Hot,
        temperature=settings.temperature,
        fan_mode=fan_speed,
        vanne_vertical_mode=VanneVerticalMode.MiddleTop,
        vanne_horizontal_mode=VanneHorizontalMode.MiddleRight,
        isee_mode=ISeeMode.ISeeOff,
        area_mode=AreaMode.Full,
        powerful=PowerfulMode.PowerfulOff
    )
    return {"status": "Heating command sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
