"""
Test file for the sann package, using PyTest.

To run the tests, in your virtual environment with all the requirements
installed, use the command: make check

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

import sann
import pytest
import random
from unittest.mock import MagicMock


@pytest.fixture
def sample_ann():
    """
    Fixture to create a sample artificial neural network (ANN) for testing.
    This ANN has 2 layers: an input layer with 3 nodes and an output layer
    with 2 nodes.
    """
    return sann.create_network([3, 2])


def test_sigmoid():
    """
    Test the sigmoid activation function.
    The sigmoid function should return a value between 0 and 1.
    """
    assert 0 <= sann.sigmoid(0) <= 1
    assert 0 <= sann.sigmoid(1) <= 1
    assert 0 <= sann.sigmoid(-1) <= 1
    assert 0 <= sann.sigmoid(100) <= 1
    assert 0 <= sann.sigmoid(-100) <= 1


def test_create_network(sample_ann):
    """
    Test the creation of an ANN with 2 layers.
    The first layer should have 3 nodes and the second layer should have 2
    nodes.
    """
    assert len(sample_ann["layers"]) == 1  # One layer after input layer
    assert len(sample_ann["layers"][0]) == 2  # Two nodes in the output layer
    assert (
        len(sample_ann["layers"][0][0]["weights"]) == 3
    )  # A node has weights for 3 inputs
    assert "bias" in sample_ann["layers"][0][0]  # A node should have a bias


def test_create_network_too_few_layers():
    """
    Test the creation of an ANN with too few layers.
    The function should raise a ValueError if the number of layers is less than 2.
    """
    with pytest.raises(ValueError):
        sann.create_network([3])  # Only one layer provided


def test_run_network(sample_ann):
    """
    Test the forward pass through the ANN with sample inputs.
    The inputs should be a list of 3 values corresponding to the input
    layer.
    """
    inputs = [0.5, 0.2, 0.8]
    outputs = sann.run_network(sample_ann, inputs)

    # Check that the output is a list of length equal to the number
    # of nodes in the output layer
    assert len(outputs) == 2
    assert all(
        0 <= output <= 1 for output in outputs
    )  # Outputs should be between 0 and 1


def test_clean_network(sample_ann):
    """
    Test the cleaning of the ANN by removing outputs from the nodes.
    """
    inputs = [0.5, 0.2, 0.8]
    # Perform a forward pass to populate outputs
    sann.run_network(sample_ann, inputs)
    # Check that outputs are present before cleaning
    assert "output" in sample_ann["layers"][0][0]
    # Clean the ANN to remove outputs
    cleaned_ann = sann.clean_network(sample_ann)
    assert "output" not in cleaned_ann["layers"][0][0]


def test_backpropagate():
    """
    Test the backpropagation of errors through the ANN.

    This will check if the weights are updated correctly after a forward pass
    and backpropagation.
    """
    # Create a sample ANN with a hidden layer and an output layer.
    sample_ann = sann.create_network([3, 5, 2])
    # Set the weights and biases to known values for testing.
    sample_ann["layers"][0][0]["weights"] = [0.5, 0.2, 0.8]
    sample_ann["layers"][0][0]["bias"] = 0
    # Perform a forward pass with sample inputs.
    inputs = [0.5, 0.2, 0.8]
    expected_outputs = [1, 0]  # Expected output for the test.
    outputs = sann.run_network(sample_ann, inputs)

    # Perform backpropagation.
    sann.backpropagate(sample_ann, inputs, expected_outputs)

    # Check if weights have been updated (not equal to initial state).
    assert sample_ann["layers"][0][0]["weights"] != [
        0.5,
        0.2,
        0.8,
    ]  # Example check.
    assert (
        sample_ann["layers"][0][0]["bias"] != 0
    )  # Bias should also be updated.

    # Check if the outputs after backpropagation are different.
    new_outputs = sann.run_network(sample_ann, inputs)
    # Outputs should change after backpropagation.
    assert new_outputs != outputs
    # Outputs should still be valid.
    assert all(0 <= output <= 1 for output in new_outputs)


def test_train(sample_ann):
    """
    Test the training of the ANN with sample data.
    This will check if the ANN can be trained and if the weights are updated.
    """
    # Update the sample ANN to have some known weights and biases.
    sample_ann["layers"][0][0]["weights"] = [0.5, 0.2, 0.8]
    sample_ann["layers"][0][0]["bias"] = 0

    # Sample training data: list of tuples (inputs, expected_output)
    train_data = [
        ([0.5, 0.2, 0.8], [1, 0]),
        ([0.1, 0.4, 0.6], [0, 1]),
    ]

    # Mock the log function to avoid printing during tests
    log = MagicMock()

    # Train the ANN
    sann.train(sample_ann, train_data, epochs=10, learning_rate=0.1, log=log)

    # Check if weights have been updated after training.
    assert sample_ann["layers"][0][0]["weights"] != [0.5, 0.2, 0.8]
    # Check if the bias has been updated.
    assert sample_ann["layers"][0][0]["bias"] != 0
    # Check the log function was called
    log.assert_called()


def test_roulette_wheel_selection():
    """
    Test the roulette wheel selection function for selecting parents based on fitness.
    """
    # Create 5 sample ANN with associated fitness values.
    anns = [sann.create_network([3, 5, 2]) for _ in range(5)]
    for ann in anns:
        ann["fitness"] = random.uniform(0, 1)  # Assign random fitness values

    result = sann.roulette_wheel_selection(anns)

    # Check the result is one of the ANNs.
    assert result in anns
    # Check that the selected ANN has a fitness value.
    assert "fitness" in result


def test_roulette_wheel_selection_zero_total_fitness():
    """
    Test the roulette wheel selection function when all fitness values are zero.
    """
    # Create 5 sample ANN with zero fitness values.
    anns = [sann.create_network([3, 5, 2]) for _ in range(5)]
    for ann in anns:
        ann["fitness"] = 0

    result = sann.roulette_wheel_selection(anns)

    # Check the result is one of the ANNs.
    assert result in anns
    # Check that the selected ANN has a fitness value.
    assert "fitness" in result


def test_crossover():
    """
    Test the crossover function for combining two parent ANNs.
    """
    # Create two sample ANNs (parents).
    mum = sann.create_network([3, 5, 2])
    dad = sann.create_network([3, 5, 2])

    # Perform crossover.
    child1, child2 = sann.crossover(mum, dad)

    # Check that the children have the same structure as the parents.
    assert len(child1["layers"]) == len(mum["layers"])
    assert len(child2["layers"]) == len(dad["layers"])
    for layer in child1["layers"] + child2["layers"]:
        assert all("weights" in node and "bias" in node for node in layer)


def test_mutate():
    """
    Test the mutation function for randomly adjusting weights and biases of an ANN.
    """
    # Create a sample ANN.
    ann = sann.create_network([3, 5, 2])

    # Store original weights and biases for comparison.
    original_weights = [
        node["weights"] for layer in ann["layers"] for node in layer
    ]
    original_biases = [
        node["bias"] for layer in ann["layers"] for node in layer
    ]

    # Perform mutation and set the mutation_chance to 1.0 for testing. All weights
    # and biases should change.
    mutated_ann = sann.mutate(ann, mutation_chance=1.0)

    # Check that at least one weight or bias has changed.
    assert any(
        original != mutated
        for original, mutated in zip(
            original_weights,
            [
                node["weights"]
                for layer in mutated_ann["layers"]
                for node in layer
            ],
        )
    ) or any(
        original != mutated
        for original, mutated in zip(
            original_biases,
            [
                node["bias"]
                for layer in mutated_ann["layers"]
                for node in layer
            ],
        )
    )


def test_simple_generate():
    """
    Test the simple_generate function for creating a new population of ANNs.
    """
    old_population = [sann.create_network([3, 5, 2]) for _ in range(10)]
    # Create test fitness values for the old population.
    for ann in old_population:
        ann["fitness"] = random.uniform(0, 1)
    # Generate the new population from the old.
    new_population = sann.simple_generate(
        old_population, fittest_proportion=0.5
    )
    # Check that the new population is the same size as the old population.
    assert len(new_population) == len(old_population)
    # Check that the new population is not the same as the old population.
    assert new_population != old_population


def test_evolve():
    """
    Ensure the process of evolving a population of ANNs proceeds in the
    expected manner.

    This test ONLY checks that the evolution process runs without errors.
    It does not validate the correctness of the evolution logic (supplied
    by the developer).
    """

    def fitness_function(ann, current_population):
        """
        This function merely sums the network's weights and bias to determine
        its "fitness", for testing purposes. This is an arbitrarily stupid
        fitness function that should be replaced with a more meaningful one.
        """
        return sum(
            sum(node["weights"]) + node["bias"]
            for layer in ann["layers"]
            for node in layer
        )

    def halt(current_population, generation_count):
        """
        Determine if the evolution process should halt.
        This is a mock function for testing purposes.
        """
        return generation_count == 10  # Halt after 10 generations

    log = MagicMock()

    result = sann.evolve(
        layers=[3, 5, 2],
        population_size=10,
        fitness_function=fitness_function,
        halt_function=halt,
        log=log,
    )

    # The log function should be called.
    log.assert_called()
    # Check that the result is a list of ANNs.
    assert isinstance(result, list)
    # The length of the result should be equal to the population size.
    assert len(result) == 10
    # Each ANN in the result has a fitness value.
    assert all("fitness" in ann for ann in result)
    # The order of the result is based on fitness.
    assert all(
        result[i]["fitness"] >= result[i + 1]["fitness"]
        for i in range(len(result) - 1)
    )
