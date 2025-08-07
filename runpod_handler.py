#!/usr/bin/env python3
"""
RunPod Serverless Handler - Production Ready
August 2025 Edition
"""

import runpod
import torch
import asyncio
import logging
import json
import traceback
import os
import time
from typing import Dict, List, Optional
from cinema_pipeline import CinemaPipeline, Scene, cleanup
from dataclasses import field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline = None

def initialize():
    """Initialize pipeline on cold start"""
    global pipeline
    if pipeline is None:
        logger.info("="*60)
        logger.info("🎬 Cinema AI Production Pipeline v2.0")
        logger.info("="*60)
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"VRAM: {vram:.1f}GB")

            # Log model capabilities based on VRAM
            if vram >= 80:
                logger.info("✅ Full Cinema Mode: All models enabled")
                logger.info("  • HunyuanVideo (13B) - Cinema quality")
                logger.info("  • LTX-Video (13B) - Real-time generation")
                logger.info("  • MusicGen-Large - Orchestral music")
                logger.info("  • AudioGen-Medium - Sound effects")
                logger.info("  • XTTS-v2 - Voice cloning")
            elif vram >= 40:
                logger.info("⚡ Balanced Mode: Optimized models")
                logger.info("  • LTX-Video (13B) - Fast generation")
                logger.info("  • MusicGen-Medium - Music generation")
                logger.info("  • XTTS-v2 - Voice cloning")
            else:
                logger.info("🚀 Fast Mode: Consumer GPU optimized")
                logger.info("  • LTX-Video (Quantized) - Quick generation")
                logger.info("  • Basic audio models")

        logger.info("="*60)
        logger.info("Initializing pipeline...")

        pipeline = CinemaPipeline()

        logger.info("✅ Pipeline ready for production!")
        logger.info("="*60)

async def process_script(job_input: Dict) -> Dict:
    """Process a full script into multiple scenes"""
    script = job_input.get("script", "")
    if not script:
        return {"error": "No script provided"}

    options = job_input.get("options", {})

    # Use DeepSeek to process script
    processed = await pipeline.process_script(script, options)
    scenes = processed['scenes']

    logger.info(f"📽️ Processing {len(scenes)} scenes from script")

    results = []
    total_start = time.time()

    for i, scene in enumerate(scenes):
        logger.info(f"Scene {i+1}/{len(scenes)}: {scene.id}")
        scene_start = time.time()

        try:
            result = await pipeline.process_complete_scene(scene)
            result["scene_number"] = i + 1
            result["scene_time"] = time.time() - scene_start
            results.append(result)

            # Log progress
            logger.info(f"  ✅ Scene {i+1} completed in {result['scene_time']:.1f}s")

        except Exception as e:
            logger.error(f"  ❌ Scene {i+1} failed: {e}")
            results.append({
                "scene_id": scene.id,
                "scene_number": i + 1,
                "error": str(e)
            })

    total_time = time.time() - total_start

    return {
        "status": "success",
        "scenes": results,
        "total_scenes": len(scenes),
        "total_processing_time": total_time,
        "average_scene_time": total_time / len(scenes) if scenes else 0,
        "metadata": processed.get('metadata', {})
    }

async def process_single_scene(job_input: Dict) -> Dict:
    """Process a single scene"""
    scene_data = job_input.get("scene", {})

    # Create Scene object from input
    scene = Scene(
        id=scene_data.get("id", f"scene_{int(time.time())}"),
        description=scene_data.get("description", ""),
        duration=scene_data.get("duration", 5),
        resolution=scene_data.get("resolution", "720p"),
        fps=scene_data.get("fps", 30),
        characters=scene_data.get("characters", []),
        dialogue=scene_data.get("dialogue", []),
        environment=scene_data.get("environment", ""),
        camera_movements=scene_data.get("camera_movements", []),
        sound_effects=scene_data.get("sound_effects", []),
        music_mood=scene_data.get("music_mood", ""),
        emotion_expressions=scene_data.get("emotion_expressions", []),
        voice_clone_samples=scene_data.get("voice_clone_samples", [])
    )

    logger.info(f"🎬 Processing single scene: {scene.id}")

    result = await pipeline.process_complete_scene(scene)

    return {
        "status": "success",
        **result
    }

def parse_script_to_scenes(script: str, options: Dict) -> List[Scene]:
    """Parse script text into Scene objects"""
    scenes = []

    # Advanced parsing options
    scene_duration = options.get("scene_duration", 10)
    resolution = options.get("resolution", "720p")
    fps = options.get("fps", 30)
    style = options.get("style", "cinematic")

    # Simple parsing - split by double newlines or scene markers
    blocks = script.split("\n\n")

    for i, block in enumerate(blocks):
        if not block.strip():
            continue

        # Parse scene elements
        lines = block.strip().split("\n")
        description = lines[0]

        # Extract dialogue if present
        dialogue = []
        for line in lines[1:]:
            if ":" in line:  # Simple dialogue detection
                character, text = line.split(":", 1)
                dialogue.append({
                    "character": character.strip(),
                    "text": text.strip()
                })

        # Detect camera movements from description
        camera_movements = []
        if "pan" in description.lower():
            camera_movements.append("pan")
        if "zoom" in description.lower():
            camera_movements.append("zoom")
        if "tracking" in description.lower():
            camera_movements.append("tracking shot")

        # Detect mood from description
        music_mood = "cinematic"
        if "action" in description.lower():
            music_mood = "epic action"
        elif "romantic" in description.lower():
            music_mood = "romantic"
        elif "suspense" in description.lower():
            music_mood = "suspenseful"

        scene = Scene(
            id=f"scene_{i+1:03d}",
            description=description,
            duration=scene_duration,
            resolution=resolution,
            fps=fps,
            dialogue=dialogue,
            camera_movements=camera_movements or ["static shot"],
            music_mood=music_mood,
            environment=style
        )

        scenes.append(scene)

    return scenes

async def process_job(job_input: Dict) -> Dict:
    """Main job processing function"""
    request_type = job_input.get("type", "script_to_video")

    logger.info(f"📋 Processing job type: {request_type}")

    try:
        if request_type == "script_to_video":
            return await process_script(job_input)

        elif request_type == "concept_to_script":
            return await process_concept(job_input)

        elif request_type == "single_scene":
            return await process_single_scene(job_input)

        elif request_type == "batch_scenes":
            return await process_batch_scenes(job_input)

        elif request_type == "health_check":
            return {
                "status": "healthy",
                "mode": pipeline.mode if pipeline else "not_initialized",
                "models_loaded": list(pipeline.models.keys()) if pipeline else [],
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
                "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0,
                "capabilities": {
                    "max_duration": 30 if pipeline and pipeline.mode == "cinema" else 15,
                    "max_resolution": "4k" if pipeline and pipeline.mode == "cinema" else "1080p",
                    "voice_cloning": pipeline and "tts" in pipeline.models,
                    "music_generation": pipeline and "musicgen" in pipeline.models,
                    "sound_effects": pipeline and "audiogen" in pipeline.models,
                    "human_sounds": pipeline and pipeline.human_sounds is not None,
                    "script_processing": pipeline and pipeline.script_processor is not None
                }
            }

        elif request_type == "list_models":
            return {
                "status": "success",
                "models": {
                    "video": ["HunyuanVideo-13B", "LTX-Video-13B"],
                    "audio": ["MusicGen-Large", "AudioGen-Medium"],
                    "tts": ["XTTS-v2"],
                    "script": ["DeepSeek-v3"],
                    "active": list(pipeline.models.keys()) if pipeline else []
                }
            }

        else:
            return {"error": f"Unknown request type: {request_type}"}

    except Exception as e:
        logger.error(f"Job processing error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

async def process_concept(job_input: Dict) -> Dict:
    """Process a concept into a full script and videos"""
    concept = job_input.get("concept", "")
    if not concept:
        return {"error": "No concept provided"}

    options = job_input.get("options", {})

    logger.info(f"🎬 Developing concept: {concept[:100]}...")

    # Develop concept into script
    result = await pipeline.develop_concept(concept, options)

    # Process scenes into videos if requested
    if options.get("generate_videos", True) and "processed_scenes" in result:
        scenes = result["processed_scenes"]

        logger.info(f"📽️ Generating {len(scenes)} videos from concept")

        video_results = []
        for scene in scenes:
            try:
                scene_result = await pipeline.process_complete_scene(scene)
                video_results.append(scene_result)
            except Exception as e:
                logger.error(f"Failed to generate video for scene: {e}")
                video_results.append({"error": str(e)})

        result["videos"] = video_results

    return {
        "status": "success",
        "concept": concept,
        "script": result.get("script_text", ""),
        "scenes": result.get("processed_scenes", []),
        "videos": result.get("videos", []),
        "metadata": result.get("metadata", {})
    }

async def process_batch_scenes(job_input: Dict) -> Dict:
    """Process multiple scenes in batch"""
    scenes_data = job_input.get("scenes", [])
    if not scenes_data:
        return {"error": "No scenes provided"}

    logger.info(f"📽️ Processing batch of {len(scenes_data)} scenes")

    results = []
    for scene_data in scenes_data:
        # Create Scene object
        scene = Scene(
            id=scene_data.get("id", f"batch_{int(time.time())}"),
            description=scene_data.get("description", ""),
            duration=scene_data.get("duration", 10),
            resolution=scene_data.get("resolution", "720p"),
            fps=scene_data.get("fps", 30),
            characters=scene_data.get("characters", []),
            dialogue=scene_data.get("dialogue", []),
            environment=scene_data.get("environment", ""),
            camera_movements=scene_data.get("camera_movements", []),
            sound_effects=scene_data.get("sound_effects", []),
            music_mood=scene_data.get("music_mood", ""),
            emotion_expressions=scene_data.get("emotion_expressions", []),
            voice_clone_samples=scene_data.get("voice_clone_samples", [])
        )

        # Add human sounds if specified
        if "human_sounds" in scene_data:
            scene.human_sounds = scene_data["human_sounds"]

        try:
            result = await pipeline.process_complete_scene(scene)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process scene {scene.id}: {e}")
            results.append({"scene_id": scene.id, "error": str(e)})

    return {
        "status": "success",
        "videos": results,
        "total_scenes": len(scenes_data)
    }

def handler(job):
    """RunPod handler function"""
    try:
        # Initialize pipeline
        initialize()

        # Get job input
        job_input = job.get("input", {})
        job_id = job.get("id", "unknown")

        logger.info(f"🎯 Job {job_id} started")
        logger.info(f"Type: {job_input.get('type', 'unknown')}")

        # Process job
        result = asyncio.run(process_job(job_input))

        # Cleanup resources
        cleanup()

        logger.info(f"✅ Job {job_id} completed successfully")

        return result

    except Exception as e:
        logger.error(f"Handler error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    logger.info("🚀 Starting RunPod Cinema AI Worker")
    logger.info("Version: 2.0 - August 2025 Edition")
    logger.info("Models: HunyuanVideo, LTX-Video, MusicGen, AudioGen, XTTS-v2")

    # Set environment variables for optimal performance
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    os.environ["CUDA_LAUNCH_BLOCKING"] = "0"

    # Start the serverless worker
    runpod.serverless.start({"handler": handler})
