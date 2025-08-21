"""
Bluetooth scanner for discovering Sphero BOLT+ robots.
"""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncGenerator, Callable

import bleak
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from .exceptions import BluetoothError, RobotNotFoundError
from .types import RobotInfo, RobotModel

logger = logging.getLogger(__name__)


class SpheroScanner:
    """Scanner for discovering Sphero BOLT+ robots via Bluetooth."""
    
    # Known Sphero device name patterns
    SPHERO_PATTERNS = {
        "SB-": RobotModel.BOLT,
        "SB+": RobotModel.BOLT_PLUS,
        "RVR": RobotModel.RVR,
        "SM-": RobotModel.MINI,
        "SK-": RobotModel.SPARK,
    }
    
    def __init__(self, scan_timeout: float = 10.0) -> None:
        """
        Initialize the scanner.
        
        Args:
            scan_timeout: Timeout for scanning operations in seconds
        """
        self.scan_timeout = scan_timeout
        self._scanner: BleakScanner | None = None
    
    async def scan_for_robots(
        self,
        model_filter: RobotModel | None = None,
        name_filter: str | None = None,
    ) -> list[RobotInfo]:
        """
        Scan for available Sphero robots.
        
        Args:
            model_filter: Filter by specific robot model
            name_filter: Filter by robot name (partial match)
            
        Returns:
            List of discovered robots
            
        Raises:
            BluetoothError: If Bluetooth scanning fails
            RobotNotFoundError: If no robots are found
        """
        try:
            devices = await BleakScanner.discover(timeout=self.scan_timeout)
            robots = []
            
            for device in devices:
                if not device.name:
                    continue
                
                robot_model = self._detect_robot_model(device.name)
                if robot_model is None:
                    continue
                
                # Apply filters
                if model_filter and robot_model != model_filter:
                    continue
                    
                if name_filter and name_filter.lower() not in device.name.lower():
                    continue
                
                robot_info = RobotInfo(
                    name=device.name,
                    address=device.address,
                    model=robot_model,
                    rssi=device.rssi,
                )
                robots.append(robot_info)
                logger.info(f"Found robot: {robot_info}")
            
            if not robots:
                raise RobotNotFoundError("No Sphero robots found")
            
            # Sort by signal strength (higher RSSI = closer)
            robots.sort(key=lambda r: r.rssi or -1000, reverse=True)
            return robots
            
        except bleak.BleakError as e:
            logger.error(f"Bluetooth scan failed: {e}")
            raise BluetoothError(f"Failed to scan for robots: {e}") from e
    
    async def scan_continuously(
        self,
        callback: Callable[[RobotInfo], None],
        model_filter: RobotModel | None = None,
        name_filter: str | None = None,
    ) -> None:
        """
        Continuously scan for robots and call callback for each discovery.
        
        Args:
            callback: Function to call when a robot is discovered
            model_filter: Filter by specific robot model
            name_filter: Filter by robot name (partial match)
            
        Raises:
            BluetoothError: If Bluetooth scanning fails
        """
        def detection_callback(device: BLEDevice, advertisement_data) -> None:
            if not device.name:
                return
            
            robot_model = self._detect_robot_model(device.name)
            if robot_model is None:
                return
            
            # Apply filters
            if model_filter and robot_model != model_filter:
                return
                
            if name_filter and name_filter.lower() not in device.name.lower():
                return
            
            robot_info = RobotInfo(
                name=device.name,
                address=device.address,
                model=robot_model,
                rssi=device.rssi,
            )
            callback(robot_info)
        
        try:
            self._scanner = BleakScanner(detection_callback=detection_callback)
            await self._scanner.start()
            logger.info("Started continuous scanning for robots")
            
        except bleak.BleakError as e:
            logger.error(f"Continuous scan failed: {e}")
            raise BluetoothError(f"Failed to start continuous scan: {e}") from e
    
    async def stop_scanning(self) -> None:
        """Stop continuous scanning."""
        if self._scanner:
            await self._scanner.stop()
            self._scanner = None
            logger.info("Stopped continuous scanning")
    
    async def find_robot_by_name(
        self,
        name: str,
        timeout: float | None = None,
    ) -> RobotInfo:
        """
        Find a specific robot by name.
        
        Args:
            name: Exact robot name to find
            timeout: Search timeout (uses default if None)
            
        Returns:
            Information about the found robot
            
        Raises:
            RobotNotFoundError: If robot is not found
            BluetoothError: If scanning fails
        """
        scan_timeout = timeout or self.scan_timeout
        original_timeout = self.scan_timeout
        
        try:
            self.scan_timeout = scan_timeout
            robots = await self.scan_for_robots(name_filter=name)
            
            # Look for exact match first
            for robot in robots:
                if robot.name == name:
                    return robot
            
            # If no exact match, look for partial match
            for robot in robots:
                if name.lower() in robot.name.lower():
                    return robot
            
            raise RobotNotFoundError(f"Robot '{name}' not found")
            
        finally:
            self.scan_timeout = original_timeout
    
    def _detect_robot_model(self, name: str) -> RobotModel | None:
        """
        Detect robot model from device name.
        
        Args:
            name: Bluetooth device name
            
        Returns:
            Robot model or None if not recognized
        """
        for pattern, model in self.SPHERO_PATTERNS.items():
            if pattern in name:
                return model
        return None
    
    async def __aenter__(self) -> SpheroScanner:
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop_scanning()