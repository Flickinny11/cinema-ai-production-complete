#!/usr/bin/env python3
"""
Complete Deployment Script for Cinema AI Production Pipeline
August 2025 Edition
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Optional

# Configuration
API_KEY = os.getenv("RUNPOD_API_KEY", "your_api_key_here")
GITHUB_REPO = "https://github.com/Flickinny11/cinema-ai-production-complete"

class CinemaAIDeployer:
    """Deploy Cinema AI to RunPod"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runpod.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_template(self) -> Optional[str]:
        """Create RunPod template"""
        print("🔧 Creating RunPod template...")

        dockerfile_url = f"{GITHUB_REPO}/blob/main/Dockerfile"

        payload = {
            "name": f"cinema-ai-production-{int(time.time())}",
            "dockerfilePath": dockerfile_url,
            "containerDiskInGb": 350,
            "volumeInGb": 100,
            "volumeMountPath": "/models",
            "env": [
                {"key": "MODEL_QUALITY", "value": "cinema"},
                {"key": "HF_HUB_ENABLE_HF_TRANSFER", "value": "1"},
                {"key": "PYTORCH_CUDA_ALLOC_CONF", "value": "max_split_size_mb:512"}
            ],
            "isServerless": True,
            "dockerArgs": "--gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864"
        }

        response = requests.post(
            f"{self.base_url}/serverless/template",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code in [200, 201]:
            result = response.json()
            template_id = result.get("id")
            print(f"✅ Template created: {template_id}")
            return template_id
        else:
            print(f"❌ Failed to create template: {response.text}")
            return None

    def check_template_status(self, template_id: str) -> str:
        """Check template build status"""
        response = requests.get(
            f"{self.base_url}/serverless/template/{template_id}",
            headers=self.headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("status", "UNKNOWN")
        return "ERROR"

    def create_endpoint(self, template_id: str) -> Optional[str]:
        """Create serverless endpoint"""
        print("🚀 Creating serverless endpoint...")

        payload = {
            "name": f"cinema-ai-endpoint-{int(time.time())}",
            "templateId": template_id,
            "gpuIds": "NVIDIA A100-SXM4-80GB,NVIDIA H100 80GB HBM3",
            "networkVolumeId": None,
            "idleTimeout": 10,
            "scalerType": "QUEUE_DELAY",
            "scalerValue": 30,
            "workersMin": 0,
            "workersMax": 10,
            "flashBoot": True  # Enable fast boot
        }

        response = requests.post(
            f"{self.base_url}/serverless/endpoint",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code in [200, 201]:
            result = response.json()
            endpoint_id = result.get("id")
            print(f"✅ Endpoint created: {endpoint_id}")
            print(f"🔗 API URL: https://api.runpod.ai/v2/{endpoint_id}")
            return endpoint_id
        else:
            print(f"❌ Failed to create endpoint: {response.text}")
            return None

    def test_endpoint(self, endpoint_id: str) -> bool:
        """Test the endpoint"""
        print(f"🧪 Testing endpoint {endpoint_id}...")

        # Health check
        response = requests.post(
            f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            headers=self.headers,
            json={"input": {"type": "health_check"}},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint health check successful!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    def deploy_complete(self):
        """Complete deployment process"""
        print("="*60)
        print("🎬 Cinema AI Production Pipeline Deployment")
        print("="*60)

        # Step 1: Create template
        template_id = self.create_template()
        if not template_id:
            print("❌ Deployment failed at template creation")
            return False

        # Step 2: Wait for build
        print("\n⏳ Waiting for template build...")
        print("This typically takes 30-60 minutes for first build")

        max_wait = 120  # 2 hours max
        check_interval = 60  # Check every minute

        for i in range(max_wait):
            status = self.check_template_status(template_id)

            if status in ["READY", "COMPLETED", "SUCCESS"]:
                print("✅ Template build completed!")
                break
            elif status in ["FAILED", "ERROR"]:
                print("❌ Template build failed!")
                return False
            else:
                print(f"⏳ Build status: {status} ({i+1}/{max_wait} minutes)")
                time.sleep(check_interval)

        # Step 3: Create endpoint
        endpoint_id = self.create_endpoint(template_id)
        if not endpoint_id:
            print("❌ Failed to create endpoint")
            return False

        # Step 4: Test endpoint
        print("\n⏳ Waiting for endpoint to initialize...")
        time.sleep(30)

        if self.test_endpoint(endpoint_id):
            print("\n" + "="*60)
            print("🎉 Deployment Successful!")
            print("="*60)
            print(f"📋 Template ID: {template_id}")
            print(f"📋 Endpoint ID: {endpoint_id}")
            print(f"🔗 API URL: https://api.runpod.ai/v2/{endpoint_id}")
            print("\n📝 Example usage:")
            print(f"""
curl -X POST https://api.runpod.ai/v2/{endpoint_id}/runsync \\
  -H 'Authorization: Bearer {self.api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "input": {{
      "type": "single_scene",
      "scene": {{
        "description": "A beautiful sunset over the ocean",
        "duration": 10,
        "resolution": "720p",
        "music_mood": "peaceful"
      }}
    }}
  }}'
            """)
            return True
        else:
            print("⚠️ Deployment completed but endpoint test failed")
            print("The endpoint may still be initializing. Try again in a few minutes.")
            return False

def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Cinema AI to RunPod")
    parser.add_argument("--api-key", type=str, help="RunPod API key")
    parser.add_argument("--template-only", action="store_true", help="Create template only")
    parser.add_argument("--endpoint-from-template", type=str, help="Create endpoint from existing template ID")
    parser.add_argument("--test-endpoint", type=str, help="Test existing endpoint ID")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or API_KEY
    if api_key == "your_api_key_here":
        print("❌ Please provide your RunPod API key")
        print("   Use --api-key or set RUNPOD_API_KEY environment variable")
        return 1

    deployer = CinemaAIDeployer(api_key)

    if args.template_only:
        template_id = deployer.create_template()
        if template_id:
            print(f"✅ Template created: {template_id}")
            return 0
        return 1

    elif args.endpoint_from_template:
        endpoint_id = deployer.create_endpoint(args.endpoint_from_template)
        if endpoint_id:
            print(f"✅ Endpoint created: {endpoint_id}")
            if deployer.test_endpoint(endpoint_id):
                return 0
        return 1

    elif args.test_endpoint:
        if deployer.test_endpoint(args.test_endpoint):
            print("✅ Endpoint is working!")
            return 0
        return 1

    else:
        # Full deployment
        if deployer.deploy_complete():
            return 0
        return 1

if __name__ == "__main__":
    sys.exit(main())
