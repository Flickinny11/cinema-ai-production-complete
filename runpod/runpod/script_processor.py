#!/usr/bin/env python3
"""
Script Processor with DeepSeek v3 Integration
Handles script parsing, scene breakdown, and concept development
"""

import os
import re
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import openai
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScriptScene:
    """Represents a parsed scene from script"""
    scene_number: int
    location: str
    time_of_day: str
    description: str
    characters: List[str]
    dialogue: List[Dict]
    actions: List[str]
    camera_directions: List[str]
    sound_effects: List[str]
    duration_estimate: int
    video_segments: List[Dict]  # Breakdown into 5s, 10s, 15s, 30s segments

@dataclass
class ScriptMetadata:
    """Script metadata and structure"""
    title: str
    genre: str
    total_scenes: int
    estimated_duration: int
    characters: List[Dict]
    locations: List[str]
    themes: List[str]

class DeepSeekScriptProcessor:
    """Process scripts using DeepSeek v3 LLM"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        # Initialize DeepSeek client
        if self.api_key:
            # DeepSeek uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            self.model = "deepseek-chat"  # DeepSeek v3
            logger.info("DeepSeek v3 initialized")
        else:
            logger.warning("No DeepSeek API key provided, using fallback parser")
            self.client = None

    async def process_script(self, script_text: str, options: Dict = None) -> Dict:
        """Process a complete script into scenes and video segments"""
        logger.info("Processing script with DeepSeek v3...")

        options = options or {}
        max_scene_duration = options.get("max_scene_duration", 30)

        if self.client:
            # Use DeepSeek for advanced processing
            scenes = await self._process_with_deepseek(script_text, max_scene_duration)
        else:
            # Fallback to rule-based parser
            scenes = self._parse_script_fallback(script_text, max_scene_duration)

        # Break down scenes into video segments
        for scene in scenes:
            scene.video_segments = self._segment_scene(scene, max_scene_duration)

        return {
            "scenes": [asdict(s) for s in scenes],
            "total_scenes": len(scenes),
            "metadata": self._extract_metadata(script_text, scenes)
        }

    async def _process_with_deepseek(self, script_text: str, max_duration: int) -> List[ScriptScene]:
        """Process script using DeepSeek v3"""

        # Comprehensive prompt for script analysis
        prompt = f"""You are an expert film script analyzer and video production planner.

Analyze this script and break it down into individual scenes with detailed information.
For each scene, provide:
1. Scene location and time
2. Characters present
3. All dialogue with speaker and emotion
4. Physical actions and movements
5. Camera directions (pan, zoom, tracking, etc.)
6. Required sound effects
7. Estimated duration
8. Break down into video segments of {max_duration} seconds or less

Also identify any non-verbal human sounds that would add realism:
- Laughter, chuckles, giggles
- Sighs, groans, grunts
- Gasps, screams, crying
- Coughs, sneezes, yawns
- Eating/drinking sounds
- Physical effort sounds

Output as JSON with this structure:
{{
    "scenes": [
        {{
            "scene_number": 1,
            "location": "INT. OFFICE - DAY",
            "time_of_day": "day",
            "description": "Detailed visual description",
            "characters": ["John", "Sarah"],
            "dialogue": [
                {{
                    "character": "John",
                    "text": "Hello",
                    "emotion": "friendly",
                    "non_verbal": ["smile", "nod"]
                }}
            ],
            "actions": ["John enters room", "Sarah looks up"],
            "camera_directions": ["medium shot", "close-up on Sarah"],
            "sound_effects": ["door opening", "papers rustling"],
            "human_sounds": ["sigh", "chuckle"],
            "duration_estimate": 15,
            "video_segments": [
                {{
                    "segment_id": "001a",
                    "duration": 10,
                    "description": "John enters and greets Sarah",
                    "camera": "medium shot to close-up"
                }}
            ]
        }}
    ]
}}

Script:
{script_text}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert script analyzer for AI video generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            result = response.choices[0].message.content

            # Parse JSON response
            data = json.loads(result)

            # Convert to ScriptScene objects
            scenes = []
            for scene_data in data["scenes"]:
                scene = ScriptScene(
                    scene_number=scene_data["scene_number"],
                    location=scene_data["location"],
                    time_of_day=scene_data.get("time_of_day", "day"),
                    description=scene_data["description"],
                    characters=scene_data["characters"],
                    dialogue=scene_data["dialogue"],
                    actions=scene_data["actions"],
                    camera_directions=scene_data.get("camera_directions", []),
                    sound_effects=scene_data.get("sound_effects", []),
                    duration_estimate=scene_data.get("duration_estimate", 10),
                    video_segments=scene_data.get("video_segments", [])
                )
                scenes.append(scene)

            return scenes

        except Exception as e:
            logger.error(f"DeepSeek processing failed: {e}")
            return self._parse_script_fallback(script_text, max_duration)

    async def develop_concept(self, concept: str, options: Dict = None) -> Dict:
        """Develop a concept into a full script"""
        logger.info(f"Developing concept: {concept[:100]}...")

        options = options or {}
        script_type = options.get("script_type", "short_film")
        target_duration = options.get("target_duration", 300)  # 5 minutes default

        if not self.client:
            return self._develop_concept_fallback(concept, options)

        # Create detailed prompt for script generation
        prompt = f"""You are an expert screenwriter and AI video production specialist.

Create a complete {script_type} script based on this concept:
"{concept}"

Requirements:
- Target duration: {target_duration} seconds
- Include detailed scene descriptions for AI video generation
- Add camera movements and cinematography notes
- Include realistic dialogue with emotions
- Add non-verbal human sounds for realism
- Break into scenes of 5-30 seconds each
- Make it visually compelling and emotionally engaging

Format the script in standard screenplay format with:
- Scene headings (INT./EXT. LOCATION - TIME)
- Action lines (present tense, visual descriptions)
- Character names (CAPS when introduced)
- Dialogue with parentheticals for emotions
- Camera directions in brackets [CLOSE-UP], [PAN LEFT]
- Sound notes in parentheses (thunder rumbles)

Also provide a JSON summary with:
- Title
- Genre
- Total scenes
- Character list with descriptions
- Key locations
- Estimated total duration
- Scene breakdown for video generation"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert screenwriter creating scripts for AI video generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=6000
            )

            result = response.choices[0].message.content

            # Extract script and JSON from response
            script_text = result.split("JSON SUMMARY:")[0].strip()
            json_text = result.split("JSON SUMMARY:")[1].strip() if "JSON SUMMARY:" in result else "{}"

            # Parse the generated script
            scenes = await self.process_script(script_text, options)

            # Parse metadata
            try:
                metadata = json.loads(json_text)
            except:
                metadata = {
                    "title": "Generated Script",
                    "genre": "Drama",
                    "estimated_duration": target_duration
                }

            return {
                "script_text": script_text,
                "scenes": scenes,
                "metadata": metadata,
                "concept": concept
            }

        except Exception as e:
            logger.error(f"Concept development failed: {e}")
            return self._develop_concept_fallback(concept, options)

    def _parse_script_fallback(self, script_text: str, max_duration: int) -> List[ScriptScene]:
        """Fallback script parser using regex patterns"""
        logger.info("Using fallback script parser...")

        scenes = []

        # Pattern for scene headings
        scene_pattern = r'(INT\.|EXT\.)\s+([^-]+)\s*-\s*(\w+)'

        # Split by scene headings
        scene_splits = re.split(scene_pattern, script_text)

        scene_number = 0
        for i in range(1, len(scene_splits), 4):
            if i + 3 < len(scene_splits):
                scene_number += 1

                location_type = scene_splits[i]
                location = scene_splits[i + 1].strip()
                time_of_day = scene_splits[i + 2].strip()
                content = scene_splits[i + 3]

                # Extract dialogue
                dialogue = []
                dialogue_pattern = r'([A-Z][A-Z\s]+)\n([^\n]+)'
                for match in re.finditer(dialogue_pattern, content):
                    character = match.group(1).strip()
                    text = match.group(2).strip()

                    # Detect emotions and non-verbal sounds
                    emotion = "neutral"
                    if "!" in text:
                        emotion = "excited"
                    elif "?" in text:
                        emotion = "questioning"
                    elif "..." in text:
                        emotion = "hesitant"

                    # Extract non-verbal sounds in brackets
                    non_verbal = re.findall(r'\[([^\]]+)\]', text)
                    text = re.sub(r'\[[^\]]+\]', '', text).strip()

                    dialogue.append({
                        "character": character,
                        "text": text,
                        "emotion": emotion,
                        "non_verbal": non_verbal
                    })

                # Extract actions (non-dialogue lines)
                actions = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not re.match(r'^[A-Z][A-Z\s]+$', line) and not re.match(dialogue_pattern, line):
                        actions.append(line)

                # Extract camera directions
                camera_directions = re.findall(r'\[([^\]]+)\]', content)

                # Extract sound effects
                sound_effects = re.findall(r'\(([^\)]+)\)', content)

                # Estimate duration (rough estimate)
                word_count = len(content.split())
                duration_estimate = min(max(word_count / 3, 5), max_duration)

                scene = ScriptScene(
                    scene_number=scene_number,
                    location=f"{location_type} {location}",
                    time_of_day=time_of_day.lower(),
                    description=actions[0] if actions else f"Scene at {location}",
                    characters=list(set([d["character"] for d in dialogue])),
                    dialogue=dialogue,
                    actions=actions,
                    camera_directions=camera_directions,
                    sound_effects=sound_effects,
                    duration_estimate=int(duration_estimate),
                    video_segments=[]
                )

                scenes.append(scene)

        # If no scenes found, create one from the entire text
        if not scenes:
            scenes.append(ScriptScene(
                scene_number=1,
                location="LOCATION",
                time_of_day="day",
                description=script_text[:200],
                characters=[],
                dialogue=[],
                actions=[script_text],
                camera_directions=["medium shot"],
                sound_effects=[],
                duration_estimate=min(30, max_duration),
                video_segments=[]
            ))

        return scenes

    def _segment_scene(self, scene: ScriptScene, max_duration: int) -> List[Dict]:
        """Break scene into video segments"""
        segments = []

        if scene.duration_estimate <= max_duration:
            # Single segment
            segments.append({
                "segment_id": f"{scene.scene_number:03d}",
                "duration": scene.duration_estimate,
                "description": scene.description,
                "dialogue": scene.dialogue,
                "camera": scene.camera_directions[0] if scene.camera_directions else "medium shot"
            })
        else:
            # Multiple segments
            remaining_duration = scene.duration_estimate
            segment_count = 0
            dialogue_index = 0

            while remaining_duration > 0:
                segment_count += 1
                segment_duration = min(max_duration, remaining_duration)

                # Distribute dialogue across segments
                dialogue_for_segment = []
                if scene.dialogue:
                    dialogues_per_segment = max(1, len(scene.dialogue) // ((scene.duration_estimate // max_duration) + 1))
                    dialogue_end = min(dialogue_index + dialogues_per_segment, len(scene.dialogue))
                    dialogue_for_segment = scene.dialogue[dialogue_index:dialogue_end]
                    dialogue_index = dialogue_end

                segments.append({
                    "segment_id": f"{scene.scene_number:03d}{chr(96 + segment_count)}",
                    "duration": segment_duration,
                    "description": f"{scene.description} (part {segment_count})",
                    "dialogue": dialogue_for_segment,
                    "camera": scene.camera_directions[segment_count - 1] if segment_count <= len(scene.camera_directions) else "medium shot"
                })

                remaining_duration -= segment_duration

        return segments

    def _develop_concept_fallback(self, concept: str, options: Dict) -> Dict:
        """Fallback concept development"""
        logger.info("Using fallback concept development...")

        # Simple template-based script generation
        script_text = f"""FADE IN:

INT. LOCATION - DAY

Based on the concept: {concept}

CHARACTER 1 enters the scene.

CHARACTER 1
(thoughtful)
This is where our story begins.

CHARACTER 2 appears.

CHARACTER 2
(curious)
What happens next?

They look at each other, understanding dawning.

FADE OUT."""

        return {
            "script_text": script_text,
            "scenes": self._parse_script_fallback(script_text, options.get("max_scene_duration", 30)),
            "metadata": {
                "title": "Generated Story",
                "concept": concept,
                "estimated_duration": 30
            }
        }

    def _extract_metadata(self, script_text: str, scenes: List[ScriptScene]) -> Dict:
        """Extract metadata from script"""

        # Extract title if present
        title_match = re.search(r'TITLE:\s*(.+)', script_text, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Untitled Script"

        # Collect all characters
        all_characters = set()
        for scene in scenes:
            all_characters.update(scene.characters)

        # Collect all locations
        all_locations = list(set([scene.location for scene in scenes]))

        # Calculate total duration
        total_duration = sum([scene.duration_estimate for scene in scenes])

        return {
            "title": title,
            "total_scenes": len(scenes),
            "total_duration": total_duration,
            "characters": list(all_characters),
            "locations": all_locations
        }
