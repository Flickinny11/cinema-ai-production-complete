#!/usr/bin/env python3
"""
Deploy Cinema AI using RunPod Web Interface
This script provides step-by-step instructions for manual deployment
"""

import webbrowser
import time

def open_runpod_console():
    """Open RunPod console in browser"""
    print("🌐 Opening RunPod Console...")
    webbrowser.open("https://runpod.io/console/serverless")

def print_deployment_instructions():
    """Print step-by-step deployment instructions"""
    print("🎬 Cinema AI Deployment Instructions")
    print("=" * 50)
    print()
    print("📋 Step-by-Step Manual Deployment:")
    print()
    print("1️⃣  OPEN RUNPOD CONSOLE")
    print("   • Go to: https://runpod.io/console/serverless")
    print("   • Login with your RunPod account")
    print()
    print("2️⃣  CREATE CUSTOM TEMPLATE")
    print("   • Click 'Custom Templates' in left sidebar")
    print("   • Click 'New Template'")
    print("   • Fill in these details:")
    print("     - Name: cinema-ai-production")
    print("     - Dockerfile URL: https://raw.githubusercontent.com/Flickinny11/cinema-ai-production-complete/main/Dockerfile")
    print("     - Container Disk: 350 GB")
    print("     - GPU Required: No (for build)")
    print("   • Click 'Create Template'")
    print()
    print("3️⃣  WAIT FOR BUILD")
    print("   • Build takes 60-90 minutes")
    print("   • You'll get an email when ready")
    print("   • Check status in console")
    print()
    print("4️⃣  CREATE ENDPOINT")
    print("   • Go to 'Endpoints' in left sidebar")
    print("   • Click 'New Endpoint'")
    print("   • Fill in these details:")
    print("     - Template: Select your cinema-ai-production template")
    print("     - Name: cinema-ai-endpoint")
    print("     - GPU Type: A100 80GB")
    print("     - Min Workers: 0")
    print("     - Max Workers: 10")
    print("     - Scale Type: Queue Delay")
    print("     - Scale Value: 5")
    print("   • Click 'Create'")
    print()
    print("5️⃣  GET YOUR ENDPOINT ID")
    print("   • Copy the endpoint ID from the endpoint page")
    print("   • Your endpoint URL: https://api.runpod.ai/v2/YOUR_ENDPOINT_ID")
    print()
    print("6️⃣  TEST YOUR ENDPOINT")
    print("   Replace YOUR_ENDPOINT_ID with your actual endpoint ID:")
    print()
    print("   curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \\")
    print("     -H 'Authorization: Bearer pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"input\": {\"type\": \"health_check\"}}'")
    print()
    print("💰 COST INFORMATION:")
    print("   • A100 80GB: $2.49/hour (when active)")
    print("   • Serverless: $0 when idle!")
    print("   • Cold start: 30-45 seconds")
    print("   • Warm start: <2 seconds")
    print()
    print("⚡ PERFORMANCE:")
    print("   • 5s video: 10-15 seconds to generate")
    print("   • 30s video: 45-60 seconds to generate")
    print("   • Only charged while processing!")

def main():
    """Main function"""
    print_deployment_instructions()

    # Ask if user wants to open RunPod console
    response = input("\n🤔 Would you like to open the RunPod console now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        open_runpod_console()

    print("\n✅ Instructions complete! Follow the steps above to deploy your Cinema AI pipeline.")

if __name__ == "__main__":
    main()
