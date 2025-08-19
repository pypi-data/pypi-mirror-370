from pyscript import when
from pyscript.web import page
import asyncio
from pyscript.ffi import create_proxy
import js
import json
import sann
from snake import SnakeWorld
from pyscript.web import audio


class HTMLSnake(SnakeWorld):
    """
    A snake. But in the world of HTML :-).
    """

    def __init__(self):
        super().__init__()
        self.canvas = page["#gameCanvas"][0]
        self.ctx = self.canvas._dom_element.getContext("2d")

    def on_food(self):
        # Slurp! (Thanks Mary)
        audio(src="./slurp.mp3").play()

    def draw(self):
        # Clear
        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        # Snake
        self.ctx.fillStyle = "green"
        for segment in self.snake:
            self.ctx.fillRect(segment[0] * 10, segment[1] * 10, 10, 10)
        # Food
        self.ctx.fillStyle = "red"
        self.ctx.fillRect(self.food[0] * 10, self.food[1] * 10, 10, 10)


# Make a snake
my_snake = HTMLSnake()
ai_mode = False

# AI toggle
@when("click", "#ai-mode")
def toggle_ai():
    global ai_mode
    ai_mode = not ai_mode

# Movements
@when("click", "#button_up")
def handle_up():
    my_snake.move_up()

@when("click", "#button_down")
def handle_down():
    my_snake.move_down()

@when("click", "#button_left")
def handle_left():
    my_snake.move_left()

@when("click", "#button_right")
def handle_right():
    my_snake.move_right()

def handle_keydown(event):
    """
    To handle key presses.
    """
    # Prevent the default action of arrow keys
    if event.key in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]:
        event.preventDefault()
    if event.key == "ArrowUp":
        my_snake.move_up()
    elif event.key == "ArrowDown":
        my_snake.move_down()
    elif event.key == "ArrowLeft":
        my_snake.move_left()
    elif event.key == "ArrowRight":
        my_snake.move_right()

# Attach event listener for keydown using create_proxy.
js.addEventListener("keydown", create_proxy(handle_keydown))

with open("ann.json", "r") as f:
    ann = json.load(f)

async def game_loop():
    """
    Loop at the given speed (between 1.0 and 0).
    """
    while my_snake.alive:
        # Check speed.
        if not ai_mode:
            speed = 1.0
        else:
            speed = 0.1
            # Get the position of the food relative to the snake's head.
            food_x, food_y = my_snake.food
            head_x, head_y = my_snake.snake[0]
            up = 1 if food_y < head_y else 0
            down = 1 if food_y > head_y else 0
            left = 1 if food_x < head_x else 0
            right = 1 if food_x > head_x else 0
            # Get the position of the snake's body segments relative to the head.
            body_up = 1 if (head_x, head_y - 1) in my_snake.snake else 0
            body_down = 1 if (head_x, head_y + 1) in my_snake.snake else 0
            body_left = 1 if (head_x - 1, head_y) in my_snake.snake else 0
            body_right = 1 if (head_x + 1, head_y) in my_snake.snake else 0
            # Create the input vector for the ANN.
            inputs = [
                up, down, left, right,
                body_up, body_down, body_left, body_right
            ]
            # Get the ANN's output.
            outputs = sann.run_network(ann, inputs)
            # Determine the direction to move based on the ANN's output.
            max_output = max(outputs)
            if max_output == outputs[0]:
                my_snake.move_up()
            elif max_output == outputs[1]:
                my_snake.move_down()
            elif max_output == outputs[2]:
                my_snake.move_left()
            elif max_output == outputs[3]:
                my_snake.move_right()
        
        my_snake.update()
        await asyncio.sleep(speed/10)

# Go!
await game_loop()

# If we get here the game has stopped, so tell the player the final score.
outcome = page.find("#outcome")
outcome.innerHTML = f"🐍🍒: <strong>{my_snake.score}</strong>"