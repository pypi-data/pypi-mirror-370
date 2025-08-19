"""
## Simple Artificial Neural Networks

Simple Artificial Neural Networks (SANN) is a naive Python implementation of
an artificial neural network (ANN) that's useful for educational purposes
and clarifying the concepts of feed-forward neural networks, backpropagation,
neuro-evolution of weights and biases, and genetic algorithms. SANN is not
intended for production use or performance-critical applications. Rather, use
it for educational, playful or small-scale projects. 😉

See:
[https://ntoll.org/article/ai-curtain/](https://ntoll.org/article/ai-curtain/)
for a comprehensive and informal exploration of the concepts behind this code.

```
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
```
"""

import math
import random


__version__ = "1.0.4"


def sum_inputs(inputs: list[tuple[float, float]]) -> float:
    """
    Calculate the activation value from a list of pairs of `x` input values
    and `w` weights. This is essentially just the dot product.
    """
    return sum([x * w for x, w in inputs])


def sigmoid(
    activation: float, threshold: float = 0.0, shape: float = 1.0
) -> float:
    """
    Calculate the output value of a sigmoid based node.

    Take the `activation` value, a `threshold` value, and a `shape` parameter,
    and return the output value found somewhere on an s-shaped sigmoid curve.
    """
    return 1 / (1 + math.exp(-((activation - threshold) / shape)))


def create_network(structure: list) -> dict:
    """
    Return a dict representing a simple artificial neural network (ANN).

    The `structure` argument should be a list containing the number of nodes in
    each layer of a fully connected feed-forward neural network.

    The resulting dictionary will contain a list of layers, where each layer
    is a list of nodes. Each node is represented as a dictionary containing
    its incoming weights from the previous layer and a bias value. The weights
    and bias are randomly initialised to a value between -1 and 1.

    The first layer is ignored since it is the input layer and has no weights
    nor bias associated with it. There must be at least two layers (an input
    layer and an output layer) for the ANN to be valid.

    Other arbitrary properties are added to the returned dictionary, such as
    a `fitness` score, which can be used for training or evolution of the ANN,
    and a `structure` that defines the topology of the ANN (i.e. the number of
    nodes in each layer).
    """
    if len(structure) < 2:
        raise ValueError(
            "ANN must have at least two layers (input and output)."
        )
    layers = []
    # Create nodes with random weights and a bias for each layer except the
    # input layer
    for i in range(1, len(structure)):
        layer = []
        for j in range(structure[i]):
            layer.append(
                {
                    "weights": [
                        random.uniform(-1, 1) for _ in range(structure[i - 1])
                    ],
                    "bias": random.uniform(-1, 1),
                }
            )
        layers.append(layer)
    result = {"structure": structure, "fitness": None, "layers": layers}
    return result


def run_network(ann: dict, inputs: list) -> list:
    """
    Perform a forward pass through the `ann` using the given `inputs`.

    The inputs are a list of values that are fed into the first layer of the
    ANN. The output of each layer is calculated and passed to the next layer
    until the final output is produced and returned as a list of values.
    """
    outputs = inputs
    for layer in ann["layers"]:
        new_outputs = []
        for node in layer:
            activation = sum_inputs(zip(outputs, node["weights"]))
            # Store the output in the node, used for backpropagation
            node["output"] = sigmoid(activation, node["bias"])
            new_outputs.append(node["output"])
        outputs = new_outputs
    return outputs


def clean_network(ann: dict) -> dict:
    """
    Remove the outputs stored in nodes to clean up the `ann`, so only the
    weights and biases remain.
    """
    for layer in ann["layers"]:
        for node in layer:
            if "output" in node:
                del node["output"]
    return ann


def backpropagate(
    ann: dict, inputs: list, expected_outputs: list, learning_rate: float = 0.1
) -> dict:
    """
    Perform backpropagation to adjust the weights of the `ann` based on the
    `expected_outputs`.

    This function calculates the error for each node in the output layer,
    propagates that error back through the network, and adjusts the weights
    accordingly. The `learning_rate` determines how much the weights are
    adjusted during each update.

    It returns the updated ANN with adjusted weights.
    """
    # Forward pass using existing function (stores outputs in nodes).
    final_outputs = run_network(ann, inputs)

    # Calculate initial errors for output layer.
    output_errors = [
        expected - actual
        for expected, actual in zip(expected_outputs, final_outputs)
    ]

    # Backpropagate through all layers.
    current_errors = output_errors
    for i in reversed(range(len(ann["layers"]))):
        layer = ann["layers"][i]

        # Get inputs to this layer.
        if i == 0:
            layer_inputs = inputs
        else:
            layer_inputs = [node["output"] for node in ann["layers"][i - 1]]

        # Update weights and biases for current layer.
        for j, node in enumerate(layer):
            # Calculate gradient using this node's stored output.
            gradient = (
                node["output"] * (1 - node["output"]) * current_errors[j]
            )

            # Update weights using inputs to this layer.
            for k in range(len(node["weights"])):
                node["weights"][k] += (
                    learning_rate * gradient * layer_inputs[k]
                )

            # Update bias.
            node["bias"] += learning_rate * gradient

        # Calculate errors for previous layer (if not input layer).
        if i > 0:
            new_errors = []
            previous_layer = ann["layers"][i - 1]
            for j in range(len(previous_layer)):
                error = sum(
                    node["output"]
                    * (1 - node["output"])
                    * current_errors[k]
                    * node["weights"][j]
                    for k, node in enumerate(layer)
                )
                new_errors.append(error)
            current_errors = new_errors

    return ann


def train(
    ann: dict,
    training_data: list[tuple[list[float], list[float]]],
    epochs: int = 1000,
    learning_rate: float = 0.1,
    log: callable = lambda x: None,
):
    """
    Supervised training of the `ann` using the provided `training_data`.

    The `training_data` is a list of tuples where each tuple contains inputs and
    the expected output. The ANN is trained for a specified number of `epochs`,
    adjusting the weights by the `learning_rate`, and based on the error
    between actual and expected outputs.

    The `log` function can be used to log progress during training. It defaults
    to a no-op function that does nothing.
    """
    log("Training ANN...")
    for _ in range(epochs):
        log(f"Epoch {_ + 1}/{epochs}")
        for inputs, expected_outputs in training_data:
            backpropagate(ann, inputs, expected_outputs, learning_rate)
        log(clean_network(ann))
    log("Training complete.")
    return ann


def roulette_wheel_selection(population: list[dict]) -> dict:
    """
    Select a neural network from the `population`, with the fittest networks
    having a higher chance of being selected.

    A random number between 0 and the total fitness score of all the ANNs in
    a population is chosen (a point within a slice of a roulette wheel). The
    code iterates through the ANNs adding up the fitness scores. When the
    subtotal is greater than the randomly chosen point it returns the ANN
    at that point "on the wheel".

    [More info.](https://en.wikipedia.org/wiki/Fitness_proportionate_selection)
    """
    total_fitness = 0.0
    for ann in population:
        if "fitness" in ann:
            total_fitness += ann["fitness"]

    if total_fitness == 0:
        # If all fitness scores are zero, select a random ANN.
        return random.choice(population)

    random_point = random.uniform(0.0, total_fitness)

    fitness_tally = 0.0
    for ann in population:
        if "fitness" in ann:
            fitness_tally += ann["fitness"]
        if fitness_tally > random_point:
            return ann


def crossover(mum: dict, dad: dict) -> tuple[dict, dict]:
    """
    Perform crossover between two parent ANNs (`mum` and `dad`) to create two
    child ANNs. The children inherit weights and biases from both parents
    through the following process:

    1. Two split points are chosen randomly. A split point is always at the
       boundary between two nodes in a layer.
    2. The first child inherits weights and biases from the `mum` up to the
       first split point, then from the `dad` until the second split point,
       and finally from the `mum` again.
    3. The second child inherits weights and biases from the `dad` up to the
       first split point, then from the `mum` until the second split point,
       and finally from the `dad` again.
    4. Nodes are treated as a continuous sequence across layers, so the split
       points can cross layer boundaries.
    5. The children are returned as a tuple of two new ANN structures.
    """
    # Flatten the nodes in both parents to treat them as a continuous sequence.
    # This makes it easier to choose split points across layers.
    flat_mum = [node for layer in mum["layers"] for node in layer]
    flat_dad = [node for layer in dad["layers"] for node in layer]

    # Choose two random split points, ensuring split1 < split2.
    split1 = random.randint(0, len(flat_mum) - 2)
    split2 = random.randint(split1 + 1, len(flat_mum) - 1)

    # Create children by slicing and combining parts from both parents.
    child1 = flat_mum[:split1] + flat_dad[split1:split2] + flat_mum[split2:]
    child2 = flat_dad[:split1] + flat_mum[split1:split2] + flat_dad[split2:]

    # Reshape flat children back into ANN expressed as layers.
    def reshape_to_layers(
        flat_ann: list, layers: list[int]
    ) -> list[list[dict]]:
        reshaped = []
        index = 0
        for layer_size in layers:
            reshaped.append(flat_ann[index : index + layer_size])
            index += layer_size
        return reshaped

    child1 = {
        "layers": reshape_to_layers(child1, mum["structure"][1:]),
        "structure": mum["structure"],
        "fitness": None,
    }
    child2 = {
        "layers": reshape_to_layers(child2, dad["structure"][1:]),
        "structure": dad["structure"],
        "fitness": None,
    }
    return child1, child2


def mutate(
    ann: dict, mutation_chance: float = 0.01, mutation_amount: float = 0.1
) -> dict:
    """
    Mutate the `ann` by randomly adjusting weights and biases. Return the
    mutated ANN.

    The `mutation_chance` determines the likelihood of each weight or bias
    being mutated. A higher `mutation_chance` means more frequent changes.

    The randomly selected weight or bias has its value changed by a small
    random amount within the -/+ `mutation_amount` range.
    """
    for layer in ann["layers"]:
        for node in layer:
            # Mutate weights
            for i in range(len(node["weights"])):
                if random.random() < mutation_chance:
                    node["weights"][i] += random.uniform(
                        -mutation_amount, mutation_amount
                    )
            # Mutate bias
            if random.random() < mutation_chance:
                node["bias"] += random.uniform(
                    -mutation_amount, mutation_amount
                )
    return ann


def simple_generate(
    old_population: list[dict],
    fittest_proportion: float = 0.5,
    mutation_chance: float = 0.01,
    mutation_amount: float = 0.1,
) -> list[dict]:
    """
    Generate a new population of ANNs by performing crossover and mutation
    on the `old_population`.

    The new population is created by selecting the fittest ANNs from the
    `old_population`. The fittest proportion is defined by the
    `fittest_proportion` argument, where 0.5 means half of the
    `old_population` is used as parents.

    The new population is filled with children created from pairs of parents
    selected using roulette wheel selection. Each pair of parents undergoes
    crossover to produce two children, which are then mutated. The new
    population is returned, which should be the same size as the
    `old_population`.

    The `mutation_chance` and `mutation_amount` parameters control the
    mutation process for the children and are passed to the `mutate`
    function.
    """
    old_length = len(old_population)
    # Select the fittest proportion of the old_population as parents.
    split_index = int(old_length * fittest_proportion)
    parents = old_population[:split_index]
    new_population = parents.copy()
    # Fill in the rest of the new_population with children created from the
    # fittest parents of the old_population.
    while len(new_population) < old_length:
        mum = roulette_wheel_selection(parents)
        dad = roulette_wheel_selection(parents)
        child1, child2 = crossover(mum, dad)
        new_population.append(mutate(child1, mutation_chance, mutation_amount))
        new_population.append(mutate(child2, mutation_chance, mutation_amount))
    return new_population[:old_length]


def evolve(
    layers: list[int],
    population_size: int,
    fitness_function: callable,
    halt_function: callable,
    generate_function: callable = simple_generate,
    fittest_proportion: float = 0.5,
    mutation_chance: float = 0.01,
    mutation_amount: float = 0.1,
    reverse: bool = True,
    log: callable = lambda x: None,
):
    """
    Evolve a population of ANNs using a genetic algorithm.

    The `layers` define the topology of the ANNs as a list of layer sizes (as
    per the `create_ann` function in this module). The `population_size` is an
    integer defining the number of ANNs in each generation.

    The `fitness_function` takes an individual ANN to evaluate and the current
    population (of siblings), and returns a fitness score that is annotated
    as the network's `ann["fitness"]` value. The `halt_function` takes the
    current population and generation count to determine if the genetic
    algorithm should stop.

    The `generate_function` should take a list of the current population
    sorted by fitness, along with the optional `fittest_proportion` that
    determines the proportion of the fittest individuals to retain. The
    `mutation_chance`, and `mutation_amount` parameters are used to control
    the mutation process. The `generate_function` returns a new unsorted
    population for the next generation.

    The `reverse` flag indicates if the fittest ANN has the highest (`True`)
    or lowest (`False`) fitness score. Finally, the `log` function can be used
    to log each generation during the course of evolution. It defaults to a
    no-op function that does nothing.

    When the genetic algorithm halts, it returns the final population
    ordered by fitness.
    """
    # Create initial population
    seed_generation = [create_network(layers) for _ in range(population_size)]
    # Sort it by fitness
    for ann in seed_generation:
        ann["fitness"] = fitness_function(ann, seed_generation)
    current_population = sorted(
        seed_generation,
        key=lambda ann: ann["fitness"],
        reverse=reverse,
    )
    generation_count = 0
    log(current_population)
    # Keep evolving until the halt function returns True.
    while not halt_function(current_population, generation_count):
        generation_count += 1
        new_generation = generate_function(
            current_population,
            fittest_proportion,
            mutation_chance,
            mutation_amount,
        )
        for ann in new_generation:
            ann["fitness"] = fitness_function(ann, new_generation)
        current_population = sorted(
            new_generation,
            key=lambda ann: ann["fitness"],
            reverse=reverse,
        )
        log(current_population)
    return current_population
