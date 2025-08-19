# Tanks A Lot!

[The source code for this example is here.](https://github.com/ntoll/sann/tree/main/examples/tanksalot)

Artificial neural networks are not the answer to everything. Working with
them requires care and attention, and sometimes a hard coded solution is
an easier way to the same result!

This example project, where neural networks control virtual and real-world
"tank bots" demonstrates these limitations.

## And now for something completely different...

These complexities are beautifully illustrated by an urban myth about Regan 
era research into the use of 
[neural networks to help tank crews](https://gwern.net/tank)
identify friend or foe in the fog of war of a tank battle.

It goes something like this...

Millions of dollars were spent training a neural network on images of Soviet
and American tanks so, in theory, the artificial neural network would
be able to quickly classify the vehicle as friend or foe. After training, 
the artificial neural network was checked against the unseen test data from
the same corpus of photographs. It passed with flying colours! 

The next step involved testing with actual hardware on a simulated 
battlefield. 

That's when things went wrong.

The artificial neural network was mis-categorising friends as foes (and vice 
versa), and demonstrating eccentric yet dangerous behaviour, like identifying
a tree or the local wildlife as an enemy. Millions of dollars later engineers
realised the problem was both simple and stupid.

In the photographic corpus, all the Soviet tanks had been photographed in the
sunshine, whereas all the American tanks had be photographed on an overcast 
and cloudy day.

Inadvertently, the neural network had been trained to categorise the weather
(or more specifically, the light conditions).

Soon after came the [AI winter](https://en.wikipedia.org/wiki/AI_winter) - 
where the over-promised capabilities of AI were called out and funding dried 
up.

## Bots with Brains

This example makes use of "tank bots" that trundle around the world. They
have two motors to drive forwards, and turning is made possible by changing
the speed of rotation of the motors so one is faster than the other (just
like how tanks steer - hence the name). The bots all have a single sensor
at the front, to tell their distance from obstacles ahead.

In this example three types of bot were created:

* A simple "stupid" bot, with hard coded rules to tell the bot to rotate one
  direction or another if something was detected ahead.
* Two bots controlled by neural networks:
    - One trained on labelled data that defined the behaviour of the hard
      coded rules in the "dumb" bot.
    - The other evolved from "living" in a virtual world containing
      obstacles and other bots.

All the core bot related code is in the `bot.py` file in this example.

These "bots" were placed into a virtual world to see how they would behave.
Here's how it looks:

<img src="./bots.gif" title="Tank bots."/>

[See these bots running live in your browser](./web/index.html).

The "stupid" bot's hard-coded instructions were:

```python title="Stupid bot's driving instructions."
def drive(self):
    """
    Very stupid hard coded rules for driving the bot.
    """
    # Close obstacle - turn around.
    if (self.distance_reading > 0):
        if self.rotate_direction is None:
            # Select a random direction in which to rotate.
            self.rotate_direction = random.choice([
                (0.0, 1.0),  # Rotate left.
                (1.0, 0.0)  # Rotate right.
            ])
        self.set_motors(*self.rotate_direction)
    else:  # No obstacle detected or far away - move forward.
        self.rotate_direction = None  # Reset rotation direction.
        self.set_motors(0.5, 0.5)  # Gently move forward.
```

Each neural network has an input layer of six nodes: one to indicate no
obstacle detected, with the other five used to indicate how close
a detected obstacle is. The output layer is simply two nodes, whose output
values control the speed of the left and right motors. Twelve nodes make up
the hidden layer in these networks. How did I arrive at twelve nodes in the
hidden layer? Trial and error and intuition.

**It took but five minutes to code the instructions for the "stupid" bot.
It took several evenings and a weekend of work to create the virtual world
in which the neural networks could be tested.**

Furthermore, the initial versions of the labelled data for supervised
learning, and the fitness function for the neuro-evolution required
significant amounts of "tweaking" based upon observations and intuitive
fiddling about.

For instance, the bot trained with labelled data wasn't (at first) sensitive
enough to distance, nor did it turn fast enough. So it ended up constantly
driving into walls.

The neuro-evolved bot was rather entertaining. At first the fitness function
was mostly based on the bot's lifespan (i.e. it didn't crash). But this
resulted in a rotating bot that went nowhere and behaved like this:

<img src="./bot_rotate.gif" title="Going round in circles." style="display: block; margin: auto;"/>

Further iteration of the fitness function involved part of the score being
derived from the number of times the bot moved position. Alas, evolution got
the better of me again:

<img src="./bot_headbanger.gif" title="Oh dear." style="display: block; margin: auto;"/>

In the end, the fitness function's score is derived from all sorts of subtle
and not-so-obvious factors that affect how a bot behaves. It took a number of
attempts to get the training of both supervised and unsupervised networks
correct so vaguely desirable results were obtained. 

To be honest, at times this felt deeply frustrating and more like trial and
error than engineering.

You can see the eventual outcome in the `train.py` and `labelled_data.json`
files in this project.

## Bots encounter the real world...

Out of a sense of fun, I decided to build an actual bot with two motors and
a distance sensor made with parts from the excellent 
[Lego SpikePrime](https://spike.legoeducation.com/) kit.

Here's what it looked like, so you can recreate the bot should you have
access to the necessary Lego kit:

<img src="./spike1.jpg">

<img src="./spike2.jpg">

<img src="./spike3.jpg">

Alternatively, it's quite easy to make an equivalent bot with non-Lego
parts and a microcontroller running MicroPython (such as an ESP32).

The code used to control the Lego bot is found in the `spike_code.py` file
in this example. As you'll see I've extracted only those functions required
from SANN to evaluate the neural network. I updated the code so it ran
without a neural network (as "stupid" bot), and with the two neural networks
trained and evolved in the virtual world. In a sense, I performed a brain
transplant from the virtual world to the real world.

If you use a non-Lego bot, you'll need to update the code for interacting
with the motors and distance sensor.

I used various instrument cases in my music room to act as obstacles in the
real world, and let the different versions of the bot loose. I think the
results speak for themselves (and are best accompanied by music):

<div>
  <div style="position:relative;padding-top:56.25%;">
<iframe src="https://www.youtube-nocookie.com/embed/QPu2aA2oq_w?si=N64ow43IXMnlANzp" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" 
style="position:absolute;top:0;left:0;width:100%;height:100%;" allowfullscreen></iframe>
  </div>
</div>

## Your challenge

Apart from the creation of a 2d virtual world in which to run and train the
bots, this example was created relatively quickly. The real-world Lego based
bot could definitely be refined and I strongly suspect the quality and
behaviour of the sensor had a lot to do with the end result. Furthermore, I
believe this example demonstrates just how difficult it is to create a useful
neural network that has to interact with the real world in any way. The cost
of training, time taken to refine the quality of the training data or fitness
function, and the fact that the "stupid" bot appears to perform just as well
helps to show that neural networks come with costs.

So, your challenge is to use SANN to improve on my shonky results. Get in
touch and tell me how you get on. Who knows, your work could be a new example
in these docs!

Best of luck!