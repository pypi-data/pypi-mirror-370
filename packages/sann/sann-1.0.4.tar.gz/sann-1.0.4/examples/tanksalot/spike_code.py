"""
Code to be run on the LEGO Spike prime.

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

from hub import port
import motor, distance_sensor
import random
import math
import runloop


# Update this dict with the trained ANN model. A brain transplant!
ann = {}


class Bot:
    """
    A class representing a bot that controls a LEGO Spike prime robot. This
    closely mimics the behavior defined in the bot.py module, but is truncated
    due to the size limitations of the Spike Prime hardware.
    """

    def __init__(self, brain=None):
        self.distance_reading = 0
        # Motor speed boost factor.
        self.boost = 10000
        self.rotate_direction = None
        self.brain = brain

    def set_motors(self, left, right):
        l_boost = int(left * self.boost)
        r_boost = -int(right * self.boost)
        print(l_boost, r_boost)
        motor.run(port.A, l_boost)
        motor.run(port.B, r_boost)

    def engage(self):
        self.detect_distance()
        self.drive()

    def detect_distance(self):
        cm = distance_sensor.distance(port.E) / 10
        result = 0
        if cm < 25:
            result = max(1, int(cm / 5))
        self.distance_reading = result

    def input_layer(self):
        input_layer = [0.0 for _ in range(6)]
        input_layer[self.distance_reading] = 1.0
        return input_layer

    def drive(self):
        if self.brain:
            # Use the neural network.
            output_layer = self.run_network(self.brain, self.input_layer())
            self.set_motors(output_layer[0], output_layer[1])
        else:
            # Fall back to hard-coded stupid bot! ;-)
            if self.distance_reading:
                if self.rotate_direction is None:
                    self.rotate_direction = random.choice(
                        [(0.0, 1.0), (1.0, 0.0)]
                    )
                self.set_motors(*self.rotate_direction)
            else:
                self.rotate_direction = None
                self.set_motors(0.5, 0.5)

    # The following three methods are copied from SANN and implement the core
    # functionality of the neural network.
    def sum_inputs(self, inputs):
        return sum([x * w for x, w in inputs])

    def sigmoid(self, activation, threshold=0.0, shape=0.5):
        return 1 / (1 + math.exp(-((activation - threshold) / shape)))

    def run_network(self, ann, input_layer: list):
        output_layer = input_layer
        for layer in ann["layers"]:
            new_outputs = []
            for node in layer:
                activation = self.sum_inputs(
                    zip(output_layer, node["weights"])
                )
                new_outputs.append(self.sigmoid(activation, node["bias"]))
            output_layer = new_outputs
        return output_layer


async def main(bot):
    while True:
        await runloop.sleep_ms(100)
        bot.engage()


bot = Bot(brain=ann)


runloop.run(main(bot))
