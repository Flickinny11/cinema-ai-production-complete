#!/usr/bin/env python3
"""
Force Deploy to RunPod and Verify Changes
"""

import requests
import base64
import json
import time

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def verify_dockerfile():
    """Verify the Dockerfile has the correct base image"""
    print("🔍 Verifying Dockerfile...")

    with open("Dockerfile", "r") as f:
        content = f.read()
        if "nvidia/cuda:11.8.0-devel-ubuntu20.04" in content:
            print("✅ Dockerfile has correct base image: nvidia/cuda:11.8.0-devel-ubuntu20.04")
            return True
        else:
            print("❌ Dockerfile has wrong base image!")
            print("Current content:")
            print(content[:500])
            return False

def force_create_template():
    """Force create a new template with current files"""
    print("🚀 Force creating RunPod template...")

    # Read current Dockerfile
    with open("Dockerfile", "r") as f:
        dockerfile = f.read()

    # Read Python files
    files = {
        "cinema_pipeline.py": base64.b64encode(open("cinema_pipeline.py", "rb").read()).decode(),
        "runpod_handler.py": base64.b64encode(open("runpod_handler.py", "rb").read()).decode(),
        "download_models.py": base64.b64encode(open("download_models.py", "rb").read()).decode()
    }

    payload = {
        "name": "cinema-ai-production-v2",
        "dockerfile": base64.b64encode(dockerfile.encode()).decode(),
        "dockerContext": files,
        "containerDiskInGb": 350,
        "dockerArgs": {
            "buildArgs": {
                "CUDA_VERSION": "11.8"
            }
        }
    }

    print("📋 Template payload:")
    print(f"  - Name: {payload['name']}")
    print(f"  - Container Disk: {payload['containerDiskInGb']}GB")
    print(f"  - CUDA Version: {payload['dockerArgs']['buildArgs']['CUDA_VERSION']}")

    response = requests.post(
        "https://api.runpod.io/v2/serverless/template",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"📡 API Response Status: {response.status_code}")
    print(f"📡 API Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Template created successfully!")
        print(f"   Template ID: {result['id']}")
        return result['id']
    else:
        print("❌ Failed to create template")
        return None

def check_github_webhook():
    """Check if GitHub webhook is properly configured"""
    print("🔗 Checking GitHub webhook status...")

    # This would require GitHub API access to check webhooks
    print("ℹ️  To verify GitHub → RunPod sync:")
    print("   1. Go to: https://github.com/Flickinny11/cinema-ai-production-complete/settings/hooks")
    print("   2. Check if RunPod webhook is configured")
    print("   3. Check recent webhook deliveries")

def main():
    print("🎬 Force Deploy to RunPod")
    print("=" * 40)

    # Step 1: Verify Dockerfile
    if not verify_dockerfile():
        print("❌ Dockerfile verification failed!")
        return

    # Step 2: Force create template
    template_id = force_create_template()
    if not template_id:
        print("❌ Template creation failed!")
        return

    # Step 3: Check GitHub webhook
    check_github_webhook()

    print("\n✅ Force deployment initiated!")
    print(f"📋 Template ID: {template_id}")
    print("🔗 Check RunPod console: https://runpod.io/console/serverless")
    print("📋 Check GitHub webhooks: https://github.com/Flickinny11/cinema-ai-production-complete/settings/hooks")

if __name__ == "__main__":
    main()
