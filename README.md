# 🎬 Cinema AI Production Pipeline v2.0

[![RunPod](https://img.shields.io/badge/Deploy%20on-RunPod-purple?style=for-the-badge)](https://runpod.io/console/deploy?template=cinema-ai-production)
[![GPU](https://img.shields.io/badge/GPU-H100%2FA100%2080GB-green?style=for-the-badge)](https://runpod.io)
[![Models](https://img.shields.io/badge/Models-HunyuanVideo%20|%20LTX--Video%20|%20MusicGen-blue?style=for-the-badge)](https://github.com)

## 🚀 Production-Ready Cinema Quality AI Video Generation

Complete pipeline for generating cinema-quality videos with:
- **Realistic facial expressions and emotions**
- **Voice cloning and multi-character dialogue**
- **Orchestral soundtracks and sound effects**
- **Lip-sync and singing capabilities**
- **Camera movements and cinematic shots**

## ✨ Key Features

### Video Generation
- **HunyuanVideo (13B)** - Cinema quality, up to 60s videos
- **LTX-Video (13B)** - Real-time generation, 30x faster
- **720p/1080p/4K** resolution support
- **Facial expressions** and **emotion rendering**
- **Camera movements** (pan, zoom, tracking, etc.)

### Audio Generation
- **MusicGen-Large** - Orchestral film scores
- **AudioGen-Medium** - Professional sound effects
- **XTTS-v2** - Voice cloning from 6s samples
- **17 languages** supported
- **Emotion and style transfer**

### Advanced Features
- **Lip-sync** for dialogue and singing
- **Multi-character scenes** with distinct voices
- **Temporal blending** for extended videos
- **Video-to-audio synthesis** (Foley)
- **Parallel processing** on H100/A100

## 📊 Performance

| Video Length | Resolution | Generation Time | GPU Required |
|-------------|------------|-----------------|--------------|
| 5 seconds | 720p | 2-10 seconds | RTX 4090+ |
| 10 seconds | 720p | 15-30 seconds | A100 40GB |
| 30 seconds | 1080p | 45-90 seconds | A100 80GB |
| 60 seconds | 1080p | 3-5 minutes | H100 80GB |

## 🛠️ Quick Deploy to RunPod

### One-Click Deploy
[![Deploy on RunPod](https://img.shields.io/badge/Deploy%20Now-RunPod-purple?style=for-the-badge&logo=rocket)](https://runpod.io/console/deploy?template=cinema-ai-production)

### Manual Deploy
```bash
# Clone repository
git clone https://github.com/Flickinny11/cinema-ai-production-complete
cd cinema-ai-production-complete

# Deploy to RunPod
python deploy_to_runpod.py
```

## 🎯 API Usage

### Generate Video from Script
```python
import requests

response = requests.post(
    "https://api.runpod.io/v2/YOUR_ENDPOINT/runsync",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "script_to_video",
            "script": """
                A majestic spaceship glides through a nebula, camera slowly zooming in.
                The ship's engines pulse with blue energy.

                CAPTAIN: "Set course for Earth. It's time to go home."

                The stars blur as the ship jumps to hyperspace.
            """,
            "resolution": "1080p",
            "fps": 30,
            "style": "cinematic sci-fi"
        }
    }
)
```

### Generate Single Scene
```python
response = requests.post(
    "https://api.runpod.io/v2/YOUR_ENDPOINT/runsync",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "single_scene",
            "scene": {
                "description": "A warrior stands on a cliff overlooking a vast battlefield at sunset",
                "duration": 10,
                "resolution": "720p",
                "camera_movements": ["slow zoom in", "pan right"],
                "music_mood": "epic orchestral",
                "sound_effects": ["wind", "distant battle sounds"],
                "dialogue": [
                    {
                        "character": "Warrior",
                        "text": "Today, we fight for freedom!",
                        "emotion": "determined"
                    }
                ],
                "voice_clone_samples": ["/path/to/warrior_voice.wav"]
            }
        }
    }
)
```

## 🎨 Scene Configuration Options

```json
{
    "description": "Scene description with details",
    "duration": 10,  // seconds (5-60)
    "resolution": "1080p",  // 480p, 720p, 1080p, 4k
    "fps": 30,  // 24, 30, 60
    "camera_movements": [
        "zoom in", "zoom out", "pan left", "pan right",
        "tilt up", "tilt down", "tracking shot", "static shot"
    ],
    "emotion_expressions": [
        "happy", "sad", "angry", "surprised", "neutral"
    ],
    "music_mood": "epic orchestral",  // romantic, suspenseful, action, etc.
    "sound_effects": ["footsteps", "wind", "thunder"],
    "dialogue": [
        {
            "character": "Hero",
            "text": "We must save the world!",
            "emotion": "determined"
        }
    ],
    "voice_clone_samples": ["path/to/voice.wav"]
}
```

## 📦 Model Information

### Video Models
- **HunyuanVideo**: 13B parameters, cinema quality, best for final production
- **LTX-Video**: 13B parameters, real-time generation, 30x faster

### Audio Models
- **MusicGen-Large**: Film score generation
- **AudioGen-Medium**: Sound effects and foley
- **XTTS-v2**: Voice cloning and TTS

### Requirements
- **Minimum**: RTX 4090 (24GB VRAM) - Fast mode
- **Recommended**: A100 40GB - Balanced mode
- **Optimal**: H100/A100 80GB - Cinema mode

## 🔧 Local Development

### Prerequisites
- NVIDIA GPU with 24GB+ VRAM
- CUDA 12.1+
- Python 3.10+
- 350GB disk space

### Installation
```bash
# Clone repository
git clone https://github.com/Flickinny11/cinema-ai-production-complete
cd cinema-ai-production-complete

# Build Docker image
docker build -t cinema-ai .

# Run locally
docker run --gpus all -p 8000:8000 cinema-ai
```

### Download Models
```bash
# Download all models (~100GB)
python download_models.py

# Download base models only (~40GB)
python download_models.py --base-only

# Download specific model
python download_models.py --model hunyuan
```

## 💰 Cost Information

- **RunPod Serverless**: $0 when idle
- **A100 80GB**: $2.49/hour when active
- **H100 80GB**: $3.99/hour when active
- **Average cost per video**: $0.10 - $0.50

## 📈 Benchmarks

| Model | 5s Video | 30s Video | Quality | VRAM |
|-------|----------|-----------|---------|------|
| HunyuanVideo | 45-60s | 4-6 min | ⭐⭐⭐⭐⭐ | 65GB |
| LTX-Video | 2s | 15-20s | ⭐⭐⭐⭐ | 24GB |

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Tencent** for HunyuanVideo
- **Lightricks** for LTX-Video
- **Meta** for AudioCraft/MusicGen
- **Coqui** for XTTS
- **RunPod** for infrastructure

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/Flickinny11/cinema-ai-production-complete/issues)
- **Discord**: [Join community](https://discord.gg/cinema-ai)
- **Documentation**: [Full docs](https://docs.cinema-ai.com)

---

**Built with ❤️ for creators, filmmakers, and AI enthusiasts**

*Cinema AI Production Pipeline v2.0 - August 2025*
