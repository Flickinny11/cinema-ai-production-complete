#!/usr/bin/env python3
"""
Simple Cinema AI Deployment to RunPod
"""

import requests
import base64
import json

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def create_template():
    """Create a serverless template"""
    print("🔧 Creating serverless template...")
    
    # Read the Dockerfile
    with open("Dockerfile", "r") as f:
        dockerfile = f.read()
    
    # Create template payload
    payload = {
        "name": "cinema-ai-production",
        "dockerfile": base64.b64encode(dockerfile.encode()).decode(),
        "containerDiskInGb": 350,
        "dockerArgs": {
            "buildArgs": {
                "CUDA_VERSION": "12.1"
            }
        }
    }
    
    # Add files to context
    files = ["cinema_pipeline.py", "runpod_handler.py", "download_models.py"]
    docker_context = {}
    
    for file in files:
        with open(file, "rb") as f:
            docker_context[file] = base64.b64encode(f.read()).decode()
    
    payload["dockerContext"] = docker_context
    
    # Make API request
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
        print(f"✅ Template created: {result['id']}")
        return result['id']
    else:
        print("❌ Failed to create template")
        return None

def create_endpoint(template_id):
    """Create endpoint from template"""
    print("🚀 Creating endpoint...")
    
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

def main():
    print("🎬 Deploying Cinema AI to RunPod")
    print("=" * 40)
    
    # Create template
    template_id = create_template()
    if not template_id:
        return
    
    # Create endpoint
    endpoint_id = create_endpoint(template_id)
    if not endpoint_id:
        return
    
    print("\n✅ Deployment Complete!")
    print(f"Template ID: {template_id}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}")
    
    print("\n🔗 Test with:")
    print(f"curl -X POST https://api.runpod.ai/v2/{endpoint_id}/runsync \\")
    print(f"  -H 'Authorization: Bearer {API_KEY}' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"input\": {{\"type\": \"health_check\"}}}}'")

if __name__ == "__main__":
    main() 