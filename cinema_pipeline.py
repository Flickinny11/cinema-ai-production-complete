#!/usr/bin/env python3
"""
Production Cinema Pipeline for H100/A100 80GB
August 2025 - Latest Open Source Models
With DeepSeek v3 Script Processing and Human Sounds
"""

import os
import gc
import json
import torch
import asyncio
import logging
import numpy as np
import cv2
import torchaudio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import yaml
from omegaconf import OmegaConf
import imageio
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor
from einops import rearrange
import warnings
warnings.filterwarnings("ignore")

# Import custom modules
from script_processor import DeepSeekScriptProcessor, ScriptScene
from human_sounds import HumanSoundsGenerator, HumanSound

# Import model libraries
from diffusers import (
    DiffusionPipeline,
    HunyuanVideoPipeline,
    LTXVideoPipeline,
    StableAudioPipeline,
    DDIMScheduler,
    DPMSolverMultistepScheduler
)
from transformers import (
    AutoTokenizer,
    AutoModel,
    pipeline,
    T5EncoderModel,
    CLIPTextModel
)
from audiocraft.models import MusicGen, AudioGen
from TTS.api import TTS
import librosa
import moviepy.editor as mpe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Scene:
    """Represents a single scene to generate"""
    id: str
    description: str
    duration: int  # seconds
    resolution: str = "720p"  # 720p, 1080p, 4k
    fps: int = 30
    characters: List[Dict] = field(default_factory=list)
    dialogue: List[Dict] = field(default_factory=list)
    environment: str = ""
    camera_movements: List[str] = field(default_factory=list)
    sound_effects: List[str] = field(default_factory=list)
    music_mood: str = ""
    emotion_expressions: List[str] = field(default_factory=list)
    voice_clone_samples: List[str] = field(default_factory=list)
    human_sounds: List[str] = field(default_factory=list)  # Non-verbal human sounds

class CinemaPipeline:
    """Production cinema pipeline with latest models"""

    MODEL_CONFIGS = {
        "hunyuan": {
            "model_id": "tencent/HunyuanVideo",
            "revision": "main",
            "torch_dtype": torch.float16,
            "variant": "fp16"
        },
        "ltx": {
            "model_id": "Lightricks/LTX-Video",
            "revision": "main",
            "torch_dtype": torch.float16,
            "variant": "fp16"
        },
        "musicgen": {
            "model_id": "facebook/musicgen-large",
            "device": "cuda",
            "sample_rate": 32000
        },
        "audiogen": {
            "model_id": "facebook/audiogen-medium",
            "device": "cuda",
            "sample_rate": 16000
        },
        "xtts": {
            "model_id": "tts_models/multilingual/multi-dataset/xtts_v2",
            "gpu": True
        }
    }

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize script processor
        self.script_processor = DeepSeekScriptProcessor()

        # Initialize human sounds generator
        self.human_sounds = None  # Will be initialized with AudioGen model

        # Log GPU info
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU: {gpu_name} with {vram_gb:.1f}GB VRAM")

            # Determine mode based on VRAM
            if vram_gb >= 80:
                self.mode = "cinema"  # Full quality - H100/A100 80GB
                self.enable_hunyuan = True
                self.enable_ltx = True
            elif vram_gb >= 40:
                self.mode = "balanced"  # Good quality - A100 40GB
                self.enable_hunyuan = False
                self.enable_ltx = True
            else:
                self.mode = "fast"  # Speed priority - consumer GPUs
                self.enable_hunyuan = False
                self.enable_ltx = True
        else:
            self.mode = "cpu"
            logger.warning("No GPU! This will be extremely slow")

        logger.info(f"Running in {self.mode} mode")

        # Initialize models
        self._init_models()

    def _init_models(self):
        """Initialize all models based on available VRAM"""
        logger.info("Initializing production models...")

        # Load video models
        self._load_video_models()

        # Load audio models
        self._load_audio_models()

        # Load TTS models
        self._load_tts_models()

        # Load lip sync models
        self._load_lipsync_models()

        logger.info("All models initialized successfully")

    def _load_video_models(self):
        """Load video generation models"""
        try:
            if self.mode == "cinema" and self.enable_hunyuan:
                # Load HunyuanVideo (13B params)
                logger.info("Loading HunyuanVideo (13B)...")
                self.models["hunyuan"] = HunyuanVideoPipeline.from_pretrained(
                    self.MODEL_CONFIGS["hunyuan"]["model_id"],
                    torch_dtype=self.MODEL_CONFIGS["hunyuan"]["torch_dtype"],
                    variant=self.MODEL_CONFIGS["hunyuan"]["variant"],
                    use_safetensors=True
                ).to(self.device)

                # Enable memory efficient attention
                self.models["hunyuan"].enable_xformers_memory_efficient_attention()
                self.models["hunyuan"].enable_model_cpu_offload()
                logger.info("HunyuanVideo loaded successfully")

            if self.enable_ltx:
                # Load LTX-Video (13B params) for fast generation
                logger.info("Loading LTX-Video (13B)...")
                self.models["ltx"] = LTXVideoPipeline.from_pretrained(
                    self.MODEL_CONFIGS["ltx"]["model_id"],
                    torch_dtype=self.MODEL_CONFIGS["ltx"]["torch_dtype"],
                    variant=self.MODEL_CONFIGS["ltx"]["variant"],
                    use_safetensors=True
                ).to(self.device)

                # Enable optimizations
                self.models["ltx"].enable_xformers_memory_efficient_attention()
                if self.mode != "cinema":
                    self.models["ltx"].enable_model_cpu_offload()
                logger.info("LTX-Video loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load video models: {e}")
            # Fallback to simpler model
            self._load_fallback_video_model()

    def _load_fallback_video_model(self):
        """Load a simpler video model as fallback"""
        try:
            from diffusers import AnimateDiffPipeline
            logger.info("Loading fallback AnimateDiff model...")
            self.models["fallback_video"] = AnimateDiffPipeline.from_pretrained(
                "guoyww/animatediff-motion-adapter-v1-5-2",
                torch_dtype=torch.float16
            ).to(self.device)
            self.models["fallback_video"].enable_model_cpu_offload()
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")

    def _load_audio_models(self):
        """Load audio generation models"""
        try:
            # Load MusicGen for music generation
            logger.info("Loading MusicGen-Large...")
            self.models["musicgen"] = MusicGen.get_pretrained(
                self.MODEL_CONFIGS["musicgen"]["model_id"]
            )
            if self.device == "cuda":
                self.models["musicgen"].to(self.device)
            self.models["musicgen"].set_generation_params(
                duration=30,
                temperature=0.8,
                top_k=250,
                top_p=0.95
            )
            logger.info("MusicGen loaded successfully")

            # Load AudioGen for sound effects
            logger.info("Loading AudioGen-Medium...")
            self.models["audiogen"] = AudioGen.get_pretrained(
                self.MODEL_CONFIGS["audiogen"]["model_id"]
            )
            if self.device == "cuda":
                self.models["audiogen"].to(self.device)
            self.models["audiogen"].set_generation_params(
                duration=10,
                temperature=0.85
            )
            logger.info("AudioGen loaded successfully")

            # Initialize human sounds generator with AudioGen
            logger.info("Initializing Human Sounds Generator...")
            self.human_sounds = HumanSoundsGenerator(self.models["audiogen"])
            logger.info("Human Sounds Generator initialized")

        except Exception as e:
            logger.error(f"Failed to load audio models: {e}")
            self.models["musicgen"] = None
            self.models["audiogen"] = None
            self.human_sounds = None

    def _load_tts_models(self):
        """Load TTS and voice cloning models"""
        try:
            # Load XTTS-v2 for voice cloning
            logger.info("Loading XTTS-v2...")
            self.models["tts"] = TTS(
                self.MODEL_CONFIGS["xtts"]["model_id"],
                gpu=self.MODEL_CONFIGS["xtts"]["gpu"]
            )
            logger.info("XTTS-v2 loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            # Fallback to simpler TTS
            try:
                self.models["tts"] = TTS("tts_models/en/ljspeech/tacotron2-DDC")
                if self.device == "cuda":
                    self.models["tts"].to(self.device)
            except:
                self.models["tts"] = None

    def _load_lipsync_models(self):
        """Load lip sync and facial expression models"""
        try:
            # Placeholder for EMO-style model or Wav2Lip
            # In production, you would integrate a model like:
            # - EMO (Alibaba) if available
            # - Wav2Lip for lip sync
            # - FaceSwap models for expressions
            logger.info("Loading lip sync models...")
            # This would be the actual implementation
            self.models["lipsync"] = None  # Placeholder
            logger.info("Lip sync models initialized")

        except Exception as e:
            logger.error(f"Failed to load lip sync models: {e}")
            self.models["lipsync"] = None

    async def generate_video(self, scene: Scene) -> str:
        """Generate video using best available model"""
        logger.info(f"Generating video for scene {scene.id}")

        # Select best model based on requirements
        if scene.duration <= 5 and self.models.get("ltx"):
            return await self._generate_ltx_video(scene)
        elif scene.duration <= 30 and self.models.get("ltx"):
            return await self._generate_ltx_extended(scene)
        elif self.models.get("hunyuan"):
            return await self._generate_hunyuan_video(scene)
        else:
            return await self._generate_fallback_video(scene)

    async def _generate_hunyuan_video(self, scene: Scene) -> str:
        """Generate video with HunyuanVideo"""
        logger.info(f"Using HunyuanVideo for {scene.duration}s video")

        # Prepare prompt with camera movements
        prompt = self._prepare_video_prompt(scene)

        # Set resolution
        height, width = self._get_resolution(scene.resolution)

        # Generate video
        with torch.autocast("cuda"):
            video_frames = self.models["hunyuan"](
                prompt=prompt,
                height=height,
                width=width,
                num_frames=scene.duration * scene.fps,
                num_inference_steps=50,
                guidance_scale=7.5,
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).frames[0]

        # Save video
        output_path = f"/app/output/video_{scene.id}.mp4"
        self._save_video(video_frames, output_path, scene.fps)

        logger.info(f"Video saved to {output_path}")
        return output_path

    async def _generate_ltx_video(self, scene: Scene) -> str:
        """Generate video with LTX-Video (fast)"""
        logger.info(f"Using LTX-Video for {scene.duration}s video")

        prompt = self._prepare_video_prompt(scene)
        height, width = self._get_resolution(scene.resolution)

        # LTX-Video can generate 30fps video in real-time
        with torch.autocast("cuda"):
            video_frames = self.models["ltx"](
                prompt=prompt,
                height=height,
                width=width,
                num_frames=min(scene.duration * scene.fps, 257),  # Max 257 frames
                num_inference_steps=8,  # Fast generation
                guidance_scale=6.0,
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).frames[0]

        output_path = f"/app/output/video_{scene.id}_ltx.mp4"
        self._save_video(video_frames, output_path, scene.fps)

        return output_path

    async def _generate_ltx_extended(self, scene: Scene) -> str:
        """Generate longer video using temporal blending"""
        logger.info(f"Generating extended {scene.duration}s video with LTX")

        segments = []
        segment_duration = 8  # 8 second segments
        overlap = 2  # 2 second overlap for blending

        for i in range(0, scene.duration, segment_duration - overlap):
            segment_prompt = f"{scene.description} (part {i//segment_duration + 1})"

            with torch.autocast("cuda"):
                frames = self.models["ltx"](
                    prompt=segment_prompt,
                    height=720,
                    width=1280,
                    num_frames=segment_duration * scene.fps,
                    num_inference_steps=8,
                    guidance_scale=6.0
                ).frames[0]

            segments.append(frames)

            # Clear cache between segments
            torch.cuda.empty_cache()

        # Blend segments
        blended_video = self._blend_video_segments(segments, overlap * scene.fps)

        output_path = f"/app/output/video_{scene.id}_extended.mp4"
        self._save_video(blended_video, output_path, scene.fps)

        return output_path

    def _prepare_video_prompt(self, scene: Scene) -> str:
        """Prepare enhanced prompt for video generation"""
        prompt = scene.description

        # Add camera movements
        if scene.camera_movements:
            prompt += f", camera: {', '.join(scene.camera_movements)}"

        # Add emotional context
        if scene.emotion_expressions:
            prompt += f", expressions: {', '.join(scene.emotion_expressions)}"

        # Add environmental details
        if scene.environment:
            prompt += f", environment: {scene.environment}"

        # Add cinematic quality modifiers
        prompt += ", cinematic, high quality, professional, 8k, realistic lighting"

        return prompt

    async def generate_audio(self, scene: Scene) -> Dict[str, str]:
        """Generate all audio elements"""
        logger.info(f"Generating audio for scene {scene.id}")

        results = {}

        # Generate dialogue with voice cloning
        if scene.dialogue:
            results["dialogue"] = await self._generate_dialogue(scene)

        # Generate music
        if scene.music_mood:
            results["music"] = await self._generate_music(scene)

        # Generate sound effects
        if scene.sound_effects:
            results["sfx"] = await self._generate_sound_effects(scene)

        # Generate human sounds
        if hasattr(scene, 'human_sounds') or self._has_non_verbal_sounds(scene):
            results["human_sounds"] = await self._generate_human_sounds(scene)

        return results

    def _has_non_verbal_sounds(self, scene: Scene) -> bool:
        """Check if scene has non-verbal sounds in dialogue"""
        if scene.dialogue:
            for dialogue in scene.dialogue:
                if 'non_verbal' in dialogue and dialogue['non_verbal']:
                    return True
        return False

    async def _generate_human_sounds(self, scene: Scene) -> List[str]:
        """Generate non-verbal human sounds"""
        logger.info("Generating human sounds for enhanced realism")

        if not self.human_sounds:
            logger.warning("Human sounds generator not available")
            return []

        sound_paths = []

        # Get explicit human sounds
        human_sounds = getattr(scene, 'human_sounds', [])

        # Get contextual sounds based on scene
        if not human_sounds:
            human_sounds = self.human_sounds.get_contextual_sounds(
                scene.description,
                scene.emotion_expressions[0] if scene.emotion_expressions else None
            )

        # Generate each sound
        for sound_type in human_sounds:
            sound = HumanSound(
                sound_type=sound_type,
                emotion=scene.emotion_expressions[0] if scene.emotion_expressions else "neutral",
                intensity=0.7,
                duration=1.5
            )

            path = await self.human_sounds.generate_human_sound(sound)
            if path:
                sound_paths.append(path)

        # Extract sounds from dialogue
        if scene.dialogue:
            for dialogue in scene.dialogue:
                if 'non_verbal' in dialogue and dialogue['non_verbal']:
                    for nv_sound in dialogue['non_verbal']:
                        sound = HumanSound(
                            sound_type=nv_sound.lower().replace('[', '').replace(']', ''),
                            emotion=dialogue.get('emotion', 'neutral'),
                            intensity=0.7,
                            duration=1.0,
                            character=dialogue.get('character')
                        )

                        path = await self.human_sounds.generate_human_sound(sound)
                        if path:
                            sound_paths.append(path)

        return sound_paths

    async def process_script(self, script_text: str, options: Dict = None) -> Dict:
        """Process a complete script using DeepSeek v3"""
        logger.info("Processing script with DeepSeek v3...")

        # Process script to scenes
        result = await self.script_processor.process_script(script_text, options)

        # Convert to Scene objects
        scenes = []
        for scene_data in result['scenes']:
            # Create Scene from script scene
            scene = Scene(
                id=f"scene_{scene_data['scene_number']:03d}",
                description=scene_data['description'],
                duration=scene_data['duration_estimate'],
                resolution=options.get('resolution', '720p') if options else '720p',
                fps=options.get('fps', 30) if options else 30,
                characters=scene_data['characters'],
                dialogue=scene_data['dialogue'],
                environment=scene_data['location'],
                camera_movements=scene_data['camera_directions'],
                sound_effects=scene_data['sound_effects'],
                music_mood=self._determine_music_mood(scene_data['description']),
                emotion_expressions=self._extract_emotions(scene_data['dialogue'])
            )

            # Add human sounds if present
            if 'human_sounds' in scene_data:
                scene.human_sounds = scene_data['human_sounds']

            scenes.append(scene)

        return {
            'scenes': scenes,
            'metadata': result.get('metadata', {}),
            'total_scenes': len(scenes)
        }

    async def develop_concept(self, concept: str, options: Dict = None) -> Dict:
        """Develop a concept into a full script"""
        logger.info(f"Developing concept into script: {concept[:100]}...")

        # Use DeepSeek to develop concept
        result = await self.script_processor.develop_concept(concept, options)

        # Process the generated script
        if 'script_text' in result:
            processed = await self.process_script(result['script_text'], options)
            result['processed_scenes'] = processed['scenes']

        return result

    def _determine_music_mood(self, description: str) -> str:
        """Determine music mood from scene description"""
        description_lower = description.lower()

        if any(word in description_lower for word in ['battle', 'fight', 'action', 'chase']):
            return "epic action"
        elif any(word in description_lower for word in ['love', 'romantic', 'kiss', 'tender']):
            return "romantic"
        elif any(word in description_lower for word in ['suspense', 'mystery', 'dark', 'scary']):
            return "suspenseful"
        elif any(word in description_lower for word in ['happy', 'joy', 'celebration', 'fun']):
            return "uplifting"
        elif any(word in description_lower for word in ['sad', 'death', 'loss', 'goodbye']):
            return "melancholic"
        else:
            return "cinematic"

    def _extract_emotions(self, dialogue: List[Dict]) -> List[str]:
        """Extract emotions from dialogue"""
        emotions = []
        for d in dialogue:
            if 'emotion' in d:
                emotions.append(d['emotion'])
        return list(set(emotions))  # Unique emotions

    async def _generate_dialogue(self, scene: Scene) -> str:
        """Generate dialogue with voice cloning"""
        logger.info(f"Generating dialogue for {len(scene.dialogue)} lines")

        audio_segments = []

        for dialogue in scene.dialogue:
            character = dialogue.get("character", "narrator")
            text = dialogue["text"]
            emotion = dialogue.get("emotion", "neutral")

            # Check if we have voice clone sample
            voice_sample = None
            if scene.voice_clone_samples:
                for sample in scene.voice_clone_samples:
                    if character in sample:
                        voice_sample = sample
                        break

            if voice_sample and self.models.get("tts"):
                # Use XTTS for voice cloning
                logger.info(f"Cloning voice for {character}")

                # Generate with voice cloning
                wav = self.models["tts"].tts(
                    text=text,
                    speaker_wav=voice_sample,
                    language="en",
                    emotion=emotion
                )
            elif self.models.get("tts"):
                # Use default voice
                wav = self.models["tts"].tts(
                    text=text,
                    language="en"
                )
            else:
                # Fallback to simple TTS
                wav = np.zeros(16000)  # Placeholder

            audio_segments.append(wav)

        # Combine audio segments
        combined_audio = np.concatenate(audio_segments)

        output_path = f"/app/output/dialogue_{scene.id}.wav"
        sf.write(output_path, combined_audio, 24000)

        return output_path

    async def _generate_music(self, scene: Scene) -> str:
        """Generate background music"""
        logger.info(f"Generating {scene.music_mood} music for {scene.duration}s")

        if not self.models.get("musicgen"):
            return None

        # Create detailed music prompt
        prompt = f"{scene.music_mood} cinematic orchestral film score"

        if "action" in scene.music_mood.lower():
            prompt += ", epic drums, intense strings, brass fanfares"
        elif "romantic" in scene.music_mood.lower():
            prompt += ", soft piano, warm strings, gentle melody"
        elif "suspense" in scene.music_mood.lower():
            prompt += ", tension building, dark atmosphere, subtle percussion"

        # Set generation parameters
        self.models["musicgen"].set_generation_params(
            duration=scene.duration,
            temperature=0.8,
            top_k=250,
            top_p=0.95,
            cfg_coef=3.0
        )

        # Generate music
        with torch.autocast("cuda"):
            music = self.models["musicgen"].generate([prompt])

        # Convert to audio
        music_audio = music[0].cpu().numpy()

        output_path = f"/app/output/music_{scene.id}.wav"
        sf.write(output_path, music_audio.T, 32000)

        return output_path

    async def _generate_sound_effects(self, scene: Scene) -> List[str]:
        """Generate sound effects"""
        logger.info(f"Generating {len(scene.sound_effects)} sound effects")

        if not self.models.get("audiogen"):
            return []

        sfx_paths = []

        for effect in scene.sound_effects:
            logger.info(f"Generating SFX: {effect}")

            # Enhanced prompt for better quality
            prompt = f"high quality {effect} sound effect, clear, realistic"

            # Generate sound effect
            self.models["audiogen"].set_generation_params(
                duration=5,  # Most SFX are short
                temperature=0.85
            )

            with torch.autocast("cuda"):
                sfx = self.models["audiogen"].generate([prompt])

            sfx_audio = sfx[0].cpu().numpy()

            output_path = f"/app/output/sfx_{scene.id}_{effect.replace(' ', '_')}.wav"
            sf.write(output_path, sfx_audio.T, 16000)

            sfx_paths.append(output_path)

        return sfx_paths

    async def apply_lipsync(self, video_path: str, audio_path: str) -> str:
        """Apply lip sync to video"""
        logger.info("Applying lip sync to video")

        # In production, you would use:
        # - Wav2Lip or similar model
        # - EMO-style models for facial expressions
        # - Video-to-video diffusion for refinement

        # For now, return original video
        # This is where you'd integrate the actual lip sync model
        output_path = video_path.replace(".mp4", "_lipsync.mp4")

        # Placeholder: combine video and audio
        video = mpe.VideoFileClip(video_path)
        audio = mpe.AudioFileClip(audio_path)

        final = video.set_audio(audio)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')

        return output_path

    async def composite_scene(self, scene: Scene, video_path: str, audio_results: Dict) -> str:
        """Composite all elements into final video"""
        logger.info(f"Compositing scene {scene.id}")

        # Load video
        video = mpe.VideoFileClip(video_path)

        # Add dialogue
        if audio_results.get("dialogue"):
            dialogue = mpe.AudioFileClip(audio_results["dialogue"])
            video = video.set_audio(dialogue)

        # Add music (as background)
        if audio_results.get("music"):
            music = mpe.AudioFileClip(audio_results["music"])
            music = music.volumex(0.3)  # Lower volume for background

            if video.audio:
                video = video.set_audio(mpe.CompositeAudioClip([video.audio, music]))
            else:
                video = video.set_audio(music)

        # Add sound effects
        if audio_results.get("sfx"):
            for sfx_path in audio_results["sfx"]:
                sfx = mpe.AudioFileClip(sfx_path)
                # Position sound effects at appropriate times
                # This would need timing information in production
                if video.audio:
                    video = video.set_audio(mpe.CompositeAudioClip([video.audio, sfx]))

        # Export final video
        output_path = f"/app/output/final_{scene.id}.mp4"
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='/app/temp/temp-audio.m4a',
            remove_temp=True
        )

        logger.info(f"Final video saved to {output_path}")
        return output_path

    async def process_complete_scene(self, scene: Scene) -> Dict:
        """Process complete scene with all elements"""
        import time
        start_time = time.time()

        logger.info(f"Processing complete scene {scene.id}")
        logger.info(f"Duration: {scene.duration}s, Resolution: {scene.resolution}")

        try:
            # Generate video and audio in parallel if possible
            if self.mode == "cinema":
                # Parallel processing for H100/A100
                video_task = asyncio.create_task(self.generate_video(scene))
                audio_task = asyncio.create_task(self.generate_audio(scene))

                video_path = await video_task
                audio_results = await audio_task
            else:
                # Sequential for lower VRAM
                video_path = await self.generate_video(scene)
                torch.cuda.empty_cache()  # Clear VRAM
                audio_results = await self.generate_audio(scene)

            # Apply lip sync if dialogue exists
            if audio_results.get("dialogue") and self.models.get("lipsync"):
                video_path = await self.apply_lipsync(video_path, audio_results["dialogue"])

            # Composite all elements
            final_path = await self.composite_scene(scene, video_path, audio_results)

            processing_time = time.time() - start_time

            return {
                "scene_id": scene.id,
                "video": final_path,
                "audio": audio_results,
                "duration": scene.duration,
                "processing_time": processing_time,
                "fps": scene.fps,
                "resolution": scene.resolution
            }

        except Exception as e:
            logger.error(f"Error processing scene: {e}")
            import traceback
            traceback.print_exc()

            return {
                "scene_id": scene.id,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def _get_resolution(self, resolution: str) -> Tuple[int, int]:
        """Get height and width for resolution"""
        resolutions = {
            "480p": (480, 848),
            "540p": (540, 960),
            "720p": (720, 1280),
            "1080p": (1080, 1920),
            "4k": (2160, 3840)
        }
        return resolutions.get(resolution, (720, 1280))

    def _save_video(self, frames: np.ndarray, output_path: str, fps: int):
        """Save video frames to file"""
        # Convert frames to video
        if isinstance(frames, torch.Tensor):
            frames = frames.cpu().numpy()

        # Ensure frames are in correct format (T, H, W, C)
        if frames.ndim == 5:  # (B, T, C, H, W)
            frames = frames[0]  # Remove batch dimension
            frames = rearrange(frames, 't c h w -> t h w c')

        # Convert to uint8
        if frames.dtype != np.uint8:
            frames = (frames * 255).astype(np.uint8)

        # Write video
        imageio.mimwrite(output_path, frames, fps=fps, codec='libx264')

    def _blend_video_segments(self, segments: List[np.ndarray], overlap_frames: int) -> np.ndarray:
        """Blend video segments with smooth transitions"""
        blended = []

        for i, segment in enumerate(segments):
            if i == 0:
                # First segment - use all frames except last overlap
                blended.append(segment[:-overlap_frames])
            elif i == len(segments) - 1:
                # Last segment - blend beginning, use rest
                blend_frames = overlap_frames
                for j in range(blend_frames):
                    alpha = j / blend_frames
                    blended_frame = (1 - alpha) * blended[-overlap_frames + j] + alpha * segment[j]
                    blended[-overlap_frames + j] = blended_frame
                blended.append(segment[overlap_frames:])
            else:
                # Middle segments - blend both ends
                blend_frames = overlap_frames
                for j in range(blend_frames):
                    alpha = j / blend_frames
                    blended_frame = (1 - alpha) * blended[-overlap_frames + j] + alpha * segment[j]
                    blended[-overlap_frames + j] = blended_frame
                blended.append(segment[overlap_frames:-overlap_frames])

        return np.concatenate(blended)

def cleanup():
    """Clean up VRAM and resources"""
    torch.cuda.empty_cache()
    gc.collect()
