import json
import random
import sann
from pyscript import when
from pyscript.web import page, div, tr, td

# Define file paths for the ANN and testing dataset.
trained_nn = "trained_nn.json"
test_file = "test_data.json"

# Load the ANN and testing dataset.
with open(trained_nn, "r") as nn:
    ann = json.load(nn)
with open(test_file, "r") as data:
    test_data = json.load(data)


@when("click", "#again")
def main(e=None):
    # Randomly select a character from the test dataset.
    character = random.choice(test_data)
    img, expected = character
    # Categorize it.
    outputs = sann.run_network(ann, img)
    result = outputs.index(max(outputs))
    # Display it.
    digit_table = page.find("#digit")[0]
    digit_table.innerHTML = ""
    row = tr()
    for i, shade in enumerate(img):
        if i % 8 == 0 and i > 1:
            digit_table.append(row)
            row=tr()
        greyscale = int((1.0 - shade) * 15)
        h = hex(greyscale)[2:]
        color = f"#{h}{h}{h}"
        box = td(div(f"{shade:.2f}", style={
            "aspect-ratio": "1/1",
            "color": "red",
        }), style={
            "width": "12.5%",
            "position": "relative",
            "background-color": color,
        })
        box.style["border"] = "1px #dfdfdf solid"
        row.append(box)
    digit_table.append(row)        
    # Display the result.
    span = page.find("#result")[0]
    if result == expected:
        # It was a correct classification.
        span.style["color"] = "green"
        span.innerHTML = str(result) + " ✅"
    else:
        # Incorrect!
        span.style["color"] = "red"
        span.innerHTML = f"{result} ❌ (expected {expected})"
    waiting = page.find("#waiting")[0]
    finished = page.find("#finished")[0]
    waiting.style["display"] = "none"
    finished.style["display"] = "block"

main()