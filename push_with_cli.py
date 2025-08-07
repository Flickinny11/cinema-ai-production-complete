#!/usr/bin/env python3
"""
Push to RunPod using CLI
"""

import subprocess
import os
import json

def check_runpod_cli():
    """Check if RunPod CLI is installed"""
    try:
        result = subprocess.run(["runpod", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ RunPod CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ RunPod CLI not found")
            return False
    except FileNotFoundError:
        print("❌ RunPod CLI not installed")
        return False

def configure_runpod():
    """Configure RunPod CLI with API key"""
    print("🔐 Configuring RunPod CLI...")
    
    # Set API key
    api_key = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"
    
    try:
        # Configure API key
        result = subprocess.run([
            "runpod", "config", "set", "api_key", api_key
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ API key configured")
            return True
        else:
            print(f"❌ Failed to configure API key: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error configuring RunPod: {e}")
        return False

def build_and_push():
    """Build and push using RunPod CLI"""
    print("🐳 Building and pushing with RunPod CLI...")
    
    try:
        # Build and push
        result = subprocess.run([
            "runpod", "project", "deploy",
            "--name", "cinema-ai-production-v2",
            "--gpu", "A100-80G",
            "--min-workers", "0",
            "--max-workers", "10"
        ], capture_output=True, text=True)
        
        print(f"📡 CLI Output: {result.stdout}")
        if result.stderr:
            print(f"📡 CLI Errors: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Successfully deployed with CLI!")
            return True
        else:
            print(f"❌ CLI deployment failed: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error with CLI deployment: {e}")
        return False

def create_project_config():
    """Create runpod.toml for CLI deployment"""
    print("📝 Creating RunPod project configuration...")
    
    config = """[project]
name = "cinema-ai-production-v2"
base_image = "nvidia/cuda:11.8.0-devel-ubuntu20.04"

[build]
gpu_required = false
system_packages = [
    "python3.8",
    "python3-pip", 
    "git",
    "ffmpeg",
    "wget",
    "curl",
    "build-essential",
    "libsndfile1"
]
python_packages = [
    "torch==2.0.1+cu118",
    "torchvision",
    "torchaudio",
    "transformers==4.40.0",
    "diffusers==0.27.0",
    "accelerate==0.30.0",
    "xformers==0.0.25.post1",
    "safetensors==0.4.2",
    "audiocraft==1.3.0",
    "TTS==0.22.0",
    "moviepy==1.0.3",
    "opencv-python==4.9.0.80",
    "llama-cpp-python==0.2.60",
    "fastapi==0.111.0",
    "uvicorn==0.30.0",
    "runpod==1.6.0",
    "psutil",
    "GPUtil"
]

[serverless]
gpu_types = ["A100-80G", "H100-80G"]
min_workers = 0
max_workers = 10
scale_type = "queue_delay"
scale_value = 5
container_disk_size_gb = 350

[runtime]
python_version = "3.8"
handler_file = "runpod_handler.py"
handler_function = "handler"
include_files = [
    "cinema_pipeline.py",
    "runpod_handler.py", 
    "download_models.py"
]
"""
    
    with open("runpod.toml", "w") as f:
        f.write(config)
    
    print("✅ Created runpod.toml")

def main():
    print("🎬 Push to RunPod using CLI")
    print("=" * 40)
    
    # Step 1: Check CLI
    if not check_runpod_cli():
        print("📦 Installing RunPod CLI...")
        subprocess.run(["pip", "install", "runpod"])
        if not check_runpod_cli():
            print("❌ Cannot proceed without RunPod CLI")
            return
    
    # Step 2: Configure RunPod
    if not configure_runpod():
        print("❌ Cannot proceed without configuration")
        return
    
    # Step 3: Create project config
    create_project_config()
    
    # Step 4: Build and push
    if build_and_push():
        print("\n🎉 Success! Your project is deployed!")
        print("🔗 Check: https://console.runpod.io/serverless")
    else:
        print("\n❌ Deployment failed")
        print("🔧 Try manual deployment in RunPod console")

if __name__ == "__main__":
    main() 