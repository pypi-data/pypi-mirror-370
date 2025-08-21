"""
Main robot control class for Sphero BOLT+ robots.
"""

from __future__ import annotations

import asyncio
import logging
import struct
import time
from typing import Callable, Any

import bleak
from bleak import BleakClient

from .exceptions import (
    ConnectionError,
    CommandError,
    SensorError,
    InvalidParameterError,
    CalibrationError,
    RobotBusyError,
)
from .types import (
    Color,
    Colors,
    ColorType,
    ConnectionState,
    RobotModel,
    RobotInfo,
    AccelerometerReading,
    GyroscopeReading,
    CompassReading,
    LocationReading,
    VelocityReading,
    BatteryReading,
    SensorReadingType,
)

logger = logging.getLogger(__name__)


class SpheroBot:
    """Main class for controlling Sphero BOLT+ robots."""
    
    # Bluetooth service UUIDs
    NORDIC_UART_SERVICE = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
    NORDIC_TX_CHAR = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    NORDIC_RX_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
    
    # Command constants
    COMMAND_START_BYTE = 0x8D
    ESCAPE_BYTE = 0xAB
    ESCAPE_ESCAPED = 0x23
    START_OF_PACKET_ESCAPED = 0x05
    END_OF_PACKET_ESCAPED = 0x50
    
    def __init__(
        self,
        robot_info: RobotInfo,
        connection_timeout: float = 10.0,
        command_timeout: float = 5.0,
    ) -> None:
        """
        Initialize robot controller.
        
        Args:
            robot_info: Information about the robot to connect to
            connection_timeout: Bluetooth connection timeout in seconds
            command_timeout: Command execution timeout in seconds
        """
        self.robot_info = robot_info
        self.connection_timeout = connection_timeout
        self.command_timeout = command_timeout
        
        self._client: BleakClient | None = None
        self._connection_state = ConnectionState.DISCONNECTED
        self._sequence_number = 0
        self._response_queue: asyncio.Queue = asyncio.Queue()
        self._sensor_callbacks: dict[str, Callable[[SensorReadingType], None]] = {}
        self._is_busy = False
        
        # Robot state
        self._stabilization_enabled = True
        self._current_heading = 0.0
        self._current_speed = 0
        self._current_color = Colors.WHITE
    
    @property
    def connection_state(self) -> ConnectionState:
        """Get current connection state."""
        return self._connection_state
    
    @property
    def is_connected(self) -> bool:
        """Check if robot is connected."""
        return self._connection_state == ConnectionState.CONNECTED
    
    @property
    def is_busy(self) -> bool:
        """Check if robot is busy executing a command."""
        return self._is_busy
    
    async def connect(self) -> None:
        """
        Connect to the robot via Bluetooth.
        
        Raises:
            ConnectionError: If connection fails
        """
        if self._connection_state == ConnectionState.CONNECTED:
            return
        
        logger.info(f"Connecting to {self.robot_info.name} at {self.robot_info.address}")
        self._connection_state = ConnectionState.CONNECTING
        
        try:
            self._client = BleakClient(
                self.robot_info.address,
                timeout=self.connection_timeout,
            )
            await self._client.connect()
            
            # Enable notifications
            await self._client.start_notify(
                self.NORDIC_RX_CHAR,
                self._notification_handler,
            )
            
            self._connection_state = ConnectionState.CONNECTED
            logger.info(f"Connected to {self.robot_info.name}")
            
            # Initialize robot
            await self._initialize_robot()
            
        except Exception as e:
            self._connection_state = ConnectionState.ERROR
            logger.error(f"Failed to connect to {self.robot_info.name}: {e}")
            raise ConnectionError(f"Failed to connect to robot: {e}") from e
    
    async def disconnect(self) -> None:
        """
        Disconnect from the robot.
        
        Raises:
            ConnectionError: If disconnection fails
        """
        if self._connection_state == ConnectionState.DISCONNECTED:
            return
        
        logger.info(f"Disconnecting from {self.robot_info.name}")
        self._connection_state = ConnectionState.DISCONNECTING
        
        try:
            if self._client and self._client.is_connected:
                await self._client.disconnect()
            
            self._connection_state = ConnectionState.DISCONNECTED
            self._client = None
            logger.info(f"Disconnected from {self.robot_info.name}")
            
        except Exception as e:
            self._connection_state = ConnectionState.ERROR
            logger.error(f"Failed to disconnect from {self.robot_info.name}: {e}")
            raise ConnectionError(f"Failed to disconnect from robot: {e}") from e
    
    async def roll(
        self,
        speed: int,
        heading: int,
        duration: float | None = None,
    ) -> None:
        """
        Make the robot roll at a specified speed and heading.
        
        Args:
            speed: Speed from 0-255
            heading: Heading in degrees (0-359)
            duration: Optional duration in seconds
            
        Raises:
            InvalidParameterError: If parameters are invalid
            CommandError: If command fails
        """
        if not 0 <= speed <= 255:
            raise InvalidParameterError(f"Speed must be 0-255, got {speed}")
        
        heading = heading % 360
        
        await self._send_command("roll", {"speed": speed, "heading": heading})
        
        self._current_speed = speed
        self._current_heading = heading
        
        if duration:
            await asyncio.sleep(duration)
            await self.stop()
    
    async def stop(self) -> None:
        """
        Stop the robot movement.
        
        Raises:
            CommandError: If command fails
        """
        await self.roll(0, self._current_heading)
    
    async def spin(self, angle: int, duration: float = 1.0) -> None:
        """
        Spin the robot by a specified angle.
        
        Args:
            angle: Angle to spin in degrees (positive = clockwise)
            duration: Duration of the spin in seconds
            
        Raises:
            CommandError: If command fails
        """
        await self._send_command("spin", {"angle": angle, "duration": duration})
        await asyncio.sleep(duration)
    
    async def set_main_led(self, color: ColorType) -> None:
        """
        Set the main LED color.
        
        Args:
            color: Color to set (Color object, RGB tuple, or hex string)
            
        Raises:
            CommandError: If command fails
        """
        color_obj = self._parse_color(color)
        await self._send_command("set_main_led", {
            "red": color_obj.red,
            "green": color_obj.green,
            "blue": color_obj.blue,
        })
        self._current_color = color_obj
    
    async def set_back_led(self, brightness: int) -> None:
        """
        Set the back LED brightness.
        
        Args:
            brightness: Brightness from 0-255
            
        Raises:
            InvalidParameterError: If brightness is invalid
            CommandError: If command fails
        """
        if not 0 <= brightness <= 255:
            raise InvalidParameterError(f"Brightness must be 0-255, got {brightness}")
        
        await self._send_command("set_back_led", {"brightness": brightness})
    
    async def set_front_led(self, color: ColorType) -> None:
        """
        Set the front LED color (BOLT+ only).
        
        Args:
            color: Color to set
            
        Raises:
            CommandError: If command fails or robot doesn't support front LED
        """
        if self.robot_info.model not in [RobotModel.BOLT, RobotModel.BOLT_PLUS]:
            raise CommandError("Front LED not supported on this robot model")
        
        color_obj = self._parse_color(color)
        await self._send_command("set_front_led", {
            "red": color_obj.red,
            "green": color_obj.green,
            "blue": color_obj.blue,
        })
    
    async def set_matrix_pixel(self, x: int, y: int, color: ColorType) -> None:
        """
        Set a single pixel on the LED matrix (BOLT/BOLT+ only).
        
        Args:
            x: X coordinate (0-7)
            y: Y coordinate (0-7)
            color: Color to set
            
        Raises:
            InvalidParameterError: If coordinates are invalid
            CommandError: If command fails or robot doesn't support matrix
        """
        if self.robot_info.model not in [RobotModel.BOLT, RobotModel.BOLT_PLUS]:
            raise CommandError("LED matrix not supported on this robot model")
        
        if not (0 <= x <= 7 and 0 <= y <= 7):
            raise InvalidParameterError(f"Matrix coordinates must be 0-7, got ({x}, {y})")
        
        color_obj = self._parse_color(color)
        await self._send_command("set_matrix_pixel", {
            "x": x,
            "y": y,
            "red": color_obj.red,
            "green": color_obj.green,
            "blue": color_obj.blue,
        })
    
    async def clear_matrix(self) -> None:
        """
        Clear the LED matrix (BOLT/BOLT+ only).
        
        Raises:
            CommandError: If command fails or robot doesn't support matrix
        """
        if self.robot_info.model not in [RobotModel.BOLT, RobotModel.BOLT_PLUS]:
            raise CommandError("LED matrix not supported on this robot model")
        
        await self._send_command("clear_matrix", {})
    
    async def scroll_matrix_text(
        self,
        text: str,
        color: ColorType = Colors.WHITE,
        speed: int = 5,
    ) -> None:
        """
        Scroll text on the LED matrix (BOLT/BOLT+ only).
        
        Args:
            text: Text to display
            color: Text color
            speed: Scroll speed (1-10, higher = faster)
            
        Raises:
            InvalidParameterError: If parameters are invalid
            CommandError: If command fails or robot doesn't support matrix
        """
        if self.robot_info.model not in [RobotModel.BOLT, RobotModel.BOLT_PLUS]:
            raise CommandError("LED matrix not supported on this robot model")
        
        if not 1 <= speed <= 10:
            raise InvalidParameterError(f"Speed must be 1-10, got {speed}")
        
        color_obj = self._parse_color(color)
        await self._send_command("scroll_matrix_text", {
            "text": text,
            "red": color_obj.red,
            "green": color_obj.green,
            "blue": color_obj.blue,
            "speed": speed,
        })
    
    async def set_stabilization(self, enabled: bool) -> None:
        """
        Enable or disable robot stabilization.
        
        Args:
            enabled: Whether to enable stabilization
            
        Raises:
            CommandError: If command fails
        """
        await self._send_command("set_stabilization", {"enabled": enabled})
        self._stabilization_enabled = enabled
    
    async def calibrate_compass(self) -> None:
        """
        Calibrate the robot's compass.
        
        Raises:
            CalibrationError: If calibration fails
            CommandError: If command fails
        """
        try:
            await self._send_command("calibrate_compass", {})
            logger.info("Compass calibration completed")
        except CommandError as e:
            raise CalibrationError(f"Compass calibration failed: {e}") from e
    
    async def get_accelerometer(self) -> AccelerometerReading:
        """
        Get accelerometer reading.
        
        Returns:
            Current accelerometer reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_accelerometer", {})
            return AccelerometerReading(
                timestamp=time.time(),
                x=response["x"],
                y=response["y"],
                z=response["z"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read accelerometer: {e}", "accelerometer") from e
    
    async def get_gyroscope(self) -> GyroscopeReading:
        """
        Get gyroscope reading.
        
        Returns:
            Current gyroscope reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_gyroscope", {})
            return GyroscopeReading(
                timestamp=time.time(),
                x=response["x"],
                y=response["y"],
                z=response["z"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read gyroscope: {e}", "gyroscope") from e
    
    async def get_compass(self) -> CompassReading:
        """
        Get compass heading.
        
        Returns:
            Current compass reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_compass", {})
            return CompassReading(
                timestamp=time.time(),
                heading=response["heading"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read compass: {e}", "compass") from e
    
    async def get_location(self) -> LocationReading:
        """
        Get robot location.
        
        Returns:
            Current location reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_location", {})
            return LocationReading(
                timestamp=time.time(),
                x=response["x"],
                y=response["y"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read location: {e}", "location") from e
    
    async def get_velocity(self) -> VelocityReading:
        """
        Get robot velocity.
        
        Returns:
            Current velocity reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_velocity", {})
            return VelocityReading(
                timestamp=time.time(),
                x=response["x"],
                y=response["y"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read velocity: {e}", "velocity") from e
    
    async def get_battery(self) -> BatteryReading:
        """
        Get battery status.
        
        Returns:
            Current battery reading
            
        Raises:
            SensorError: If reading fails
        """
        try:
            response = await self._send_command("get_battery", {})
            return BatteryReading(
                timestamp=time.time(),
                percentage=response["percentage"],
                voltage=response["voltage"],
            )
        except CommandError as e:
            raise SensorError(f"Failed to read battery: {e}", "battery") from e
    
    def register_sensor_callback(
        self,
        sensor_type: str,
        callback: Callable[[SensorReadingType], None],
    ) -> None:
        """
        Register a callback for sensor data updates.
        
        Args:
            sensor_type: Type of sensor ("accelerometer", "gyroscope", etc.)
            callback: Function to call with sensor readings
        """
        self._sensor_callbacks[sensor_type] = callback
    
    def unregister_sensor_callback(self, sensor_type: str) -> None:
        """
        Unregister a sensor callback.
        
        Args:
            sensor_type: Type of sensor to unregister
        """
        self._sensor_callbacks.pop(sensor_type, None)
    
    async def _initialize_robot(self) -> None:
        """Initialize robot after connection."""
        logger.info("Initializing robot")
        # Add any initialization commands here
        await self.set_stabilization(True)
        await self.set_main_led(Colors.GREEN)
        await asyncio.sleep(0.5)
        await self.set_main_led(Colors.WHITE)
    
    async def _send_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Send a command to the robot.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            Command response
            
        Raises:
            ConnectionError: If not connected
            RobotBusyError: If robot is busy
            CommandError: If command fails
        """
        if not self.is_connected or not self._client:
            raise ConnectionError("Robot not connected")
        
        if self._is_busy:
            raise RobotBusyError("Robot is busy executing another command")
        
        self._is_busy = True
        
        try:
            # Build command packet
            packet = self._build_command_packet(command, params)
            
            # Send command
            await self._client.write_gatt_char(self.NORDIC_TX_CHAR, packet)
            
            # Wait for response
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=self.command_timeout,
            )
            
            if response.get("error"):
                raise CommandError(f"Command failed: {response['error']}", command)
            
            return response
            
        except asyncio.TimeoutError:
            raise CommandError(f"Command timeout: {command}", command)
        
        except Exception as e:
            raise CommandError(f"Command failed: {e}", command) from e
        
        finally:
            self._is_busy = False
    
    def _build_command_packet(self, command: str, params: dict[str, Any]) -> bytes:
        """Build a command packet for the robot."""
        # This is a simplified implementation
        # In a real implementation, you would need to follow the Sphero protocol
        self._sequence_number = (self._sequence_number + 1) % 256
        
        command_data = {
            "command": command,
            "params": params,
            "seq": self._sequence_number,
        }
        
        # Convert to JSON and encode
        import json
        json_data = json.dumps(command_data).encode("utf-8")
        
        # Add packet header and checksum (simplified)
        packet = struct.pack("!B", self.COMMAND_START_BYTE) + json_data
        return packet
    
    def _parse_color(self, color: ColorType) -> Color:
        """
        Parse various color formats into a Color object.
        
        Args:
            color: Color in various formats
            
        Returns:
            Color object
            
        Raises:
            InvalidParameterError: If color format is invalid
        """
        if isinstance(color, Color):
            return color
        
        if isinstance(color, (tuple, list)) and len(color) == 3:
            r, g, b = color
            if all(0 <= c <= 255 for c in [r, g, b]):
                return Color(int(r), int(g), int(b))
        
        if isinstance(color, str):
            try:
                return Color.from_hex(color)
            except ValueError:
                pass
        
        raise InvalidParameterError(f"Invalid color format: {color}")
    
    async def _notification_handler(self, sender, data: bytearray) -> None:
        """Handle notifications from the robot."""
        try:
            # Parse response data (simplified)
            import json
            response_str = data.decode("utf-8")
            response = json.loads(response_str)
            
            # Handle sensor data
            if response.get("type") == "sensor":
                await self._handle_sensor_data(response)
            else:
                # Queue command response
                await self._response_queue.put(response)
                
        except Exception as e:
            logger.error(f"Failed to handle notification: {e}")
    
    async def _handle_sensor_data(self, data: dict[str, Any]) -> None:
        """Handle incoming sensor data."""
        sensor_type = data.get("sensor")
        if sensor_type in self._sensor_callbacks:
            try:
                # Convert to appropriate sensor reading type
                reading = self._create_sensor_reading(sensor_type, data)
                if reading:
                    self._sensor_callbacks[sensor_type](reading)
            except Exception as e:
                logger.error(f"Error in sensor callback: {e}")
    
    def _create_sensor_reading(self, sensor_type: str, data: dict[str, Any]) -> SensorReadingType | None:
        """Create appropriate sensor reading object."""
        timestamp = time.time()
        
        if sensor_type == "accelerometer":
            return AccelerometerReading(timestamp, data["x"], data["y"], data["z"])
        elif sensor_type == "gyroscope":
            return GyroscopeReading(timestamp, data["x"], data["y"], data["z"])
        elif sensor_type == "compass":
            return CompassReading(timestamp, data["heading"])
        elif sensor_type == "location":
            return LocationReading(timestamp, data["x"], data["y"])
        elif sensor_type == "velocity":
            return VelocityReading(timestamp, data["x"], data["y"])
        elif sensor_type == "battery":
            return BatteryReading(timestamp, data["percentage"], data["voltage"])
        
        return None
    
    async def __aenter__(self) -> SpheroBot:
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()