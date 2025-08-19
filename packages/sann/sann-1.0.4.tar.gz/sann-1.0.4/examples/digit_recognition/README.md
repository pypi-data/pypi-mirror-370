# Numeric Digit Recognition

This is an interesting, if contrived, example of how artificial neural 
networks allow computers to do character recognition. Put simply, this
project trains a neural network to recognise the digits 0-9 from 
handwritten input.

[See the network categorize digits here.](./web/index.html)

[The source code for this example is here.](https://github.com/ntoll/sann/tree/main/examples/digit_recognition)

The data used for training and testing is contained in the 
`optdigits.tra` (training) and `optdigits.tes` (testing) files. The
`optdigits.names` file contains a description of the size and shape of
the data. The source of this data is the 
[Optical Recognition of Handwritten Digits](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits),
a [Creative Commons](https://creativecommons.org/licenses/by/4.0/legalcode)
licensed dataset containing 5620 images pre-organised into training and
testing sets.

Just run the `train.py` script to emit a JSON representation of the
trained neural network (saved as the file, `nn.json`).