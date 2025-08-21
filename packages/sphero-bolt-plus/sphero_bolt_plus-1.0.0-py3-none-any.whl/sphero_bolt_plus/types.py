"""
Type definitions and enums for Sphero BOLT+ library.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import NamedTuple, Union


class RobotModel(enum.Enum):
    """Supported Sphero robot models."""
    BOLT = "bolt"
    BOLT_PLUS = "bolt_plus"
    RVR = "rvr"
    MINI = "mini"
    SPARK = "spark"


class ConnectionState(enum.Enum):
    """Robot connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class Color(NamedTuple):
    """RGB color representation."""
    red: int
    green: int
    blue: int
    
    @classmethod
    def from_hex(cls, hex_color: str) -> Color:
        """Create color from hex string (e.g., '#FF0000' or 'FF0000')."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: {hex_color}")
        
        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16),
        )
    
    def to_hex(self) -> str:
        """Convert color to hex string."""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
    
    def __str__(self) -> str:
        return f"Color(r={self.red}, g={self.green}, b={self.blue})"


# Predefined colors
class Colors:
    """Common color definitions."""
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)
    ORANGE = Color(255, 165, 0)
    PURPLE = Color(128, 0, 128)
    PINK = Color(255, 192, 203)


@dataclass
class SensorReading:
    """Base class for sensor readings."""
    timestamp: float


@dataclass
class AccelerometerReading(SensorReading):
    """Accelerometer sensor reading."""
    x: float
    y: float
    z: float


@dataclass
class GyroscopeReading(SensorReading):
    """Gyroscope sensor reading."""
    x: float
    y: float
    z: float


@dataclass
class CompassReading(SensorReading):
    """Compass sensor reading."""
    heading: float


@dataclass
class LocationReading(SensorReading):
    """Location sensor reading."""
    x: float
    y: float


@dataclass
class VelocityReading(SensorReading):
    """Velocity sensor reading."""
    x: float
    y: float


@dataclass
class BatteryReading(SensorReading):
    """Battery sensor reading."""
    percentage: int
    voltage: float


@dataclass
class RobotInfo:
    """Information about a discovered robot."""
    name: str
    address: str
    model: RobotModel
    rssi: int | None = None


# Type aliases
ColorType = Union[Color, tuple[int, int, int], str]
SensorReadingType = Union[
    AccelerometerReading,
    GyroscopeReading,
    CompassReading,
    LocationReading,
    VelocityReading,
    BatteryReading,
]