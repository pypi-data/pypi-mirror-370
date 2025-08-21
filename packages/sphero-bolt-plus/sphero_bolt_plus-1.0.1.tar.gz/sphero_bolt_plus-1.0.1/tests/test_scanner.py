"""
Tests for SpheroScanner class.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bleak.backends.device import BLEDevice

from sphero_bolt_plus.scanner import SpheroScanner
from sphero_bolt_plus.types import RobotModel, RobotInfo
from sphero_bolt_plus.exceptions import BluetoothError, RobotNotFoundError


class TestSpheroScanner:
    """Test SpheroScanner functionality."""
    
    @pytest.fixture
    def scanner(self):
        """Create a SpheroScanner instance for testing."""
        return SpheroScanner(scan_timeout=5.0)
    
    @pytest.fixture
    def mock_ble_devices(self):
        """Create mock BLE devices for testing."""
        devices = []
        
        # BOLT+ device
        device1 = MagicMock(spec=BLEDevice)
        device1.name = "SB+-1234"
        device1.address = "AA:BB:CC:DD:EE:FF"
        device1.rssi = -45
        devices.append(device1)
        
        # BOLT device
        device2 = MagicMock(spec=BLEDevice)
        device2.name = "SB-5678"
        device2.address = "BB:CC:DD:EE:FF:AA"
        device2.rssi = -55
        devices.append(device2)
        
        # Non-Sphero device
        device3 = MagicMock(spec=BLEDevice)
        device3.name = "Other Device"
        device3.address = "CC:DD:EE:FF:AA:BB"
        device3.rssi = -65
        devices.append(device3)
        
        # Device without name
        device4 = MagicMock(spec=BLEDevice)
        device4.name = None
        device4.address = "DD:EE:FF:AA:BB:CC"
        device4.rssi = -75
        devices.append(device4)
        
        return devices
    
    def test_detect_robot_model(self, scanner):
        """Test robot model detection from device names."""
        assert scanner._detect_robot_model("SB+-1234") == RobotModel.BOLT_PLUS
        assert scanner._detect_robot_model("SB-5678") == RobotModel.BOLT
        assert scanner._detect_robot_model("RVR-9999") == RobotModel.RVR
        assert scanner._detect_robot_model("SM-1111") == RobotModel.MINI
        assert scanner._detect_robot_model("SK-2222") == RobotModel.SPARK
        assert scanner._detect_robot_model("Unknown Device") is None
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_scan_for_robots_success(self, mock_discover, scanner, mock_ble_devices):
        """Test successful robot scanning."""
        mock_discover.return_value = mock_ble_devices
        
        robots = await scanner.scan_for_robots()
        
        assert len(robots) == 2  # Only Sphero devices
        assert robots[0].name == "SB+-1234"  # Higher RSSI comes first
        assert robots[0].model == RobotModel.BOLT_PLUS
        assert robots[1].name == "SB-5678"
        assert robots[1].model == RobotModel.BOLT
        
        mock_discover.assert_called_once_with(timeout=5.0)
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_scan_for_robots_with_model_filter(self, mock_discover, scanner, mock_ble_devices):
        """Test scanning with model filter."""
        mock_discover.return_value = mock_ble_devices
        
        robots = await scanner.scan_for_robots(model_filter=RobotModel.BOLT_PLUS)
        
        assert len(robots) == 1
        assert robots[0].name == "SB+-1234"
        assert robots[0].model == RobotModel.BOLT_PLUS
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_scan_for_robots_with_name_filter(self, mock_discover, scanner, mock_ble_devices):
        """Test scanning with name filter."""
        mock_discover.return_value = mock_ble_devices
        
        robots = await scanner.scan_for_robots(name_filter="1234")
        
        assert len(robots) == 1
        assert robots[0].name == "SB+-1234"
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_scan_for_robots_no_robots_found(self, mock_discover, scanner):
        """Test scanning when no robots are found."""
        mock_discover.return_value = []
        
        with pytest.raises(RobotNotFoundError, match="No Sphero robots found"):
            await scanner.scan_for_robots()
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_scan_for_robots_bluetooth_error(self, mock_discover, scanner):
        """Test scanning with Bluetooth error."""
        from bleak import BleakError
        mock_discover.side_effect = BleakError("Bluetooth adapter not found")
        
        with pytest.raises(BluetoothError, match="Failed to scan for robots"):
            await scanner.scan_for_robots()
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_find_robot_by_name_success(self, mock_discover, scanner, mock_ble_devices):
        """Test finding robot by exact name."""
        mock_discover.return_value = mock_ble_devices
        
        robot = await scanner.find_robot_by_name("SB+-1234")
        
        assert robot.name == "SB+-1234"
        assert robot.model == RobotModel.BOLT_PLUS
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_find_robot_by_name_partial_match(self, mock_discover, scanner, mock_ble_devices):
        """Test finding robot by partial name match."""
        mock_discover.return_value = mock_ble_devices
        
        robot = await scanner.find_robot_by_name("1234")
        
        assert robot.name == "SB+-1234"
        assert robot.model == RobotModel.BOLT_PLUS
    
    @pytest.mark.asyncio
    @patch('sphero_bolt_plus.scanner.BleakScanner.discover')
    async def test_find_robot_by_name_not_found(self, mock_discover, scanner, mock_ble_devices):
        """Test finding robot that doesn't exist."""
        mock_discover.return_value = mock_ble_devices
        
        with pytest.raises(RobotNotFoundError, match="Robot 'NonExistent' not found"):
            await scanner.find_robot_by_name("NonExistent")
    
    @pytest.mark.asyncio
    async def test_continuous_scanning(self, scanner):
        """Test continuous scanning setup."""
        callback = MagicMock()
        
        with patch('sphero_bolt_plus.scanner.BleakScanner') as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance
            
            await scanner.scan_continuously(callback)
            
            mock_scanner_class.assert_called_once()
            mock_scanner_instance.start.assert_called_once()
            
            # Test stop scanning
            await scanner.stop_scanning()
            mock_scanner_instance.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, scanner):
        """Test using scanner as async context manager."""
        with patch.object(scanner, 'stop_scanning', new_callable=AsyncMock) as mock_stop:
            async with scanner as s:
                assert s is scanner
            
            mock_stop.assert_called_once()