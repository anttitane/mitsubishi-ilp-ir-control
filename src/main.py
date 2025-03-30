import os
import yaml
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from contextlib import asynccontextmanager
from ir_sender.ir_sender import LogLevel
from ir_sender.mitsubishi import (
    Mitsubishi, ClimateMode, FanMode, VanneVerticalMode, VanneHorizontalMode,
    ISeeMode, AreaMode, PowerfulMode
)

# Load configuration from file
def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, "..", "config.yaml")
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Error loading configuration: {str(e)}")

config = load_config()

# Define enums for cleaner API interfaces
class FanSpeedEnum(str, Enum):
    LOW = "low"
    MED = "med"
    HIGH = "high"
    AUTO = "auto"

class VerticalModeEnum(str, Enum):
    AUTO = "auto"
    TOP = "top"
    MIDDLE_TOP = "middle_top"
    MIDDLE = "middle"
    MIDDLE_BOTTOM = "middle_bottom"
    BOTTOM = "bottom"
    SWING = "swing"

class HorizontalModeEnum(str, Enum):
    NOT_SET = "not_set"
    LEFT = "left"
    MIDDLE_LEFT = "middle_left"
    MIDDLE = "middle"
    MIDDLE_RIGHT = "middle_right"
    RIGHT = "right"
    SWING = "swing"

# Define request and response models
class AirPumpRequest(BaseModel):
    temperature: int = Field(..., ge=16, le=31, description="Temperature setting (16-31°C)")
    fan_speed: FanSpeedEnum = Field(FanSpeedEnum.AUTO, description="Fan speed setting")
    vertical_mode: VerticalModeEnum = Field(VerticalModeEnum.MIDDLE, description="Vertical vane position")
    horizontal_mode: HorizontalModeEnum = Field(HorizontalModeEnum.MIDDLE, description="Horizontal vane position")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 16 or v > 31:
            raise ValueError('Temperature must be between 16 and 31')
        return v

class AirPumpState(BaseModel):
    power: bool = Field(False, description="Power state (on/off)")
    mode: Optional[str] = Field(None, description="Current mode (cool/heat/off)")
    temperature: Optional[int] = Field(None, description="Temperature setting (16-31°C)")
    fan_speed: Optional[FanSpeedEnum] = Field(None, description="Fan speed setting")
    vertical_mode: Optional[VerticalModeEnum] = Field(None, description="Vertical vane position")
    horizontal_mode: Optional[HorizontalModeEnum] = Field(None, description="Horizontal vane position")
    last_updated: Optional[str] = Field(None, description="Last updated timestamp")

class ApiResponse(BaseModel):
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Map enum values to IR sender constants
FAN_SPEED_MAP = {
    FanSpeedEnum.LOW: FanMode.Speed1,
    FanSpeedEnum.MED: FanMode.Speed2,
    FanSpeedEnum.HIGH: FanMode.Speed3,
    FanSpeedEnum.AUTO: FanMode.Auto
}

VERTICAL_MODE_MAP = {
    VerticalModeEnum.AUTO: VanneVerticalMode.Auto,
    VerticalModeEnum.TOP: VanneVerticalMode.Top,
    VerticalModeEnum.MIDDLE_TOP: VanneVerticalMode.MiddleTop,
    VerticalModeEnum.MIDDLE: VanneVerticalMode.Middle,
    VerticalModeEnum.MIDDLE_BOTTOM: VanneVerticalMode.MiddleBottom,
    VerticalModeEnum.BOTTOM: VanneVerticalMode.Bottom,
    VerticalModeEnum.SWING: VanneVerticalMode.Swing
}

HORIZONTAL_MODE_MAP = {
    HorizontalModeEnum.NOT_SET: VanneHorizontalMode.NotSet,
    HorizontalModeEnum.LEFT: VanneHorizontalMode.Left,
    HorizontalModeEnum.MIDDLE_LEFT: VanneHorizontalMode.MiddleLeft,
    HorizontalModeEnum.MIDDLE: VanneHorizontalMode.Middle,
    HorizontalModeEnum.MIDDLE_RIGHT: VanneHorizontalMode.MiddleRight,
    HorizontalModeEnum.RIGHT: VanneHorizontalMode.Right,
    HorizontalModeEnum.SWING: VanneHorizontalMode.Swing
}

# Initialize Air Pump Controller as dependency
class AirPumpController:
    def __init__(self):
        self.gpio_pin = config['gpio']['pin']
        self.controller = Mitsubishi(self.gpio_pin, LogLevel.ErrorsOnly)
        # Initialize state tracking
        self._state = AirPumpState()
        from datetime import datetime
        self._state.last_updated = datetime.now().isoformat()
    
    def turn_off(self) -> None:
        self.controller.power_off()
        # Update state
        self._state.power = False
        self._state.mode = "off"
        from datetime import datetime
        self._state.last_updated = datetime.now().isoformat()
    
    def send_command(self, climate_mode, request: AirPumpRequest) -> None:
        self.controller.send_command(
            climate_mode=climate_mode,
            temperature=request.temperature,
            fan_mode=FAN_SPEED_MAP[request.fan_speed],
            vanne_vertical_mode=VERTICAL_MODE_MAP[request.vertical_mode],
            vanne_horizontal_mode=HORIZONTAL_MODE_MAP[request.horizontal_mode],
            isee_mode=ISeeMode.ISeeOff,
            area_mode=AreaMode.Full,
            powerful=PowerfulMode.PowerfulOff
        )
        
        # Update state after sending command
        self._state.power = True
        self._state.mode = "cool" if climate_mode == ClimateMode.Cold else "heat"
        self._state.temperature = request.temperature
        self._state.fan_speed = request.fan_speed
        self._state.vertical_mode = request.vertical_mode
        self._state.horizontal_mode = request.horizontal_mode
        from datetime import datetime
        self._state.last_updated = datetime.now().isoformat()
    
    def get_state(self) -> AirPumpState:
        return self._state

# Singleton instance of the controller to maintain state across requests
_controller_instance = None

# Dependency for AirPumpController
def get_controller():
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = AirPumpController()
    return _controller_instance

# Set up lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting Mitsubishi ILP IR Control API...")
    yield
    # Shutdown logic
    print("Shutting down Mitsubishi ILP IR Control API...")

# Create FastAPI app
app = FastAPI(
    title="Mitsubishi ILP IR Control API",
    description="Control your Mitsubishi HVAC system via IR signals",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_config = config.get("cors", {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", ["*"]),
    allow_origin_regex=cors_config.get("allow_origin_regex", None),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
    allow_credentials=True,
)

# Get path to the React build folder
UI_BUILD_DIR = os.path.join(os.path.dirname(__file__), "react_ui", "build")

# Mount the 'build' folder at the UI path
app.mount("/ui", StaticFiles(directory=UI_BUILD_DIR, html=True), name="static")

# Root endpoint
@app.get("/", response_model=ApiResponse, tags=["General"])
async def read_root():
    """Root endpoint with API information."""
    return ApiResponse(
        status="success",
        message="Mitsubishi ILP IR Control API",
        details={"docs_url": "/docs", "ui_url": "/ui"}
    )

# Endpoint to turn off the air pump
@app.post("/air_pump/off/", response_model=ApiResponse, tags=["Air Pump Control"])
async def turn_off_air_pump(controller: AirPumpController = Depends(get_controller)):
    """Turn off the air pump."""
    try:
        controller.turn_off()
        return ApiResponse(status="success", message="Air pump turned off")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to turn off air pump: {str(e)}")

# Endpoint for cooling
@app.post("/air_pump/cool/", response_model=ApiResponse, tags=["Air Pump Control"])
async def cool_air_pump(
    request: AirPumpRequest, 
    controller: AirPumpController = Depends(get_controller)
):
    """Send cooling command to the air pump."""
    try:
        controller.send_command(ClimateMode.Cold, request)
        return ApiResponse(
            status="success", 
            message="Cooling command sent",
            details={
                "mode": "cool",
                "settings": request.dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send cooling command: {str(e)}")

# Endpoint for heating
@app.post("/air_pump/heat/", response_model=ApiResponse, tags=["Air Pump Control"])
async def heat_air_pump(
    request: AirPumpRequest, 
    controller: AirPumpController = Depends(get_controller)
):
    """Send heating command to the air pump."""
    try:
        controller.send_command(ClimateMode.Hot, request)
        return ApiResponse(
            status="success", 
            message="Heating command sent",
            details={
                "mode": "heat",
                "settings": request.dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send heating command: {str(e)}")

# Endpoint to get the current state of the air pump
@app.get("/air_pump/state/", response_model=ApiResponse, tags=["Air Pump Control"])
async def get_air_pump_state(controller: AirPumpController = Depends(get_controller)):
    """Get the current state of the air pump."""
    try:
        state = controller.get_state()
        return ApiResponse(
            status="success", 
            message="Current air pump state retrieved",
            details=state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get air pump state: {str(e)}")

# Health check endpoint
@app.get("/health", response_model=ApiResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return ApiResponse(status="healthy")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
