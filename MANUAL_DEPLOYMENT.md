# 🚀 Manual RunPod Deployment Guide

## Step 1: Access RunPod Console
1. Go to [RunPod Console](https://runpod.io/console)
2. Sign in with your account

## Step 2: Create Template
1. Navigate to **"Serverless"** → **"Templates"**
2. Click **"Create Template"**
3. Fill in the following details:

### Template Configuration
- **Name**: `cinema-ai-production-v2`
- **Description**: `Cinema-quality AI video generation with HunyuanVideo, LTX-Video, MusicGen, AudioGen, XTTS-v2`
- **Dockerfile URL**: `https://github.com/Flickinny11/cinema-ai-production-complete/blob/main/Dockerfile`
- **Container Disk**: `350 GB`
- **Volume Size**: `100 GB`
- **Volume Mount Path**: `/models`

### Environment Variables
Add these environment variables:
- `MODEL_QUALITY` = `cinema`
- `HF_HUB_ENABLE_HF_TRANSFER` = `1`
- `PYTORCH_CUDA_ALLOC_CONF` = `max_split_size_mb:512`
- `DEEPSEEK_API_KEY` = `[your_deepseek_api_key]` (optional)

### Docker Arguments
```
--gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864
```

## Step 3: Create Endpoint
1. After template is built, go to **"Serverless"** → **"Endpoints"**
2. Click **"Create Endpoint"**
3. Fill in the following:

### Endpoint Configuration
- **Name**: `cinema-ai-endpoint`
- **Template**: Select your created template
- **GPU Types**: 
  - `NVIDIA A100-SXM4-80GB`
  - `NVIDIA H100 80GB HBM3`
- **Idle Timeout**: `10 minutes`
- **Min Workers**: `0`
- **Max Workers**: `10`
- **Scaler Type**: `QUEUE_DELAY`
- **Scaler Value**: `30 seconds`

## Step 4: Test Your Endpoint

### Health Check
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"input": {"type": "health_check"}}'
```

### Generate Test Video
```python
import requests

response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync",
    headers={
        "Authorization": "Bearer YOUR_RUNPOD_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "type": "single_scene",
            "scene": {
                "description": "A robot and human shake hands in a futuristic city",
                "duration": 10,
                "resolution": "720p",
                "dialogue": [
                    {
                        "character": "Robot",
                        "text": "Together, we can build a better future.",
                        "emotion": "hopeful"
                    }
                ],
                "camera_movements": ["slow zoom in"],
                "music_mood": "uplifting orchestral"
            }
        }
    }
)

print(response.json())
```

## Step 5: Monitor Deployment
1. Check template build status in RunPod console
2. Monitor endpoint logs for any issues
3. Test with health check before full video generation

## Expected Timeline
- **Template Build**: 30-60 minutes (first time)
- **Model Downloads**: 10-20 minutes (cached after first run)
- **Video Generation**: 2-10 seconds for 5s videos, 15-90 seconds for 30s videos

## Troubleshooting

### If Template Build Fails
1. Check Dockerfile syntax
2. Verify GitHub repository is public
3. Ensure sufficient disk space (350GB)

### If Endpoint Fails
1. Check GPU availability
2. Verify environment variables
3. Monitor logs for model download issues

### Performance Optimization
- Use H100 80GB for best performance
- A100 80GB for cost-effective option
- Enable volume mounting for model caching

## API Usage Examples

### Full Script Processing
```python
response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "script_to_video",
            "script": """
                A majestic spaceship glides through a nebula.
                CAPTAIN: "Set course for Earth."
                The stars blur as the ship jumps to hyperspace.
            """,
            "resolution": "1080p",
            "fps": 30
        }
    }
)
```

### Batch Scene Generation
```python
response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "type": "batch_scenes",
            "scenes": [
                {
                    "description": "Sunrise over mountains",
                    "duration": 5,
                    "resolution": "720p"
                },
                {
                    "description": "Ocean waves crashing",
                    "duration": 5,
                    "resolution": "720p"
                }
            ]
        }
    }
)
```

## Success Indicators
✅ Template builds successfully  
✅ Endpoint responds to health checks  
✅ Video generation completes  
✅ Audio sync works properly  
✅ Models cache correctly  

Your Cinema AI pipeline is now ready for production! 🎬
