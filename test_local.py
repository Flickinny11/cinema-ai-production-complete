#!/usr/bin/env python3
"""Test the pipeline locally"""

import asyncio
from cinema_pipeline import CinemaPipeline, Scene

async def test():
    print("Testing Cinema Pipeline...")

    # Initialize
    pipeline = CinemaPipeline()

    # Test scene
    scene = Scene(
        id="test-001",
        description="A spaceship flies through space",
        duration=5,
        characters=[],
        dialogue=[],
        environment="Outer space",
        objects=["spaceship", "stars"],
        camera_movements=["tracking shot"],
        sound_effects=["engine hum"],
        music_mood="epic"
    )

    # Process
    result = await pipeline.process_complete_scene(scene)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test())
