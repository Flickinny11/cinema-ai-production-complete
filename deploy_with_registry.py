#!/usr/bin/env python3
"""
Deploy Cinema AI using RunPod's Container Registry
"""

import requests
import base64
import json
import time

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def create_container_image():
    """Create container image on RunPod"""
    print("🔧 Creating container image on RunPod...")

    # Read Dockerfile
    with open("Dockerfile", "r") as f:
        dockerfile = f.read()

    # Read Python files
    files = {
        "cinema_pipeline.py": base64.b64encode(open("cinema_pipeline.py", "rb").read()).decode(),
        "runpod_handler.py": base64.b64encode(open("runpod_handler.py", "rb").read()).decode(),
        "download_models.py": base64.b64encode(open("download_models.py", "rb").read()).decode()
    }

    payload = {
        "name": "cinema-ai-production",
        "dockerfile": base64.b64encode(dockerfile.encode()).decode(),
        "dockerContext": files,
        "containerDiskInGb": 350,
        "dockerArgs": {
            "buildArgs": {
                "CUDA_VERSION": "11.8"
            }
        }
    }

    response = requests.post(
        "https://api.runpod.io/v2/serverless/template",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Container image created: {result['id']}")
        return result['id']
    else:
        print("❌ Failed to create container image")
        return None

def create_endpoint(template_id):
    """Create endpoint from template"""
    print("🚀 Creating serverless endpoint...")

    payload = {
        "name": "cinema-ai-endpoint",
        "templateId": template_id,
        "gpuType": "A100-80G",
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

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Endpoint created: {result['id']}")
        return result['id']
    else:
        print("❌ Failed to create endpoint")
        return None

def check_template_status(template_id):
    """Check if template is ready"""
    print("⏳ Checking template build status...")

    response = requests.get(
        f"https://api.runpod.io/v2/serverless/template/{template_id}",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Template status: {result.get('status', 'unknown')}")
        return result.get('status') == 'READY'
    else:
        print(f"Failed to check status: {response.status_code}")
        return False

def main():
    print("🎬 Deploying Cinema AI to RunPod Container Registry")
    print("=" * 55)

    # Step 1: Create container image
    template_id = create_container_image()
    if not template_id:
        print("❌ Failed to create container image. Exiting.")
        return

    # Step 2: Wait for build to complete
    print("\n⏳ Waiting for container image to build...")
    print("   This may take 60-90 minutes.")
    print("   You'll receive an email when ready.")
    print("   Check status at: https://runpod.io/console/serverless")

    # Step 3: Create endpoint (can be done after build completes)
    print("\n📋 Next Steps:")
    print("1. Wait for the container image to finish building")
    print("2. Run this script again to create the endpoint:")
    print(f"   python deploy_with_registry.py --create-endpoint {template_id}")

    print(f"\n📋 Template ID: {template_id}")
    print("🔗 Check status: https://runpod.io/console/serverless")

if __name__ == "__main__":
    main()
