# SnAIke

This project is an example of unsupervised training (via evolution) of 
a neural network that controls a snake looking for food in a simple 2d
game world. Use the arrow keys to change the direction of the snake, or
click on the `[]`🤖 checkbox to toggle the neuro-evolved AI autopilot.

[Play the game here.](./web/index.html)

[The source code for this example is here.](https://github.com/ntoll/sann/tree/main/examples/snaike)

The network (ANN) receives 8 inputs representing the game state:

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

See the configuration values at the start of `train.py` for the settings
that refine the neuro-evolutionary process. The `fitness_function` and
`halt_function` control the specifics of the evolutionary process.

Just run the `train.py` script to emit a JSON representation of the
trained neural network (saved as the file, `fittest_ann.json`).