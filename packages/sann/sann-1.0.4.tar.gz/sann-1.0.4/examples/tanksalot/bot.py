"""
A naive representation of a trundle bot and its world. Used to test the neural
network's ability to learn how to navigate the world.

Copyright (c) 2025 Nicholas H.Tollervey (ntoll@ntoll.org).

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys

sys.path.append("../../")  # Adjust path to import sann module

import math
import random
import sann


class Bot:
    """
    Represents a simple bot with two motors: left and right. Each motor can
    have a value in the range of: 1 (max forwards) to 0 (stopped). The bot
    can move in any direction by adjusting the speed of its motors like a
    tank.

    The bot also has a single sensor: to detect distance. The distance sensor
    measures the distance to the nearest obstacle with six possible ranges (0
    [nothing detected], 1 [very close], 2 [close], 3 [medium], 4 [far], or 5
    [very far]).

    To make the bot useful it should first detect the world using its sensor,
    some sort of computation should be performed to determine the state of the
    bot's motors, and then the motors should be set accordingly.

    For convenience, the bot also provides an `input_layer` method that returns
    a list of inputs to a neural network. This list contains the distance
    sensor reading, represented as a list of floating-point numbers. The six
    indices represent the six possible states for the distance sensor reading.
    The index 0 represents no obstacle detected, while index 5 represents an
    obstacle very far away. The active state is represented by a 1.0 in the
    corresponding index, while all other indices are 0.0.
    """

    def __init__(self):
        """
        Initialise the bot's motors and sensors.
        """
        self.left_motor = 0  # Default off.
        self.right_motor = 0  # Default off.
        self.distance_reading = 0  # Default no distance detected.
        self.collided = False  # Default not collided.

    def set_motors(self, left: float, right: float):
        """
        Set the state of the left and right motors. Valid values are between
        1 (forwards) and 0 (off). If the bot has collided with something the
        motors are stopped.
        """
        self.left_motor = left
        self.right_motor = right

    def engage(self):
        """
        Detect readings from the distance sensor and adjust the bot's motors
        accordingly.
        """
        self.detect_distance()
        self.drive()

    def detect_distance(self):
        """
        Detect the distance to the nearest obstacle in front of the bot. The
        distance can be one of:

        - 0 (nothing detected)
        - 1 (very close)
        - 2 (close)
        - 3 (medium)
        - 4 (far)
        - 5 (very far)
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )

    def drive(self):
        """
        Called immediately after the world has been detected. Update the bot's
        driving.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )

    def input_layer(self):
        """
        Return the inputs to the neural network. This is a list of nodes
        representingthe bot's current colour sensor reading, and distance
        sensor reading.
        """
        input_layer = [0.0 for _ in range(6)]  # 6 distance values.
        # Set distance sensor reading.
        input_layer[self.distance_reading] = 1.0
        return input_layer


class StupidBot(Bot):
    """
    A bot with very naive hard coded instructions for navigating the world.
    """

    def __init__(self):
        super().__init__()
        self.rotate_direction = None

    def drive(self):
        """
        Very stupid hard coded rules for driving the bot.
        """
        if self.distance_reading > 0:  # Close obstacle - turn around
            if self.rotate_direction is None:
                self.rotate_direction = random.choice([(0.0, 1.0), (1.0, 0.0)])
            self.set_motors(*self.rotate_direction)
        else:  # No obstacle detected or far away - move forward
            self.rotate_direction = None  # Reset rotation direction
            self.set_motors(0.5, 0.5)


class SANNBot(Bot):
    """
    A bot that uses a neural network to navigate the world.
    """

    def __init__(self, world, brain):
        super().__init__()
        # The virtual world in which the bot finds itself.
        self.world = world
        # The ANN associated with this bot.
        self.brain = brain
        # The bot's lifespan measured in ticks.
        self.lifespan = 0
        # To contain the number of unique positions in the world the
        # bot has encountered, and the number of times they have been
        # visited. This is used to punish wall-banging behaviour.
        self.travel_log = {}
        # To contain the number of obstacles successfully detected, used
        # to assess the bot's fitness.
        self.obstacles_detected = 0

    def detect_distance(self):
        self.distance_reading = self.world.get_distance_ahead(
            self.x, self.y, self.angle
        )
        if self.distance_reading > 0:
            self.obstacles_detected += 1

    def drive(self):
        """
        Update the bot's motors based on its brain's output given the current
        state of its sensors.

        There are two outputs, one for each wheel.
        """
        # Run the sensors through the neural network to get an output
        # decision.
        outputs = sann.run_network(self.brain, self.input_layer())
        # Set the motor values according to the ANN's output.
        self.set_motors(left=outputs[0], right=outputs[1])


class BotWorld:
    """
    Represents a simple virtual world for the bot to navigate. The world is a
    grid of cells where the bot can move around. The world may contain
    obstacles which the bot can detect using its sensors. The world can also
    contain multiple bots that can interact with each other. The edge of the
    world does NOT wrap around and encountering the edge is considered the
    same as encountering an obstacle.
    """

    # How the obstacles might be represented visually.
    WALL_OBSTACLE = "🧱"

    def __init__(self, width: int = 200, height: int = 200):
        """
        Initialise the world with a given width and height.
        """
        self.width = width
        self.height = height
        self.obstacles = {}  # Dictionary of obstacle positions.
        self.bots = []  # a list of bots found in the world.

    def update_world(self):
        """
        Draw the world, including all bots and obstacles.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )

    def add_bot(self, bot: Bot):
        """
        Add a bot to the world.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass."
        )

    def add_obstacle(self, x: int, y: int):
        """
        Add an obstacle to the world at the given coordinates. The obstacle
        type can be specified (default is a wall).
        """
        self.obstacles[(x, y)] = self.WALL_OBSTACLE

    def get_direction_from_angle(self, angle):
        """
        Calculate the direction the bot is facing (dx, dy) from its angle.
        """
        angle_rad = math.radians(angle)
        return math.sin(angle_rad), -math.cos(angle_rad)

    def get_distance_ahead(self, x, y, angle):
        """
        Get the distance to any obstacles in front of the bot using a wider
        sensor field of view. The sensor scans three rays: left-ahead,
        straight-ahead, and right-ahead, then returns the closest detection.
        """
        # Define sensor field of view (sensors are not a single line).
        sensor_angles = [
            angle - 15,  # left-ahead
            angle,  # straight-ahead
            angle + 15,  # right-ahead
        ]
        # Default: no obstacle detected.
        closest_distance = 0
        # Scan each direction in the sensor field of view.
        for sensor_angle in sensor_angles:
            dx, dy = self.get_direction_from_angle(sensor_angle)
            # Scan the range of cells ahead for this direction in the
            # field of view.
            for dist in range(1, 6):
                # Target cell coordinates.
                nx = int(round(x + dx * dist))
                ny = int(round(y + dy * dist))
                # Check if the target cell is within bounds.
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    if closest_distance == 0 or dist < closest_distance:
                        closest_distance = dist
                    break
                # Check if the target cell is occupied by an obstacle.
                if (nx, ny) in self.obstacles:
                    if closest_distance == 0 or dist < closest_distance:
                        closest_distance = dist
                    break
                # Check for other bots at this position.
                if any(other.x == nx and other.y == ny for other in self.bots):
                    if closest_distance == 0 or dist < closest_distance:
                        closest_distance = dist
                    break
        return closest_distance

    def tick(self):
        """
        Update the world by one tick. This will move all bots and check for
        collisions with obstacles or other bots.
        """
        for bot in self.bots:
            # Move the bot based on its current state.
            if not bot.collided:
                bot.engage()
        self.update_world()


class TrainingWorld(BotWorld):
    """
    A virtual world for training bots.
    """

    def add_bot(self, bot: SANNBot, x: int, y: int, angle: float = 0.0):
        """
        Annotate the bot with a bunch of implementation details for the sake
        of convenience in the web world.
        """
        bot.x = x
        bot.y = y
        # Fractional position tracking for smooth low-speed movement.
        bot.fx = float(x)
        bot.fy = float(y)
        bot.angle = angle % 360
        self.bots.append(bot)

    def update_world(self):
        """
        Update the state of the world by moving all bots and checking for
        collisions.
        """
        # Remove dead bots
        self.bots = [bot for bot in self.bots if not bot.collided]
        for bot in self.bots:
            bot.lifespan += 1
            # Forward speed is limited by the slower motor.
            forward_speed = min(bot.left_motor, bot.right_motor)

            # Handle forward movement if there's any.
            if forward_speed > 0:
                dx = math.sin(math.radians(bot.angle)) * forward_speed * 2
                dy = -math.cos(math.radians(bot.angle)) * forward_speed * 2
                # Calculate new fractional position.
                new_fx = bot.fx + dx
                new_fy = bot.fy + dy
                # New grid x/y coordinates.
                nx, ny = int(round(new_fx)), int(round(new_fy))
                # Check if the proposed new position is within bounds and
                # free from obstacles.
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in self.obstacles
                ):
                    # Only update fractional and integer positions if
                    # movement is valid.
                    bot.fx, bot.fy = new_fx, new_fy
                    bot.x, bot.y = nx, ny
                    # Update a counter in bot.travel_log for the visited
                    # coordinate.
                    bot.travel_log[(nx, ny)] = (
                        bot.travel_log.get((nx, ny), 0) + 1
                    )
                else:
                    # Oops. Collision detected!
                    bot.collided = True
            # Always handle rotation (whether moving forward or not).
            # Rotation speed is based on motor difference.
            rotation_speed = (bot.right_motor - bot.left_motor) * 10.0
            bot.angle = (bot.angle + rotation_speed) % 360
