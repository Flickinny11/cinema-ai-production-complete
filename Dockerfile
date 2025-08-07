# Production Cinema AI Pipeline - H100/A100 80GB Optimized
# Updated August 2025 with latest models
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0" \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    TORCH_BACKENDS_CUDNN_BENCHMARK=1 \
    HF_HOME=/models/cache \
    DIFFUSERS_CACHE=/models/diffusers \
    AUDIOCRAFT_CACHE_DIR=/models/audiocraft

# Set PATH and LD_LIBRARY_PATH
ENV PATH=/usr/local/cuda/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-pip \
    git \
    git-lfs \
    wget \
    curl \
    ffmpeg \
    build-essential \
    libsndfile1 \
    libsndfile1-dev \
    libportaudio2 \
    portaudio19-dev \
    sox \
    libsox-dev \
    libsox-fmt-all \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3.10 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# Install PyTorch 2.3.0 with CUDA 12.1
RUN python3.10 -m pip install --no-cache-dir \
    torch==2.3.0 \
    torchvision==0.18.0 \
    torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install core ML packages
RUN python3.10 -m pip install --no-cache-dir \
    transformers==4.44.0 \
    diffusers==0.30.0 \
    accelerate==0.33.0 \
    safetensors==0.4.4 \
    sentencepiece==0.2.0 \
    protobuf==4.25.3

# Install xformers for memory efficiency
RUN python3.10 -m pip install --no-cache-dir \
    xformers==0.0.26.post1 \
    --index-url https://download.pytorch.org/whl/cu121

# Install video generation dependencies
RUN python3.10 -m pip install --no-cache-dir \
    einops==0.8.0 \
    scipy==1.13.0 \
    imageio==2.34.0 \
    imageio-ffmpeg==0.4.9 \
    opencv-python==4.10.0.84 \
    decord==0.6.0 \
    av==12.3.0

# Install audio packages
RUN python3.10 -m pip install --no-cache-dir \
    audiocraft==1.3.0 \
    librosa==0.10.2 \
    soundfile==0.12.1 \
    pydub==0.25.1 \
    pyaudio==0.2.14

# Install TTS packages (XTTS)
RUN python3.10 -m pip install --no-cache-dir \
    TTS==0.22.0 \
    gruut==2.4.0 \
    phonemizer==3.2.1

# Install Hugging Face Hub for model downloads
RUN python3.10 -m pip install --no-cache-dir \
    huggingface-hub==0.24.0 \
    hf-transfer==0.1.6

# Install video processing
RUN python3.10 -m pip install --no-cache-dir \
    moviepy==1.0.3 \
    ffmpeg-python==0.2.0 \
    scikit-video==1.1.11

# Install additional AI packages
RUN python3.10 -m pip install --no-cache-dir \
    timm==1.0.7 \
    omegaconf==2.3.0 \
    pytorch-lightning==2.3.0 \
    einops-exts==0.0.4 \
    rotary-embedding-torch==0.5.3

# Install API and utility packages
RUN python3.10 -m pip install --no-cache-dir \
    fastapi==0.111.0 \
    uvicorn==0.30.0 \
    runpod==1.6.0 \
    psutil==6.0.0 \
    GPUtil==1.4.0 \
    tqdm==4.66.4 \
    pyyaml==6.0.1

# Enable HF Transfer for faster downloads
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Create directories
RUN mkdir -p /models /models/cache /models/audiocraft /models/hunyuan /models/ltx \
    /models/musicgen /models/xtts /models/foley /app/output /app/temp

# Copy Python files
COPY cinema_pipeline.py /app/
COPY runpod_handler.py /app/
COPY download_models.py /app/
COPY model_configs.yaml /app/

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

WORKDIR /app

# Download base models during build (optional - comment out for faster builds)
# RUN python3.10 download_models.py --base-only

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]
