"""
Tests for type definitions and color handling.
"""

import pytest
from sphero_bolt_plus.types import (
    Color,
    Colors,
    RobotModel,
    ConnectionState,
    RobotInfo,
    AccelerometerReading,
    GyroscopeReading,
    CompassReading,
    LocationReading,
    VelocityReading,
    BatteryReading,
)


class TestColor:
    """Test Color class functionality."""
    
    def test_color_creation(self):
        """Test creating Color objects."""
        color = Color(255, 128, 64)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
    
    def test_color_from_hex(self):
        """Test creating Color from hex string."""
        color = Color.from_hex("#FF8040")
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        
        color = Color.from_hex("FF8040")
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
    
    def test_color_from_hex_invalid(self):
        """Test invalid hex color formats."""
        with pytest.raises(ValueError):
            Color.from_hex("#FF80")  # Too short
        
        with pytest.raises(ValueError):
            Color.from_hex("#GGGGGG")  # Invalid hex chars
    
    def test_color_to_hex(self):
        """Test converting Color to hex string."""
        color = Color(255, 128, 64)
        assert color.to_hex() == "#ff8040"
    
    def test_color_str(self):
        """Test Color string representation."""
        color = Color(255, 128, 64)
        assert str(color) == "Color(r=255, g=128, b=64)"
    
    def test_predefined_colors(self):
        """Test predefined color constants."""
        assert Colors.RED == Color(255, 0, 0)
        assert Colors.GREEN == Color(0, 255, 0)
        assert Colors.BLUE == Color(0, 0, 255)
        assert Colors.WHITE == Color(255, 255, 255)
        assert Colors.BLACK == Color(0, 0, 0)


class TestEnums:
    """Test enum definitions."""
    
    def test_robot_model_enum(self):
        """Test RobotModel enum values."""
        assert RobotModel.BOLT.value == "bolt"
        assert RobotModel.BOLT_PLUS.value == "bolt_plus"
        assert RobotModel.RVR.value == "rvr"
        assert RobotModel.MINI.value == "mini"
        assert RobotModel.SPARK.value == "spark"
    
    def test_connection_state_enum(self):
        """Test ConnectionState enum values."""
        assert ConnectionState.DISCONNECTED.value == "disconnected"
        assert ConnectionState.CONNECTING.value == "connecting"
        assert ConnectionState.CONNECTED.value == "connected"
        assert ConnectionState.DISCONNECTING.value == "disconnecting"
        assert ConnectionState.ERROR.value == "error"


class TestDataClasses:
    """Test data class definitions."""
    
    def test_robot_info(self):
        """Test RobotInfo data class."""
        robot = RobotInfo(
            name="SB-1234",
            address="AA:BB:CC:DD:EE:FF",
            model=RobotModel.BOLT_PLUS,
            rssi=-45,
        )
        
        assert robot.name == "SB-1234"
        assert robot.address == "AA:BB:CC:DD:EE:FF"
        assert robot.model == RobotModel.BOLT_PLUS
        assert robot.rssi == -45
    
    def test_accelerometer_reading(self):
        """Test AccelerometerReading data class."""
        reading = AccelerometerReading(
            timestamp=1234567.0,
            x=0.1,
            y=0.2,
            z=0.9,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.x == 0.1
        assert reading.y == 0.2
        assert reading.z == 0.9
    
    def test_gyroscope_reading(self):
        """Test GyroscopeReading data class."""
        reading = GyroscopeReading(
            timestamp=1234567.0,
            x=10.0,
            y=20.0,
            z=30.0,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.x == 10.0
        assert reading.y == 20.0
        assert reading.z == 30.0
    
    def test_compass_reading(self):
        """Test CompassReading data class."""
        reading = CompassReading(
            timestamp=1234567.0,
            heading=90.0,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.heading == 90.0
    
    def test_location_reading(self):
        """Test LocationReading data class."""
        reading = LocationReading(
            timestamp=1234567.0,
            x=100.0,
            y=200.0,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.x == 100.0
        assert reading.y == 200.0
    
    def test_velocity_reading(self):
        """Test VelocityReading data class."""
        reading = VelocityReading(
            timestamp=1234567.0,
            x=10.5,
            y=20.5,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.x == 10.5
        assert reading.y == 20.5
    
    def test_battery_reading(self):
        """Test BatteryReading data class."""
        reading = BatteryReading(
            timestamp=1234567.0,
            percentage=75,
            voltage=7.4,
        )
        
        assert reading.timestamp == 1234567.0
        assert reading.percentage == 75
        assert reading.voltage == 7.4