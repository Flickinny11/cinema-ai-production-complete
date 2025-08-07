#!/usr/bin/env python3
"""
Push to RunPod Registry
"""

import requests
import base64
import json
import os

# RunPod API Configuration
API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"
REGISTRY_URL = "https://registry.runpod.io"

def login_to_registry():
    """Login to RunPod registry"""
    print("🔐 Logging into RunPod registry...")

    # Get registry credentials from RunPod API
    response = requests.post(
        "https://api.runpod.io/v2/user/registry",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={}
    )

    if response.status_code == 200:
        registry_data = response.json()
        print("✅ Got registry credentials")
        return registry_data
    else:
        print(f"❌ Failed to get registry credentials: {response.status_code}")
        return None

def build_and_push_image():
    """Build and push image to RunPod registry"""
    print("🐳 Building and pushing to RunPod registry...")

    # Read Dockerfile
    with open("Dockerfile", "r") as f:
        dockerfile_content = f.read()

    # Read Python files
    files = {
        "cinema_pipeline.py": base64.b64encode(open("cinema_pipeline.py", "rb").read()).decode(),
        "runpod_handler.py": base64.b64encode(open("runpod_handler.py", "rb").read()).decode(),
        "download_models.py": base64.b64encode(open("download_models.py", "rb").read()).decode()
    }

    # Build payload
    payload = {
        "name": "cinema-ai-production-v2",
        "dockerfile": base64.b64encode(dockerfile_content.encode()).decode(),
        "dockerContext": files,
        "containerDiskInGb": 350,
        "dockerArgs": {
            "buildArgs": {
                "CUDA_VERSION": "11.8"
            }
        }
    }

    print("📋 Building image with:")
    print(f"  - Name: {payload['name']}")
    print(f"  - Container Disk: {payload['containerDiskInGb']}GB")
    print(f"  - CUDA Version: {payload['dockerArgs']['buildArgs']['CUDA_VERSION']}")

    # Build image
    response = requests.post(
        "https://api.runpod.io/v2/serverless/template",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"📡 Build Response Status: {response.status_code}")
    print(f"📡 Build Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Image built successfully!")
        print(f"📋 Template ID: {result.get('id', 'N/A')}")
        return result.get('id')
    else:
        print(f"❌ Build failed!")
        return None

def create_endpoint_from_registry(template_id):
    """Create endpoint from registry template"""
    print("🚀 Creating endpoint from registry template...")

    payload = {
        "name": "cinema-ai-endpoint-v2",
        "templateId": template_id,
        "gpuType": "NVIDIA A100-SXM4-80GB",
        "minWorkers": 0,
        "maxWorkers": 10,
        "scalerType": "QUEUE_DELAY",
        "scalerValue": 5
    }

    response = requests.post(
        "https://api.runpod.io/v2/serverless/endpoint",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"📡 Endpoint Response Status: {response.status_code}")
    print(f"📡 Endpoint Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Endpoint created successfully!")
        print(f"📋 Endpoint ID: {result.get('id', 'N/A')}")
        return result.get('id')
    else:
        print(f"❌ Endpoint creation failed!")
        return None

def trigger_runpod_hub_sync():
    """Trigger RunPod Hub to sync with new release"""
    print("🔄 Triggering RunPod Hub sync...")

    # Create a webhook trigger
    webhook_url = "https://api.runpod.io/v2/hub/sync"

    payload = {
        "repository": "Flickinny11/cinema-ai-production-complete",
        "branch": "master",
        "trigger": "manual"
    }

    response = requests.post(
        webhook_url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"📡 Sync Response Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Sync triggered successfully!")
    else:
        print(f"❌ Sync failed: {response.text}")

def main():
    print("🎬 Push to RunPod Registry")
    print("=" * 40)

    # Step 1: Login to registry
    registry_data = login_to_registry()
    if not registry_data:
        print("❌ Cannot proceed without registry access")
        return

    # Step 2: Build and push image
    template_id = build_and_push_image()
    if not template_id:
        print("❌ Cannot proceed without template")
        return

    # Step 3: Create endpoint
    endpoint_id = create_endpoint_from_registry(template_id)
    if endpoint_id:
        print(f"\n🎉 Success! Your endpoint is ready:")
        print(f"🔗 Endpoint ID: {endpoint_id}")
        print(f"🔗 Console: https://console.runpod.io/serverless/{endpoint_id}")

    # Step 4: Trigger RunPod Hub sync
    trigger_runpod_hub_sync()

    print("\n📋 Next Steps:")
    print("1. Check RunPod Hub: https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")
    print("2. Click 'Check for Updates' button")
    print("3. Wait for sync to complete")

if __name__ == "__main__":
    main()
