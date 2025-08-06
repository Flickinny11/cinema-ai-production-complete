# Cinema AI Production Pipeline

Complete production pipeline for cinema-quality AI video generation.

## Architecture

- **Dockerfile**: Container with all dependencies
- **cinema_pipeline.py**: Main workflow that generates videos
- **runpod_handler.py**: RunPod serverless handler
- **download_models.py**: Optional model downloader

## Deployment to RunPod

1. Push to GitHub:
```bash
git push origin main
```

2. Create RunPod Template:
   - Go to RunPod Console > Serverless > Templates
   - New Template with Dockerfile URL from this repo
   - Container Disk: 350GB

3. Create Endpoint:
   - GPU: A100 80GB or H100 80GB
   - Min Workers: 0 (serverless)
   - Max Workers: 10

## API Usage

```python
import requests

response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={
        "input": {
            "type": "script_to_video",
            "script": "Your script here..."
        }
    }
)
```

## Performance

- 5s scene: 10-15 seconds
- 30s scene: 45-60 seconds
- Only charged while processing!

## Created by Flickinny11
