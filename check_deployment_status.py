#!/usr/bin/env python3
"""
Check Deployment Status and Verify RunPod Sync
"""

import requests
import json
import time

def check_github_repository():
    """Check GitHub repository status"""
    print("🔍 Checking GitHub Repository...")
    print("📋 Repository: https://github.com/Flickinny11/cinema-ai-production-complete")

    # Check if we can access the raw Dockerfile
    dockerfile_url = "https://raw.githubusercontent.com/Flickinny11/cinema-ai-production-complete/master/Dockerfile"

    try:
        response = requests.get(dockerfile_url, timeout=10)
        if response.status_code == 200:
            content = response.text
            if "nvidia/cuda:11.8.0-devel-ubuntu20.04" in content:
                print("✅ GitHub has correct Dockerfile with CUDA 11.8")
                return True
            else:
                print("❌ GitHub has wrong Dockerfile!")
                print("Current content:")
                print(content[:500])
                return False
        else:
            print(f"❌ Cannot access GitHub Dockerfile: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing GitHub: {e}")
        return False

def check_runpod_hub_sync():
    """Check if RunPod Hub is syncing from GitHub"""
    print("\n🔗 Checking RunPod Hub Sync...")
    print("📋 RunPod Hub: https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")

    print("ℹ️  Manual verification steps:")
    print("   1. Go to RunPod Hub console")
    print("   2. Check if project shows all requirements met")
    print("   3. Check if Dockerfile shows correct base image")
    print("   4. Check if build is using latest GitHub version")

def check_webhook_status():
    """Check GitHub webhook configuration"""
    print("\n🔗 Checking GitHub Webhook...")
    print("📋 Webhook URL: https://github.com/Flickinny11/cinema-ai-production-complete/settings/hooks")

    print("ℹ️  To verify webhook:")
    print("   1. Go to repository settings")
    print("   2. Check 'Webhooks' section")
    print("   3. Verify RunPod webhook is configured")
    print("   4. Check recent webhook deliveries")

def check_manual_deployment():
    """Provide manual deployment instructions"""
    print("\n🚀 Manual Deployment Instructions:")
    print("=" * 50)
    print()
    print("Since RunPod Hub might not be auto-syncing, try manual deployment:")
    print()
    print("1️⃣  Go to RunPod Console:")
    print("   https://runpod.io/console/serverless")
    print()
    print("2️⃣  Create Custom Template:")
    print("   - Click 'Custom Templates'")
    print("   - Click 'New Template'")
    print("   - Name: cinema-ai-production-v2")
    print("   - Dockerfile URL: https://raw.githubusercontent.com/Flickinny11/cinema-ai-production-complete/master/Dockerfile")
    print("   - Container Disk: 350 GB")
    print()
    print("3️⃣  Verify Dockerfile Content:")
    print("   - Should show: FROM nvidia/cuda:11.8.0-devel-ubuntu20.04")
    print("   - Should show: torch==2.0.1+cu118")
    print()
    print("4️⃣  Create Endpoint:")
    print("   - GPU: A100 80GB")
    print("   - Min Workers: 0")
    print("   - Max Workers: 10")
    print()

def main():
    print("🎬 Deployment Status Check")
    print("=" * 40)

    # Check GitHub repository
    github_ok = check_github_repository()

    # Check RunPod Hub sync
    check_runpod_hub_sync()

    # Check webhook status
    check_webhook_status()

    # Provide manual deployment instructions
    check_manual_deployment()

    if github_ok:
        print("\n✅ GitHub repository is correct!")
        print("❓ RunPod Hub might not be auto-syncing")
        print("💡 Try manual deployment using the instructions above")
    else:
        print("\n❌ GitHub repository has issues!")
        print("🔧 Fix GitHub first, then try RunPod deployment")

if __name__ == "__main__":
    main()
