# 🎬 Cinema AI Production Deployment Guide

## Overview
This guide provides multiple methods to deploy your Cinema AI pipeline to RunPod serverless infrastructure.

## 🚀 Deployment Methods

### Method 1: Web Interface (Recommended)
**Easiest and most reliable method**

1. **Open RunPod Console**
   - Go to: https://runpod.io/console/serverless
   - Login with your RunPod account

2. **Create Custom Template**
   - Click 'Custom Templates' in left sidebar
   - Click 'New Template'
   - Fill in details:
     - **Name**: `cinema-ai-production`
     - **Dockerfile URL**: `https://raw.githubusercontent.com/Flickinny11/cinema-ai-production-complete/main/Dockerfile`
     - **Container Disk**: `350 GB`
     - **GPU Required**: `No` (for build)
   - Click 'Create Template'

3. **Wait for Build**
   - Build takes 60-90 minutes
   - You'll receive an email when ready
   - Check status in console

4. **Create Endpoint**
   - Go to 'Endpoints' in left sidebar
   - Click 'New Endpoint'
   - Fill in details:
     - **Template**: Select your `cinema-ai-production` template
     - **Name**: `cinema-ai-endpoint`
     - **GPU Type**: `A100 80GB`
     - **Min Workers**: `0`
     - **Max Workers**: `10`
     - **Scale Type**: `Queue Delay`
     - **Scale Value**: `5`
   - Click 'Create'

### Method 2: VS Code Extension
**For VS Code users**

1. **Install RunPod Extension**
   - Open VS Code
   - Go to Extensions (Cmd+Shift+X)
   - Search for "RunPod"
   - Install the official RunPod extension

2. **Configure Extension**
   - Open Command Palette (Cmd+Shift+P)
   - Type "RunPod: Configure"
   - Enter your API key: `pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e`

3. **Deploy**
   - Right-click on the `cinema-ai-production-complete` folder
   - Select "Deploy to RunPod"
   - Follow the prompts

### Method 3: RunPod CLI
**For command line users**

```bash
# Install RunPod CLI
pip install runpod

# Configure with API key
runpod config
# Enter: pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e

# Deploy from project directory
cd cinema-ai-production-complete
runpod project deploy
```

## 🧪 Testing Your Endpoint

### Health Check
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H 'Authorization: Bearer pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e' \
  -H 'Content-Type: application/json' \
  -d '{"input": {"type": "health_check"}}'
```

### Video Generation
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H 'Authorization: Bearer pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e' \
  -H 'Content-Type: application/json' \
  -d '{"input": {"type": "script_to_video", "script": "A beautiful sunset over the ocean"}}'
```

### Using the Test Script
```bash
# Test health check
python test_endpoint.py YOUR_ENDPOINT_ID

# Test video generation
python test_endpoint.py YOUR_ENDPOINT_ID "A beautiful sunset over the ocean"
```

## 💰 Cost Information

- **A100 80GB**: $2.49/hour (when active)
- **H100 80GB**: $3.99/hour (when active)
- **Serverless**: $0 when idle!
- **Cold start**: 30-45 seconds
- **Warm start**: <2 seconds

## ⚡ Performance

- **5s video**: 10-15 seconds to generate
- **30s video**: 45-60 seconds to generate
- **Only charged while processing!**

## 📁 Project Structure

```
cinema-ai-production-complete/
├── Dockerfile                 # Container definition
├── cinema_pipeline.py         # Main AI pipeline
├── runpod_handler.py          # Serverless handler
├── download_models.py         # Model downloader
├── test_local.py             # Local testing
├── test_endpoint.py          # Endpoint testing
├── deploy_web_interface.py   # Web deployment guide
├── deploy_with_registry.py   # Registry deployment
├── runpod.toml              # RunPod CLI config
└── README.md                # Project documentation
```

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check Dockerfile syntax
   - Ensure all dependencies are correct
   - Verify CUDA version compatibility

2. **Endpoint Not Responding**
   - Check if template build is complete
   - Verify endpoint configuration
   - Test with health check first

3. **Authentication Errors**
   - Verify API key is correct
   - Check API key permissions
   - Ensure account has credits

### Support

- **RunPod Documentation**: https://docs.runpod.io/
- **GitHub Repository**: https://github.com/Flickinny11/cinema-ai-production-complete
- **RunPod Console**: https://runpod.io/console/serverless

## 🎯 Next Steps

1. **Deploy using Method 1 (Web Interface)**
2. **Wait for build to complete (60-90 minutes)**
3. **Create endpoint from template**
4. **Test with health check**
5. **Generate your first video!**

---

**Created by**: Cinema AI Production Pipeline
**Repository**: https://github.com/Flickinny11/cinema-ai-production-complete
**API Key**: `pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e`
