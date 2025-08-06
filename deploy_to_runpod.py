#!/usr/bin/env python3
"""
Deploy Cinema AI Pipeline to RunPod Serverless
"""

import requests
import base64
import os
import json
import time

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"
BASE_URL = "https://api.runpod.io/v2"

def read_file_content(file_path):
    """Read file content and return as base64 string"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def create_serverless_template():
    """Create template via API"""
    print("🔧 Creating serverless template...")

    # Read Dockerfile
    dockerfile_content = read_file_content("Dockerfile")

    # Read Python files
    files_content = {
        "cinema_pipeline.py": read_file_content("cinema_pipeline.py"),
        "runpod_handler.py": read_file_content("runpod_handler.py"),
        "download_models.py": read_file_content("download_models.py")
    }

    # Create template
    response = requests.post(
        f"{BASE_URL}/serverless/template",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "name": "cinema-ai-production",
            "dockerfile": dockerfile_content,
            "dockerContext": files_content,
            "containerDiskInGb": 350,
            "dockerArgs": {
                "buildArgs": {
                    "CUDA_VERSION": "12.1"
                }
            }
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Template created successfully!")
        print(f"   Template ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Failed to create template: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def create_endpoint(template_id):
    """Create endpoint from template"""
    print("🚀 Creating serverless endpoint...")

    response = requests.post(
        f"{BASE_URL}/serverless/endpoint",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "name": "cinema-ai-endpoint",
            "templateId": template_id,
            "gpuType": "A100-80G",
            "minWorkers": 0,
            "maxWorkers": 10,
            "scalerType": "QUEUE_DELAY",
            "scalerValue": 5
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Endpoint created successfully!")
        print(f"   Endpoint ID: {result['id']}")
        print(f"   Endpoint URL: https://api.runpod.ai/v2/{result['id']}")
        return result
    else:
        print(f"❌ Failed to create endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_endpoint(endpoint_id):
    """Test the endpoint with a health check"""
    print("🧪 Testing endpoint...")

    response = requests.post(
        f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "input": {
                "type": "health_check"
            }
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Endpoint test successful!")
        print(f"   Response: {result}")
        return True
    else:
        print(f"❌ Endpoint test failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Main deployment function"""
    print("🎬 Cinema AI Pipeline Deployment to RunPod")
    print("=" * 50)

    # Step 1: Create template
    template_id = create_serverless_template()
    if not template_id:
        print("❌ Failed to create template. Exiting.")
        return

    # Step 2: Create endpoint
    endpoint_result = create_endpoint(template_id)
    if not endpoint_result:
        print("❌ Failed to create endpoint. Exiting.")
        return

    endpoint_id = endpoint_result['id']

    # Step 3: Wait for build to complete
    print("⏳ Waiting for build to complete (this may take 60-90 minutes)...")
    print("   You'll receive an email when the build is ready.")
    print("   You can check status at: https://runpod.io/console/serverless")

    # Step 4: Test endpoint (optional - can be done later)
    print("\n📋 Deployment Summary:")
    print(f"   Template ID: {template_id}")
    print(f"   Endpoint ID: {endpoint_id}")
    print(f"   Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}")
    print("\n🔗 Test your endpoint with:")
    print(f"   curl -X POST https://api.runpod.ai/v2/{endpoint_id}/runsync \\")
    print(f"     -H 'Authorization: Bearer {API_KEY}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"input\": {{\"type\": \"health_check\"}}}}'")

    print("\n💰 Cost Information:")
    print("   • A100 80GB: $2.49/hour (when active)")
    print("   • Serverless: $0 when idle!")
    print("   • Cold start: 30-45 seconds")
    print("   • Warm start: <2 seconds")

if __name__ == "__main__":
    main()
