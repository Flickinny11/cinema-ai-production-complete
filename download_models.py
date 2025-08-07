#!/usr/bin/env python3
"""
Download and cache models for Cinema AI Pipeline
August 2025 Edition
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
from transformers import AutoModel, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelDownloader:
    """Download and cache all required models"""

    MODELS = {
        "video": {
            "hunyuan": {
                "repo_id": "tencent/HunyuanVideo",
                "files": ["*.safetensors", "*.json", "*.txt"],
                "revision": "main",
                "cache_dir": "/models/hunyuan"
            },
            "ltx": {
                "repo_id": "Lightricks/LTX-Video",
                "files": ["*.safetensors", "*.json", "*.txt", "*.bin"],
                "revision": "main",
                "cache_dir": "/models/ltx"
            },
            "ltx_vae": {
                "repo_id": "Lightricks/ltxv-vae",
                "files": ["*.safetensors", "*.json"],
                "revision": "main",
                "cache_dir": "/models/ltx"
            }
        },
        "audio": {
            "musicgen": {
                "repo_id": "facebook/musicgen-large",
                "files": ["*.bin", "*.json", "*.txt"],
                "revision": "main",
                "cache_dir": "/models/musicgen"
            },
            "audiogen": {
                "repo_id": "facebook/audiogen-medium",
                "files": ["*.bin", "*.json", "*.txt"],
                "revision": "main",
                "cache_dir": "/models/audiogen"
            },
            "encodec": {
                "repo_id": "facebook/encodec_32khz",
                "files": ["*.bin", "*.json"],
                "revision": "main",
                "cache_dir": "/models/encodec"
            }
        },
        "tts": {
            "xtts": {
                "repo_id": "coqui/XTTS-v2",
                "files": ["*.pth", "*.json", "*.txt", "config.json", "vocab.json"],
                "revision": "main",
                "cache_dir": "/models/xtts"
            }
        },
        "text_encoders": {
            "clip": {
                "repo_id": "openai/clip-vit-large-patch14",
                "files": ["*.bin", "*.json", "*.txt"],
                "revision": "main",
                "cache_dir": "/models/clip"
            },
            "t5": {
                "repo_id": "google/flan-t5-xl",
                "files": ["*.safetensors", "*.json", "*.txt"],
                "revision": "main",
                "cache_dir": "/models/t5"
            }
        }
    }

    def __init__(self, base_only=False, specific_model=None):
        self.base_only = base_only
        self.specific_model = specific_model
        self.total_downloaded = 0
        self.failed_models = []

    def download_all(self):
        """Download all models"""
        logger.info("="*60)
        logger.info("🎬 Cinema AI Model Downloader")
        logger.info("="*60)

        if self.specific_model:
            self._download_specific_model()
        else:
            self._download_all_models()

        logger.info("="*60)
        logger.info(f"✅ Download complete!")
        logger.info(f"Total models downloaded: {self.total_downloaded}")

        if self.failed_models:
            logger.warning(f"⚠️ Failed models: {', '.join(self.failed_models)}")

        logger.info("="*60)

    def _download_all_models(self):
        """Download all model categories"""
        for category, models in self.MODELS.items():
            logger.info(f"\n📦 Downloading {category.upper()} models...")

            for model_name, config in models.items():
                if self.base_only and model_name not in ["ltx", "musicgen", "xtts"]:
                    logger.info(f"  ⏭️ Skipping {model_name} (base_only mode)")
                    continue

                self._download_model(model_name, config)

    def _download_specific_model(self):
        """Download a specific model"""
        found = False

        for category, models in self.MODELS.items():
            if self.specific_model in models:
                config = models[self.specific_model]
                logger.info(f"📦 Downloading {self.specific_model} from {category}")
                self._download_model(self.specific_model, config)
                found = True
                break

        if not found:
            logger.error(f"❌ Model '{self.specific_model}' not found")
            logger.info("Available models:")
            for category, models in self.MODELS.items():
                logger.info(f"  {category}: {', '.join(models.keys())}")

    def _download_model(self, name: str, config: Dict):
        """Download a single model"""
        logger.info(f"  📥 Downloading {name}...")

        try:
            # Create cache directory
            cache_dir = Path(config["cache_dir"])
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Check if already downloaded
            marker_file = cache_dir / f".{name}_downloaded"
            if marker_file.exists():
                logger.info(f"    ✅ Already downloaded")
                return

            # Download model
            if "files" in config:
                # Download specific files
                for pattern in config["files"]:
                    try:
                        if "*" in pattern:
                            # Download all files matching pattern
                            snapshot_download(
                                repo_id=config["repo_id"],
                                revision=config.get("revision", "main"),
                                cache_dir=cache_dir,
                                allow_patterns=pattern,
                                ignore_patterns=["*.md", "*.py"],
                                resume_download=True,
                                local_dir_use_symlinks=False
                            )
                        else:
                            # Download specific file
                            hf_hub_download(
                                repo_id=config["repo_id"],
                                filename=pattern,
                                revision=config.get("revision", "main"),
                                cache_dir=cache_dir,
                                resume_download=True,
                                local_dir_use_symlinks=False
                            )
                    except Exception as e:
                        logger.warning(f"    ⚠️ Could not download {pattern}: {e}")
            else:
                # Download entire repository
                snapshot_download(
                    repo_id=config["repo_id"],
                    revision=config.get("revision", "main"),
                    cache_dir=cache_dir,
                    ignore_patterns=["*.md", "*.py"],
                    resume_download=True,
                    local_dir_use_symlinks=False
                )

            # Create marker file
            marker_file.touch()

            self.total_downloaded += 1
            logger.info(f"    ✅ {name} downloaded successfully")

        except Exception as e:
            logger.error(f"    ❌ Failed to download {name}: {e}")
            self.failed_models.append(name)

    def verify_downloads(self):
        """Verify all models are downloaded"""
        logger.info("\n🔍 Verifying model downloads...")

        all_good = True

        for category, models in self.MODELS.items():
            for model_name, config in models.items():
                cache_dir = Path(config["cache_dir"])
                marker_file = cache_dir / f".{model_name}_downloaded"

                if marker_file.exists():
                    logger.info(f"  ✅ {model_name}: OK")
                else:
                    logger.warning(f"  ❌ {model_name}: Missing")
                    all_good = False

        if all_good:
            logger.info("\n✅ All models verified!")
        else:
            logger.warning("\n⚠️ Some models are missing. Run download again.")

        return all_good

    def estimate_size(self):
        """Estimate total download size"""
        sizes = {
            "hunyuan": "~50GB",
            "ltx": "~35GB",
            "musicgen": "~7GB",
            "audiogen": "~5GB",
            "xtts": "~2GB",
            "encodec": "~500MB",
            "clip": "~600MB",
            "t5": "~3GB"
        }

        logger.info("\n📊 Estimated model sizes:")
        total = 0

        for category, models in self.MODELS.items():
            category_total = 0
            logger.info(f"\n  {category.upper()}:")

            for model_name in models.keys():
                if model_name in sizes:
                    logger.info(f"    • {model_name}: {sizes[model_name]}")

        logger.info(f"\n  Total estimated size: ~100GB")
        logger.info("  Note: Actual size may vary")

def main():
    parser = argparse.ArgumentParser(description="Download models for Cinema AI")
    parser.add_argument("--base-only", action="store_true",
                      help="Download only base models (faster)")
    parser.add_argument("--model", type=str,
                      help="Download specific model")
    parser.add_argument("--verify", action="store_true",
                      help="Verify downloads only")
    parser.add_argument("--estimate", action="store_true",
                      help="Estimate download sizes")

    args = parser.parse_args()

    downloader = ModelDownloader(
        base_only=args.base_only,
        specific_model=args.model
    )

    if args.estimate:
        downloader.estimate_size()
    elif args.verify:
        downloader.verify_downloads()
    else:
        downloader.download_all()
        downloader.verify_downloads()

if __name__ == "__main__":
    main()
