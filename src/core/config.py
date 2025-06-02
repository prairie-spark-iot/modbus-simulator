from datetime import datetime
from typing import Dict, Any, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base configuration
BASE_CONFIG = {
    "DEBUG": True,
    "MODBUS_HOST": "localhost",
    "MODBUS_PORT": 502,
    "WEB_PORT": 8000,
    "WS_PUSH_INTERVAL": 1.0,
    "MAX_RETRIES": 3,
    "HEARTBEAT_TIMEOUT": 30,
    "CACHE_TIMEOUT": 5,
    "READ_TIMEOUT": 1.0,  # Modbus read timeout in seconds
    "RETRY_INTERVAL": 2.0  # Retry interval in seconds
}

# Device configuration
DEVICES = {
    1: {"name": "Temperature and Humidity Sensor", "type": "sensor"},
    2: {"name": "Power Meter", "type": "meter"},
    3: {"name": "AC Controller", "type": "controller"},
    4: {"name": "Air Quality Sensor", "type": "sensor"},
    5: {"name": "PLC/IO Module", "type": "controller"},
    6: {"name": "Smart Light Controller", "type": "controller"},
    7: {"name": "Smart Plug", "type": "controller"}
}


class SharedState:
    """Shared state class for sharing state between application components"""

    def __init__(self):
        self.modbus_running = False
        self.web_running = False
        self.last_error: Optional[str] = None
        self.last_error_time: Optional[datetime] = None
        self._device_status: Dict[int, Dict[str, Any]] = {}

    def set_error(self, error: str) -> None:
        """Set error message"""
        self.last_error = error
        self.last_error_time = datetime.now()

    def clear_error(self) -> None:
        """Clear error message"""
        self.last_error = None
        self.last_error_time = None

    def update_device_status(self, device_id: int, status: Dict[str, Any]) -> None:
        """Update device status"""
        self._device_status[device_id] = status

    def get_device_status(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get device status"""
        return self._device_status.get(device_id)

    def get_all_device_status(self) -> Dict[int, Dict[str, Any]]:
        """Get all device status"""
        return self._device_status.copy()


# Create shared state instance
shared_state = SharedState()
