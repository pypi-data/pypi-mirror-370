"""
Basic movement example for Sphero BOLT+ robots.

This example demonstrates:
- Scanning for robots
- Connecting to a robot
- Basic movement commands
- LED control
"""

import asyncio
import logging
from sphero_bolt_plus import SpheroScanner, SpheroBot, Colors

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating basic robot control."""
    
    logger.info("Starting Sphero BOLT+ basic movement demo")
    
    # Step 1: Scan for available robots
    logger.info("Scanning for Sphero robots...")
    async with SpheroScanner(scan_timeout=10.0) as scanner:
        robots = await scanner.scan_for_robots()
        
        if not robots:
            logger.error("No robots found! Make sure your robot is on and nearby.")
            return
        
        logger.info(f"Found {len(robots)} robot(s):")
        for i, robot in enumerate(robots):
            logger.info(f"  {i+1}. {robot.name} ({robot.model.value}) - RSSI: {robot.rssi}")
    
    # Step 2: Connect to the first robot
    selected_robot = robots[0]
    logger.info(f"Connecting to {selected_robot.name}...")
    
    async with SpheroBot(selected_robot) as robot:
        logger.info("Connected successfully!")
        
        # Step 3: Initialize - flash green to show we're connected
        await robot.set_main_led(Colors.GREEN)
        await asyncio.sleep(0.5)
        await robot.set_main_led(Colors.WHITE)
        
        # Step 4: Basic movements
        logger.info("Starting movement sequence...")
        
        # Move forward (north) for 2 seconds
        logger.info("Moving forward...")
        await robot.set_main_led(Colors.BLUE)
        await robot.roll(speed=80, heading=0, duration=2.0)
        
        # Turn right and move
        logger.info("Turning right...")
        await robot.set_main_led(Colors.YELLOW)
        await robot.roll(speed=80, heading=90, duration=2.0)
        
        # Turn around and move back
        logger.info("Turning around...")
        await robot.set_main_led(Colors.RED)
        await robot.roll(speed=80, heading=180, duration=2.0)
        
        # Turn left and return to start
        logger.info("Returning to start...")
        await robot.set_main_led(Colors.CYAN)
        await robot.roll(speed=80, heading=270, duration=2.0)
        
        # Stop and spin
        logger.info("Stopping and spinning...")
        await robot.stop()
        await robot.set_main_led(Colors.PURPLE)
        await robot.spin(360, duration=3.0)
        
        # Final stop
        await robot.stop()
        await robot.set_main_led(Colors.GREEN)
        logger.info("Demo completed!")
        
        await asyncio.sleep(1.0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise