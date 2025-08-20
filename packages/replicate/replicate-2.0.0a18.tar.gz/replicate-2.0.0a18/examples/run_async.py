import asyncio

from replicate import AsyncReplicate

replicate = AsyncReplicate()

# https://replicate.com/stability-ai/sdxl
model_version = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
prompts = [f"A chariot pulled by a team of {count} rainbow unicorns" for count in ["two", "four", "six", "eight"]]


async def main() -> None:
    # Create tasks with asyncio.gather directly
    tasks = [replicate.run(model_version, input={"prompt": prompt}) for prompt in prompts]

    results = await asyncio.gather(*tasks)
    print(results)


asyncio.run(main())
