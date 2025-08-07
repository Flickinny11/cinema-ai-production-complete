#!/usr/bin/env python3
"""
Trigger RunPod Hub Sync
"""

import requests
import json

# RunPod API Configuration
API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def trigger_manual_sync():
    """Trigger manual sync of RunPod Hub"""
    print("🔄 Triggering manual RunPod Hub sync...")

    # Try different sync endpoints
    sync_endpoints = [
        "https://api.runpod.io/v2/hub/sync",
        "https://api.runpod.io/v2/hub/Flickinny11/cinema-ai-production-complete/sync",
        "https://api.runpod.io/v2/hub/project/sync"
    ]

    payload = {
        "repository": "Flickinny11/cinema-ai-production-complete",
        "branch": "master",
        "trigger": "manual"
    }

    for endpoint in sync_endpoints:
        print(f"📡 Trying endpoint: {endpoint}")

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )

            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response: {response.text}")

            if response.status_code == 200:
                print(f"✅ Sync triggered successfully via {endpoint}")
                return True
            elif response.status_code == 404:
                print(f"❌ Endpoint not found: {endpoint}")
            else:
                print(f"⚠️  Unexpected response from {endpoint}")

        except Exception as e:
            print(f"❌ Error with {endpoint}: {e}")

    return False

def check_hub_status():
    """Check RunPod Hub project status"""
    print("🔍 Checking RunPod Hub project status...")

    try:
        response = requests.get(
            "https://api.runpod.io/v2/hub/Flickinny11/cinema-ai-production-complete",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30
        )

        print(f"📡 Hub Status Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Project Status: {json.dumps(data, indent=2)}")
        else:
            print(f"📡 Response: {response.text}")

    except Exception as e:
        print(f"❌ Error checking hub status: {e}")

def create_webhook_trigger():
    """Create a webhook to trigger sync"""
    print("🔗 Creating webhook trigger...")

    webhook_payload = {
        "url": "https://api.runpod.io/v2/hub/webhook",
        "events": ["push"],
        "repository": "Flickinny11/cinema-ai-production-complete"
    }

    try:
        response = requests.post(
            "https://api.runpod.io/v2/hub/webhook",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=webhook_payload,
            timeout=30
        )

        print(f"📡 Webhook Response: {response.status_code}")
        print(f"📡 Webhook Response: {response.text}")

    except Exception as e:
        print(f"❌ Error creating webhook: {e}")

def main():
    print("🎬 Trigger RunPod Hub Sync")
    print("=" * 40)

    # Step 1: Check current hub status
    check_hub_status()

    # Step 2: Try manual sync
    if trigger_manual_sync():
        print("\n✅ Manual sync triggered!")
    else:
        print("\n❌ Manual sync failed")

    # Step 3: Try webhook approach
    create_webhook_trigger()

    print("\n📋 Manual Steps:")
    print("1. Go to: https://console.runpod.io/hub/Flickinny11/cinema-ai-production-complete")
    print("2. Look for 'Check for Updates' button")
    print("3. Click it to manually trigger sync")
    print("4. Wait for the sync to complete")
    print("5. Check if all requirements are now met")

if __name__ == "__main__":
    main()
