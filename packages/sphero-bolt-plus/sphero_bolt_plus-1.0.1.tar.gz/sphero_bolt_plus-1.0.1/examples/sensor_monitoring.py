"""
Sensor monitoring example for Sphero BOLT+ robots.

This example demonstrates:
- Reading various sensor data
- Real-time sensor streaming
- Sensor calibration
- Data logging and analysis
"""

import asyncio
import logging
import time
from typing import Dict, List
from dataclasses import dataclass
from sphero_bolt_plus import (
    SpheroScanner,
    SpheroBot,
    Colors,
    AccelerometerReading,
    GyroscopeReading,
    CompassReading,
    BatteryReading,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SensorLog:
    """Data structure for sensor logging."""
    timestamp: float
    accelerometer: AccelerometerReading | None = None
    gyroscope: GyroscopeReading | None = None
    compass: CompassReading | None = None
    battery: BatteryReading | None = None


class SensorMonitor:
    """Class to handle sensor monitoring and logging."""
    
    def __init__(self):
        self.sensor_logs: List[SensorLog] = []
        self.monitoring = False
        
    def log_accelerometer(self, reading: AccelerometerReading):
        """Log accelerometer data."""
        logger.info(f"Accel: X={reading.x:.2f}, Y={reading.y:.2f}, Z={reading.z:.2f}")
        
        # Detect significant movement
        magnitude = (reading.x**2 + reading.y**2 + reading.z**2)**0.5
        if magnitude > 2.0:  # Threshold for "significant" movement
            logger.warning(f"High acceleration detected! Magnitude: {magnitude:.2f}")
    
    def log_gyroscope(self, reading: GyroscopeReading):
        """Log gyroscope data."""
        logger.info(f"Gyro: X={reading.x:.2f}, Y={reading.y:.2f}, Z={reading.z:.2f}")
        
        # Detect spinning
        spin_rate = (reading.x**2 + reading.y**2 + reading.z**2)**0.5
        if spin_rate > 100:  # Threshold for spinning
            logger.warning(f"Fast rotation detected! Rate: {spin_rate:.2f}")
    
    def log_compass(self, reading: CompassReading):
        """Log compass data."""
        logger.info(f"Compass: {reading.heading:.1f}°")
    
    def log_battery(self, reading: BatteryReading):
        """Log battery data."""
        logger.info(f"Battery: {reading.percentage}% ({reading.voltage:.2f}V)")
        
        if reading.percentage < 20:
            logger.warning("Low battery! Please charge your robot.")


async def read_all_sensors(robot: SpheroBot) -> SensorLog:
    """Read all available sensors and create a sensor log entry."""
    timestamp = time.time()
    log = SensorLog(timestamp=timestamp)
    
    try:
        # Read all sensors concurrently
        tasks = [
            robot.get_accelerometer(),
            robot.get_gyroscope(), 
            robot.get_compass(),
            robot.get_battery(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to read sensor {i}: {result}")
                continue
                
            if i == 0:  # accelerometer
                log.accelerometer = result
            elif i == 1:  # gyroscope
                log.gyroscope = result
            elif i == 2:  # compass
                log.compass = result
            elif i == 3:  # battery
                log.battery = result
        
        return log
        
    except Exception as e:
        logger.error(f"Error reading sensors: {e}")
        return log


async def sensor_calibration_demo(robot: SpheroBot):
    """Demonstrate sensor calibration."""
    logger.info("Starting sensor calibration demo...")
    
    # Signal calibration start
    await robot.set_main_led(Colors.YELLOW)
    
    logger.info("Calibrating compass - keep robot stationary...")
    try:
        await robot.calibrate_compass()
        logger.info("Compass calibration completed!")
        await robot.set_main_led(Colors.GREEN)
    except Exception as e:
        logger.error(f"Compass calibration failed: {e}")
        await robot.set_main_led(Colors.RED)
    
    await asyncio.sleep(2.0)
    await robot.set_main_led(Colors.WHITE)


async def movement_tracking_demo(robot: SpheroBot):
    """Demonstrate tracking robot movement with sensors."""
    logger.info("Starting movement tracking demo...")
    
    monitor = SensorMonitor()
    
    # Set up sensor callbacks for real-time monitoring
    robot.register_sensor_callback("accelerometer", monitor.log_accelerometer)
    robot.register_sensor_callback("gyroscope", monitor.log_gyroscope)
    
    # Perform various movements while monitoring
    movements = [
        ("Moving forward", lambda: robot.roll(100, 0, duration=2.0)),
        ("Spinning right", lambda: robot.spin(180, duration=1.5)),
        ("Moving backward", lambda: robot.roll(100, 180, duration=2.0)),
        ("Spinning left", lambda: robot.spin(-180, duration=1.5)),
    ]
    
    for description, movement in movements:
        logger.info(f"Movement: {description}")
        await robot.set_main_led(Colors.BLUE)
        await movement()
        await robot.set_main_led(Colors.WHITE)
        await asyncio.sleep(1.0)
    
    # Stop monitoring
    robot.unregister_sensor_callback("accelerometer")
    robot.unregister_sensor_callback("gyroscope")
    
    await robot.stop()


async def sensor_logging_demo(robot: SpheroBot, duration: int = 10):
    """Log sensor data for a specified duration."""
    logger.info(f"Logging sensor data for {duration} seconds...")
    
    logs = []
    start_time = time.time()
    
    await robot.set_main_led(Colors.CYAN)
    
    while time.time() - start_time < duration:
        log = await read_all_sensors(robot)
        logs.append(log)
        
        # Print summary every 2 seconds
        if len(logs) % 4 == 0:  # Assuming ~2 readings per second
            logger.info(f"Logged {len(logs)} sensor readings...")
        
        await asyncio.sleep(0.5)  # Read sensors every 500ms
    
    await robot.set_main_led(Colors.WHITE)
    
    # Analyze logged data
    logger.info("Analyzing sensor data...")
    
    if logs:
        # Calculate averages
        accel_x_avg = sum(log.accelerometer.x for log in logs if log.accelerometer) / len(logs)
        accel_y_avg = sum(log.accelerometer.y for log in logs if log.accelerometer) / len(logs)
        accel_z_avg = sum(log.accelerometer.z for log in logs if log.accelerometer) / len(logs)
        
        compass_readings = [log.compass.heading for log in logs if log.compass]
        compass_avg = sum(compass_readings) / len(compass_readings) if compass_readings else 0
        
        battery_readings = [log.battery.percentage for log in logs if log.battery]
        battery_avg = sum(battery_readings) / len(battery_readings) if battery_readings else 0
        
        logger.info(f"Sensor Summary ({len(logs)} readings):")
        logger.info(f"  Average Acceleration: X={accel_x_avg:.2f}, Y={accel_y_avg:.2f}, Z={accel_z_avg:.2f}")
        logger.info(f"  Average Compass Heading: {compass_avg:.1f}°")
        logger.info(f"  Average Battery Level: {battery_avg:.1f}%")


async def main():
    """Main function demonstrating sensor monitoring."""
    
    logger.info("Starting Sphero BOLT+ sensor monitoring demo")
    
    # Scan for robots
    async with SpheroScanner() as scanner:
        robots = await scanner.scan_for_robots()
        
        if not robots:
            logger.error("No robots found!")
            return
        
        logger.info(f"Found {len(robots)} robot(s)")
    
    # Connect to first robot
    async with SpheroBot(robots[0]) as robot:
        logger.info(f"Connected to {robot.robot_info.name}")
        
        # Signal connection
        await robot.set_main_led(Colors.GREEN)
        await asyncio.sleep(1.0)
        
        # Run sensor demonstrations
        demos = [
            ("Sensor Calibration", sensor_calibration_demo),
            ("Single Sensor Reading", lambda r: read_all_sensors(r)),
            ("Movement Tracking", movement_tracking_demo),
            ("Data Logging", lambda r: sensor_logging_demo(r, duration=10)),
        ]
        
        for i, (name, demo) in enumerate(demos, 1):
            logger.info(f"Running demo {i}/{len(demos)}: {name}")
            
            try:
                result = await demo(robot)
                if result:  # For single sensor reading
                    logger.info("Single sensor reading completed")
                    
            except Exception as e:
                logger.error(f"Demo '{name}' failed: {e}")
            
            await asyncio.sleep(2.0)  # Pause between demos
        
        # Final signal
        await robot.set_main_led(Colors.GREEN)
        logger.info("Sensor monitoring demo completed!")
        
        await asyncio.sleep(2.0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise