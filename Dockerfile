# Production Cinema AI Pipeline - H100/A100 80GB Optimized
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=${CUDA_HOME}/bin:${PATH} \
    LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH} \
    TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0" \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    TORCH_BACKENDS_CUDNN_BENCHMARK=1 \
    HF_HOME=/models/cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip git git-lfs wget curl ffmpeg \
    build-essential libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
RUN pip3 install --no-cache-dir \
    torch==2.2.0+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    transformers==4.40.0 diffusers==0.27.0 accelerate==0.30.0 \
    xformers==0.0.25.post1 safetensors==0.4.2 \
    audiocraft==1.3.0 TTS==0.22.0 \
    moviepy==1.0.3 opencv-python==4.9.0.80 \
    llama-cpp-python==0.2.60 \
    fastapi==0.111.0 uvicorn==0.30.0 \
    runpod==1.6.0 psutil GPUtil

# Create directories
RUN mkdir -p /models /app/output /app/temp

# Copy Python files (we'll create these next)
COPY cinema_pipeline.py /app/
COPY runpod_handler.py /app/
COPY download_models.py /app/

# Download models during build (optional - can skip for faster builds)
# RUN python3 /app/download_models.py

WORKDIR /app
ENTRYPOINT ["python3", "-u", "runpod_handler.py"]
