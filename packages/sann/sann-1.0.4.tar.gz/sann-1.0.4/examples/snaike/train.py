"""
Training script for playing the game of snake using a feedforward neural
network as defined in the `sann` module and otherwise standard Python. This
script trains the model to play the game by simulating the game environment and
using the ANN to make decisions based on the game state. Newer and better
versions of the ANN are evolved using a genetic algorithm approach.

Since this should work with MicroPython the script does not use any external
libraries other than those in the (MicroPython) Python standard library.

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
import json
import rich
import sann
from snake import SnakeWorld
from rich.progress import Progress

# The number of ANNs in each generation.
population_size = 200
# The maximum number of generations to train for.
max_generations = 100
# The current highest fitness score.
current_max_fitness = 0
# The number of generations since the last fitness improvement.
fitness_last_updated = 0
# The maximum number of ticks allowed in a single game.
max_game_ticks = 10000
# The name of the file to save the fittest ANN.
fittest_ann_file = "fittest_ann.json"


def fitness_function(ann, current_population):
    """
    Calculate the fitness of an ANN based on its performance in the Snake
    game. The fitness is determined by how long the snake survives and how
    many items of food it eats.

    The ANN receives 8 inputs representing the game state:

    - 4 inputs indicating the direction towards the next food item in the
      vertical (up, down) and horizontal (left, right) axes. For example,
      if the food was in a row above the snake's head the up input would be
      1 and the down input would be 0. If the food was in a column to the
      right of the snake's head the right input would be 1 and the left input
      would be 0.
    - 4 inputs indicating the direction of the snake's body segments relative
      to the snake's head. These inputs are also in the vertical (up, down)
      and horizontal (left, right) axes. If the snake's body is adjacent
      in any of these directions, the corresponding input is set to 1,
      otherwise it is set to 0.

    The ANN outputs a direction for the snake to move in, which is then
    applied to the game world. There are four possible outputs: up, down,
    left, and right. The snake's movement is determined by the output with
    the highest activation value from the ANN.

    The snake's fitness is measured by how many food items it eats before
    it dies or before the maximum number of ticks is reached (i.e. the
    game times out).
    """
    sw = SnakeWorld()

    for i in range(max_game_ticks):
        # Up to max_game_ticks iterations of the game.
        if not sw.alive:
            # The snake is dead. No point continuing.
            break
        # Get the position of the food relative to the snake's head.
        food_x, food_y = sw.food
        head_x, head_y = sw.snake[0]
        up = 1 if food_y < head_y else 0
        down = 1 if food_y > head_y else 0
        left = 1 if food_x < head_x else 0
        right = 1 if food_x > head_x else 0
        # Get the position of the snake's body segments relative to the head.
        body_up = 1 if (head_x, head_y - 1) in sw.snake else 0
        body_down = 1 if (head_x, head_y + 1) in sw.snake else 0
        body_left = 1 if (head_x - 1, head_y) in sw.snake else 0
        body_right = 1 if (head_x + 1, head_y) in sw.snake else 0
        # Create the input vector for the ANN.
        inputs = [
            up,
            down,
            left,
            right,
            body_up,
            body_down,
            body_left,
            body_right,
        ]
        # Get the ANN's output.
        outputs = sann.run_network(ann, inputs)
        # Determine the direction to move based on the ANN's output.
        max_output = max(outputs)
        if max_output == outputs[0]:
            sw.move_up()
        elif max_output == outputs[1]:
            sw.move_down()
        elif max_output == outputs[2]:
            sw.move_left()
        elif max_output == outputs[3]:
            sw.move_right()
        # Update the game state.
        sw.update()
    # The fitness is the score of the snake (i.e. how many food items it ate).
    return sw.score


def halt_function(current_population, generation_count):
    """
    If the current population has not improved for 10 generations,
    halt the training process. Or, if the generation_count exceeds 1000,
    also halt the training process.
    """
    if generation_count > max_generations:
        return True

    global current_max_fitness
    global fitness_last_updated

    # Check if the current population has improved.
    if current_population[0]["fitness"] > current_max_fitness:
        current_max_fitness = current_population[0]["fitness"]
        # Reset the fitness last updated counter.
        fitness_last_updated = 0
        return False  # Continue training
    else:
        # Increment the fitness last updated counter.
        fitness_last_updated += 1
        # If the fitness has not improved for 10 generations, halt training.
        if fitness_last_updated > 10:
            return True
        else:
            return False


def main():
    """
    Main function to run the training process.
    """

    # Create a progress bar for visual feedback.
    with Progress() as progress:
        evolution_task = progress.add_task(
            "Training...", total=max_generations
        )

        def handle_log(data):
            progress.update(
                evolution_task,
                advance=1,
                description=f"Max fitness: {current_max_fitness}",
            )

        population = sann.evolve(
            layers=[8, 16, 4],
            population_size=population_size,
            fitness_function=fitness_function,
            halt_function=halt_function,
            log=handle_log,
        )

    # Save the fittest ANN to a file.
    with open(fittest_ann_file, "w") as f:
        ann = sann.clean_network(population[0])
        json.dump(ann, f, indent=2)
        rich.print(
            f"[green]Fittest ANN saved to: [bold]{fittest_ann_file}[/bold][/green]"
        )


if __name__ == "__main__":
    main()
