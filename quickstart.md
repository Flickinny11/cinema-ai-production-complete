# 🚀 Cinema AI Quick Start Guide

## 30-Second Deploy to RunPod

```bash
# 1. Clone the repository
git clone https://github.com/Flickinny11/cinema-ai-production-complete
cd cinema-ai-production-complete

# 2. Deploy to RunPod (replace with your API key)
export RUNPOD_API_KEY="your_api_key_here"
python deploy_complete.py

# 3. Wait for deployment (30-60 minutes first time)
# You'll get an endpoint URL when ready
```

## Test Your Endpoint

```bash
# Quick test
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"input": {"type": "health_check"}}'
```

## Generate Your First Video

```python
import requests

# Simple 10-second video with dialogue and music
response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "single_scene",
            "scene": {
                "description": "A robot and human shake hands in a futuristic city, symbolizing peace between AI and humanity",
                "duration": 10,
                "resolution": "720p",
                "dialogue": [
                    {
                        "character": "Robot",
                        "text": "Together, we can build a better future.",
                        "emotion": "hopeful"
                    },
                    {
                        "character": "Human",
                        "text": "Yes, in harmony and understanding.",
                        "emotion": "optimistic"
                    }
                ],
                "camera_movements": ["slow zoom in", "circle around"],
                "music_mood": "uplifting orchestral",
                "sound_effects": ["city ambience", "handshake"]
            }
        }
    }
)

print(response.json())
```

## What You Get

✅ **Video Features:**
- Cinema-quality visuals (HunyuanVideo or LTX-Video)
- Realistic facial expressions and emotions
- Professional camera movements
- 720p/1080p/4K resolution

✅ **Audio Features:**
- Voice cloning from 6-second samples
- Multi-character dialogue with emotions
- Orchestral film scores (MusicGen)
- Professional sound effects (AudioGen)
- Lip-sync for speaking and singing

✅ **Performance:**
- 5s video: 2-10 seconds generation
- 30s video: 15-90 seconds generation
- Real-time generation with LTX-Video
- Cinema quality with HunyuanVideo

## Available Models

| Model | Purpose | Speed | Quality |
|-------|---------|-------|---------|
| **HunyuanVideo** | Cinema production | Slower | ⭐⭐⭐⭐⭐ |
| **LTX-Video** | Fast generation | 30x faster | ⭐⭐⭐⭐ |
| **MusicGen** | Film scores | Fast | ⭐⭐⭐⭐⭐ |
| **AudioGen** | Sound effects | Fast | ⭐⭐⭐⭐ |
| **XTTS-v2** | Voice cloning | Real-time | ⭐⭐⭐⭐⭐ |

## Scene Options

```json
{
    "description": "Detailed scene description",
    "duration": 5-60,  // seconds
    "resolution": "480p|720p|1080p|4k",
    "fps": 24|30|60,
    "camera_movements": [
        "zoom in", "zoom out", "pan left", "pan right",
        "tilt up", "tilt down", "tracking shot", "static shot",
        "circle around", "dolly in", "dolly out"
    ],
    "emotion_expressions": [
        "happy", "sad", "angry", "surprised", "fearful",
        "disgusted", "contemptuous", "neutral", "determined"
    ],
    "music_mood": "epic|romantic|suspenseful|action|peaceful",
    "sound_effects": ["any sound effect description"],
    "dialogue": [
        {
            "character": "Name",
            "text": "What they say",
            "emotion": "how they feel"
        }
    ],
    "voice_clone_samples": ["path/to/6second_voice.wav"]
}
```

## Pricing

- **Idle**: $0/hour (serverless scales to zero)
- **Active**: $2.49/hour (A100) or $3.99/hour (H100)
- **Average cost per video**: $0.10 - $0.50

## Tips for Best Results

1. **Descriptions**: Be specific and cinematic
   - ❌ "A person walks"
   - ✅ "A lone warrior walks through misty mountains at dawn, cape flowing in the wind"

2. **Camera Movements**: Use film terminology
   - "dolly in" for smooth forward movement
   - "tracking shot" to follow action
   - "crane shot" for overhead views

3. **Emotions**: Specify for each dialogue line
   - Adds realistic facial expressions
   - Enhances voice acting quality

4. **Music Mood**: Combine descriptors
   - "epic orchestral battle music"
   - "romantic piano with strings"
   - "dark suspenseful ambient"

## Need Help?

- 📚 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/Flickinny11/cinema-ai-production-complete/issues)
- 💬 [Discord Community](https://discord.gg/cinema-ai)

---

**Ready to create cinema-quality AI videos? Deploy now and start generating!** 🎬
