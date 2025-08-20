import rich

import replicate

outputs = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "astronaut riding a rocket like a horse"},
)
rich.print(outputs)
for index, output in enumerate(outputs):
    with open(f"output_{index}.webp", "wb") as file:
        file.write(output.read())
