"""
LED matrix demonstration for Sphero BOLT+ robots.

This example demonstrates:
- LED matrix pixel control
- Text scrolling
- Matrix animations
- Color patterns

Note: This example requires a BOLT or BOLT+ robot with LED matrix support.
"""

import asyncio
import logging
from sphero_bolt_plus import SpheroScanner, SpheroBot, Colors, Color, RobotModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def draw_smiley_face(robot: SpheroBot):
    """Draw a simple smiley face on the LED matrix."""
    logger.info("Drawing smiley face...")
    
    # Clear matrix first
    await robot.clear_matrix()
    await asyncio.sleep(0.5)
    
    # Eyes
    await robot.set_matrix_pixel(2, 2, Colors.YELLOW)
    await robot.set_matrix_pixel(5, 2, Colors.YELLOW)
    
    # Nose
    await robot.set_matrix_pixel(3, 4, Colors.RED)
    
    # Mouth (smile)
    await robot.set_matrix_pixel(1, 6, Colors.GREEN)
    await robot.set_matrix_pixel(2, 6, Colors.GREEN)
    await robot.set_matrix_pixel(4, 6, Colors.GREEN)
    await robot.set_matrix_pixel(5, 6, Colors.GREEN)
    await robot.set_matrix_pixel(6, 6, Colors.GREEN)
    
    await asyncio.sleep(3.0)


async def rainbow_pattern(robot: SpheroBot):
    """Create a rainbow pattern on the LED matrix."""
    logger.info("Creating rainbow pattern...")
    
    await robot.clear_matrix()
    
    colors = [
        Colors.RED,
        Colors.ORANGE,
        Colors.YELLOW,
        Colors.GREEN,
        Colors.CYAN,
        Colors.BLUE,
        Colors.PURPLE,
        Colors.MAGENTA,
    ]
    
    # Fill matrix with rainbow colors
    for x in range(8):
        color = colors[x]
        for y in range(8):
            await robot.set_matrix_pixel(x, y, color)
            await asyncio.sleep(0.1)  # Slow fill for effect
    
    await asyncio.sleep(2.0)


async def scrolling_demo(robot: SpheroBot):
    """Demonstrate scrolling text on the LED matrix."""
    logger.info("Scrolling text demo...")
    
    messages = [
        ("HELLO!", Colors.GREEN),
        ("WORLD", Colors.BLUE),
        ("SPHERO", Colors.RED),
        ("ROCKS!", Colors.YELLOW),
    ]
    
    for message, color in messages:
        await robot.scroll_matrix_text(message, color, speed=6)
        await asyncio.sleep(len(message) * 0.5)  # Wait for scroll to complete


async def matrix_animation(robot: SpheroBot):
    """Create a simple animation on the LED matrix."""
    logger.info("Running matrix animation...")
    
    # Bouncing dot animation
    positions = [
        (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
        (6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1),
    ]
    
    for i, (x, y) in enumerate(positions):
        await robot.clear_matrix()
        
        # Change color based on position
        hue = (i * 30) % 360
        color = Color(
            int(255 * (1 + abs(x - 3.5) / 3.5)) // 2,
            int(255 * (1 - abs(y - 3.5) / 3.5)) // 2,
            128,
        )
        
        await robot.set_matrix_pixel(x, y, color)
        await asyncio.sleep(0.2)


async def main():
    """Main function demonstrating LED matrix features."""
    
    logger.info("Starting Sphero BOLT+ LED matrix demo")
    
    # Scan for BOLT/BOLT+ robots only
    async with SpheroScanner() as scanner:
        robots = await scanner.scan_for_robots(
            model_filter=RobotModel.BOLT_PLUS  # Change to BOLT if needed
        )
        
        if not robots:
            logger.error("No BOLT/BOLT+ robots found! LED matrix requires BOLT or BOLT+.")
            return
        
        logger.info(f"Found {len(robots)} BOLT+ robot(s)")
    
    # Connect to first robot
    async with SpheroBot(robots[0]) as robot:
        logger.info(f"Connected to {robot.robot_info.name}")
        
        # Check if robot supports LED matrix
        if robot.robot_info.model not in [RobotModel.BOLT, RobotModel.BOLT_PLUS]:
            logger.error("This robot doesn't support LED matrix!")
            return
        
        # Signal connection with main LED
        await robot.set_main_led(Colors.GREEN)
        await asyncio.sleep(0.5)
        await robot.set_main_led(Colors.BLACK)
        
        # Run various matrix demonstrations
        demos = [
            draw_smiley_face,
            rainbow_pattern,
            scrolling_demo,
            matrix_animation,
        ]
        
        for i, demo in enumerate(demos, 1):
            logger.info(f"Running demo {i}/{len(demos)}: {demo.__name__}")
            await demo(robot)
            await asyncio.sleep(1.0)  # Pause between demos
        
        # Clear matrix and signal completion
        await robot.clear_matrix()
        await robot.set_main_led(Colors.GREEN)
        logger.info("LED matrix demo completed!")
        
        await asyncio.sleep(2.0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise