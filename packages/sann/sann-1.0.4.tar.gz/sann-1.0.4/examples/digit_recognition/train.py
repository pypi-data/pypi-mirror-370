"""
Training script for a simple digit recognition model using a feedforward neural network
as defined in the `sann` module and otherwise standard Python. This script loads the
optdigits.tra and optdigits.tes datasets, trains the model with the .tra data, and
evaluates its performance with the .tes data.

Since this should work with MicroPython the script does not use any external libraries
other than those in the (MicroPython) Python standard library.

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
import sann
from rich.progress import Progress


def load_data(file_path):
    """
    Load the dataset from the specified file path. The dataset is expected to be in a
    CSV format where each line contains pixel values followed by the label. The pixel
    values are integers representing grayscale values (0-16) and the label is an
    integer from 0 to 9 representing the digit class. The pixel values are normalized
    by dividing by 16 to scale them to the range [0, 1].
    """
    data = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            pixels = [pixel / 16 for pixel in list(map(int, parts[:-1]))]
            label = int(parts[-1])
            data.append((pixels, label))
    return data


def preprocess_data(data):
    """
    Preprocess the dataset by converting labels to the expected output layer format
    for the ANN.
    """
    processed_data = []
    for pixels, label in data:
        output_layer = [0] * 10
        output_layer[label] = 1
        processed_data.append((pixels, output_layer))
    return processed_data


def train_model(train_data, layers, epochs=1000, learning_rate=0.1, log=print):
    """
    Train a simple artificial neural network (ANN) using the provided training data.

    Args:
        train_data: List of tuples (pixels, output) for training.
        layers: List defining the structure of the ANN (e.g., [64, 32, 10]).
        epochs: Number of training iterations.
        learning_rate: Learning rate for weight updates.

    Returns:
        The trained ANN model.
    """
    # Initialize the ANN with the specified layers
    ann = sann.create_network(layers)

    # Train the ANN
    sann.train(
        ann, train_data, epochs=epochs, learning_rate=learning_rate, log=log
    )

    return ann


def evaluate_model(ann, test_data):
    """
    Evaluate the trained ANN model using the test data.

    Args:
        ann: The trained ANN model.
        test_data: List of tuples (pixels, label) for testing.

    Returns:
        The accuracy of the model on the test data.
    """
    correct_predictions = 0
    for pixels, label in test_data:
        outputs = sann.run_network(ann, pixels)
        predicted_label = outputs.index(max(outputs))
        if predicted_label == label:
            correct_predictions += 1
    accuracy = correct_predictions / len(test_data)
    return accuracy


def main():
    # Define file paths for training and testing datasets
    train_file = "optdigits.tra"
    test_file = "optdigits.tes"

    # Load training and testing data
    train_data = preprocess_data(load_data(train_file))
    test_data = load_data(test_file)

    # Number of epochs to train over
    epochs = 100

    # Learning rate (rate of change as weights are adjusted)
    learning_rate = 0.1

    # Define the ANN structure (input layer, hidden layer, output layer)
    layers = [
        64,
        32,
        10,
    ]  # Example: 64 input nodes, 32 hidden nodes, 10 output nodes

    # Will eventually hold the best ANN found during training.
    best_ann = {}

    # The best accuracy score for the ANN to beat.
    best_accuracy = 0

    with Progress() as progress:
        training_task = progress.add_task("Training network", total=epochs)

        def handle_log(data):
            if isinstance(data, dict):
                accuracy = evaluate_model(data, test_data)
                nonlocal best_accuracy
                if accuracy > best_accuracy:
                    nonlocal best_ann
                    best_accuracy = accuracy
                    best_ann = dict(data)
                progress.update(
                    training_task,
                    advance=1,
                    description=f"Model accuracy: {accuracy * 100:.2f}%",
                )

        # Train the model
        ann = train_model(
            train_data,
            layers,
            epochs=epochs,
            learning_rate=learning_rate,
            log=handle_log,
        )

        # Remove the outputs stored in nodes to clean up the ANN
        ann = sann.clean_network(ann)

    with open("nn.json", "w") as f:
        json.dump(best_ann, f, indent=2)


if __name__ == "__main__":
    main()
