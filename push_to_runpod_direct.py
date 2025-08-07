#!/usr/bin/env python3
"""
Push directly to RunPod Registry
"""

import requests
import base64
import json
import os

# RunPod API Configuration
API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def push_to_runpod_registry():
    """Push Docker image to RunPod registry"""
    print("🐳 Pushing to RunPod registry...")

    # Read Dockerfile
    with open("Dockerfile", "r") as f:
        dockerfile_content = f.read()

    # Read Python files
    files = {
        "cinema_pipeline.py": base64.b64encode(open("cinema_pipeline.py", "rb").read()).decode(),
        "runpod_handler.py": base64.b64encode(open("runpod_handler.py", "rb").read()).decode(),
        "download_models.py": base64.b64encode(open("download_models.py", "rb").read()).decode()
    }

    # Build payload for RunPod registry
    payload = {
        "name": "cinema-ai-production-v3",
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

    # Try different RunPod API endpoints
    endpoints = [
        "https://api.runpod.io/v2/serverless/template",
        "https://api.runpod.io/v2/registry/build",
        "https://api.runpod.io/v2/container/build"
    ]

    for endpoint in endpoints:
        print(f"\n📡 Trying endpoint: {endpoint}")

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )

            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response: {response.text}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully pushed to RunPod registry!")
                print(f"📋 Template/Image ID: {result.get('id', 'N/A')}")
                return result.get('id')
            elif response.status_code == 404:
                print(f"❌ Endpoint not found: {endpoint}")
            else:
                print(f"⚠️  Unexpected response from {endpoint}")

        except Exception as e:
            print(f"❌ Error with {endpoint}: {e}")

    return None

def create_endpoint_from_registry(template_id):
    """Create endpoint from registry template"""
    if not template_id:
        print("❌ No template ID provided")
        return None

    print("🚀 Creating endpoint from registry template...")

    payload = {
        "name": "cinema-ai-endpoint-v3",
        "templateId": template_id,
        "gpuType": "NVIDIA A100-SXM4-80GB",
        "minWorkers": 0,
        "maxWorkers": 10,
        "scalerType": "QUEUE_DELAY",
        "scalerValue": 5
    }

    try:
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

    except Exception as e:
        print(f"❌ Error creating endpoint: {e}")
        return None

def trigger_runpod_hub_sync():
    """Trigger RunPod Hub sync"""
    print("🔄 Triggering RunPod Hub sync...")

    # Try to trigger sync via API
    sync_payload = {
        "repository": "Flickinny11/cinema-ai-production-complete",
        "branch": "master",
        "trigger": "manual"
    }

    sync_endpoints = [
        "https://api.runpod.io/v2/hub/sync",
        "https://api.runpod.io/v2/hub/Flickinny11/cinema-ai-production-complete/sync"
    ]

    for endpoint in sync_endpoints:
        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=sync_payload,
                timeout=30
            )

            print(f"📡 Sync Response Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Sync triggered successfully!")
                return True
            else:
                print(f"❌ Sync failed: {response.text}")

        except Exception as e:
            print(f"❌ Error triggering sync: {e}")

    return False

def main():
    print("🎬 Push to RunPod Registry")
    print("=" * 40)

    # Step 1: Push to RunPod registry
    template_id = push_to_runpod_registry()

    if template_id:
        print(f"\n✅ Successfully pushed to RunPod registry!")
        print(f"📋 Template ID: {template_id}")

        # Step 2: Create endpoint
        endpoint_id = create_endpoint_from_registry(template_id)
        if endpoint_id:
            print(f"\n🎉 Success! Your endpoint is ready:")
            print(f"🔗 Endpoint ID: {endpoint_id}")
            print(f"🔗 Console: https://console.runpod.io/serverless/{endpoint_id}")
    else:
        print("\n❌ Failed to push to RunPod registry")

    # Step 3: Trigger RunPod Hub sync
    trigger_runpod_hub_sync()

    print("\n📋 Manual Steps:")
    print("1. Check RunPod Hub: https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")
    print("2. Click 'Check for Updates' button")
    print("3. Wait for sync to complete")
    print("4. Verify all requirements are met")

if __name__ == "__main__":
    main()
