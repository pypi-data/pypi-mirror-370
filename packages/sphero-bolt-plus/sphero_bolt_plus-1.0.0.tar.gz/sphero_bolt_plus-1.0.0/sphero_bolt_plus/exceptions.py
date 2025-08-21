"""
Exception classes for Sphero BOLT+ library.
"""

from __future__ import annotations


class SpheroError(Exception):
    """Base exception class for Sphero BOLT+ library."""
    pass


class ConnectionError(SpheroError):
    """Raised when robot connection fails or is lost."""
    pass


class CommandError(SpheroError):
    """Raised when a robot command fails."""
    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class SensorError(SpheroError):
    """Raised when sensor reading fails."""
    def __init__(self, message: str, sensor_type: str | None = None) -> None:
        super().__init__(message)
        self.sensor_type = sensor_type


class BluetoothError(SpheroError):
    """Raised when Bluetooth communication fails."""
    pass


class RobotNotFoundError(SpheroError):
    """Raised when no robot is found during scanning."""
    pass


class InvalidParameterError(SpheroError):
    """Raised when invalid parameters are passed to methods."""
    pass


class RobotBusyError(SpheroError):
    """Raised when robot is busy executing another command."""
    pass


class CalibrationError(SpheroError):
    """Raised when robot calibration fails."""
    pass