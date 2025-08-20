#!/usr/bin/env python3

# TODO: Add proper type annotations
# type: ignore

"""
Example of using the experimental replicate.use() interface
"""

import replicate

print("Testing replicate.use() functionality...")

# Test 1: Simple text model
print("\n1. Testing simple text model...")
try:
    hello_world = replicate.use("replicate/hello-world")
    result = hello_world(text="Alice")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Test 2: Image generation model
print("\n2. Testing image generation model...")
try:
    from replicate.lib._predictions_use import get_path_url

    flux_dev = replicate.use("black-forest-labs/flux-dev")
    outputs = flux_dev(
        prompt="a cat wearing a wizard hat, digital art",
        num_outputs=1,
        aspect_ratio="1:1",
        output_format="webp",
        guidance=3.5,
        num_inference_steps=28,
    )
    print(f"Generated output: {outputs}")
    if isinstance(outputs, list):
        print(f"Generated {len(outputs)} image(s)")
        for i, output in enumerate(outputs):
            print(f"  Image {i}: {output}")
            # Get the URL without downloading
            url = get_path_url(output)
            if url:
                print(f"  URL: {url}")
    else:
        print(f"Single output: {outputs}")
        url = get_path_url(outputs)
        if url:
            print(f"  URL: {url}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

# Test 3: Language model with streaming
print("\n3. Testing language model with streaming...")
try:
    llama = replicate.use("meta/meta-llama-3-8b-instruct", streaming=True)
    output = llama(prompt="Write a haiku about Python programming", max_tokens=50)
    print("Streaming output:")
    for chunk in output:
        print(chunk, end="", flush=True)
    print()
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

# Test 4: Using async
print("\n4. Testing async functionality...")
import asyncio


async def test_async():
    try:
        hello_world = replicate.use("replicate/hello-world", use_async=True)
        result = await hello_world(text="Bob")
        print(f"Async result: {result}")

        print("\n4b. Testing async streaming...")
        llama = replicate.use("meta/meta-llama-3-8b-instruct", streaming=True, use_async=True)
        output = await llama(prompt="Write a short poem about async/await", max_tokens=50)
        print("Async streaming output:")
        async for chunk in output:
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(test_async())

print("\nDone!")
