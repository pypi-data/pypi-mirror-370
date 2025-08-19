"""
This script uses SANN to train a bot to navigate a simple virtual world. The
resulting model can be used to control a SPIKE Prime based bot with similar
capabilities.

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

from examples.digit_recognition.train import train_model
import sann
import json
import rich
import random
from bot import SANNBot, TrainingWorld
from rich.progress import Progress

# ANN layers
layers = [6, 12, 2]
# The number of ANNs in each generation.
population_size = 100
# The maximum number of generations to train for.
max_generations = 100
# The current highest fitness score.
current_max_fitness = 0
# The number of generations since the last fitness improvement.
fitness_last_updated = 0
# Fitness plateau duration (in generations). If the fitness has not improved
# for this many generations, training will be halted.
fitness_plateau_duration = 50
# The maximum number of ticks allowed in a single game.
max_game_ticks = 1000
# The name of the file to save the fittest ANN.
fittest_ann_file = "ann_evolved.json"


def fitness_function(ann, current_population):
    """
    Calculate the fitness of a bot's ann based on its performance in the
    training world. The top 4 fittest bots from the current_population
    are also added to the world, to give the current ann based bot others
    to avoid.
    """
    # Create the training world and populate it with static obstacles.
    tw = TrainingWorld(40, 40)
    # Walls around the edges.
    for x in range(40):
        tw.add_obstacle(x, 0)
        tw.add_obstacle(x, 39)
    for y in range(40):
        tw.add_obstacle(0, y)
        tw.add_obstacle(39, y)
    # Add a random amount of randomly placed walls into the world while
    # keeping track of the positions of the walls so bots cannot be added
    # to the same position.
    wall_positions = set()
    for _ in range(random.randint(10, 20)):
        x = random.randint(1, 38)
        y = random.randint(1, 38)
        wall_positions.add((x, y))
    for pos in wall_positions:
        tw.add_obstacle(*pos)
    # Add the bot, whose fitness we're checking, to the world, whilst
    # avoiding the walls.
    while True:
        x = random.randint(1, 38)
        y = random.randint(1, 38)
        if (x, y) not in wall_positions:
            break
    bot = SANNBot(tw, ann)
    tw.add_bot(bot, x, y)
    # Now add the top 4 fittest bots from the current population to the world.
    for ann in current_population[:4]:
        while True:
            x = random.randint(1, 38)
            y = random.randint(1, 38)
            if (x, y) not in wall_positions:
                break
        tw.add_bot(SANNBot(tw, ann), x, y)
    # Now run the world for the maximum number of ticks
    for _ in range(max_game_ticks):
        tw.tick()
        if bot.collided:
            # No need to continue if the bot has collided with something.
            break
    fitness = 0.0
    # The fittest bots will survive the longest in the world by avoiding all
    # the obstacles, so the bot's lifespan is one measure of its fitness.
    fitness += bot.lifespan
    # The number of obstacles successfully detected is also a measure of
    # fitness.
    fitness += bot.obstacles_detected
    # The number of positions in the world that the bot has been able to visit
    # also indicates an ability to successfully navigate around the world.
    # However, we penalise the bot for wall-banging behaviour by adding a cost
    # for each position it has visited multiple times.
    for pos, count in bot.travel_log.items():
        fitness -= count
    fitness += len(bot.travel_log) * 2
    # If the bot has collided with something, that's a bad thing. So punish the
    # fitness score by penalising earlier collisions more heavily, relative to
    # how long the bot survived.
    if bot.collided:
        fitness -= 10
    fitness = max(0, fitness)
    return fitness


def halt_function(current_population, generation_count):
    """
    If the current population has not improved for fitness_plateau_duration
    generations, halt the training process. Or, if the generation_count
    exceeds 1000, also halt the training process.
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
        # If the fitness has not improved for fitness_plateau_duration
        # generations, halt training.
        if fitness_last_updated > fitness_plateau_duration:
            return True
        else:
            return False


def evolve():
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
            layers=layers,
            population_size=population_size,
            fitness_function=fitness_function,
            halt_function=halt_function,
            log=handle_log,
        )

    # Save the fittest ANN to a file.
    with open(fittest_ann_file, "w") as f:
        ann = sann.clean_network(population[0])
        ann["fitness"] = current_max_fitness
        json.dump(ann, f, indent=2)
        rich.print(
            f"[green]Fittest ANN ({current_max_fitness}) saved to: [bold]{fittest_ann_file}[/bold][/green]"
        )


def evaluate_model(ann, dataset):
    """
    Evaluate the performance of the given ANN on the training world.

    Round the actual outputs to the nearest integer to do a fuzzy comparison.
    """
    average_score = 0
    for inputs, expected_outputs in dataset:
        outputs = sann.run_network(ann, inputs)
        outputs = [round(o) for o in outputs if o < 0.2 or o > 0.8]
        average_score += sum(
            1
            for expected, actual in zip(expected_outputs, outputs)
            if expected == actual
        ) / len(expected_outputs)
    return average_score / len(dataset)


def backprop_train(data):
    """
    Train the ANN using backpropagation on the provided dataset.
    """
    # Number of epochs to train over
    epochs = 10000

    # Learning rate (rate of change as weights are adjusted)
    learning_rate = 0.1

    with Progress() as progress:
        training_task = progress.add_task("Training network", total=epochs)

        # Load the training data.
        with open(data, "r") as f:
            dataset = json.load(f)

        # Initialize the ANN with the specified layers
        ann = sann.create_network(layers)

        def handle_log(data):
            accuracy = evaluate_model(ann, dataset)
            progress.update(
                training_task,
                advance=1,
                description=f"Model score: {accuracy}",
            )

        # Train the ANN
        ann = sann.train(
            ann,
            dataset,
            epochs=epochs,
            learning_rate=learning_rate,
            log=handle_log,
        )

        # Remove the outputs stored in nodes to clean up the ANN
        ann = sann.clean_network(ann)

    with open("ann_supervised.json", "w") as f:
        json.dump(ann, f, indent=2)


if __name__ == "__main__":
    evolve()
    backprop_train("labelled_data.json")
