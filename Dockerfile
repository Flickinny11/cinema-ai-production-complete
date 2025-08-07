# Production Cinema AI Pipeline - H100/A100 80GB Optimized
FROM nvidia/cuda:11.8.0-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0" \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    TORCH_BACKENDS_CUDNN_BENCHMARK=1 \
    HF_HOME=/models/cache

# Set PATH and LD_LIBRARY_PATH using absolute paths
ENV PATH=/usr/local/cuda/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3-pip \
    git \
    git-lfs \
    wget \
    curl \
    ffmpeg \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is using Python 3.8
RUN python3.8 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# Install PyTorch first with explicit CUDA version
RUN python3.8 -m pip install --no-cache-dir \
    torch==2.0.1+cu118 \
    torchvision==0.15.2+cu118 \
    torchaudio==2.0.2+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

# Install core ML packages
RUN python3.8 -m pip install --no-cache-dir \
    transformers==4.40.0 \
    diffusers==0.27.0 \
    accelerate==0.30.0 \
    safetensors==0.4.2

# Install xformers compatible with PyTorch 2.0.1
RUN python3.8 -m pip install --no-cache-dir \
    xformers==0.0.20 \
    --index-url https://download.pytorch.org/whl/cu118

# Install audio packages (these can be problematic, install separately)
RUN python3.8 -m pip install --no-cache-dir audiocraft==1.3.0 || \
    python3.8 -m pip install --no-cache-dir audiocraft

RUN python3.8 -m pip install --no-cache-dir TTS==0.22.0 || \
    python3.8 -m pip install --no-cache-dir TTS

# Install video and image processing
RUN python3.8 -m pip install --no-cache-dir \
    moviepy==1.0.3 \
    opencv-python==4.9.0.80

# Install llama-cpp-python with CUDA support
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
RUN python3.8 -m pip install --no-cache-dir llama-cpp-python==0.2.60

# Install API and utility packages
RUN python3.8 -m pip install --no-cache-dir \
    fastapi==0.111.0 \
    uvicorn==0.30.0 \
    runpod==1.6.0 \
    psutil \
    GPUtil

# Create directories
RUN mkdir -p /models /app/output /app/temp

# Copy Python files
COPY cinema_pipeline.py /app/
COPY runpod_handler.py /app/
COPY download_models.py /app/

# Set Python 3.8 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

WORKDIR /app

# Use python3.8 explicitly in the entrypoint
ENTRYPOINT ["python3.8", "-u", "runpod_handler.py"]
