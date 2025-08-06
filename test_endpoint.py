#!/usr/bin/env python3
"""
Test Cinema AI RunPod Endpoint
"""

import requests
import json
import sys

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def test_health_check(endpoint_id):
    """Test endpoint health check"""
    print(f"🧪 Testing endpoint: {endpoint_id}")

    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": {
            "type": "health_check"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ Health check successful!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_video_generation(endpoint_id, script):
    """Test video generation"""
    print(f"🎬 Testing video generation: {endpoint_id}")

    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": {
            "type": "script_to_video",
            "script": script
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=300)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ Video generation successful!")
            return True
        else:
            print("❌ Video generation failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_endpoint.py <endpoint_id> [script]")
        print("Example: python test_endpoint.py abc123")
        print("Example: python test_endpoint.py abc123 'A beautiful sunset over the ocean'")
        return

    endpoint_id = sys.argv[1]
    script = sys.argv[2] if len(sys.argv) > 2 else "A beautiful sunset over the ocean"

    print("🎬 Cinema AI Endpoint Tester")
    print("=" * 30)

    # Test health check
    if test_health_check(endpoint_id):
        print("\n✅ Endpoint is working!")

        # Test video generation
        print(f"\n🎬 Testing video generation with script: '{script}'")
        test_video_generation(endpoint_id, script)
    else:
        print("\n❌ Endpoint is not working. Please check:")
        print("   • Endpoint ID is correct")
        print("   • Endpoint is built and ready")
        print("   • API key is valid")

if __name__ == "__main__":
    main()
