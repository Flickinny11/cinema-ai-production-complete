# Cinema AI Production Pipeline

[![RunPod](https://img.shields.io/badge/RunPod-Deploy-purple)](https://runpod.io/console/deploy?template=cinema-ai-production-complete&ref=github)
[![GitHub](https://img.shields.io/github/v/release/Flickinny11/cinema-ai-production-complete)](https://github.com/Flickinny11/cinema-ai-production-complete/releases)

Complete production pipeline for cinema-quality AI video generation, ready for RunPod Serverless deployment.

## Features

- **Video Generation**: HunyuanVideo (65GB VRAM) for cinema quality
- **Audio**: XTTS-v2 for voice cloning, MusicGen for orchestral scores
- **Script Processing**: Qwen 2.5 32B for intelligent parsing
- **Production Ready**: Optimized for H100/A100 80GB GPUs

## Quick Deploy to RunPod

[![Deploy on RunPod](https://img.shields.io/badge/Deploy%20on-RunPod-purple?style=for-the-badge)](https://runpod.io/console/deploy?template=Flickinny11/cinema-ai-production-complete)

## Architecture

- `cinema_pipeline.py` - Main video generation workflow
- `runpod_handler.py` - RunPod serverless handler
- `Dockerfile` - Container configuration
- `.runpod/hub.json` - RunPod Hub configuration

## Performance

| Scene Length | Generation Time | GPU Required |
|--------------|----------------|--------------|
| 5 seconds | 10-15 seconds | A100 80GB |
| 30 seconds | 45-60 seconds | A100 80GB |
| 5 minutes | 5-8 minutes | H100 80GB |

## API Usage

```python
import requests

response = requests.post(
    "https://api.runpod.io/v2/YOUR_ENDPOINT/runsync",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={
        "input": {
            "type": "script_to_video",
            "script": "Your movie script here..."
        }
    }
)
```

## Testing

```bash
# Run local tests
python test_local.py

# Run RunPod tests
runpodctl test
```

## Requirements

- **GPU**: NVIDIA A100 80GB or H100 80GB
- **VRAM**: 80GB minimum
- **Disk**: 350GB for models
- **CUDA**: 12.1+

## Cost

- **Serverless**: $0 when idle
- **A100 80GB**: $2.49/hour when active
- **H100 80GB**: $3.99/hour when active

## License

MIT

## Author

Created by @Flickinny11
