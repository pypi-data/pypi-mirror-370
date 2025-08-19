import json
from bot import StupidBot, SANNBot, BotWorld
from pyscript.web import page
import asyncio
import math
import random


class WebBot(StupidBot):
    """
    A bot that works within the virtual world defined by a WebBotWorld instance.
    Bots based on this class are intended to run in a web browser environment.
    """

    def __init__(self, world):
        super().__init__()
        self.world = world

    def detect_distance(self):
        self.distance_reading = self.world.get_distance_ahead(
            self.x, self.y, self.angle
        )


class WebBotWorld(BotWorld):
    """
    A web-based implementation of the bot world that includes a canvas for
    rendering the bots and their environment.
    """

    def __init__(self, width: int = 200, height: int = 200):
        """
        Add a bunch of web-specific initialization code here.
        """
        super().__init__(width, height)
        self.canvas = page.find("#botworld-canvas")[0]
        self.ctx = self.canvas.getContext("2d")
        self.trails = {}
        self.trail_max_length = 12

    def add_bot(
        self,
        bot: WebBot,
        x: int,
        y: int,
        angle: float = 0.0,
        color: list = (0, 100, 255),
    ):
        """
        Annotate the bot with a bunch of implementation details for the sake
        of convenience in the web world.
        """
        bot.x = x
        bot.y = y
        bot.angle = angle % 360
        bot.color = color
        # Fractional position tracking for smooth low-speed movement.
        bot.fx = float(x)
        bot.fy = float(y)
        self.bots.append(bot)
        # List of (x, y, age) tuples for each bread-crumb (circle) on the
        # trail.
        self.trails[bot] = []

    async def tick(self):
        for bot in self.bots:
            # Move the bot based on its current state.
            bot.engage()
            print(
                bot.distance_reading,
                bot.left_motor,
                bot.right_motor,
                bot.collided,
            )
        await self.update_world()

    async def update_world(self):
        """
        Update the state of the world by moving all bots and checking for
        collisions.
        """
        # Required for animating to the new state.
        old_positions = {}
        for bot in self.bots:
            if bot.collided:
                continue
            # Needed for animation purposes.
            old_positions[bot] = (bot.fx, bot.fy)
            # Tank-style movement: bot moves forward only when both motors
            # work together.
            # If motors are different, the bot rotates around the slower motor.
            left_motor = bot.left_motor
            right_motor = bot.right_motor

            # Forward speed is limited by the slower motor.
            forward_speed = min(left_motor, right_motor)

            # Handle forward movement if there's any.
            if forward_speed > 0:
                dx = math.sin(math.radians(bot.angle)) * forward_speed * 2
                dy = -math.cos(math.radians(bot.angle)) * forward_speed * 2
                # Calculate new fractional position
                new_fx = bot.fx + dx
                new_fy = bot.fy + dy
                nx, ny = int(round(new_fx)), int(round(new_fy))
                # Check if the proposed new position is within bounds and free
                # from obstacles.
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in self.obstacles
                ):
                    # Only update fractional and integer positions if movement
                    # is valid.
                    bot.fx, bot.fy = new_fx, new_fy
                    bot.x, bot.y = nx, ny
                    # Add trail breadcrumb at fractional position for smooth
                    # diagonal trails.
                    self.trails[bot].append((bot.fx, bot.fy, 0))
                    while len(self.trails[bot]) > self.trail_max_length:
                        self.trails[bot].pop(0)
                else:
                    # Oops. Collision detected!
                    print("Bot collided with obstacle or boundary!")
                    bot.collided = True
            # Always handle rotation (whether moving forward or not).
            # Rotation speed is based on motor difference.
            rotation_speed = (right_motor - left_motor) * 10.0
            bot.angle = (bot.angle + rotation_speed) % 360

        # Always age all trail entries regardless of movement
        for bot in self.trails:
            for i in range(len(self.trails[bot])):
                trail_x, trail_y, age = self.trails[bot][i]
                self.trails[bot][i] = (trail_x, trail_y, age + 1)
            # Remove fully faded trail entries (age > trail_max_length means
            # opacity <= 0).
            self.trails[bot] = [
                (x, y, age)
                for x, y, age in self.trails[bot]
                if age <= self.trail_max_length
            ]
        # Now take the old positions and animate to the new positions found in
        # self.bots.
        await self.animate_movement(old_positions, self.bots)

    async def animate_movement(self, old_positions, new_bots):
        """
        Animate the movement of bots from their old positions to their new
        positions.

        Mostly written by an LLM with prompting from a human (canvas animation
        is not something I know about).

        But it seems to work!
        """
        tile_size = 20
        base_steps = 10
        # Move the bot by a small amount each step, with base_steps being the
        # number of steps to move to the new position.
        for step in range(1, base_steps + 1):
            # Clear the canvas.
            self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
            # And draw the static elements.
            self.draw_static(self.ctx, tile_size)
            # Re-draw each bot at its new "step" position.
            for bot in new_bots:
                # Use fractional positions for smooth diagonal movement
                new_fx, new_fy = bot.fx, bot.fy
                old_fx, old_fy = old_positions.get(bot, (new_fx, new_fy))
                angle_deg = bot.angle
                # Interpolate fractional position for smooth animation.
                draw_x = old_fx + (new_fx - old_fx) * (step / base_steps)
                draw_y = old_fy + (new_fy - old_fy) * (step / base_steps)
                # Convert fractional coordinates to canvas coordinates.
                canvas_x = draw_x * tile_size + tile_size // 2
                canvas_y = draw_y * tile_size + tile_size // 2
                # Draw sensor line first (so it appears underneath the bot)
                self.draw_sensor_line(
                    canvas_x, canvas_y, angle_deg, bot, tile_size
                )
                # The following code is the LLM's main contribution. No idea
                # what it's doing, but it seems to work. ;-)
                # Save context for rotation.
                self.ctx.save()
                # Move to bot position and rotate.
                self.ctx.translate(canvas_x, canvas_y)
                self.ctx.rotate(math.radians(angle_deg))
                # Draw custom bot shape that looks like it has two motors.
                self.draw_bot_shape(tile_size, bot)
                # Restore context.
                self.ctx.restore()

            # Sleep for a consistent amount so the animation appears smooth,
            # regardless of bot speed.
            await asyncio.sleep(0.01)

    def draw_bot_shape(self, tile_size, bot):
        """
        Draw a bot shape that looks like it has two motors seen from above.
        If the bot has collided, draw an explosion emoji instead.

        Mostly created by an LLM with colour features added by a human.
        """
        if bot.collided:
            ctx = self.ctx
            ctx.font = "48px serif"
            ctx.fillText("💥", -tile_size // 2, -tile_size // 2)
            return
        ctx = self.ctx
        # Size relative to tile, increased for better visibility but may
        # look like there are overlapping elements.
        size = tile_size * 1.4
        # Main body (rectangle).
        ctx.fillStyle = "#333333"  # Dark gray body
        ctx.fillRect(-size / 4, -size / 3, size / 2, size * 0.6)
        # Left motor (wheel).
        ctx.fillStyle = "#666666"  # Lighter gray for motors
        ctx.fillRect(-size / 3, -size / 4, size / 8, size / 2)
        # Right motor (wheel).
        ctx.fillRect(size / 4, -size / 4, size / 8, size / 2)
        # Front direction indicator (small rectangle at front),
        # indicating the bot's colour.
        r, g, b = bot.color
        ctx.fillStyle = f"rgb({r}, {g}, {b})"
        ctx.fillRect(-size / 8, -size / 3, size / 4, size / 10)
        # Center dot to show rotation point
        ctx.fillStyle = "#fff"
        ctx.beginPath()
        ctx.arc(0, 0, size / 12, 0, 2 * math.pi)
        ctx.fill()

    def draw_sensor_line(self, bot_x, bot_y, angle_deg, bot, tile_size):
        """
        Draw lines showing the bot's wide-field sensor readings.
        Shows three sensor rays: left-ahead, straight-ahead, and right-ahead
        to visualize the bot's field of view.

        When nothing is detected, the sensor should be a light grey line. As
        objects are detected, the closer they become, the darker the colour.
        """
        if bot.collided:
            return

        max_sensor_range = 5

        # Draw three sensor rays with 15° spread to show field of view
        sensor_angles = [
            angle_deg - 15,  # left-ahead
            angle_deg,  # straight-ahead
            angle_deg + 15,  # right-ahead
        ]

        for i, sensor_angle in enumerate(sensor_angles):
            # Get individual distance reading for this ray
            ray_distance = self.get_single_ray_distance(
                int(bot.fx), int(bot.fy), sensor_angle
            )

            # Calculate line length based on detection
            if ray_distance == 0:
                line_length = max_sensor_range * tile_size
                effective_intensity = 0.3  # Very light for no detection
            else:
                line_length = ray_distance * tile_size
                # Closer = darker (lower intensity)
                min_intensity = 0.1  # Nearly black for close objects
                max_intensity = 0.8  # Light gray for distant objects
                intensity_range = max_intensity - min_intensity
                distance_factor = (ray_distance - 1) / (max_sensor_range - 1)
                effective_intensity = (
                    min_intensity + intensity_range * distance_factor
                )

            # Make outer rays slightly more transparent to show they're secondary
            if i != 1:  # Not the center ray
                effective_intensity *= 0.9

            # Calculate line end coordinates
            angle_rad = math.radians(sensor_angle)
            end_x = bot_x + math.sin(angle_rad) * line_length
            end_y = bot_y - math.cos(angle_rad) * line_length

            # Draw the sensor ray
            self.ctx.save()
            color_value = int(effective_intensity * 255)
            self.ctx.strokeStyle = (
                f"rgb({color_value}, {color_value}, {color_value})"
            )
            self.ctx.lineWidth = 1
            self.ctx.setLineDash([3, 2])  # Dotted line
            self.ctx.beginPath()
            self.ctx.moveTo(bot_x, bot_y)
            self.ctx.lineTo(end_x, end_y)
            self.ctx.stroke()
            self.ctx.restore()

    def get_single_ray_distance(self, x, y, angle):
        """
        Get distance for a single sensor ray (helper for visualization).
        """
        dx, dy = self.get_direction_from_angle(angle)

        for dist in range(1, 6):
            nx = int(round(x + dx * dist))
            ny = int(round(y + dy * dist))

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                return dist
            if (nx, ny) in self.obstacles:
                return dist
            if any(other.x == nx and other.y == ny for other in self.bots):
                return dist
        return 0

    def draw_static(self, ctx, tile_size):
        """
        Draw all the static / unmoving objects in the world.
        """
        # Set canvas dimensions
        self.canvas.width = self.width * tile_size
        self.canvas.height = self.height * tile_size
        # Set font properties for static elements emoji.
        ctx.font = f"{tile_size-4}px serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        # Draw obstacles
        for (x, y), kind in self.obstacles.items():
            canvas_x = x * tile_size + tile_size // 2
            canvas_y = y * tile_size + tile_size // 2
            ctx.fillText(kind, canvas_x, canvas_y)
        # Draw continuous trail lines with fading effect at the end.
        self.draw_trail_breadcrumbs(ctx, tile_size)

    def draw_trail_breadcrumbs(self, ctx, tile_size):
        """
        Draw breadcrumb trail points for each bot with fading effect.
        """
        for bot in self.bots:
            # Get the historical trail points for the bot.
            trail_points = self.trails[bot]
            if len(trail_points) < 1:
                continue
            # Get bot-specific color
            r, g, b = bot.color
            # Draw each breadcrumb point
            for fx, fy, age in trail_points:
                # Calculate opacity based on age (adjusted for longer trail)
                opacity = max(0.0, 1.0 - (age * 2.0 / self.trail_max_length))
                # Skip drawing if fully transparent
                if opacity <= 0.0:
                    continue
                # Convert fractional coordinates to canvas coordinates
                canvas_x = fx * tile_size + tile_size // 2
                canvas_y = fy * tile_size + tile_size // 2
                # Draw breadcrumbs
                ctx.save()
                ctx.fillStyle = f"rgba({r}, {g}, {b}, {opacity})"
                ctx.beginPath()
                ctx.arc(canvas_x, canvas_y, 1.5, 0, 2 * math.pi)
                ctx.fill()
                ctx.restore()


# Now let's write the actual game..!


# Let there be light!
bw = WebBotWorld(40, 40)


# Create irregular walls around the perimeter with protrusions and concaves
# along with some interior walls for added complexity.

# Top edge - with irregular pattern
for x in range(40):
    bw.add_obstacle(x, 0)
    if x in [5, 6, 7, 15, 16, 20, 21, 22, 30, 31]:
        bw.add_obstacle(x, 1)
    if x in [10, 11, 25, 26, 35]:
        bw.add_obstacle(x, 2)

# Bottom edge - with different irregular pattern
for x in range(40):
    bw.add_obstacle(x, 39)
    if x in [3, 4, 8, 9, 18, 19, 28, 29, 33, 34]:
        bw.add_obstacle(x, 38)
    if x in [12, 13, 23, 24, 37]:
        bw.add_obstacle(x, 37)

# Left edge - with irregular pattern
for y in range(40):
    bw.add_obstacle(0, y)
    if y in [4, 5, 12, 13, 14, 22, 23, 32, 33]:
        bw.add_obstacle(1, y)
    if y in [8, 18, 28]:
        bw.add_obstacle(2, y)

# Right edge - with different irregular pattern
for y in range(40):
    bw.add_obstacle(39, y)
    if y in [6, 7, 16, 17, 24, 25, 26, 34, 35]:
        bw.add_obstacle(38, y)
    if y in [10, 20, 30]:
        bw.add_obstacle(37, y)

# Add some corner reinforcements and interesting shapes
# Top-left corner extension
bw.add_obstacle(1, 1)
bw.add_obstacle(2, 1)
bw.add_obstacle(1, 2)

# Top-right corner extension
bw.add_obstacle(38, 1)
bw.add_obstacle(37, 1)
bw.add_obstacle(38, 2)

# Bottom-left corner extension
bw.add_obstacle(1, 38)
bw.add_obstacle(2, 38)
bw.add_obstacle(1, 37)

# Bottom-right corner extension
bw.add_obstacle(38, 38)
bw.add_obstacle(37, 38)
bw.add_obstacle(38, 37)

# Add some interior walls to create a more interesting environment
# Vertical walls
for y in range(10, 20):
    bw.add_obstacle(10, y)
    bw.add_obstacle(30, y)

# Horizontal walls
for x in range(15, 25):
    bw.add_obstacle(x, 15)
    bw.add_obstacle(x, 25)

# Create some wall corners and obstacles
bw.add_obstacle(5, 5)
bw.add_obstacle(6, 5)
bw.add_obstacle(5, 6)

bw.add_obstacle(34, 34)
bw.add_obstacle(35, 34)
bw.add_obstacle(34, 35)

# Add some bots!

# Stupid hand-coded bot.
bot = WebBot(bw)
# Place bot in the center of the larger world
bw.add_bot(bot, 20, 20, 0, (0, 255, 0))  # Explicitly set angle to 0 (north)


def add_sann_bot(ann_file, bw, color):
    with open(ann_file, "r") as f:
        ann = json.load(f)
    bot = SANNBot(bw, ann)
    location = random.randint(10, 30)
    angle = random.randint(0, 360)
    bw.add_bot(bot, location, location, angle, color)


anns = {"ann_supervised.json": (255, 0, 0), "ann_evolved.json": (255, 140, 0)}

# anns = {}

for filename, color in anns.items():
    add_sann_bot(filename, bw, color)


async def main():
    while True:
        await bw.tick()


print("Bot world initialized. Starting main loop...")
await main()
