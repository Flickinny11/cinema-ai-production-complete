#!/usr/bin/env python3
"""
Verify RunPod Hub Configuration
"""

import json
import os

def verify_hub_configuration():
    """Verify RunPod Hub configuration"""
    print("🔍 Verifying RunPod Hub Configuration")
    print("=" * 50)

    # Check hub.json
    hub_file = ".runpod/hub.json"
    if not os.path.exists(hub_file):
        print("❌ hub.json not found!")
        return False

    try:
        with open(hub_file, 'r') as f:
            hub_config = json.load(f)

        print("✅ hub.json is valid JSON")

        # Check required fields
        required_fields = ["version", "name", "git_url", "template", "serverless", "runtime"]
        for field in required_fields:
            if field not in hub_config:
                print(f"❌ Missing required field: {field}")
                return False
            else:
                print(f"✅ Found required field: {field}")

        # Check template configuration
        template = hub_config.get("template", {})
        if "dockerfile_path" not in template:
            print("❌ Missing dockerfile_path in template")
            return False
        else:
            print(f"✅ Found dockerfile_path: {template['dockerfile_path']}")

        # Check build configuration
        if "build" in hub_config:
            build = hub_config["build"]
            if "base_image" in build:
                print(f"✅ Found base_image: {build['base_image']}")
            if "python_packages" in build:
                print(f"✅ Found {len(build['python_packages'])} python packages")
        else:
            print("⚠️  No build configuration found")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ hub.json is not valid JSON: {e}")
        return False

def verify_github_repository():
    """Verify GitHub repository is accessible"""
    print("\n🔗 Verifying GitHub Repository...")

    import requests

    # Check if we can access the repository
    repo_url = "https://api.github.com/repos/Flickinny11/cinema-ai-production-complete"
    try:
        response = requests.get(repo_url, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository accessible: {repo_data['full_name']}")
            print(f"   Private: {repo_data['private']}")
            print(f"   Default branch: {repo_data['default_branch']}")
            return True
        else:
            print(f"❌ Cannot access repository: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing repository: {e}")
        return False

def verify_dockerfile():
    """Verify Dockerfile is correct"""
    print("\n🐳 Verifying Dockerfile...")

    dockerfile = "Dockerfile"
    if not os.path.exists(dockerfile):
        print("❌ Dockerfile not found!")
        return False

    with open(dockerfile, 'r') as f:
        content = f.read()

    # Check for correct base image
    if "nvidia/cuda:11.8.0-devel-ubuntu20.04" in content:
        print("✅ Dockerfile has correct base image")
    else:
        print("❌ Dockerfile has wrong base image!")
        return False

    # Check for correct PyTorch version
    if "torch==2.0.1+cu118" in content:
        print("✅ Dockerfile has correct PyTorch version")
    else:
        print("❌ Dockerfile has wrong PyTorch version!")
        return False

    return True

def check_runpod_hub_status():
    """Provide RunPod Hub status information"""
    print("\n📋 RunPod Hub Status:")
    print("=" * 30)
    print()
    print("🔗 RunPod Hub URL:")
    print("   https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")
    print()
    print("📋 What RunPod Hub should do:")
    print("   1. Detect .runpod/hub.json configuration")
    print("   2. Build Docker image from GitHub repository")
    print("   3. Create template with correct base image")
    print("   4. Make project available for deployment")
    print()
    print("🔍 If RunPod Hub is not working:")
    print("   1. Check if project appears in RunPod Hub console")
    print("   2. Check if all requirements show as met")
    print("   3. Check if Dockerfile shows correct base image")
    print("   4. Try refreshing the RunPod Hub page")

def main():
    print("🎬 RunPod Hub Verification")
    print("=" * 40)

    # Verify hub configuration
    hub_ok = verify_hub_configuration()

    # Verify GitHub repository
    github_ok = verify_github_repository()

    # Verify Dockerfile
    dockerfile_ok = verify_dockerfile()

    # Check RunPod Hub status
    check_runpod_hub_status()

    if hub_ok and github_ok and dockerfile_ok:
        print("\n✅ All verifications passed!")
        print("🎯 RunPod Hub should be working correctly")
        print("🔗 Check: https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")
    else:
        print("\n❌ Some verifications failed!")
        print("🔧 Fix the issues above before RunPod Hub will work")

if __name__ == "__main__":
    main()
