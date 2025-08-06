#!/usr/bin/env python3
"""
Verify RunPod Handler Configuration
"""

import os
import sys

def verify_handler():
    """Verify handler script exists and is properly configured"""
    print("🔍 Verifying RunPod Handler Configuration")
    print("=" * 40)
    
    # Check if handler file exists
    handler_file = "runpod_handler.py"
    if os.path.exists(handler_file):
        print(f"✅ Handler file exists: {handler_file}")
    else:
        print(f"❌ Handler file missing: {handler_file}")
        return False
    
    # Check if handler function exists
    try:
        with open(handler_file, 'r') as f:
            content = f.read()
            if 'def handler(' in content:
                print("✅ Handler function found")
            else:
                print("❌ Handler function not found")
                return False
    except Exception as e:
        print(f"❌ Error reading handler: {e}")
        return False
    
    # Check hub.json configuration
    hub_file = ".runpod/hub.json"
    if os.path.exists(hub_file):
        print(f"✅ Hub configuration exists: {hub_file}")
    else:
        print(f"❌ Hub configuration missing: {hub_file}")
        return False
    
    # Check tests.json
    tests_file = ".runpod/tests.json"
    if os.path.exists(tests_file):
        print(f"✅ Tests configuration exists: {tests_file}")
    else:
        print(f"❌ Tests configuration missing: {tests_file}")
        return False
    
    # Check Dockerfile
    dockerfile = "Dockerfile"
    if os.path.exists(dockerfile):
        print(f"✅ Dockerfile exists: {dockerfile}")
    else:
        print(f"❌ Dockerfile missing: {dockerfile}")
        return False
    
    # Check README badge
    readme_file = "README.md"
    if os.path.exists(readme_file):
        with open(readme_file, 'r') as f:
            content = f.read()
            if 'api.runpod.io/badge' in content:
                print("✅ RunPod badge found in README")
            else:
                print("❌ RunPod badge missing from README")
                return False
    
    print("\n✅ All RunPod Hub requirements verified!")
    return True

if __name__ == "__main__":
    success = verify_handler()
    if success:
        print("\n🎉 Your project is ready for RunPod Hub!")
    else:
        print("\n❌ Some requirements are missing. Please fix them.")
        sys.exit(1) 