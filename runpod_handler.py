#!/usr/bin/env python3
"""
RunPod Serverless Handler
This receives requests and calls the pipeline
"""

import runpod
import torch
import asyncio
import logging
import json
import traceback
from cinema_pipeline import CinemaPipeline, Scene, cleanup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline
pipeline = None

def initialize():
    """Initialize pipeline on cold start"""
    global pipeline
    if pipeline is None:
        logger.info("="*50)
        logger.info("Initializing Cinema Pipeline")
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"VRAM: {vram:.1f}GB")
        logger.info("="*50)

        pipeline = CinemaPipeline()
        logger.info("Pipeline ready!")

async def process_job(job_input):
    """Process the actual job"""
    request_type = job_input.get("type", "script_to_video")

    if request_type == "script_to_video":
        script = job_input.get("script", "")
        if not script:
            return {"error": "No script provided"}

        # Process script
        scenes = await pipeline.process_script(script)
        logger.info(f"Processing {len(scenes)} scenes")

        # Generate each scene
        results = []
        for i, scene in enumerate(scenes):
            logger.info(f"Scene {i+1}/{len(scenes)}")
            result = await pipeline.process_complete_scene(scene)
            results.append(result)

        return {
            "status": "success",
            "scenes": results,
            "total_scenes": len(scenes)
        }

    elif request_type == "health_check":
        return {
            "status": "healthy",
            "mode": pipeline.mode if pipeline else "not_initialized",
            "models": list(pipeline.models.keys()) if pipeline else []
        }

    else:
        return {"error": f"Unknown type: {request_type}"}

def handler(job):
    """RunPod handler function"""
    try:
        # Initialize
        initialize()

        # Get input
        job_input = job.get("input", {})
        logger.info(f"Job: {job.get('id')} Type: {job_input.get('type')}")

        # Process
        result = asyncio.run(process_job(job_input))

        # Cleanup
        cleanup()

        return result

    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("Starting RunPod Worker")
    runpod.serverless.start({"handler": handler})
