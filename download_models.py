#!/usr/bin/env python3
"""
Download models during Docker build (optional)
Skip this for faster builds, models will download on first run
"""

import os
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download

def download_models():
    print("Downloading models...")

    models = {
        # Add model downloads here if you want them in the image
        # This makes the image huge but speeds up cold starts
    }

    print("Model download complete (or skipped)")

if __name__ == "__main__":
    download_models()
