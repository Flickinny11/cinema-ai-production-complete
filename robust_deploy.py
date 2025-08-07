#!/usr/bin/env python3
"""
Robust RunPod Deployment with Error Handling
"""

import requests
import json
import time
import sys

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def create_template_via_api():
    """Create template using direct Dockerfile URL"""
    print("🔧 Creating RunPod template...")
    
    # Use the raw GitHub URL for your fixed Dockerfile
    dockerfile_url = "https://raw.githubusercontent.com/Flickinny11/cinema-ai-production-complete/main/Dockerfile"
    
    payload = {
        "name": f"cinema-ai-production-{int(time.time())}",  # Unique name
        "imageName": "runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04",  # Fallback base image
        "dockerfilePath": dockerfile_url,
        "containerDiskInGb": 350,
        "volumeInGb": 0,
        "volumeMountPath": "/workspace",
        "env": [
            {"key": "MODEL_QUALITY", "value": "cinema"},
            {"key": "PARALLEL_PROCESSING", "value": "true"},
            {"key": "HF_HOME", "value": "/models/cache"}
        ],
        "isServerless": True
    }
    
    response = requests.post(
        "https://api.runpod.io/v2/template",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        template_id = result.get('id') or result.get('templateId')
        print(f"✅ Template created: {template_id}")
        return template_id
    else:
        print(f"❌ Failed to create template: {response.text}")
        
        # Try alternative endpoint
        print("🔄 Trying alternative endpoint...")
        response = requests.post(
            "https://api.runpod.io/v2/serverless/template",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            template_id = result.get('id')
            print(f"✅ Template created via serverless endpoint: {template_id}")
            return template_id
        else:
            print(f"❌ Alternative endpoint also failed: {response.text}")
            return None

def check_template_status(template_id):
    """Check template build status"""
    print(f"⏳ Checking template {template_id} status...")
    
    endpoints = [
        f"https://api.runpod.io/v2/template/{template_id}",
        f"https://api.runpod.io/v2/serverless/template/{template_id}"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'UNKNOWN')
                print(f"📋 Template Status: {status}")
                
                if 'buildLogs' in data:
                    print("📝 Build Logs (last 10 lines):")
                    logs = data['buildLogs'].split('\n')[-10:]
                    for log in logs:
                        print(f"   {log}")
                
                return status
        except Exception as e:
            print(f"⚠️ Error checking status at {endpoint}: {e}")
    
    return "UNKNOWN"

def create_endpoint(template_id):
    """Create serverless endpoint"""
    print("🚀 Creating serverless endpoint...")
    
    payload = {
        "name": f"cinema-ai-endpoint-{int(time.time())}",
        "templateId": template_id,
        "gpuIds": "NVIDIA A100-SXM4-80GB,NVIDIA A100 80GB PCIe",  # Multiple GPU options
        "networkVolumeId": None,
        "locations": None,  # Let RunPod choose best location
        "idleTimeout": 5,
        "scalerType": "QUEUE_DELAY",
        "scalerValue": 30,
        "workersMin": 0,
        "workersMax": 3,  # Start with fewer workers
        "flashBoot": False
    }
    
    response = requests.post(
        "https://api.runpod.io/v2/serverless/endpoint",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        endpoint_id = result.get('id')
        print(f"✅ Endpoint created: {endpoint_id}")
        print(f"🔗 Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}")
        return endpoint_id
    else:
        print(f"❌ Failed to create endpoint: {response.text}")
        return None

def test_endpoint(endpoint_id):
    """Test the endpoint"""
    print(f"🧪 Testing endpoint {endpoint_id}...")
    
    # Wait a bit for endpoint to initialize
    print("⏳ Waiting 30 seconds for endpoint to initialize...")
    time.sleep(30)
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/health"
    
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Endpoint is healthy!")
            return True
        else:
            print(f"⚠️ Endpoint returned status {response.status_code}")
            
            # Try a runsync test
            print("🧪 Trying runsync health check...")
            response = requests.post(
                f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"input": {"type": "health_check"}},
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ Runsync health check successful!")
                print(f"📋 Response: {response.json()}")
                return True
            else:
                print(f"❌ Runsync test failed: {response.status_code}")
                print(f"📋 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def main():
    print("🎬 Robust RunPod Deployment")
    print("=" * 50)
    
    # Step 1: Create template
    template_id = create_template_via_api()
    if not template_id:
        print("\n❌ Failed to create template")
        print("🔧 Troubleshooting steps:")
        print("1. Verify your API key is correct")
        print("2. Check you have sufficient credits")
        print("3. Try the web console: https://runpod.io/console/serverless")
        return 1
    
    # Step 2: Monitor build
    print("\n⏳ Monitoring template build...")
    print("This typically takes 30-60 minutes for first build")
    
    max_wait = 120  # 2 hours max
    check_interval = 60  # Check every minute
    
    for i in range(max_wait):
        status = check_template_status(template_id)
        
        if status in ["READY", "COMPLETED", "SUCCESS"]:
            print("✅ Template build completed!")
            break
        elif status in ["FAILED", "ERROR"]:
            print("❌ Template build failed!")
            print("Check build logs in RunPod console for details")
            return 1
        else:
            print(f"⏳ Build in progress... ({i+1}/{max_wait} minutes)")
            time.sleep(check_interval)
    
    # Step 3: Create endpoint
    endpoint_id = create_endpoint(template_id)
    if not endpoint_id:
        print("\n❌ Failed to create endpoint")
        return 1
    
    # Step 4: Test endpoint
    if test_endpoint(endpoint_id):
        print("\n🎉 Deployment successful!")
        print(f"📋 Template ID: {template_id}")
        print(f"📋 Endpoint ID: {endpoint_id}")
        print(f"🔗 API URL: https://api.runpod.ai/v2/{endpoint_id}")
        print("\n📝 Test your endpoint with:")
        print(f"curl -X POST https://api.runpod.ai/v2/{endpoint_id}/runsync \\")
        print(f"  -H 'Authorization: Bearer {API_KEY}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"input\": {{\"type\": \"health_check\"}}}}'")
        return 0
    else:
        print("\n⚠️ Deployment completed but endpoint test failed")
        print("The endpoint may still be initializing. Try again in a few minutes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
