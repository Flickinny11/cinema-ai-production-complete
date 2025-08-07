#!/usr/bin/env python3
"""
Test Cinema AI Production Pipeline
"""

import asyncio
import logging
from cinema_pipeline import CinemaPipeline, Scene

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pipeline():
    """Test the production pipeline"""

    logger.info("="*60)
    logger.info("🎬 Cinema AI Production Pipeline Test")
    logger.info("="*60)

    # Initialize pipeline
    pipeline = CinemaPipeline()

    # Test Scene 1: Simple dialogue scene
    scene1 = Scene(
        id="test_001",
        description="A astronaut stands on Mars, looking at Earth in the sky. Red dust swirls around. Camera slowly zooms in on the astronaut's face showing determination",
        duration=10,
        resolution="720p",
        fps=30,
        dialogue=[
            {
                "character": "Astronaut",
                "text": "Houston, we have successfully landed on Mars. This is a historic moment for humanity.",
                "emotion": "proud"
            }
        ],
        environment="Mars surface, red desert, Earth visible in sky",
        camera_movements=["slow zoom in", "pan up to Earth"],
        sound_effects=["wind", "radio static"],
        music_mood="epic inspiring",
        emotion_expressions=["determined", "proud", "hopeful"]
    )

    logger.info("\n📽️ Test 1: Mars Landing Scene")
    result1 = await pipeline.process_complete_scene(scene1)
    logger.info(f"✅ Result: {result1}")

    # Test Scene 2: Action scene with music
    scene2 = Scene(
        id="test_002",
        description="A samurai warrior battles in a bamboo forest during a thunderstorm. Lightning illuminates the scene. Fast-paced sword fighting with dramatic movements",
        duration=15,
        resolution="1080p",
        fps=30,
        environment="Bamboo forest, rain, lightning, night",
        camera_movements=["dynamic tracking", "quick cuts", "slow motion moments"],
        sound_effects=["thunder", "rain", "sword clashing", "footsteps"],
        music_mood="intense action orchestral",
        emotion_expressions=["fierce", "focused"]
    )

    logger.info("\n📽️ Test 2: Samurai Battle Scene")
    result2 = await pipeline.process_complete_scene(scene2)
    logger.info(f"✅ Result: {result2}")

    # Test Scene 3: Emotional dialogue with voice cloning
    scene3 = Scene(
        id="test_003",
        description="Two characters have an emotional conversation by a lake at sunset. Close-up shots of faces showing deep emotions",
        duration=20,
        resolution="720p",
        fps=24,
        dialogue=[
            {
                "character": "Sarah",
                "text": "I've been waiting for you all these years. I never gave up hope.",
                "emotion": "tearful joy"
            },
            {
                "character": "John",
                "text": "I'm sorry it took so long. I promise I'll never leave again.",
                "emotion": "remorseful"
            },
            {
                "character": "Sarah",
                "text": "Let's not waste another moment. We have so much lost time to make up for.",
                "emotion": "hopeful"
            }
        ],
        environment="Lakeside at sunset, golden hour lighting",
        camera_movements=["close-up faces", "over-shoulder shots", "slow push in"],
        sound_effects=["gentle waves", "birds"],
        music_mood="emotional romantic piano",
        emotion_expressions=["tearful", "joyful", "loving"]
    )

    logger.info("\n📽️ Test 3: Emotional Dialogue Scene")
    result3 = await pipeline.process_complete_scene(scene3)
    logger.info(f"✅ Result: {result3}")

    logger.info("\n="*60)
    logger.info("✅ All tests completed successfully!")
    logger.info("="*60)

async def test_models_individually():
    """Test each model component individually"""

    logger.info("🧪 Testing individual model components...")

    pipeline = CinemaPipeline()

    # Test video generation
    if pipeline.models.get("ltx"):
        logger.info("Testing LTX-Video...")
        test_scene = Scene(
            id="ltx_test",
            description="A beautiful sunset over the ocean with waves",
            duration=5,
            resolution="720p"
        )
        video = await pipeline.generate_video(test_scene)
        logger.info(f"✅ LTX-Video: {video}")

    # Test music generation
    if pipeline.models.get("musicgen"):
        logger.info("Testing MusicGen...")
        test_scene = Scene(
            id="music_test",
            description="Test",
            duration=10,
            music_mood="epic orchestral"
        )
        audio = await pipeline._generate_music(test_scene)
        logger.info(f"✅ MusicGen: {audio}")

    # Test TTS
    if pipeline.models.get("tts"):
        logger.info("Testing XTTS...")
        test_scene = Scene(
            id="tts_test",
            description="Test",
            dialogue=[{"character": "Test", "text": "Hello, this is a test of the text to speech system."}]
        )
        dialogue = await pipeline._generate_dialogue(test_scene)
        logger.info(f"✅ XTTS: {dialogue}")

    logger.info("✅ Individual model tests complete!")

def main():
    """Main test function"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--individual":
        asyncio.run(test_models_individually())
    else:
        asyncio.run(test_pipeline())

if __name__ == "__main__":
    main()
