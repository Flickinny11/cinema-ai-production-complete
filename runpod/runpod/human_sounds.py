#!/usr/bin/env python3
"""
Human Sounds Generator
Generates realistic non-verbal human sounds for enhanced realism
"""

import os
import logging
import numpy as np
import torch
import soundfile as sf
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from audiocraft.models import AudioGen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HumanSound:
    """Represents a human sound effect"""
    sound_type: str
    emotion: str
    intensity: float  # 0.0 to 1.0
    duration: float  # seconds
    character: Optional[str] = None
    context: Optional[str] = None

class HumanSoundsGenerator:
    """Generate realistic non-verbal human sounds"""

    # Comprehensive catalog of human sounds
    SOUND_CATALOG = {
        # Laughter variations
        "laughter": {
            "types": ["hearty laugh", "chuckle", "giggle", "snicker", "cackle", "belly laugh", "nervous laugh"],
            "emotions": ["joy", "amusement", "nervousness", "sarcasm"],
            "duration": (0.5, 3.0)
        },

        # Vocal expressions
        "sigh": {
            "types": ["deep sigh", "light sigh", "frustrated sigh", "content sigh", "relieved sigh"],
            "emotions": ["frustration", "relief", "contentment", "exhaustion"],
            "duration": (1.0, 2.5)
        },

        "groan": {
            "types": ["painful groan", "frustrated groan", "tired groan", "annoyed groan"],
            "emotions": ["pain", "frustration", "exhaustion", "annoyance"],
            "duration": (0.5, 2.0)
        },

        "moan": {
            "types": ["painful moan", "sad moan", "tired moan"],
            "emotions": ["pain", "sadness", "exhaustion"],
            "duration": (0.5, 2.0)
        },

        "grunt": {
            "types": ["effort grunt", "acknowledgment grunt", "frustrated grunt"],
            "emotions": ["effort", "acknowledgment", "frustration"],
            "duration": (0.2, 1.0)
        },

        # Emotional sounds
        "cry": {
            "types": ["sobbing", "weeping", "sniffling", "wailing", "quiet crying"],
            "emotions": ["sadness", "joy", "pain", "relief"],
            "duration": (2.0, 5.0)
        },

        "scream": {
            "types": ["terror scream", "excitement scream", "pain scream", "surprise scream"],
            "emotions": ["terror", "excitement", "pain", "surprise"],
            "duration": (0.5, 2.0)
        },

        "gasp": {
            "types": ["shocked gasp", "surprised gasp", "fearful gasp", "breathless gasp"],
            "emotions": ["shock", "surprise", "fear", "exhaustion"],
            "duration": (0.3, 1.0)
        },

        # Physical sounds
        "cough": {
            "types": ["dry cough", "wet cough", "clearing throat", "choking cough", "polite cough"],
            "emotions": ["discomfort", "illness", "nervousness", "attention-seeking"],
            "duration": (0.3, 2.0)
        },

        "sneeze": {
            "types": ["loud sneeze", "quiet sneeze", "multiple sneezes", "suppressed sneeze"],
            "emotions": ["neutral", "embarrassment"],
            "duration": (0.5, 1.5)
        },

        "yawn": {
            "types": ["tired yawn", "bored yawn", "contagious yawn", "suppressed yawn"],
            "emotions": ["tiredness", "boredom"],
            "duration": (2.0, 4.0)
        },

        "hiccup": {
            "types": ["single hiccup", "multiple hiccups", "loud hiccup", "squeaky hiccup"],
            "emotions": ["surprise", "embarrassment"],
            "duration": (0.2, 0.5)
        },

        # Bodily functions (tasteful)
        "stomach_growl": {
            "types": ["hungry stomach growl", "digestion sounds"],
            "emotions": ["hunger", "embarrassment"],
            "duration": (1.0, 3.0)
        },

        "burp": {
            "types": ["small burp", "suppressed burp", "accidental burp"],
            "emotions": ["embarrassment", "satisfaction"],
            "duration": (0.3, 1.0)
        },

        # Eating/drinking sounds
        "eating": {
            "types": ["chewing", "munching", "crunching", "slurping", "swallowing"],
            "emotions": ["enjoyment", "hunger"],
            "duration": (0.5, 2.0)
        },

        "drinking": {
            "types": ["sipping", "gulping", "swallowing liquid", "ahh after drinking"],
            "emotions": ["thirst", "satisfaction"],
            "duration": (0.5, 2.0)
        },

        # Breathing sounds
        "breathing": {
            "types": ["heavy breathing", "panting", "wheezing", "calm breathing", "holding breath"],
            "emotions": ["exhaustion", "fear", "calm", "anticipation"],
            "duration": (2.0, 5.0)
        },

        # Vocal reactions
        "hmm": {
            "types": ["thinking hmm", "skeptical hmm", "interested hmm", "confused hmm"],
            "emotions": ["contemplation", "skepticism", "interest", "confusion"],
            "duration": (0.5, 1.5)
        },

        "ah": {
            "types": ["realization ah", "understanding ah", "surprised ah"],
            "emotions": ["realization", "understanding", "surprise"],
            "duration": (0.3, 1.0)
        },

        "oh": {
            "types": ["surprised oh", "disappointed oh", "interested oh"],
            "emotions": ["surprise", "disappointment", "interest"],
            "duration": (0.3, 1.0)
        },

        # Physical effort
        "effort": {
            "types": ["lifting grunt", "pushing sound", "straining", "exertion"],
            "emotions": ["determination", "struggle"],
            "duration": (0.5, 2.0)
        },

        # Sleep sounds
        "sleep": {
            "types": ["snoring", "sleep talking", "mumbling", "peaceful breathing"],
            "emotions": ["peaceful", "restless"],
            "duration": (2.0, 5.0)
        }
    }

    def __init__(self, audiogen_model=None):
        self.audiogen = audiogen_model

        # Initialize AudioGen if not provided
        if self.audiogen is None:
            try:
                from audiocraft.models import AudioGen
                self.audiogen = AudioGen.get_pretrained('facebook/audiogen-medium')
                if torch.cuda.is_available():
                    self.audiogen.to("cuda")
                logger.info("AudioGen initialized for human sounds")
            except Exception as e:
                logger.warning(f"Could not initialize AudioGen: {e}")
                self.audiogen = None

    async def generate_human_sound(self, sound: HumanSound) -> Optional[str]:
        """Generate a specific human sound"""

        if not self.audiogen:
            logger.warning("AudioGen not available for human sound generation")
            return None

        # Create detailed prompt
        prompt = self._create_sound_prompt(sound)

        logger.info(f"Generating human sound: {prompt}")

        try:
            # Set generation parameters
            self.audiogen.set_generation_params(
                duration=sound.duration,
                temperature=0.8,
                top_k=250,
                top_p=0.95
            )

            # Generate sound
            with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
                audio = self.audiogen.generate([prompt])

            # Convert to numpy and save
            audio_data = audio[0].cpu().numpy()

            # Apply intensity scaling
            audio_data = audio_data * sound.intensity

            # Add some variation
            audio_data = self._add_variation(audio_data, sound)

            # Save to file
            output_path = f"/app/output/human_sound_{sound.sound_type}_{int(time.time())}.wav"
            sf.write(output_path, audio_data.T, 16000)

            return output_path

        except Exception as e:
            logger.error(f"Failed to generate human sound: {e}")
            return None

    def _create_sound_prompt(self, sound: HumanSound) -> str:
        """Create detailed prompt for sound generation"""

        # Get sound variations
        sound_info = self.SOUND_CATALOG.get(sound.sound_type, {})
        sound_types = sound_info.get("types", [sound.sound_type])

        # Select appropriate variation
        if sound.emotion:
            # Match emotion to sound type
            matching_types = [t for t in sound_types if sound.emotion.lower() in t.lower()]
            sound_variant = matching_types[0] if matching_types else sound_types[0]
        else:
            sound_variant = random.choice(sound_types)

        # Build prompt
        prompt_parts = [f"human {sound_variant}"]

        # Add emotion context
        if sound.emotion:
            prompt_parts.append(f"{sound.emotion} emotion")

        # Add intensity
        if sound.intensity > 0.7:
            prompt_parts.append("intense")
        elif sound.intensity < 0.3:
            prompt_parts.append("subtle")

        # Add character context
        if sound.character:
            # Infer gender/age if specified
            if "male" in sound.character.lower():
                prompt_parts.append("male voice")
            elif "female" in sound.character.lower():
                prompt_parts.append("female voice")
            elif "child" in sound.character.lower():
                prompt_parts.append("child voice")
            elif "elderly" in sound.character.lower() or "old" in sound.character.lower():
                prompt_parts.append("elderly voice")

        # Add context
        if sound.context:
            prompt_parts.append(f"in {sound.context}")

        # Add quality modifiers
        prompt_parts.extend(["realistic", "natural", "human", "authentic"])

        return ", ".join(prompt_parts)

    def _add_variation(self, audio: np.ndarray, sound: HumanSound) -> np.ndarray:
        """Add natural variation to generated sound"""

        # Add slight pitch variation
        if sound.sound_type in ["laughter", "cry", "scream"]:
            # These sounds naturally have pitch variation
            pitch_var = np.random.normal(1.0, 0.05)
            # Simple pitch shift by resampling (approximation)
            if pitch_var != 1.0:
                import scipy.signal
                audio = scipy.signal.resample(audio, int(len(audio) * pitch_var))

        # Add amplitude envelope for naturalness
        if sound.sound_type in ["sigh", "yawn", "breathing"]:
            # Create envelope
            envelope = self._create_envelope(len(audio), sound.sound_type)
            audio = audio * envelope

        # Add slight noise for realism
        if sound.sound_type in ["breathing", "whisper", "sigh"]:
            noise = np.random.normal(0, 0.001, audio.shape)
            audio = audio + noise

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95

        return audio

    def _create_envelope(self, length: int, sound_type: str) -> np.ndarray:
        """Create amplitude envelope for natural sound shaping"""

        envelope = np.ones(length)

        if sound_type in ["sigh", "yawn"]:
            # Gradual rise and fall
            attack = int(length * 0.3)
            decay = int(length * 0.7)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[attack:] = np.linspace(1, 0.3, length - attack)

        elif sound_type in ["cough", "sneeze"]:
            # Sharp attack, quick decay
            attack = int(length * 0.1)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[attack:] = np.exp(-np.linspace(0, 5, length - attack))

        elif sound_type == "breathing":
            # Sinusoidal for breathing
            envelope = 0.5 + 0.5 * np.sin(np.linspace(0, 4 * np.pi, length))

        return envelope

    async def generate_scene_human_sounds(self, scene_data: Dict) -> List[str]:
        """Generate all human sounds for a scene"""

        sound_paths = []

        # Extract human sounds from scene
        human_sounds = scene_data.get("human_sounds", [])
        dialogue = scene_data.get("dialogue", [])

        # Generate sounds from explicit list
        for sound_type in human_sounds:
            sound = HumanSound(
                sound_type=sound_type,
                emotion=scene_data.get("emotion", "neutral"),
                intensity=0.7,
                duration=self.SOUND_CATALOG.get(sound_type, {}).get("duration", (1.0, 2.0))[0]
            )

            path = await self.generate_human_sound(sound)
            if path:
                sound_paths.append(path)

        # Extract sounds from dialogue (e.g., [laughs], [sighs])
        for dialogue_item in dialogue:
            non_verbal = dialogue_item.get("non_verbal", [])
            character = dialogue_item.get("character", "")
            emotion = dialogue_item.get("emotion", "neutral")

            for nv_sound in non_verbal:
                # Parse non-verbal sound
                sound_type = self._parse_non_verbal(nv_sound)

                if sound_type:
                    sound = HumanSound(
                        sound_type=sound_type,
                        emotion=emotion,
                        intensity=0.7,
                        duration=1.5,
                        character=character
                    )

                    path = await self.generate_human_sound(sound)
                    if path:
                        sound_paths.append(path)

        return sound_paths

    def _parse_non_verbal(self, text: str) -> Optional[str]:
        """Parse non-verbal sound description to sound type"""

        text = text.lower().strip()

        # Direct mappings
        mappings = {
            "laughs": "laughter",
            "laugh": "laughter",
            "chuckles": "laughter",
            "giggles": "laughter",
            "sighs": "sigh",
            "sigh": "sigh",
            "groans": "groan",
            "groan": "groan",
            "gasps": "gasp",
            "gasp": "gasp",
            "coughs": "cough",
            "cough": "cough",
            "sneezes": "sneeze",
            "sneeze": "sneeze",
            "cries": "cry",
            "cry": "cry",
            "sobs": "cry",
            "screams": "scream",
            "scream": "scream",
            "yawns": "yawn",
            "yawn": "yawn",
            "hiccups": "hiccup",
            "hiccup": "hiccup",
            "burps": "burp",
            "burp": "burp",
            "grunts": "grunt",
            "grunt": "grunt",
            "moans": "moan",
            "moan": "moan",
            "breathes heavily": "breathing",
            "pants": "breathing",
            "wheezes": "breathing"
        }

        for key, value in mappings.items():
            if key in text:
                return value

        return None

    def get_contextual_sounds(self, scene_description: str, emotion: str = None) -> List[str]:
        """Suggest appropriate human sounds based on scene context"""

        suggestions = []

        # Emotional context
        if emotion:
            if emotion in ["happy", "joy", "excited"]:
                suggestions.extend(["laughter", "giggle"])
            elif emotion in ["sad", "depressed"]:
                suggestions.extend(["sigh", "cry", "sniffle"])
            elif emotion in ["angry", "frustrated"]:
                suggestions.extend(["groan", "grunt", "heavy_breathing"])
            elif emotion in ["scared", "fearful"]:
                suggestions.extend(["gasp", "scream", "breathing"])
            elif emotion in ["tired", "exhausted"]:
                suggestions.extend(["yawn", "sigh", "groan"])

        # Scene context
        scene_lower = scene_description.lower()

        if "eating" in scene_lower or "dinner" in scene_lower or "restaurant" in scene_lower:
            suggestions.extend(["eating", "drinking", "satisfied_sigh"])

        if "running" in scene_lower or "chase" in scene_lower or "exercise" in scene_lower:
            suggestions.extend(["breathing", "panting", "effort"])

        if "sleeping" in scene_lower or "bedroom" in scene_lower or "night" in scene_lower:
            suggestions.extend(["yawn", "sleep", "peaceful_breathing"])

        if "surprise" in scene_lower or "shock" in scene_lower:
            suggestions.extend(["gasp", "oh", "ah"])

        if "thinking" in scene_lower or "contemplating" in scene_lower:
            suggestions.extend(["hmm", "ah", "thoughtful_sigh"])

        return list(set(suggestions))  # Remove duplicates
