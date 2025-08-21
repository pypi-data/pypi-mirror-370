"""
Sphero BOLT+ Python Library

A modern Python library for controlling Sphero BOLT+ robots with enhanced features,
improved async support, and full type annotations.
"""

__version__ = "1.0.1"
__author__ = "Assistant"
__email__ = "assistant@example.com"

from .robot import SpheroBot
from .scanner import SpheroScanner
from .types import Color, Colors, RobotModel, ConnectionState
from .exceptions import (
    SpheroError,
    ConnectionError,
    CommandError,
    SensorError,
    BluetoothError,
)

__all__ = [
    "SpheroBot",
    "SpheroScanner", 
    "Color",
    "Colors",
    "RobotModel",
    "ConnectionState",
    "SpheroError",
    "ConnectionError", 
    "CommandError",
    "SensorError",
    "BluetoothError",
]