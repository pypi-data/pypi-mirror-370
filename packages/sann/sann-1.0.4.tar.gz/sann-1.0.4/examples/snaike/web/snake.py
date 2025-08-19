"""
A naive implementation of a simple snake game world. Used to test the
neural network's ability to learn how to play the game.

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

import random


class SnakeWorld:
    """
    Represents the snake's world of 40x40 squares. The snake can move
    around the world, eating food and growing longer. The snake's
    position is represented as a list of tuples, where each tuple
    represents a segment of the snake's body. The first tuple is the
    head of the snake, and the last tuple is the tail.

    The food is represented as a tuple, indicating its position in the world.

    The snake can move in four directions: up, down, left, and right.
    The snake's direction is represented as a tuple, where the first item
    is the horizontal direction (-1 for left, 0 for no movement, 1 for right)
    and the second item is the vertical direction (-1 for up, 0 for no
    movement, 1 for down). The snake cannot move in the opposite direction
    to its current movement.

    The draw method is not implemented here, as it is expected to be
    implemented in a subclass that handles the rendering of the game.
    """

    def __init__(self):
        """
        Initialise snake and food settings along with game state.
        """
        # Initial snake position and body of three segments.
        self.snake = [(5, 5), (5, 6), (5, 7)]
        # Food position.
        self.food = (random.randint(1, 39), random.randint(1, 39))
        # Initial direction is up.
        self.snake_direction = (0, -1)
        # Game state.
        self.score = 0
        self.alive = True

    def update(self):
        """
        Move the game state forward by one tick of the clock.
        """
        if not self.alive:
            # The snake is dead. Poor old snake.
            return
        # Move the snake.
        new_head = (
            self.snake[0][0] + self.snake_direction[0],
            self.snake[0][1] + self.snake_direction[1],
        )
        # Wrap the snake around the canvas edges.
        new_head = (new_head[0] % 40, new_head[1] % 40)
        if new_head in self.snake:
            # Collision with body. You're dead. Nothing more to do.
            self.alive = False
            return
        # Good to go so add the new head to the snake.
        self.snake.insert(0, new_head)
        # Check for food collision.
        if self.snake[0] == self.food:
            self.score += 1  # Increase score.
            self.food = (
                random.randint(1, 39),
                random.randint(1, 39),
            )  # New food position.
            self.on_food()
        else:
            # Remove tail segment if no food eaten.
            self.snake.pop()
        # Draw the game.
        self.draw()

    def move_up(self):
        """
        Change the snake's direction to up.
        """
        if self.snake_direction != (0, 1):
            self.snake_direction = (0, -1)

    def move_down(self):
        """
        Change the snake's direction to down.
        """
        if self.snake_direction != (0, -1):
            self.snake_direction = (0, 1)

    def move_left(self):
        """
        Change the snake's direction to left.
        """
        if self.snake_direction != (1, 0):
            self.snake_direction = (-1, 0)

    def move_right(self):
        """
        Change the snake's direction to right.
        """
        if self.snake_direction != (-1, 0):
            self.snake_direction = (1, 0)

    def on_food(self):
        """
        Called when the snake eats food. This method can be overridden
        to implement custom behavior when food is eaten.
        """
        pass

    def draw(self):
        """
        Draw the game state. This method should be implemented in a subclass
        that handles the rendering of the game.
        """
        pass
