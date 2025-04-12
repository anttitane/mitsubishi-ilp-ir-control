import os
import glob
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TemperatureSensor:
    """Temperature sensor using DS1820 1-wire sensor"""
    
    def __init__(self, device_path, enabled=True, refresh_interval=60):
        """Initialize the temperature sensor
        
        Args:
            device_path (str): Path to the 1-wire device
            enabled (bool): Whether to enable temperature reading
            refresh_interval (int): How often to refresh the temperature data in seconds
                                   (0 means read on each request)
        """
        self.device_path = device_path
        self.enabled = enabled
        self.refresh_interval = refresh_interval
        self.last_reading = None
        self.last_reading_time = None
        
        if self.enabled:
            self._load_kernel_modules()
    
    def _load_kernel_modules(self):
        """Load required kernel modules for 1-wire temperature sensors"""
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            logger.info("1-wire kernel modules loaded")
        except Exception as e:
            logger.error(f"Failed to load 1-wire kernel modules: {str(e)}")
    
    def read_temperature(self, force=False):
        """Read temperature from the sensor
        
        Args:
            force (bool): Force a new reading even if cache is available
            
        Returns:
            float: Temperature in Celsius or None if reading fails
        """
        if not self.enabled:
            logger.info("Temperature sensor is disabled")
            return None
        
        # Return cached reading if available and not expired
        if not force and self.last_reading is not None and self.refresh_interval > 0:
            time_since_last_reading = (datetime.now() - self.last_reading_time).total_seconds()
            if time_since_last_reading < self.refresh_interval:
                logger.debug(f"Returning cached temperature: {self.last_reading}°C")
                return self.last_reading
        
        # Get a new reading
        try:
            # Find device file
            device_file = f"{self.device_path}/w1_slave"
            
            # Read raw data from the sensor
            with open(device_file, 'r') as f:
                lines = f.readlines()
            
            # Parse the temperature
            if "YES" in lines[0]:  # CRC check passed
                temp_pos = lines[1].find('t=')
                if temp_pos != -1:
                    temp_string = lines[1][temp_pos + 2:]
                    temp_c = float(temp_string) / 1000.0
                    
                    # Cache the reading
                    self.last_reading = temp_c
                    self.last_reading_time = datetime.now()
                    
                    logger.debug(f"Temperature reading: {temp_c}°C")
                    return temp_c
            
            logger.warning("Invalid temperature reading")
            return None
            
        except FileNotFoundError:
            logger.error(f"Temperature sensor not found at: {self.device_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading temperature: {str(e)}")
            return None
